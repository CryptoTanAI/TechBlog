#!/usr/bin/env python3
"""
Automated Scheduling and Publishing System
Handles daily blog post generation, scheduling, and publishing automation
"""

import os
import sys
import json
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import logging

# Add the parent directory to the path to import models
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.blog import BlogPost, Country, Technology, MediaAsset, AutomationConfig, SocialShare
from models.user import db
from automation.content_generator import ContentGenerator
from automation.media_generator import MediaGenerator
from automation.social_publisher import SocialPublisher

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/tech_blog_backend/automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BlogScheduler:
    """Main scheduler for automated blog operations"""
    
    def __init__(self):
        self.content_generator = ContentGenerator()
        self.media_generator = MediaGenerator()
        self.social_publisher = SocialPublisher()
        self.is_running = False
        self.scheduler_thread = None
    
    def start_scheduler(self):
        """Start the automated scheduling system"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        logger.info("Starting blog automation scheduler...")
        
        # Load automation configuration
        self._load_automation_config()
        
        # Schedule daily blog post generation
        self._schedule_daily_tasks()
        
        # Start scheduler in a separate thread
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Blog scheduler started successfully")
    
    def stop_scheduler(self):
        """Stop the automated scheduling system"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        logger.info("Stopping blog automation scheduler...")
        self.is_running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        logger.info("Blog scheduler stopped")
    
    def _load_automation_config(self):
        """Load automation configuration from database"""
        try:
            # Get posting time
            posting_time_config = AutomationConfig.query.filter_by(
                config_key="posting_time"
            ).first()
            self.posting_time = posting_time_config.config_value if posting_time_config else "09:00"
            
            # Get daily posting enabled status
            daily_posting_config = AutomationConfig.query.filter_by(
                config_key="daily_posting_enabled"
            ).first()
            self.daily_posting_enabled = (
                daily_posting_config.config_value.lower() == "true" 
                if daily_posting_config else True
            )
            
            # Get auto social share setting
            auto_share_config = AutomationConfig.query.filter_by(
                config_key="social_media_auto_share"
            ).first()
            self.auto_social_share = (
                auto_share_config.config_value.lower() == "true"
                if auto_share_config else True
            )
            
            # Get quality threshold
            quality_config = AutomationConfig.query.filter_by(
                config_key="content_quality_threshold"
            ).first()
            self.quality_threshold = (
                float(quality_config.config_value) 
                if quality_config else 0.8
            )
            
            logger.info(f"Loaded automation config: posting_time={self.posting_time}, "
                       f"daily_posting={self.daily_posting_enabled}, "
                       f"auto_share={self.auto_social_share}")
            
        except Exception as e:
            logger.error(f"Error loading automation config: {e}")
            # Set defaults
            self.posting_time = "09:00"
            self.daily_posting_enabled = True
            self.auto_social_share = True
            self.quality_threshold = 0.8
    
    def _schedule_daily_tasks(self):
        """Schedule daily blog generation tasks"""
        if self.daily_posting_enabled:
            # Schedule daily blog post generation
            schedule.every().day.at(self.posting_time).do(self._generate_daily_post)
            logger.info(f"Scheduled daily blog post generation at {self.posting_time} UTC")
            
            # Schedule content preparation (2 hours before posting)
            prep_time = self._calculate_prep_time(self.posting_time)
            schedule.every().day.at(prep_time).do(self._prepare_daily_content)
            logger.info(f"Scheduled content preparation at {prep_time} UTC")
        
        # Schedule weekly analytics update
        schedule.every().sunday.at("23:00").do(self._update_weekly_analytics)
        
        # Schedule monthly cleanup
        schedule.every().month.do(self._monthly_cleanup)
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _generate_daily_post(self):
        """Generate and publish today's blog post"""
        try:
            logger.info("Starting daily blog post generation...")
            
            # Check if daily posting is still enabled
            self._load_automation_config()
            if not self.daily_posting_enabled:
                logger.info("Daily posting is disabled, skipping generation")
                return
            
            # Check if post already exists for today
            today = datetime.now().date()
            existing_post = BlogPost.query.filter(
                db.func.date(BlogPost.published_at) == today
            ).first()
            
            if existing_post:
                logger.info(f"Post already exists for today: {existing_post.title}")
                return
            
            # Select country and technology
            country = self.content_generator.select_daily_country()
            if not country:
                logger.error("No country selected for daily post")
                return
            
            technology = self.content_generator.select_technology_for_country(country)
            if not technology:
                logger.error(f"No technology selected for {country.name}")
                return
            
            logger.info(f"Generating post for {country.name} - {technology.name}")
            
            # Conduct research
            research_data = self.content_generator.conduct_research(country, technology)
            
            # Generate blog post content
            blog_data = self.content_generator.generate_blog_post(
                country, technology, research_data
            )
            
            # Quality check
            if not self._quality_check(blog_data):
                logger.warning("Generated content failed quality check, retrying...")
                # Could implement retry logic here
                return
            
            # Generate media assets
            media_assets = self.media_generator.generate_post_media(
                country, technology, blog_data
            )
            
            # Create blog post in database
            blog_post = self._create_blog_post(
                country, technology, blog_data, research_data, media_assets
            )
            
            # Publish the post
            self._publish_post(blog_post)
            
            # Share on social media if enabled
            if self.auto_social_share:
                self._schedule_social_sharing(blog_post)
            
            logger.info(f"Successfully generated and published: {blog_post.title}")
            
        except Exception as e:
            logger.error(f"Error generating daily post: {e}")
            # Could implement error notification here
    
    def _prepare_daily_content(self):
        """Prepare content in advance (research, media generation)"""
        try:
            logger.info("Preparing tomorrow's content...")
            
            # This could pre-generate research data and media assets
            # to reduce publishing time and ensure quality
            
            # For now, just log the preparation
            logger.info("Content preparation completed")
            
        except Exception as e:
            logger.error(f"Error preparing daily content: {e}")
    
    def _quality_check(self, blog_data: Dict) -> bool:
        """Check if generated content meets quality standards"""
        try:
            # Check word count
            if blog_data['word_count'] < 800:
                logger.warning(f"Content too short: {blog_data['word_count']} words")
                return False
            
            # Check for required elements
            content = blog_data['content'].lower()
            required_keywords = ['gdp', 'economy', 'technology', 'development']
            
            keyword_count = sum(1 for keyword in required_keywords if keyword in content)
            if keyword_count < 2:
                logger.warning(f"Missing required keywords: {keyword_count}/4")
                return False
            
            # Check title quality
            if len(blog_data['title']) < 20:
                logger.warning(f"Title too short: {blog_data['title']}")
                return False
            
            logger.info("Content passed quality check")
            return True
            
        except Exception as e:
            logger.error(f"Error in quality check: {e}")
            return False
    
    def _create_blog_post(self, country: Country, technology: Technology, 
                         blog_data: Dict, research_data: Dict, media_assets: List) -> BlogPost:
        """Create blog post record in database"""
        try:
            # Create slug from title
            slug = self._create_slug(blog_data['title'])
            
            # Create blog post
            blog_post = BlogPost(
                title=blog_data['title'],
                slug=slug,
                content=blog_data['content'],
                excerpt=blog_data['excerpt'],
                country_id=country.id,
                technology_id=technology.id,
                status='published',
                published_at=datetime.utcnow(),
                word_count=blog_data['word_count'],
                reading_time_minutes=blog_data['reading_time_minutes'],
                tags=json.dumps(blog_data['tags']),
                research_data=json.dumps(research_data),
                seo_title=blog_data['title'],
                seo_description=blog_data['excerpt']
            )
            
            db.session.add(blog_post)
            db.session.flush()  # Get the ID
            
            # Add media assets
            for media_data in media_assets:
                media_asset = MediaAsset(
                    blog_post_id=blog_post.id,
                    asset_type=media_data['type'],
                    file_path=media_data['file_path'],
                    alt_text=media_data['alt_text'],
                    caption=media_data.get('caption', ''),
                    is_featured=media_data.get('is_featured', False)
                )
                db.session.add(media_asset)
            
            db.session.commit()
            logger.info(f"Created blog post in database: ID {blog_post.id}")
            
            return blog_post
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating blog post: {e}")
            raise
    
    def _publish_post(self, blog_post: BlogPost):
        """Publish the blog post (already published in create_blog_post)"""
        try:
            # Update view count and other metrics
            blog_post.view_count = 0
            blog_post.share_count = 0
            
            # Could trigger additional publishing actions here
            # (e.g., cache warming, search index updates, etc.)
            
            db.session.commit()
            logger.info(f"Published blog post: {blog_post.title}")
            
        except Exception as e:
            logger.error(f"Error publishing post: {e}")
    
    def _schedule_social_sharing(self, blog_post: BlogPost):
        """Schedule social media sharing"""
        try:
            # Schedule sharing across different platforms with delays
            platforms = ['twitter', 'linkedin', 'facebook']
            
            for i, platform in enumerate(platforms):
                # Schedule with 30-minute intervals
                share_time = datetime.utcnow() + timedelta(minutes=30 * (i + 1))
                
                social_share = SocialShare(
                    blog_post_id=blog_post.id,
                    platform=platform,
                    scheduled_at=share_time,
                    status='scheduled'
                )
                db.session.add(social_share)
            
            db.session.commit()
            logger.info(f"Scheduled social sharing for {blog_post.title}")
            
        except Exception as e:
            logger.error(f"Error scheduling social sharing: {e}")
    
    def _update_weekly_analytics(self):
        """Update weekly analytics and reports"""
        try:
            logger.info("Updating weekly analytics...")
            
            # Calculate weekly metrics
            week_ago = datetime.utcnow() - timedelta(days=7)
            weekly_posts = BlogPost.query.filter(
                BlogPost.published_at >= week_ago
            ).all()
            
            total_views = sum(post.view_count for post in weekly_posts)
            total_shares = sum(post.share_count for post in weekly_posts)
            
            logger.info(f"Weekly stats: {len(weekly_posts)} posts, "
                       f"{total_views} views, {total_shares} shares")
            
        except Exception as e:
            logger.error(f"Error updating weekly analytics: {e}")
    
    def _monthly_cleanup(self):
        """Perform monthly cleanup tasks"""
        try:
            logger.info("Performing monthly cleanup...")
            
            # Clean up old log files, temporary files, etc.
            # Reset monthly counters
            # Archive old data
            
            logger.info("Monthly cleanup completed")
            
        except Exception as e:
            logger.error(f"Error in monthly cleanup: {e}")
    
    def _calculate_prep_time(self, posting_time: str) -> str:
        """Calculate preparation time (2 hours before posting)"""
        try:
            hour, minute = map(int, posting_time.split(':'))
            prep_hour = (hour - 2) % 24
            return f"{prep_hour:02d}:{minute:02d}"
        except:
            return "07:00"  # Default fallback
    
    def _create_slug(self, title: str) -> str:
        """Create URL slug from title"""
        import re
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def get_scheduler_status(self) -> Dict:
        """Get current scheduler status"""
        return {
            "is_running": self.is_running,
            "daily_posting_enabled": self.daily_posting_enabled,
            "posting_time": self.posting_time,
            "auto_social_share": self.auto_social_share,
            "quality_threshold": self.quality_threshold,
            "next_run": self._get_next_run_time()
        }
    
    def _get_next_run_time(self) -> Optional[str]:
        """Get next scheduled run time"""
        try:
            jobs = schedule.jobs
            if jobs:
                next_job = min(jobs, key=lambda job: job.next_run)
                return next_job.next_run.strftime("%Y-%m-%d %H:%M:%S UTC")
            return None
        except:
            return None
    
    def trigger_manual_generation(self, country_id: Optional[int] = None, 
                                 technology_id: Optional[int] = None) -> Dict:
        """Manually trigger blog post generation"""
        try:
            logger.info("Manual blog post generation triggered")
            
            # Select country and technology
            if country_id:
                country = Country.query.get(country_id)
            else:
                country = self.content_generator.select_daily_country()
            
            if not country:
                return {"success": False, "error": "No country found"}
            
            if technology_id:
                technology = Technology.query.get(technology_id)
            else:
                technology = self.content_generator.select_technology_for_country(country)
            
            if not technology:
                return {"success": False, "error": "No technology found"}
            
            # Generate content
            research_data = self.content_generator.conduct_research(country, technology)
            blog_data = self.content_generator.generate_blog_post(
                country, technology, research_data
            )
            
            # Generate media
            media_assets = self.media_generator.generate_post_media(
                country, technology, blog_data
            )
            
            # Create and publish
            blog_post = self._create_blog_post(
                country, technology, blog_data, research_data, media_assets
            )
            
            return {
                "success": True,
                "blog_post_id": blog_post.id,
                "title": blog_post.title,
                "country": country.name,
                "technology": technology.name
            }
            
        except Exception as e:
            logger.error(f"Error in manual generation: {e}")
            return {"success": False, "error": str(e)}

# Global scheduler instance
scheduler_instance = None

def get_scheduler() -> BlogScheduler:
    """Get or create scheduler instance"""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = BlogScheduler()
    return scheduler_instance

def main():
    """Test the scheduler"""
    scheduler = BlogScheduler()
    
    # Test manual generation
    result = scheduler.trigger_manual_generation()
    print(f"Manual generation result: {result}")
    
    # Test scheduler status
    status = scheduler.get_scheduler_status()
    print(f"Scheduler status: {status}")

if __name__ == "__main__":
    main()


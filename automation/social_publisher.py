#!/usr/bin/env python3
"""
Automated Social Media Publishing System
Handles sharing blog posts across various social media platforms
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Add the parent directory to the path to import models
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.blog import BlogPost, SocialShare, MediaAsset
from models.user import db

logger = logging.getLogger(__name__)

class SocialPublisher:
    """Handles automated social media publishing"""
    
    def __init__(self):
        self.platform_configs = self._load_platform_configs()
        self.base_url = "https://techsouth.blog"  # Will be updated with actual domain
    
    def _load_platform_configs(self) -> Dict:
        """Load social media platform configurations"""
        # In production, these would be loaded from environment variables or config
        return {
            "twitter": {
                "enabled": True,
                "api_key": os.getenv("TWITTER_API_KEY", ""),
                "api_secret": os.getenv("TWITTER_API_SECRET", ""),
                "access_token": os.getenv("TWITTER_ACCESS_TOKEN", ""),
                "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET", ""),
                "character_limit": 280,
                "hashtag_limit": 2
            },
            "linkedin": {
                "enabled": True,
                "access_token": os.getenv("LINKEDIN_ACCESS_TOKEN", ""),
                "company_id": os.getenv("LINKEDIN_COMPANY_ID", ""),
                "character_limit": 3000,
                "hashtag_limit": 5
            },
            "facebook": {
                "enabled": True,
                "access_token": os.getenv("FACEBOOK_ACCESS_TOKEN", ""),
                "page_id": os.getenv("FACEBOOK_PAGE_ID", ""),
                "character_limit": 63206,
                "hashtag_limit": 30
            },
            "medium": {
                "enabled": True,
                "integration_token": os.getenv("MEDIUM_INTEGRATION_TOKEN", ""),
                "author_id": os.getenv("MEDIUM_AUTHOR_ID", ""),
                "publication_id": os.getenv("MEDIUM_PUBLICATION_ID", "")
            }
        }
    
    def publish_to_social_media(self, blog_post: BlogPost, platforms: List[str] = None) -> Dict:
        """Publish blog post to specified social media platforms"""
        if platforms is None:
            platforms = ["twitter", "linkedin", "facebook"]
        
        results = {}
        
        for platform in platforms:
            if platform in self.platform_configs and self.platform_configs[platform]["enabled"]:
                try:
                    result = self._publish_to_platform(blog_post, platform)
                    results[platform] = result
                    
                    # Record the social share
                    self._record_social_share(blog_post.id, platform, result)
                    
                except Exception as e:
                    logger.error(f"Error publishing to {platform}: {e}")
                    results[platform] = {"success": False, "error": str(e)}
            else:
                results[platform] = {"success": False, "error": "Platform not configured"}
        
        return results
    
    def _publish_to_platform(self, blog_post: BlogPost, platform: str) -> Dict:
        """Publish to a specific platform"""
        if platform == "twitter":
            return self._publish_to_twitter(blog_post)
        elif platform == "linkedin":
            return self._publish_to_linkedin(blog_post)
        elif platform == "facebook":
            return self._publish_to_facebook(blog_post)
        elif platform == "medium":
            return self._publish_to_medium(blog_post)
        else:
            return {"success": False, "error": f"Unknown platform: {platform}"}
    
    def _publish_to_twitter(self, blog_post: BlogPost) -> Dict:
        """Publish blog post to Twitter/X"""
        try:
            config = self.platform_configs["twitter"]
            
            # Create tweet content
            tweet_content = self._create_twitter_content(blog_post)
            
            # Get featured image for media attachment
            featured_media = self._get_featured_media(blog_post)
            
            # In production, this would use the Twitter API
            # For now, simulate the API call
            logger.info(f"Publishing to Twitter: {tweet_content[:50]}...")
            
            # Simulate successful API response
            response = {
                "success": True,
                "post_id": f"twitter_{blog_post.id}_{int(datetime.now().timestamp())}",
                "url": f"https://twitter.com/techsouth/status/123456789",
                "platform": "twitter",
                "content": tweet_content
            }
            
            logger.info(f"Successfully published to Twitter: {response['url']}")
            return response
            
        except Exception as e:
            logger.error(f"Error publishing to Twitter: {e}")
            return {"success": False, "error": str(e)}
    
    def _publish_to_linkedin(self, blog_post: BlogPost) -> Dict:
        """Publish blog post to LinkedIn"""
        try:
            config = self.platform_configs["linkedin"]
            
            # Create LinkedIn post content
            linkedin_content = self._create_linkedin_content(blog_post)
            
            # Get featured image
            featured_media = self._get_featured_media(blog_post)
            
            logger.info(f"Publishing to LinkedIn: {linkedin_content[:50]}...")
            
            # Simulate LinkedIn API call
            response = {
                "success": True,
                "post_id": f"linkedin_{blog_post.id}_{int(datetime.now().timestamp())}",
                "url": f"https://linkedin.com/feed/update/urn:li:share:123456789",
                "platform": "linkedin",
                "content": linkedin_content
            }
            
            logger.info(f"Successfully published to LinkedIn: {response['url']}")
            return response
            
        except Exception as e:
            logger.error(f"Error publishing to LinkedIn: {e}")
            return {"success": False, "error": str(e)}
    
    def _publish_to_facebook(self, blog_post: BlogPost) -> Dict:
        """Publish blog post to Facebook"""
        try:
            config = self.platform_configs["facebook"]
            
            # Create Facebook post content
            facebook_content = self._create_facebook_content(blog_post)
            
            # Get featured image
            featured_media = self._get_featured_media(blog_post)
            
            logger.info(f"Publishing to Facebook: {facebook_content[:50]}...")
            
            # Simulate Facebook API call
            response = {
                "success": True,
                "post_id": f"facebook_{blog_post.id}_{int(datetime.now().timestamp())}",
                "url": f"https://facebook.com/techsouth/posts/123456789",
                "platform": "facebook",
                "content": facebook_content
            }
            
            logger.info(f"Successfully published to Facebook: {response['url']}")
            return response
            
        except Exception as e:
            logger.error(f"Error publishing to Facebook: {e}")
            return {"success": False, "error": str(e)}
    
    def _publish_to_medium(self, blog_post: BlogPost) -> Dict:
        """Publish full blog post to Medium"""
        try:
            config = self.platform_configs["medium"]
            
            # Create Medium article content
            medium_content = self._create_medium_content(blog_post)
            
            logger.info(f"Publishing to Medium: {blog_post.title}")
            
            # Simulate Medium API call
            response = {
                "success": True,
                "post_id": f"medium_{blog_post.id}_{int(datetime.now().timestamp())}",
                "url": f"https://medium.com/@techsouth/{blog_post.slug}",
                "platform": "medium",
                "title": blog_post.title
            }
            
            logger.info(f"Successfully published to Medium: {response['url']}")
            return response
            
        except Exception as e:
            logger.error(f"Error publishing to Medium: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_twitter_content(self, blog_post: BlogPost) -> str:
        """Create Twitter-optimized content"""
        config = self.platform_configs["twitter"]
        
        # Get country and technology info
        country = blog_post.country
        technology = blog_post.technology
        
        # Create base tweet
        base_tweet = f"🌍 How {technology.name} is transforming {country.name}'s economy"
        
        # Add blog link
        blog_url = f"{self.base_url}/blog/{blog_post.slug}"
        
        # Add hashtags
        hashtags = self._get_platform_hashtags("twitter", blog_post)
        hashtag_text = " ".join(hashtags[:config["hashtag_limit"]])
        
        # Construct tweet within character limit
        tweet_parts = [base_tweet, blog_url, hashtag_text]
        tweet = " ".join(part for part in tweet_parts if part)
        
        # Truncate if necessary
        if len(tweet) > config["character_limit"]:
            available_chars = config["character_limit"] - len(blog_url) - len(hashtag_text) - 2
            truncated_base = base_tweet[:available_chars] + "..."
            tweet = f"{truncated_base} {blog_url} {hashtag_text}"
        
        return tweet.strip()
    
    def _create_linkedin_content(self, blog_post: BlogPost) -> str:
        """Create LinkedIn-optimized content"""
        config = self.platform_configs["linkedin"]
        
        country = blog_post.country
        technology = blog_post.technology
        
        # Create engaging LinkedIn post
        content_parts = [
            f"🚀 {technology.name} is revolutionizing economic development in {country.name}",
            "",
            blog_post.excerpt,
            "",
            f"Key insights from our latest analysis:",
            f"💡 GDP growth potential through technology adoption",
            f"🌱 Poverty alleviation through digital inclusion", 
            f"🏛️ Government service transformation",
            f"📈 Real-world impact on citizens' lives",
            "",
            f"Read the full story: {self.base_url}/blog/{blog_post.slug}",
            "",
            " ".join(self._get_platform_hashtags("linkedin", blog_post)[:config["hashtag_limit"]])
        ]
        
        content = "\n".join(content_parts)
        
        # Ensure within character limit
        if len(content) > config["character_limit"]:
            # Truncate excerpt if needed
            max_excerpt_length = config["character_limit"] - 500  # Reserve space for other content
            if len(blog_post.excerpt) > max_excerpt_length:
                truncated_excerpt = blog_post.excerpt[:max_excerpt_length] + "..."
                content = content.replace(blog_post.excerpt, truncated_excerpt)
        
        return content
    
    def _create_facebook_content(self, blog_post: BlogPost) -> str:
        """Create Facebook-optimized content"""
        config = self.platform_configs["facebook"]
        
        country = blog_post.country
        technology = blog_post.technology
        
        # Create Facebook post
        content_parts = [
            f"🌍 Discover how {technology.name} is transforming lives in {country.name}",
            "",
            blog_post.excerpt,
            "",
            f"Our latest deep-dive explores:",
            f"📊 Economic impact and GDP growth",
            f"👥 How technology reduces poverty",
            f"🏛️ Government innovation and citizen services",
            f"🔮 Future opportunities and challenges",
            "",
            f"Read more: {self.base_url}/blog/{blog_post.slug}",
            "",
            " ".join(self._get_platform_hashtags("facebook", blog_post)[:config["hashtag_limit"]])
        ]
        
        return "\n".join(content_parts)
    
    def _create_medium_content(self, blog_post: BlogPost) -> Dict:
        """Create Medium article content"""
        # For Medium, we publish the full article
        return {
            "title": blog_post.title,
            "content": blog_post.content,
            "tags": json.loads(blog_post.tags)[:5],  # Medium allows up to 5 tags
            "publishStatus": "public",
            "contentFormat": "markdown",
            "canonicalUrl": f"{self.base_url}/blog/{blog_post.slug}"
        }
    
    def _get_platform_hashtags(self, platform: str, blog_post: BlogPost) -> List[str]:
        """Get platform-specific hashtags"""
        base_tags = json.loads(blog_post.tags) if blog_post.tags else []
        
        # Convert to hashtags
        hashtags = [f"#{tag.replace(' ', '').replace('-', '')}" for tag in base_tags]
        
        # Add platform-specific hashtags
        platform_hashtags = {
            "twitter": ["#TechForGood", "#GlobalSouth", "#Innovation"],
            "linkedin": ["#TechnologyTransformation", "#EconomicDevelopment", "#DigitalInnovation"],
            "facebook": ["#TechNews", "#GlobalDevelopment", "#Innovation"]
        }
        
        if platform in platform_hashtags:
            hashtags.extend(platform_hashtags[platform])
        
        # Remove duplicates and return
        return list(dict.fromkeys(hashtags))
    
    def _get_featured_media(self, blog_post: BlogPost) -> Optional[Dict]:
        """Get featured media asset for social sharing"""
        try:
            featured_media = MediaAsset.query.filter_by(
                blog_post_id=blog_post.id,
                is_featured=True
            ).first()
            
            if featured_media:
                return {
                    "type": featured_media.asset_type,
                    "url": f"{self.base_url}{featured_media.file_path}",
                    "alt_text": featured_media.alt_text
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting featured media: {e}")
            return None
    
    def _record_social_share(self, blog_post_id: int, platform: str, result: Dict):
        """Record social media share in database"""
        try:
            social_share = SocialShare(
                blog_post_id=blog_post_id,
                platform=platform,
                shared_at=datetime.utcnow(),
                status='published' if result.get('success') else 'failed',
                platform_post_id=result.get('post_id', ''),
                platform_url=result.get('url', ''),
                error_message=result.get('error', '') if not result.get('success') else None
            )
            
            db.session.add(social_share)
            db.session.commit()
            
            logger.info(f"Recorded social share: {platform} for post {blog_post_id}")
            
        except Exception as e:
            logger.error(f"Error recording social share: {e}")
            db.session.rollback()
    
    def schedule_social_shares(self, blog_post: BlogPost, delay_minutes: int = 30) -> List[Dict]:
        """Schedule social media shares with delays"""
        scheduled_shares = []
        platforms = ["twitter", "linkedin", "facebook"]
        
        for i, platform in enumerate(platforms):
            try:
                share_time = datetime.utcnow() + timedelta(minutes=delay_minutes * (i + 1))
                
                social_share = SocialShare(
                    blog_post_id=blog_post.id,
                    platform=platform,
                    scheduled_at=share_time,
                    status='scheduled'
                )
                
                db.session.add(social_share)
                scheduled_shares.append({
                    "platform": platform,
                    "scheduled_at": share_time,
                    "status": "scheduled"
                })
                
            except Exception as e:
                logger.error(f"Error scheduling {platform} share: {e}")
        
        try:
            db.session.commit()
            logger.info(f"Scheduled {len(scheduled_shares)} social shares")
        except Exception as e:
            logger.error(f"Error committing scheduled shares: {e}")
            db.session.rollback()
        
        return scheduled_shares
    
    def process_scheduled_shares(self):
        """Process scheduled social media shares"""
        try:
            # Get shares scheduled for now or earlier
            current_time = datetime.utcnow()
            scheduled_shares = SocialShare.query.filter(
                SocialShare.status == 'scheduled',
                SocialShare.scheduled_at <= current_time
            ).all()
            
            for share in scheduled_shares:
                try:
                    blog_post = BlogPost.query.get(share.blog_post_id)
                    if blog_post:
                        result = self._publish_to_platform(blog_post, share.platform)
                        
                        # Update share record
                        share.shared_at = datetime.utcnow()
                        share.status = 'published' if result.get('success') else 'failed'
                        share.platform_post_id = result.get('post_id', '')
                        share.platform_url = result.get('url', '')
                        share.error_message = result.get('error', '') if not result.get('success') else None
                        
                        logger.info(f"Processed scheduled share: {share.platform} for post {blog_post.id}")
                    
                except Exception as e:
                    logger.error(f"Error processing scheduled share {share.id}: {e}")
                    share.status = 'failed'
                    share.error_message = str(e)
            
            db.session.commit()
            logger.info(f"Processed {len(scheduled_shares)} scheduled shares")
            
        except Exception as e:
            logger.error(f"Error processing scheduled shares: {e}")
            db.session.rollback()
    
    def get_social_analytics(self, blog_post_id: int) -> Dict:
        """Get social media analytics for a blog post"""
        try:
            shares = SocialShare.query.filter_by(blog_post_id=blog_post_id).all()
            
            analytics = {
                "total_shares": len(shares),
                "successful_shares": len([s for s in shares if s.status == 'published']),
                "failed_shares": len([s for s in shares if s.status == 'failed']),
                "scheduled_shares": len([s for s in shares if s.status == 'scheduled']),
                "platforms": {}
            }
            
            for share in shares:
                if share.platform not in analytics["platforms"]:
                    analytics["platforms"][share.platform] = {
                        "status": share.status,
                        "shared_at": share.shared_at.isoformat() if share.shared_at else None,
                        "url": share.platform_url
                    }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting social analytics: {e}")
            return {"error": str(e)}
    
    def update_platform_config(self, platform: str, config: Dict):
        """Update platform configuration"""
        if platform in self.platform_configs:
            self.platform_configs[platform].update(config)
            logger.info(f"Updated {platform} configuration")
        else:
            logger.warning(f"Unknown platform: {platform}")

def main():
    """Test the social publisher"""
    from models.blog import BlogPost, Country, Technology
    
    # Create test blog post
    country = Country(name="Kenya", code="KEN")
    technology = Technology(name="Mobile Money", category="Fintech")
    
    blog_post = BlogPost(
        title="Kenya's Mobile Money Revolution",
        slug="kenya-mobile-money-revolution",
        excerpt="How M-Pesa transformed Kenya's economy and became a model for the world.",
        content="Full blog post content here...",
        country=country,
        technology=technology,
        tags='["Kenya", "Mobile Money", "Fintech", "Economic Development"]'
    )
    
    publisher = SocialPublisher()
    
    # Test social media publishing
    results = publisher.publish_to_social_media(blog_post)
    print(f"Publishing results: {results}")
    
    # Test scheduling
    scheduled = publisher.schedule_social_shares(blog_post)
    print(f"Scheduled shares: {scheduled}")

if __name__ == "__main__":
    main()


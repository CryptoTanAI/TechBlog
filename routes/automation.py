#!/usr/bin/env python3
"""
Automation API Routes
Provides endpoints for controlling and monitoring the automated blog generation system
"""

import os
import sys
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json

# Add the parent directory to the path to import models
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.blog import BlogPost, Country, Technology, AutomationConfig, SocialShare
from models.user import db
from automation.scheduler import get_scheduler
from automation.content_generator import ContentGenerator
from automation.social_publisher import SocialPublisher

automation_bp = Blueprint('automation', __name__)

# Initialize automation components
content_generator = ContentGenerator()
social_publisher = SocialPublisher()

@automation_bp.route('/automation/status', methods=['GET'])
def get_automation_status():
    """Get current automation system status"""
    try:
        scheduler = get_scheduler()
        status = scheduler.get_scheduler_status()
        
        # Add additional status information
        status.update({
            "total_posts": BlogPost.query.count(),
            "posts_this_month": BlogPost.query.filter(
                BlogPost.published_at >= datetime.now().replace(day=1)
            ).count(),
            "scheduled_shares": SocialShare.query.filter_by(status='scheduled').count(),
            "last_post": _get_last_post_info()
        })
        
        return jsonify({
            "success": True,
            "status": status
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@automation_bp.route('/automation/config', methods=['GET'])
def get_automation_config():
    """Get automation configuration settings"""
    try:
        configs = AutomationConfig.query.all()
        config_dict = {config.config_key: config.config_value for config in configs}
        
        return jsonify({
            "success": True,
            "config": config_dict
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@automation_bp.route('/automation/config', methods=['POST'])
def update_automation_config():
    """Update automation configuration settings"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No configuration data provided"
            }), 400
        
        updated_configs = []
        
        for key, value in data.items():
            config = AutomationConfig.query.filter_by(config_key=key).first()
            
            if config:
                config.config_value = str(value)
                config.updated_at = datetime.utcnow()
            else:
                config = AutomationConfig(
                    config_key=key,
                    config_value=str(value),
                    description=f"Auto-generated config for {key}"
                )
                db.session.add(config)
            
            updated_configs.append(key)
        
        db.session.commit()
        
        # Restart scheduler if critical settings changed
        critical_settings = ['daily_posting_enabled', 'posting_time']
        if any(setting in updated_configs for setting in critical_settings):
            scheduler = get_scheduler()
            if scheduler.is_running:
                scheduler.stop_scheduler()
                scheduler.start_scheduler()
        
        return jsonify({
            "success": True,
            "message": f"Updated {len(updated_configs)} configuration settings",
            "updated_configs": updated_configs
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@automation_bp.route('/automation/start', methods=['POST'])
def start_automation():
    """Start the automation scheduler"""
    try:
        scheduler = get_scheduler()
        
        if scheduler.is_running:
            return jsonify({
                "success": False,
                "message": "Automation is already running"
            }), 400
        
        scheduler.start_scheduler()
        
        return jsonify({
            "success": True,
            "message": "Automation scheduler started successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@automation_bp.route('/automation/stop', methods=['POST'])
def stop_automation():
    """Stop the automation scheduler"""
    try:
        scheduler = get_scheduler()
        
        if not scheduler.is_running:
            return jsonify({
                "success": False,
                "message": "Automation is not running"
            }), 400
        
        scheduler.stop_scheduler()
        
        return jsonify({
            "success": True,
            "message": "Automation scheduler stopped successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@automation_bp.route('/automation/generate', methods=['POST'])
def manual_generate_post():
    """Manually trigger blog post generation"""
    try:
        data = request.get_json() or {}
        
        country_id = data.get('country_id')
        technology_id = data.get('technology_id')
        
        scheduler = get_scheduler()
        result = scheduler.trigger_manual_generation(country_id, technology_id)
        
        if result['success']:
            return jsonify({
                "success": True,
                "message": "Blog post generated successfully",
                "blog_post": result
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('error', 'Unknown error')
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@automation_bp.route('/automation/preview', methods=['POST'])
def preview_generation():
    """Preview what would be generated without actually creating a post"""
    try:
        data = request.get_json() or {}
        
        country_id = data.get('country_id')
        technology_id = data.get('technology_id')
        
        # Select country and technology
        if country_id:
            country = Country.query.get(country_id)
        else:
            country = content_generator.select_daily_country()
        
        if not country:
            return jsonify({
                "success": False,
                "error": "No country found"
            }), 400
        
        if technology_id:
            technology = Technology.query.get(technology_id)
        else:
            technology = content_generator.select_technology_for_country(country)
        
        if not technology:
            return jsonify({
                "success": False,
                "error": "No technology found"
            }), 400
        
        # Generate preview data
        research_data = content_generator.conduct_research(country, technology)
        blog_data = content_generator.generate_blog_post(country, technology, research_data)
        
        preview = {
            "country": {
                "id": country.id,
                "name": country.name,
                "code": country.code,
                "region": country.region
            },
            "technology": {
                "id": technology.id,
                "name": technology.name,
                "category": technology.category
            },
            "blog_preview": {
                "title": blog_data['title'],
                "excerpt": blog_data['excerpt'],
                "word_count": blog_data['word_count'],
                "reading_time": blog_data['reading_time_minutes'],
                "tags": blog_data['tags']
            },
            "research_summary": {
                "sections": list(research_data.keys()),
                "economic_impact": research_data.get('economic_impact', {}),
                "case_studies_count": len(research_data.get('case_studies', []))
            }
        }
        
        return jsonify({
            "success": True,
            "preview": preview
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@automation_bp.route('/automation/schedule', methods=['GET'])
def get_schedule():
    """Get upcoming scheduled posts"""
    try:
        # Get scheduled social shares as a proxy for upcoming posts
        scheduled_shares = SocialShare.query.filter_by(
            status='scheduled'
        ).order_by(SocialShare.scheduled_at).limit(10).all()
        
        schedule_items = []
        for share in scheduled_shares:
            blog_post = BlogPost.query.get(share.blog_post_id)
            if blog_post:
                schedule_items.append({
                    "id": share.id,
                    "blog_post_id": blog_post.id,
                    "title": blog_post.title,
                    "country": blog_post.country.name,
                    "technology": blog_post.technology.name,
                    "platform": share.platform,
                    "scheduled_at": share.scheduled_at.isoformat(),
                    "status": share.status
                })
        
        return jsonify({
            "success": True,
            "scheduled_items": schedule_items,
            "count": len(schedule_items)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@automation_bp.route('/automation/analytics', methods=['GET'])
def get_automation_analytics():
    """Get automation system analytics"""
    try:
        # Time ranges
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Post analytics
        total_posts = BlogPost.query.count()
        posts_this_week = BlogPost.query.filter(
            BlogPost.published_at >= week_ago
        ).count()
        posts_this_month = BlogPost.query.filter(
            BlogPost.published_at >= month_ago
        ).count()
        
        # Social media analytics
        total_shares = SocialShare.query.count()
        successful_shares = SocialShare.query.filter_by(status='published').count()
        failed_shares = SocialShare.query.filter_by(status='failed').count()
        
        # Country distribution
        country_stats = db.session.query(
            Country.name,
            db.func.count(BlogPost.id).label('post_count')
        ).join(BlogPost).group_by(Country.name).order_by(
            db.func.count(BlogPost.id).desc()
        ).limit(10).all()
        
        # Technology distribution
        tech_stats = db.session.query(
            Technology.name,
            db.func.count(BlogPost.id).label('post_count')
        ).join(BlogPost).group_by(Technology.name).order_by(
            db.func.count(BlogPost.id).desc()
        ).limit(10).all()
        
        # Engagement metrics
        total_views = db.session.query(
            db.func.sum(BlogPost.view_count)
        ).scalar() or 0
        
        total_social_shares = db.session.query(
            db.func.sum(BlogPost.share_count)
        ).scalar() or 0
        
        analytics = {
            "posts": {
                "total": total_posts,
                "this_week": posts_this_week,
                "this_month": posts_this_month,
                "avg_per_week": posts_this_month / 4 if posts_this_month > 0 else 0
            },
            "social_media": {
                "total_shares": total_shares,
                "successful_shares": successful_shares,
                "failed_shares": failed_shares,
                "success_rate": (successful_shares / total_shares * 100) if total_shares > 0 else 0
            },
            "engagement": {
                "total_views": total_views,
                "total_social_shares": total_social_shares,
                "avg_views_per_post": (total_views / total_posts) if total_posts > 0 else 0
            },
            "distribution": {
                "top_countries": [{"name": name, "posts": count} for name, count in country_stats],
                "top_technologies": [{"name": name, "posts": count} for name, count in tech_stats]
            }
        }
        
        return jsonify({
            "success": True,
            "analytics": analytics
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@automation_bp.route('/automation/social/publish', methods=['POST'])
def publish_to_social():
    """Manually publish a blog post to social media"""
    try:
        data = request.get_json()
        
        if not data or 'blog_post_id' not in data:
            return jsonify({
                "success": False,
                "error": "Blog post ID is required"
            }), 400
        
        blog_post_id = data['blog_post_id']
        platforms = data.get('platforms', ['twitter', 'linkedin', 'facebook'])
        
        blog_post = BlogPost.query.get(blog_post_id)
        if not blog_post:
            return jsonify({
                "success": False,
                "error": "Blog post not found"
            }), 404
        
        # Publish to social media
        results = social_publisher.publish_to_social_media(blog_post, platforms)
        
        return jsonify({
            "success": True,
            "message": "Social media publishing completed",
            "results": results
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@automation_bp.route('/automation/social/schedule', methods=['POST'])
def schedule_social_shares():
    """Schedule social media shares for a blog post"""
    try:
        data = request.get_json()
        
        if not data or 'blog_post_id' not in data:
            return jsonify({
                "success": False,
                "error": "Blog post ID is required"
            }), 400
        
        blog_post_id = data['blog_post_id']
        delay_minutes = data.get('delay_minutes', 30)
        
        blog_post = BlogPost.query.get(blog_post_id)
        if not blog_post:
            return jsonify({
                "success": False,
                "error": "Blog post not found"
            }), 404
        
        # Schedule social shares
        scheduled_shares = social_publisher.schedule_social_shares(blog_post, delay_minutes)
        
        return jsonify({
            "success": True,
            "message": f"Scheduled {len(scheduled_shares)} social media shares",
            "scheduled_shares": scheduled_shares
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@automation_bp.route('/automation/logs', methods=['GET'])
def get_automation_logs():
    """Get recent automation system logs"""
    try:
        # In production, this would read from log files
        # For now, return sample log data
        
        sample_logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "Daily blog post generation completed successfully",
                "details": "Generated post for Kenya - Mobile Money"
            },
            {
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "level": "INFO", 
                "message": "Social media sharing completed",
                "details": "Published to Twitter, LinkedIn, Facebook"
            },
            {
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "level": "INFO",
                "message": "Content research completed",
                "details": "Researched 6 sections for blog post"
            }
        ]
        
        return jsonify({
            "success": True,
            "logs": sample_logs,
            "count": len(sample_logs)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def _get_last_post_info():
    """Get information about the last published post"""
    try:
        last_post = BlogPost.query.filter_by(
            status='published'
        ).order_by(BlogPost.published_at.desc()).first()
        
        if last_post:
            return {
                "id": last_post.id,
                "title": last_post.title,
                "country": last_post.country.name,
                "technology": last_post.technology.name,
                "published_at": last_post.published_at.isoformat(),
                "view_count": last_post.view_count
            }
        
        return None
        
    except Exception as e:
        return {"error": str(e)}

# Error handlers
@automation_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@automation_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500


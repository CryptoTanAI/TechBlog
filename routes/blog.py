from flask import Blueprint, jsonify, request
from datetime import datetime
import json
from sqlalchemy import desc, func
from models.user import db
from models.blog import BlogPost, Country, Technology, MediaAsset, SocialShare, AutomationConfig

blog_bp = Blueprint('blog', __name__)

# Blog Posts Routes
@blog_bp.route('/posts', methods=['GET'])
def get_posts():
    """Get all blog posts with optional filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', 'published')
    country_id = request.args.get('country_id', type=int)
    technology_id = request.args.get('technology_id', type=int)
    
    query = BlogPost.query
    
    if status:
        query = query.filter_by(status=status)
    if country_id:
        query = query.filter_by(country_id=country_id)
    if technology_id:
        query = query.filter_by(technology_id=technology_id)
    
    posts = query.order_by(desc(BlogPost.published_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'posts': [post.to_dict(include_content=False) for post in posts.items],
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page,
        'per_page': per_page
    })

@blog_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Get a specific blog post by ID"""
    post = BlogPost.query.get_or_404(post_id)
    
    # Increment view count
    post.view_count += 1
    db.session.commit()
    
    return jsonify(post.to_dict())

@blog_bp.route('/posts/slug/<string:slug>', methods=['GET'])
def get_post_by_slug(slug):
    """Get a specific blog post by slug"""
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    
    # Increment view count
    post.view_count += 1
    db.session.commit()
    
    return jsonify(post.to_dict())

@blog_bp.route('/posts', methods=['POST'])
def create_post():
    """Create a new blog post"""
    data = request.json
    
    post = BlogPost(
        title=data['title'],
        slug=data['slug'],
        content=data['content'],
        excerpt=data.get('excerpt'),
        featured_image_url=data.get('featured_image_url'),
        country_id=data['country_id'],
        technology_id=data['technology_id'],
        author_id=data['author_id'],
        gdp_impact=json.dumps(data.get('gdp_impact', {})),
        poverty_impact=json.dumps(data.get('poverty_impact', {})),
        government_impact=json.dumps(data.get('government_impact', {})),
        meta_description=data.get('meta_description'),
        meta_keywords=data.get('meta_keywords'),
        status=data.get('status', 'draft')
    )
    
    if data.get('published_at'):
        post.published_at = datetime.fromisoformat(data['published_at'])
    elif post.status == 'published':
        post.published_at = datetime.utcnow()
    
    if data.get('scheduled_for'):
        post.scheduled_for = datetime.fromisoformat(data['scheduled_for'])
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify(post.to_dict()), 201

@blog_bp.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Update an existing blog post"""
    post = BlogPost.query.get_or_404(post_id)
    data = request.json
    
    post.title = data.get('title', post.title)
    post.slug = data.get('slug', post.slug)
    post.content = data.get('content', post.content)
    post.excerpt = data.get('excerpt', post.excerpt)
    post.featured_image_url = data.get('featured_image_url', post.featured_image_url)
    post.country_id = data.get('country_id', post.country_id)
    post.technology_id = data.get('technology_id', post.technology_id)
    post.meta_description = data.get('meta_description', post.meta_description)
    post.meta_keywords = data.get('meta_keywords', post.meta_keywords)
    post.status = data.get('status', post.status)
    
    if data.get('gdp_impact'):
        post.gdp_impact = json.dumps(data['gdp_impact'])
    if data.get('poverty_impact'):
        post.poverty_impact = json.dumps(data['poverty_impact'])
    if data.get('government_impact'):
        post.government_impact = json.dumps(data['government_impact'])
    
    if data.get('published_at'):
        post.published_at = datetime.fromisoformat(data['published_at'])
    elif post.status == 'published' and not post.published_at:
        post.published_at = datetime.utcnow()
    
    if data.get('scheduled_for'):
        post.scheduled_for = datetime.fromisoformat(data['scheduled_for'])
    
    post.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(post.to_dict())

@blog_bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete a blog post"""
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return '', 204

# Countries Routes
@blog_bp.route('/countries', methods=['GET'])
def get_countries():
    """Get all countries"""
    countries = Country.query.order_by(Country.name).all()
    return jsonify([country.to_dict() for country in countries])

@blog_bp.route('/countries', methods=['POST'])
def create_country():
    """Create a new country"""
    data = request.json
    
    country = Country(
        name=data['name'],
        code=data['code'],
        flag_url=data.get('flag_url'),
        region=data.get('region'),
        population=data.get('population'),
        gdp_usd=data.get('gdp_usd'),
        gdp_per_capita=data.get('gdp_per_capita')
    )
    
    db.session.add(country)
    db.session.commit()
    
    return jsonify(country.to_dict()), 201

@blog_bp.route('/countries/<int:country_id>', methods=['GET'])
def get_country(country_id):
    """Get a specific country with its blog posts"""
    country = Country.query.get_or_404(country_id)
    country_data = country.to_dict()
    country_data['blog_posts'] = [post.to_dict(include_content=False) for post in country.blog_posts]
    return jsonify(country_data)

@blog_bp.route('/countries/<int:country_id>', methods=['PUT'])
def update_country(country_id):
    """Update a country"""
    country = Country.query.get_or_404(country_id)
    data = request.json
    
    country.name = data.get('name', country.name)
    country.code = data.get('code', country.code)
    country.flag_url = data.get('flag_url', country.flag_url)
    country.region = data.get('region', country.region)
    country.population = data.get('population', country.population)
    country.gdp_usd = data.get('gdp_usd', country.gdp_usd)
    country.gdp_per_capita = data.get('gdp_per_capita', country.gdp_per_capita)
    
    db.session.commit()
    return jsonify(country.to_dict())

# Technologies Routes
@blog_bp.route('/technologies', methods=['GET'])
def get_technologies():
    """Get all technologies"""
    technologies = Technology.query.order_by(Technology.name).all()
    return jsonify([tech.to_dict() for tech in technologies])

@blog_bp.route('/technologies', methods=['POST'])
def create_technology():
    """Create a new technology"""
    data = request.json
    
    technology = Technology(
        name=data['name'],
        category=data.get('category'),
        description=data.get('description')
    )
    
    db.session.add(technology)
    db.session.commit()
    
    return jsonify(technology.to_dict()), 201

@blog_bp.route('/technologies/<int:tech_id>', methods=['GET'])
def get_technology(tech_id):
    """Get a specific technology with its blog posts"""
    technology = Technology.query.get_or_404(tech_id)
    tech_data = technology.to_dict()
    tech_data['blog_posts'] = [post.to_dict(include_content=False) for post in technology.blog_posts]
    return jsonify(tech_data)

# Media Assets Routes
@blog_bp.route('/posts/<int:post_id>/media', methods=['POST'])
def add_media_asset(post_id):
    """Add a media asset to a blog post"""
    post = BlogPost.query.get_or_404(post_id)
    data = request.json
    
    asset = MediaAsset(
        blog_post_id=post_id,
        asset_type=data['asset_type'],
        file_url=data['file_url'],
        file_name=data.get('file_name'),
        alt_text=data.get('alt_text'),
        caption=data.get('caption'),
        order_index=data.get('order_index', 0)
    )
    
    db.session.add(asset)
    db.session.commit()
    
    return jsonify(asset.to_dict()), 201

@blog_bp.route('/media/<int:asset_id>', methods=['DELETE'])
def delete_media_asset(asset_id):
    """Delete a media asset"""
    asset = MediaAsset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    return '', 204

# Social Sharing Routes
@blog_bp.route('/posts/<int:post_id>/share', methods=['POST'])
def share_post(post_id):
    """Record a social media share"""
    post = BlogPost.query.get_or_404(post_id)
    data = request.json
    
    share = SocialShare(
        blog_post_id=post_id,
        platform=data['platform'],
        share_url=data.get('share_url'),
        share_text=data.get('share_text'),
        shared_at=datetime.utcnow()
    )
    
    db.session.add(share)
    
    # Update post share count
    post.share_count += 1
    
    db.session.commit()
    
    return jsonify(share.to_dict()), 201

# Analytics Routes
@blog_bp.route('/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """Get overall blog analytics"""
    total_posts = BlogPost.query.filter_by(status='published').count()
    total_views = db.session.query(func.sum(BlogPost.view_count)).scalar() or 0
    total_shares = db.session.query(func.sum(BlogPost.share_count)).scalar() or 0
    total_countries = Country.query.count()
    total_technologies = Technology.query.count()
    
    # Most popular posts
    popular_posts = BlogPost.query.filter_by(status='published').order_by(desc(BlogPost.view_count)).limit(5).all()
    
    # Recent posts
    recent_posts = BlogPost.query.filter_by(status='published').order_by(desc(BlogPost.published_at)).limit(5).all()
    
    return jsonify({
        'total_posts': total_posts,
        'total_views': total_views,
        'total_shares': total_shares,
        'total_countries': total_countries,
        'total_technologies': total_technologies,
        'popular_posts': [post.to_dict(include_content=False) for post in popular_posts],
        'recent_posts': [post.to_dict(include_content=False) for post in recent_posts]
    })

# Automation Configuration Routes
@blog_bp.route('/automation/config', methods=['GET'])
def get_automation_config():
    """Get all automation configuration settings"""
    configs = AutomationConfig.query.all()
    return jsonify([config.to_dict() for config in configs])

@blog_bp.route('/automation/config', methods=['POST'])
def create_automation_config():
    """Create or update automation configuration"""
    data = request.json
    
    # Check if config already exists
    config = AutomationConfig.query.filter_by(config_key=data['config_key']).first()
    
    if config:
        # Update existing config
        config.config_value = data['config_value']
        config.description = data.get('description', config.description)
        config.is_active = data.get('is_active', config.is_active)
        config.updated_at = datetime.utcnow()
    else:
        # Create new config
        config = AutomationConfig(
            config_key=data['config_key'],
            config_value=data['config_value'],
            description=data.get('description'),
            is_active=data.get('is_active', True)
        )
        db.session.add(config)
    
    db.session.commit()
    return jsonify(config.to_dict()), 201

@blog_bp.route('/automation/config/<string:config_key>', methods=['GET'])
def get_automation_config_by_key(config_key):
    """Get specific automation configuration by key"""
    config = AutomationConfig.query.filter_by(config_key=config_key).first_or_404()
    return jsonify(config.to_dict())

# Search Routes
@blog_bp.route('/search', methods=['GET'])
def search_posts():
    """Search blog posts by title, content, or country/technology"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if not query:
        return jsonify({'posts': [], 'total': 0, 'pages': 0, 'current_page': page})
    
    # Search in title, content, and related country/technology names
    search_filter = BlogPost.title.contains(query) | \
                   BlogPost.content.contains(query) | \
                   BlogPost.meta_keywords.contains(query)
    
    posts = BlogPost.query.filter(search_filter).filter_by(status='published').order_by(
        desc(BlogPost.published_at)
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'posts': [post.to_dict(include_content=False) for post in posts.items],
        'total': posts.total,
        'pages': posts.pages,
        'current_page': page,
        'per_page': per_page,
        'query': query
    })


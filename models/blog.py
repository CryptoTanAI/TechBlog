from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.user import db

class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(3), unique=True, nullable=False)  # ISO country code
    flag_url = db.Column(db.String(200))
    region = db.Column(db.String(50))  # Africa, Asia, Latin America, etc.
    population = db.Column(db.BigInteger)
    gdp_usd = db.Column(db.BigInteger)
    gdp_per_capita = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with blog posts
    blog_posts = db.relationship('BlogPost', backref='country', lazy=True)
    
    def __repr__(self):
        return f'<Country {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'flag_url': self.flag_url,
            'region': self.region,
            'population': self.population,
            'gdp_usd': self.gdp_usd,
            'gdp_per_capita': self.gdp_per_capita,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Technology(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50))  # AI, Blockchain, IoT, etc.
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with blog posts
    blog_posts = db.relationship('BlogPost', backref='technology', lazy=True)
    
    def __repr__(self):
        return f'<Technology {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    featured_image_url = db.Column(db.String(500))
    
    # Foreign keys
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)
    technology_id = db.Column(db.Integer, db.ForeignKey('technology.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Impact metrics
    gdp_impact = db.Column(db.Text)  # JSON string with GDP impact data
    poverty_impact = db.Column(db.Text)  # JSON string with poverty alleviation data
    government_impact = db.Column(db.Text)  # JSON string with government services data
    
    # SEO and metadata
    meta_description = db.Column(db.String(160))
    meta_keywords = db.Column(db.String(200))
    
    # Status and publishing
    status = db.Column(db.String(20), default='draft')  # draft, published, scheduled
    published_at = db.Column(db.DateTime)
    scheduled_for = db.Column(db.DateTime)
    
    # Analytics
    view_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref='blog_posts')
    media_assets = db.relationship('MediaAsset', backref='blog_post', lazy=True, cascade='all, delete-orphan')
    social_shares = db.relationship('SocialShare', backref='blog_post', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'
    
    def to_dict(self, include_content=True):
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'featured_image_url': self.featured_image_url,
            'country': self.country.to_dict() if self.country else None,
            'technology': self.technology.to_dict() if self.technology else None,
            'author': self.author.to_dict() if self.author else None,
            'gdp_impact': self.gdp_impact,
            'poverty_impact': self.poverty_impact,
            'government_impact': self.government_impact,
            'meta_description': self.meta_description,
            'meta_keywords': self.meta_keywords,
            'status': self.status,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'view_count': self.view_count,
            'share_count': self.share_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'media_assets': [asset.to_dict() for asset in self.media_assets] if self.media_assets else []
        }
        
        if include_content:
            data['content'] = self.content
            
        return data

class MediaAsset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    asset_type = db.Column(db.String(20), nullable=False)  # image, video, infographic
    file_url = db.Column(db.String(500), nullable=False)
    file_name = db.Column(db.String(200))
    alt_text = db.Column(db.String(200))
    caption = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<MediaAsset {self.file_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'blog_post_id': self.blog_post_id,
            'asset_type': self.asset_type,
            'file_url': self.file_url,
            'file_name': self.file_name,
            'alt_text': self.alt_text,
            'caption': self.caption,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SocialShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # twitter, facebook, linkedin, medium
    share_url = db.Column(db.String(500))
    share_text = db.Column(db.Text)
    shared_at = db.Column(db.DateTime)
    engagement_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SocialShare {self.platform}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'blog_post_id': self.blog_post_id,
            'platform': self.platform,
            'share_url': self.share_url,
            'share_text': self.share_text,
            'shared_at': self.shared_at.isoformat() if self.shared_at else None,
            'engagement_count': self.engagement_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AutomationConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False)
    config_value = db.Column(db.Text)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AutomationConfig {self.config_key}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


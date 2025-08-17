# Newsletter Backend Integration for TechSouth

## 1. Newsletter Model (add to models/newsletter.py)

from models.user import db
from datetime import datetime

class NewsletterSubscriber(db.Model):
    __tablename__ = 'newsletter_subscribers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    source = db.Column(db.String(100), default='website')
    preferences = db.Column(db.JSON, default=lambda: {
        'weekly_digest': True,
        'breaking_news': True,
        'research_reports': True
    })
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'subscribed_at': self.subscribed_at.isoformat(),
            'is_active': self.is_active,
            'source': self.source,
            'preferences': self.preferences
        }

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

## 2. Newsletter Routes (add to routes/newsletter.py)

from flask import Blueprint, request, jsonify
from models.user import db
from models.newsletter import NewsletterSubscriber
import re

newsletter_bp = Blueprint('newsletter', __name__)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@newsletter_bp.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if already subscribed
        existing = NewsletterSubscriber.query.filter_by(email=email).first()
        if existing:
            if existing.is_active:
                return jsonify({'message': 'Already subscribed'}), 200
            else:
                # Reactivate subscription
                existing.is_active = True
                existing.subscribed_at = datetime.utcnow()
                db.session.commit()
                return jsonify({'message': 'Subscription reactivated'}), 200
        
        # Create new subscription
        subscriber = NewsletterSubscriber(email=email)
        db.session.add(subscriber)
        db.session.commit()
        
        # TODO: Send welcome email
        # send_welcome_email(email)
        
        return jsonify({
            'message': 'Successfully subscribed to TechSouth Weekly',
            'subscriber': subscriber.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Subscription failed'}), 500

@newsletter_bp.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        subscriber = NewsletterSubscriber.query.filter_by(email=email).first()
        if not subscriber:
            return jsonify({'error': 'Email not found'}), 404
        
        subscriber.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Successfully unsubscribed'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Unsubscribe failed'}), 500

@newsletter_bp.route('/subscribers', methods=['GET'])
def get_subscribers():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        subscribers = NewsletterSubscriber.query.filter_by(is_active=True)\
            .order_by(NewsletterSubscriber.subscribed_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'subscribers': [s.to_dict() for s in subscribers.items],
            'total': subscribers.total,
            'pages': subscribers.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch subscribers'}), 500

## 3. Email Service Integration (add to automation/email_service.py)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email = os.getenv('EMAIL_ADDRESS')
        self.password = os.getenv('EMAIL_PASSWORD')
    
    def send_welcome_email(self, subscriber_email):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = subscriber_email
            msg['Subject'] = "Welcome to TechSouth Weekly!"
            
            body = f"""
            Welcome to TechSouth Weekly!
            
            Thank you for subscribing to our newsletter. You'll now receive:
            
            • Weekly insights on Global South technology trends
            • Exclusive research reports and analysis
            • Case studies from successful tech implementations
            • Policy updates and their implications
            
            You can manage your preferences or unsubscribe at any time.
            
            Best regards,
            The TechSouth Team
            
            ---
            TechSouth - Empowering the Global South through Technology
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
            return False
    
    def send_newsletter(self, subject, content, subscriber_emails):
        try:
            for email in subscriber_emails:
                msg = MIMEMultipart()
                msg['From'] = self.email
                msg['To'] = email
                msg['Subject'] = subject
                
                msg.attach(MIMEText(content, 'html'))
                
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
                server.quit()
            
            return True
        except Exception as e:
            print(f"Failed to send newsletter: {e}")
            return False

## 4. Integration with Main App (update main.py)

# Add these imports
from routes.newsletter import newsletter_bp
from models.newsletter import NewsletterSubscriber

# Register the blueprint
app.register_blueprint(newsletter_bp, url_prefix='/api/newsletter')

# Update database creation
with app.app_context():
    db.create_all()

## 5. Environment Variables (add to Railway)

# Add these environment variables in Railway:
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

## 6. Newsletter Automation Integration (update automation/scheduler.py)

from models.newsletter import NewsletterSubscriber
from automation.email_service import EmailService

def send_weekly_newsletter():
    try:
        # Get active subscribers
        subscribers = NewsletterSubscriber.query.filter_by(is_active=True).all()
        emails = [s.email for s in subscribers]
        
        if not emails:
            print("No subscribers found")
            return
        
        # Generate newsletter content
        latest_posts = BlogPost.query.order_by(BlogPost.published_at.desc()).limit(5).all()
        
        content = generate_newsletter_html(latest_posts)
        subject = f"TechSouth Weekly - {datetime.now().strftime('%B %d, %Y')}"
        
        # Send newsletter
        email_service = EmailService()
        success = email_service.send_newsletter(subject, content, emails)
        
        if success:
            print(f"Newsletter sent to {len(emails)} subscribers")
        else:
            print("Failed to send newsletter")
            
    except Exception as e:
        print(f"Newsletter automation failed: {e}")

def generate_newsletter_html(posts):
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1a365d; color: white; padding: 2rem; text-align: center;">
            <h1>TechSouth Weekly</h1>
            <p>Technology insights from the Global South</p>
        </div>
        
        <div style="padding: 2rem;">
            <h2>This Week's Highlights</h2>
            
            {"".join([f'''
            <div style="border-bottom: 1px solid #eee; padding: 1rem 0;">
                <h3 style="color: #1a365d;">{post.title}</h3>
                <p style="color: #666;">{post.excerpt}</p>
                <p style="font-size: 0.9em; color: #999;">
                    {post.country.name} • {post.technology.category}
                </p>
            </div>
            ''' for post in posts])}
            
            <div style="text-align: center; margin-top: 2rem;">
                <a href="https://your-domain.com" 
                   style="background: #f6ad55; color: #1a365d; padding: 1rem 2rem; 
                          text-decoration: none; border-radius: 0.5rem; font-weight: bold;">
                    Read More on TechSouth
                </a>
            </div>
        </div>
        
        <div style="background: #f7fafc; padding: 1rem; text-align: center; font-size: 0.9em; color: #666;">
            <p>You're receiving this because you subscribed to TechSouth Weekly.</p>
            <p><a href="https://your-domain.com/unsubscribe">Unsubscribe</a></p>
        </div>
    </body>
    </html>
    """
    return html

# Add to scheduler
schedule.every().monday.at("09:00").do(send_weekly_newsletter)

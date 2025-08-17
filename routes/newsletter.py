from flask import Blueprint, request, jsonify
from models.user import db
from models.newsletter import NewsletterSubscriber
from datetime import datetime
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
        
        return jsonify({
            'message': 'Successfully subscribed to TechSouth Weekly',
            'subscriber': subscriber.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Subscription failed'}), 500

@newsletter_bp.route('/subscribers', methods=['GET'])
def get_subscribers():
    try:
        subscribers = NewsletterSubscriber.query.filter_by(is_active=True)\
            .order_by(NewsletterSubscriber.subscribed_at.desc()).all()
        
        return jsonify({
            'subscribers': [s.to_dict() for s in subscribers],
            'total': len(subscribers)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch subscribers'}), 500

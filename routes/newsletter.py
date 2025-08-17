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
        
        # Check if already subscribed (case-insensitive)
        existing = NewsletterSubscriber.query.filter(
            db.func.lower(NewsletterSubscriber.email) == email
        ).first()
        
        if existing:
            if existing.is_active:
                return jsonify({'error': 'Already subscribed'}), 409
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
        
        return jsonify({'message': 'Successfully subscribed to TechSouth Weekly!'}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Newsletter subscription error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@newsletter_bp.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        subscriber = NewsletterSubscriber.query.filter(
            db.func.lower(NewsletterSubscriber.email) == email
        ).first()
        
        if not subscriber:
            return jsonify({'error': 'Email not found'}), 404
        
        subscriber.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Successfully unsubscribed'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@newsletter_bp.route('/subscribers', methods=['GET'])
def get_subscribers():
    try:
        # Only show active subscribers
        subscribers = NewsletterSubscriber.query.filter_by(is_active=True).all()
        
        return jsonify({
            'subscribers': [subscriber.to_dict() for subscriber in subscribers],
            'total': len(subscribers)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@newsletter_bp.route('/cleanup-duplicates', methods=['POST'])
def cleanup_duplicates():
    """Remove duplicate email addresses, keeping the most recent one"""
    try:
        # Find all unique emails
        unique_emails = db.session.query(NewsletterSubscriber.email).distinct().all()
        
        removed_count = 0
        for (email,) in unique_emails:
            # Get all subscribers with this email
            duplicates = NewsletterSubscriber.query.filter_by(email=email).order_by(NewsletterSubscriber.subscribed_at.desc()).all()
            
            if len(duplicates) > 1:
                # Keep the most recent one, remove the rest
                for duplicate in duplicates[1:]:
                    db.session.delete(duplicate)
                    removed_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Removed {removed_count} duplicate entries',
            'removed_count': removed_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

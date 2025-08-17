#!/usr/bin/env python3
"""
Data seeding script for the tech blog platform
Populates the database with initial countries, technologies, and configuration
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db, User
from src.models.blog import Country, Technology, AutomationConfig
from src.main import app
import json

def seed_countries():
    """Seed the database with Global South countries"""
    countries_data = [
        # Africa
        {"name": "Kenya", "code": "KEN", "region": "Africa", "population": 54000000, "gdp_usd": 115000000000, "gdp_per_capita": 2130},
        {"name": "Nigeria", "code": "NGA", "region": "Africa", "population": 223000000, "gdp_usd": 441000000000, "gdp_per_capita": 1980},
        {"name": "South Africa", "code": "ZAF", "region": "Africa", "population": 60000000, "gdp_usd": 419000000000, "gdp_per_capita": 6980},
        {"name": "Rwanda", "code": "RWA", "region": "Africa", "population": 13000000, "gdp_usd": 11000000000, "gdp_per_capita": 850},
        {"name": "Ghana", "code": "GHA", "region": "Africa", "population": 33000000, "gdp_usd": 77000000000, "gdp_per_capita": 2330},
        {"name": "Ethiopia", "code": "ETH", "region": "Africa", "population": 123000000, "gdp_usd": 107000000000, "gdp_per_capita": 870},
        
        # Asia
        {"name": "India", "code": "IND", "region": "Asia", "population": 1400000000, "gdp_usd": 3700000000000, "gdp_per_capita": 2640},
        {"name": "Bangladesh", "code": "BGD", "region": "Asia", "population": 171000000, "gdp_usd": 460000000000, "gdp_per_capita": 2690},
        {"name": "Vietnam", "code": "VNM", "region": "Asia", "population": 98000000, "gdp_usd": 409000000000, "gdp_per_capita": 4180},
        {"name": "Indonesia", "code": "IDN", "region": "Asia", "population": 275000000, "gdp_usd": 1400000000000, "gdp_per_capita": 5090},
        {"name": "Philippines", "code": "PHL", "region": "Asia", "population": 115000000, "gdp_usd": 394000000000, "gdp_per_capita": 3430},
        {"name": "Pakistan", "code": "PAK", "region": "Asia", "population": 235000000, "gdp_usd": 347000000000, "gdp_per_capita": 1480},
        
        # Latin America
        {"name": "Brazil", "code": "BRA", "region": "Latin America", "population": 216000000, "gdp_usd": 2100000000000, "gdp_per_capita": 9720},
        {"name": "Mexico", "code": "MEX", "region": "Latin America", "population": 128000000, "gdp_usd": 1700000000000, "gdp_per_capita": 13270},
        {"name": "Colombia", "code": "COL", "region": "Latin America", "population": 52000000, "gdp_usd": 314000000000, "gdp_per_capita": 6040},
        {"name": "Peru", "code": "PER", "region": "Latin America", "population": 33000000, "gdp_usd": 223000000000, "gdp_per_capita": 6760},
        {"name": "Argentina", "code": "ARG", "region": "Latin America", "population": 46000000, "gdp_usd": 487000000000, "gdp_per_capita": 10590},
        {"name": "Chile", "code": "CHL", "region": "Latin America", "population": 20000000, "gdp_usd": 317000000000, "gdp_per_capita": 15850},
        
        # Middle East & Other
        {"name": "Turkey", "code": "TUR", "region": "Middle East", "population": 85000000, "gdp_usd": 819000000000, "gdp_per_capita": 9640},
        {"name": "Egypt", "code": "EGY", "region": "Africa", "population": 109000000, "gdp_usd": 469000000000, "gdp_per_capita": 4300},
    ]
    
    for country_data in countries_data:
        existing = Country.query.filter_by(code=country_data["code"]).first()
        if not existing:
            country = Country(**country_data)
            db.session.add(country)
            print(f"Added country: {country_data['name']}")
    
    db.session.commit()
    print(f"Seeded {len(countries_data)} countries")

def seed_technologies():
    """Seed the database with emerging technologies"""
    technologies_data = [
        {
            "name": "Artificial Intelligence",
            "category": "AI/ML",
            "description": "Machine learning, deep learning, and AI applications in healthcare, agriculture, education, and government services"
        },
        {
            "name": "Blockchain",
            "category": "Fintech",
            "description": "Distributed ledger technology for financial inclusion, supply chain transparency, and digital identity"
        },
        {
            "name": "Internet of Things",
            "category": "Infrastructure",
            "description": "Connected devices and sensors for smart cities, agriculture monitoring, and infrastructure management"
        },
        {
            "name": "Mobile Money",
            "category": "Fintech",
            "description": "Mobile payment systems and digital financial services for financial inclusion"
        },
        {
            "name": "Digital Identity",
            "category": "Government",
            "description": "Biometric and digital identity systems for government service delivery and financial inclusion"
        },
        {
            "name": "Telemedicine",
            "category": "Healthcare",
            "description": "Remote healthcare delivery through digital platforms and mobile health applications"
        },
        {
            "name": "EdTech",
            "category": "Education",
            "description": "Educational technology platforms for remote learning and digital skills development"
        },
        {
            "name": "AgTech",
            "category": "Agriculture",
            "description": "Agricultural technology including precision farming, crop monitoring, and supply chain optimization"
        },
        {
            "name": "Clean Energy",
            "category": "Energy",
            "description": "Solar, wind, and other renewable energy technologies with smart grid integration"
        },
        {
            "name": "5G Networks",
            "category": "Infrastructure",
            "description": "Next-generation mobile networks enabling high-speed connectivity and IoT applications"
        },
        {
            "name": "E-Government",
            "category": "Government",
            "description": "Digital government services and platforms for citizen engagement and service delivery"
        },
        {
            "name": "Drone Technology",
            "category": "Infrastructure",
            "description": "Unmanned aerial vehicles for delivery, monitoring, and emergency response"
        }
    ]
    
    for tech_data in technologies_data:
        existing = Technology.query.filter_by(name=tech_data["name"]).first()
        if not existing:
            technology = Technology(**tech_data)
            db.session.add(technology)
            print(f"Added technology: {tech_data['name']}")
    
    db.session.commit()
    print(f"Seeded {len(technologies_data)} technologies")

def seed_automation_config():
    """Seed automation configuration settings"""
    config_data = [
        {
            "config_key": "daily_posting_enabled",
            "config_value": "true",
            "description": "Enable or disable daily automated blog post generation"
        },
        {
            "config_key": "posting_time",
            "config_value": "09:00",
            "description": "Time of day to publish new blog posts (UTC)"
        },
        {
            "config_key": "country_rotation_strategy",
            "config_value": "balanced_regional",
            "description": "Strategy for selecting countries: random, regional_focus, balanced_regional"
        },
        {
            "config_key": "social_media_auto_share",
            "config_value": "true",
            "description": "Automatically share new posts to social media platforms"
        },
        {
            "config_key": "content_quality_threshold",
            "config_value": "0.8",
            "description": "Minimum quality score for auto-publishing (0.0-1.0)"
        },
        {
            "config_key": "max_posts_per_country_per_month",
            "config_value": "4",
            "description": "Maximum number of posts per country per month to ensure variety"
        },
        {
            "config_key": "research_data_sources",
            "config_value": json.dumps([
                "World Bank API",
                "Academic Papers",
                "Government Reports",
                "Technology News",
                "Economic Indicators"
            ]),
            "description": "Data sources for automated research"
        },
        {
            "config_key": "target_post_length",
            "config_value": "1500",
            "description": "Target word count for generated blog posts"
        }
    ]
    
    for config in config_data:
        existing = AutomationConfig.query.filter_by(config_key=config["config_key"]).first()
        if not existing:
            automation_config = AutomationConfig(**config)
            db.session.add(automation_config)
            print(f"Added config: {config['config_key']}")
    
    db.session.commit()
    print(f"Seeded {len(config_data)} automation configurations")

def seed_admin_user():
    """Create an admin user for the platform"""
    admin_email = "admin@techblog.com"
    existing_admin = User.query.filter_by(email=admin_email).first()
    
    if not existing_admin:
        admin_user = User(
            username="admin",
            email=admin_email
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"Created admin user: {admin_email}")
    else:
        print("Admin user already exists")

def main():
    """Main seeding function"""
    with app.app_context():
        print("Starting database seeding...")
        
        # Create all tables
        db.create_all()
        print("Database tables created")
        
        # Seed data
        seed_admin_user()
        seed_countries()
        seed_technologies()
        seed_automation_config()
        
        print("Database seeding completed successfully!")

if __name__ == "__main__":
    main()


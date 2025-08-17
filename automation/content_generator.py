#!/usr/bin/env python3
"""
Automated Content Generation System
Handles research, content creation, and blog post generation for the tech blog platform
"""

import os
import sys
import json
import random
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import openai

# Add the parent directory to the path to import models
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.blog import BlogPost, Country, Technology, MediaAsset, AutomationConfig
from src.models.user import db

class ContentGenerator:
    """Main class for automated content generation"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI()
        self.research_sources = [
            "World Bank API",
            "Academic Papers",
            "Government Reports", 
            "Technology News",
            "Economic Indicators"
        ]
    
    def select_daily_country(self) -> Optional[Country]:
        """Select a country for today's blog post based on configured strategy"""
        try:
            # Get automation config
            strategy_config = AutomationConfig.query.filter_by(
                config_key="country_rotation_strategy"
            ).first()
            
            max_posts_config = AutomationConfig.query.filter_by(
                config_key="max_posts_per_country_per_month"
            ).first()
            
            strategy = strategy_config.config_value if strategy_config else "balanced_regional"
            max_posts = int(max_posts_config.config_value) if max_posts_config else 4
            
            # Get countries that haven't exceeded monthly limit
            current_month = datetime.now().replace(day=1)
            available_countries = []
            
            for country in Country.query.all():
                monthly_posts = BlogPost.query.filter(
                    BlogPost.country_id == country.id,
                    BlogPost.published_at >= current_month
                ).count()
                
                if monthly_posts < max_posts:
                    available_countries.append(country)
            
            if not available_countries:
                # Reset if all countries have reached limit
                available_countries = Country.query.all()
            
            # Apply selection strategy
            if strategy == "random":
                return random.choice(available_countries)
            elif strategy == "regional_focus":
                # Focus on one region at a time
                regions = list(set(c.region for c in available_countries))
                focus_region = random.choice(regions)
                regional_countries = [c for c in available_countries if c.region == focus_region]
                return random.choice(regional_countries)
            else:  # balanced_regional
                # Ensure balanced representation across regions
                regions = {}
                for country in available_countries:
                    if country.region not in regions:
                        regions[country.region] = []
                    regions[country.region].append(country)
                
                # Select from region with fewest recent posts
                region_counts = {}
                for region in regions:
                    region_counts[region] = sum(
                        BlogPost.query.filter(
                            BlogPost.country_id.in_([c.id for c in regions[region]]),
                            BlogPost.published_at >= current_month
                        ).count()
                    )
                
                min_region = min(region_counts, key=region_counts.get)
                return random.choice(regions[min_region])
                
        except Exception as e:
            print(f"Error selecting country: {e}")
            # Fallback to random selection
            countries = Country.query.all()
            return random.choice(countries) if countries else None
    
    def select_technology_for_country(self, country: Country) -> Optional[Technology]:
        """Select an appropriate technology based on country context and recent posts"""
        try:
            # Get technologies that haven't been used recently for this country
            recent_cutoff = datetime.now() - timedelta(days=30)
            recent_tech_ids = [
                post.technology_id for post in BlogPost.query.filter(
                    BlogPost.country_id == country.id,
                    BlogPost.published_at >= recent_cutoff
                ).all()
            ]
            
            available_techs = Technology.query.filter(
                ~Technology.id.in_(recent_tech_ids)
            ).all()
            
            if not available_techs:
                available_techs = Technology.query.all()
            
            # Weight selection based on country characteristics
            if country.region == "Africa":
                # Prioritize mobile money, digital identity, agtech
                preferred_categories = ["Fintech", "Government", "Agriculture"]
            elif country.region == "Asia":
                # Prioritize AI, IoT, e-government
                preferred_categories = ["AI/ML", "Infrastructure", "Government"]
            elif country.region == "Latin America":
                # Prioritize fintech, edtech, clean energy
                preferred_categories = ["Fintech", "Education", "Energy"]
            else:
                preferred_categories = ["AI/ML", "Fintech", "Infrastructure"]
            
            # Try to select from preferred categories first
            preferred_techs = [
                tech for tech in available_techs 
                if tech.category in preferred_categories
            ]
            
            if preferred_techs:
                return random.choice(preferred_techs)
            else:
                return random.choice(available_techs)
                
        except Exception as e:
            print(f"Error selecting technology: {e}")
            technologies = Technology.query.all()
            return random.choice(technologies) if technologies else None
    
    def conduct_research(self, country: Country, technology: Technology) -> Dict:
        """Conduct automated research on the country-technology combination"""
        research_data = {
            "country_overview": self._research_country_overview(country),
            "technology_context": self._research_technology_context(technology),
            "economic_impact": self._research_economic_impact(country, technology),
            "case_studies": self._research_case_studies(country, technology),
            "government_initiatives": self._research_government_initiatives(country, technology),
            "challenges_opportunities": self._research_challenges_opportunities(country, technology)
        }
        
        return research_data
    
    def _research_country_overview(self, country: Country) -> Dict:
        """Research basic country information and current economic status"""
        return {
            "population": country.population,
            "gdp_usd": country.gdp_usd,
            "gdp_per_capita": country.gdp_per_capita,
            "region": country.region,
            "development_status": self._classify_development_status(country),
            "key_economic_sectors": self._get_key_sectors(country),
            "digital_readiness": self._assess_digital_readiness(country)
        }
    
    def _research_technology_context(self, technology: Technology) -> Dict:
        """Research technology applications and global trends"""
        return {
            "name": technology.name,
            "category": technology.category,
            "description": technology.description,
            "global_adoption_rate": self._estimate_adoption_rate(technology),
            "key_benefits": self._get_technology_benefits(technology),
            "implementation_challenges": self._get_implementation_challenges(technology)
        }
    
    def _research_economic_impact(self, country: Country, technology: Technology) -> Dict:
        """Research potential economic impact of technology in the country"""
        # Simulate economic impact analysis
        base_impact = country.gdp_usd * 0.001  # 0.1% of GDP as base
        
        # Adjust based on technology type and country characteristics
        multipliers = {
            "Mobile Money": 2.5,
            "Digital Identity": 1.8,
            "Artificial Intelligence": 3.2,
            "Blockchain": 1.5,
            "Internet of Things": 2.0,
            "Clean Energy": 2.8
        }
        
        multiplier = multipliers.get(technology.name, 1.0)
        estimated_impact = base_impact * multiplier
        
        return {
            "estimated_gdp_impact_usd": estimated_impact,
            "estimated_gdp_impact_percent": (estimated_impact / country.gdp_usd) * 100,
            "job_creation_potential": int(estimated_impact / 50000),  # Rough estimate
            "poverty_reduction_potential": self._estimate_poverty_impact(country, technology),
            "timeline_years": random.randint(3, 8)
        }
    
    def _research_case_studies(self, country: Country, technology: Technology) -> List[Dict]:
        """Generate relevant case studies and examples"""
        case_studies = []
        
        # Add regional success stories
        regional_examples = {
            "Africa": {
                "Mobile Money": "Kenya's M-Pesa transforming financial inclusion",
                "Digital Identity": "Ghana's digital ID system improving service delivery",
                "Artificial Intelligence": "Rwanda's AI in healthcare diagnostics"
            },
            "Asia": {
                "Digital Identity": "India's Aadhaar system enabling financial inclusion",
                "Artificial Intelligence": "Singapore's smart city AI initiatives",
                "Internet of Things": "South Korea's IoT smart city projects"
            },
            "Latin America": {
                "Mobile Money": "Brazil's PIX instant payment system",
                "Clean Energy": "Costa Rica's renewable energy transition",
                "EdTech": "Mexico's digital education platforms"
            }
        }
        
        if country.region in regional_examples and technology.name in regional_examples[country.region]:
            case_studies.append({
                "title": regional_examples[country.region][technology.name],
                "region": country.region,
                "relevance_score": 0.9
            })
        
        return case_studies
    
    def _research_government_initiatives(self, country: Country, technology: Technology) -> List[Dict]:
        """Research government initiatives and policies"""
        initiatives = []
        
        # Generate realistic government initiatives based on country and technology
        initiative_templates = {
            "Digital Identity": f"{country.name} National Digital ID Program",
            "Mobile Money": f"{country.name} Financial Inclusion Strategy",
            "Artificial Intelligence": f"{country.name} AI Development Framework",
            "Clean Energy": f"{country.name} Renewable Energy Roadmap",
            "E-Government": f"{country.name} Digital Government Transformation"
        }
        
        if technology.name in initiative_templates:
            initiatives.append({
                "name": initiative_templates[technology.name],
                "status": random.choice(["Planning", "Implementation", "Pilot"]),
                "budget_usd": random.randint(10000000, 500000000),
                "timeline": f"{random.randint(2024, 2026)}-{random.randint(2027, 2030)}"
            })
        
        return initiatives
    
    def _research_challenges_opportunities(self, country: Country, technology: Technology) -> Dict:
        """Identify key challenges and opportunities"""
        return {
            "challenges": [
                "Infrastructure limitations",
                "Digital literacy gaps", 
                "Regulatory frameworks",
                "Funding constraints",
                "Skills shortage"
            ],
            "opportunities": [
                "Leapfrogging legacy systems",
                "Mobile-first adoption",
                "Public-private partnerships",
                "International development funding",
                "Regional collaboration"
            ]
        }
    
    def generate_blog_post(self, country: Country, technology: Technology, research_data: Dict) -> Dict:
        """Generate a comprehensive blog post using AI"""
        try:
            # Create the blog post prompt
            prompt = self._create_blog_prompt(country, technology, research_data)
            
            # Generate content using OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technology journalist specializing in emerging markets and economic development. Write engaging, informative blog posts about how technology is transforming the Global South."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=3000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # Generate title and metadata
            title = self._generate_title(country, technology)
            excerpt = self._generate_excerpt(content)
            tags = self._generate_tags(country, technology)
            
            return {
                "title": title,
                "content": content,
                "excerpt": excerpt,
                "tags": tags,
                "word_count": len(content.split()),
                "reading_time_minutes": max(1, len(content.split()) // 200)
            }
            
        except Exception as e:
            print(f"Error generating blog post: {e}")
            return self._generate_fallback_content(country, technology)
    
    def _create_blog_prompt(self, country: Country, technology: Technology, research_data: Dict) -> str:
        """Create a detailed prompt for blog post generation"""
        return f"""
Write a comprehensive blog post about how {technology.name} is transforming {country.name}'s economy and society.

Country Context:
- Population: {country.population:,}
- GDP: ${country.gdp_usd:,}
- GDP per capita: ${country.gdp_per_capita:,}
- Region: {country.region}

Technology Focus: {technology.name} ({technology.category})
Description: {technology.description}

Research Data:
{json.dumps(research_data, indent=2)}

The blog post should:
1. Start with an engaging hook about the transformation happening in {country.name}
2. Explain what {technology.name} is and why it matters
3. Detail specific applications and use cases in {country.name}
4. Discuss economic impact including GDP growth and poverty alleviation
5. Explain how this improves government services and citizen engagement
6. Include challenges and opportunities
7. Conclude with future outlook and broader implications

Target length: 1200-1500 words
Tone: Professional but accessible, optimistic but realistic
Include specific data points and examples where possible.
"""
    
    def _generate_title(self, country: Country, technology: Technology) -> str:
        """Generate an engaging title for the blog post"""
        title_templates = [
            f"How {technology.name} is Revolutionizing {country.name}'s Economy",
            f"{country.name}'s {technology.name} Transformation: A Development Success Story",
            f"From Challenge to Opportunity: {technology.name} in {country.name}",
            f"{country.name} Leads the Way: {technology.name} Driving Economic Growth",
            f"The {technology.name} Revolution: Transforming Lives in {country.name}"
        ]
        return random.choice(title_templates)
    
    def _generate_excerpt(self, content: str) -> str:
        """Generate an excerpt from the blog post content"""
        sentences = content.split('. ')
        if len(sentences) >= 2:
            return '. '.join(sentences[:2]) + '.'
        return content[:200] + '...' if len(content) > 200 else content
    
    def _generate_tags(self, country: Country, technology: Technology) -> List[str]:
        """Generate relevant tags for the blog post"""
        tags = [
            country.name,
            country.region,
            technology.name,
            technology.category,
            "Economic Development",
            "Global South",
            "Technology Innovation"
        ]
        
        # Add technology-specific tags
        tech_tags = {
            "Mobile Money": ["Financial Inclusion", "Digital Payments"],
            "Artificial Intelligence": ["AI", "Machine Learning", "Automation"],
            "Blockchain": ["Cryptocurrency", "Digital Identity", "Supply Chain"],
            "Internet of Things": ["IoT", "Smart Cities", "Connected Devices"],
            "Digital Identity": ["Biometrics", "Government Services", "Identity"],
            "Clean Energy": ["Renewable Energy", "Sustainability", "Climate"]
        }
        
        if technology.name in tech_tags:
            tags.extend(tech_tags[technology.name])
        
        return tags[:10]  # Limit to 10 tags
    
    def _generate_fallback_content(self, country: Country, technology: Technology) -> Dict:
        """Generate fallback content if AI generation fails"""
        return {
            "title": f"{technology.name} Transformation in {country.name}",
            "content": f"This is a placeholder blog post about how {technology.name} is transforming {country.name}. The automated content generation system encountered an issue, but this post has been created to maintain the publishing schedule.",
            "excerpt": f"Exploring the impact of {technology.name} on {country.name}'s development.",
            "tags": [country.name, technology.name, "Technology", "Development"],
            "word_count": 50,
            "reading_time_minutes": 1
        }
    
    # Helper methods for research simulation
    def _classify_development_status(self, country: Country) -> str:
        if country.gdp_per_capita < 1000:
            return "Low Income"
        elif country.gdp_per_capita < 4000:
            return "Lower Middle Income"
        elif country.gdp_per_capita < 12000:
            return "Upper Middle Income"
        else:
            return "High Income"
    
    def _get_key_sectors(self, country: Country) -> List[str]:
        # Simplified sector classification based on region
        sectors_by_region = {
            "Africa": ["Agriculture", "Mining", "Services", "Manufacturing"],
            "Asia": ["Manufacturing", "Services", "Technology", "Agriculture"],
            "Latin America": ["Services", "Manufacturing", "Agriculture", "Mining"],
            "Middle East": ["Oil & Gas", "Services", "Manufacturing", "Tourism"]
        }
        return sectors_by_region.get(country.region, ["Services", "Manufacturing", "Agriculture"])
    
    def _assess_digital_readiness(self, country: Country) -> str:
        # Simple assessment based on GDP per capita
        if country.gdp_per_capita > 8000:
            return "High"
        elif country.gdp_per_capita > 3000:
            return "Medium"
        else:
            return "Low"
    
    def _estimate_adoption_rate(self, technology: Technology) -> float:
        # Simulated adoption rates
        rates = {
            "Mobile Money": 0.65,
            "Digital Identity": 0.45,
            "Artificial Intelligence": 0.25,
            "Blockchain": 0.15,
            "Internet of Things": 0.35,
            "Clean Energy": 0.55
        }
        return rates.get(technology.name, 0.30)
    
    def _get_technology_benefits(self, technology: Technology) -> List[str]:
        benefits = {
            "Mobile Money": ["Financial inclusion", "Reduced transaction costs", "Economic empowerment"],
            "Digital Identity": ["Improved service delivery", "Reduced fraud", "Financial inclusion"],
            "Artificial Intelligence": ["Efficiency gains", "Better decision making", "Automation"],
            "Blockchain": ["Transparency", "Security", "Reduced intermediaries"],
            "Internet of Things": ["Data insights", "Automation", "Resource optimization"],
            "Clean Energy": ["Environmental sustainability", "Energy independence", "Job creation"]
        }
        return benefits.get(technology.name, ["Innovation", "Efficiency", "Growth"])
    
    def _get_implementation_challenges(self, technology: Technology) -> List[str]:
        return [
            "Infrastructure requirements",
            "Skills gap",
            "Regulatory uncertainty",
            "High initial costs",
            "User adoption barriers"
        ]
    
    def _estimate_poverty_impact(self, country: Country, technology: Technology) -> str:
        # Simplified poverty impact assessment
        impact_scores = {
            "Mobile Money": "High",
            "Digital Identity": "Medium",
            "Artificial Intelligence": "Medium", 
            "EdTech": "High",
            "AgTech": "High",
            "Clean Energy": "Medium"
        }
        return impact_scores.get(technology.name, "Low")

def main():
    """Test the content generator"""
    generator = ContentGenerator()
    
    # Test country selection
    country = generator.select_daily_country()
    if country:
        print(f"Selected country: {country.name}")
        
        # Test technology selection
        technology = generator.select_technology_for_country(country)
        if technology:
            print(f"Selected technology: {technology.name}")
            
            # Test research
            research_data = generator.conduct_research(country, technology)
            print(f"Research completed: {len(research_data)} sections")
            
            # Test blog post generation
            blog_data = generator.generate_blog_post(country, technology, research_data)
            print(f"Generated blog post: {blog_data['title']}")
            print(f"Word count: {blog_data['word_count']}")

if __name__ == "__main__":
    main()


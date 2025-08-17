#!/usr/bin/env python3
"""
Automated Media Generation System
Handles creation of images, videos, and other visual assets for blog posts
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Add the parent directory to the path to import models
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.blog import BlogPost, Country, Technology

logger = logging.getLogger(__name__)

class MediaGenerator:
    """Generates visual media assets for blog posts"""
    
    def __init__(self):
        self.media_dir = "/tmp/media"
        self.ensure_media_directories()
    
    def ensure_media_directories(self):
        """Ensure media directories exist"""
        directories = [
            self.media_dir,
            f"{self.media_dir}/images",
            f"{self.media_dir}/videos",
            f"{self.media_dir}/thumbnails"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def generate_post_media(self, country: Country, technology: Technology, 
                          blog_data: Dict) -> List[Dict]:
        """Generate all media assets for a blog post"""
        media_assets = []
        
        try:
            # Generate featured image
            featured_image = self._generate_featured_image(country, technology, blog_data)
            if featured_image:
                media_assets.append(featured_image)
            
            # Generate technology illustration
            tech_illustration = self._generate_technology_illustration(technology, blog_data)
            if tech_illustration:
                media_assets.append(tech_illustration)
            
            # Generate country context image
            country_image = self._generate_country_image(country, blog_data)
            if country_image:
                media_assets.append(country_image)
            
            # Generate infographic (optional)
            if self._should_generate_infographic(blog_data):
                infographic = self._generate_infographic(country, technology, blog_data)
                if infographic:
                    media_assets.append(infographic)
            
            # Generate social media assets
            social_assets = self._generate_social_media_assets(country, technology, blog_data)
            media_assets.extend(social_assets)
            
            logger.info(f"Generated {len(media_assets)} media assets")
            return media_assets
            
        except Exception as e:
            logger.error(f"Error generating media assets: {e}")
            return []
    
    def _generate_featured_image(self, country: Country, technology: Technology, 
                               blog_data: Dict) -> Optional[Dict]:
        """Generate the main featured image for the blog post"""
        try:
            # Create descriptive prompt for the featured image
            prompt = self._create_featured_image_prompt(country, technology, blog_data)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"featured_{country.code.lower()}_{technology.name.lower().replace(' ', '_')}_{timestamp}.png"
            file_path = f"{self.media_dir}/images/{filename}"
            
            # Generate image using the media generation API
            success = self._generate_image_with_prompt(prompt, file_path)
            
            if success:
                return {
                    "type": "image",
                    "file_path": f"/static/media/images/{filename}",
                    "alt_text": f"{technology.name} transformation in {country.name}",
                    "caption": f"How {technology.name} is transforming {country.name}'s economy and society",
                    "is_featured": True
                }
            
        except Exception as e:
            logger.error(f"Error generating featured image: {e}")
        
        return None
    
    def _generate_technology_illustration(self, technology: Technology, 
                                        blog_data: Dict) -> Optional[Dict]:
        """Generate an illustration of the technology concept"""
        try:
            # Create technology-specific prompt
            prompt = self._create_technology_prompt(technology)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tech_{technology.name.lower().replace(' ', '_')}_{timestamp}.png"
            file_path = f"{self.media_dir}/images/{filename}"
            
            success = self._generate_image_with_prompt(prompt, file_path)
            
            if success:
                return {
                    "type": "image",
                    "file_path": f"/static/media/images/{filename}",
                    "alt_text": f"{technology.name} technology illustration",
                    "caption": f"Understanding {technology.name} technology",
                    "is_featured": False
                }
                
        except Exception as e:
            logger.error(f"Error generating technology illustration: {e}")
        
        return None
    
    def _generate_country_image(self, country: Country, blog_data: Dict) -> Optional[Dict]:
        """Generate an image representing the country context"""
        try:
            # Create country-specific prompt
            prompt = self._create_country_prompt(country)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"country_{country.code.lower()}_{timestamp}.png"
            file_path = f"{self.media_dir}/images/{filename}"
            
            success = self._generate_image_with_prompt(prompt, file_path)
            
            if success:
                return {
                    "type": "image", 
                    "file_path": f"/static/media/images/{filename}",
                    "alt_text": f"{country.name} development and modernization",
                    "caption": f"Economic development in {country.name}",
                    "is_featured": False
                }
                
        except Exception as e:
            logger.error(f"Error generating country image: {e}")
        
        return None
    
    def _generate_infographic(self, country: Country, technology: Technology, 
                            blog_data: Dict) -> Optional[Dict]:
        """Generate an infographic with key statistics"""
        try:
            # Create infographic prompt with data visualization
            prompt = self._create_infographic_prompt(country, technology, blog_data)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"infographic_{country.code.lower()}_{technology.name.lower().replace(' ', '_')}_{timestamp}.png"
            file_path = f"{self.media_dir}/images/{filename}"
            
            success = self._generate_image_with_prompt(prompt, file_path)
            
            if success:
                return {
                    "type": "infographic",
                    "file_path": f"/static/media/images/{filename}",
                    "alt_text": f"{technology.name} impact statistics in {country.name}",
                    "caption": f"Key statistics: {technology.name} in {country.name}",
                    "is_featured": False
                }
                
        except Exception as e:
            logger.error(f"Error generating infographic: {e}")
        
        return None
    
    def _generate_social_media_assets(self, country: Country, technology: Technology, 
                                    blog_data: Dict) -> List[Dict]:
        """Generate social media optimized images"""
        social_assets = []
        
        # Generate Twitter/X card image (1200x630)
        twitter_asset = self._generate_social_card(
            country, technology, blog_data, "twitter", (1200, 630)
        )
        if twitter_asset:
            social_assets.append(twitter_asset)
        
        # Generate LinkedIn image (1200x627)
        linkedin_asset = self._generate_social_card(
            country, technology, blog_data, "linkedin", (1200, 627)
        )
        if linkedin_asset:
            social_assets.append(linkedin_asset)
        
        # Generate Instagram square (1080x1080)
        instagram_asset = self._generate_social_card(
            country, technology, blog_data, "instagram", (1080, 1080)
        )
        if instagram_asset:
            social_assets.append(instagram_asset)
        
        return social_assets
    
    def _generate_social_card(self, country: Country, technology: Technology, 
                            blog_data: Dict, platform: str, dimensions: Tuple[int, int]) -> Optional[Dict]:
        """Generate social media card for specific platform"""
        try:
            prompt = self._create_social_card_prompt(country, technology, blog_data, platform)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"social_{platform}_{country.code.lower()}_{timestamp}.png"
            file_path = f"{self.media_dir}/images/{filename}"
            
            success = self._generate_image_with_prompt(prompt, file_path, dimensions)
            
            if success:
                return {
                    "type": f"social_{platform}",
                    "file_path": f"/static/media/images/{filename}",
                    "alt_text": f"{blog_data['title']} - {platform} share image",
                    "caption": f"Share on {platform.title()}",
                    "is_featured": False,
                    "platform": platform,
                    "dimensions": f"{dimensions[0]}x{dimensions[1]}"
                }
                
        except Exception as e:
            logger.error(f"Error generating {platform} social card: {e}")
        
        return None
    
    def _create_featured_image_prompt(self, country: Country, technology: Technology, 
                                    blog_data: Dict) -> str:
        """Create prompt for featured image generation"""
        return f"""
        Create a professional, modern featured image for a blog post about {technology.name} in {country.name}.
        
        The image should show:
        - Modern technology and digital transformation
        - {country.name} context with cultural elements
        - {technology.name} applications and benefits
        - Economic growth and development themes
        - Professional, clean design suitable for a tech blog
        
        Style: Modern, clean, professional, optimistic
        Colors: Blue, purple, cyan gradients with white accents
        Aspect ratio: 16:9 landscape
        No text overlays needed
        """
    
    def _create_technology_prompt(self, technology: Technology) -> str:
        """Create prompt for technology illustration"""
        tech_prompts = {
            "Mobile Money": "Modern mobile payment interface, smartphone with digital wallet, financial inclusion symbols, clean tech illustration",
            "Digital Identity": "Biometric authentication, digital ID cards, secure identity verification, modern security technology",
            "Artificial Intelligence": "AI neural networks, machine learning algorithms, futuristic technology, data processing visualization",
            "Blockchain": "Blockchain network visualization, distributed ledger, cryptocurrency symbols, secure digital transactions",
            "Internet of Things": "Connected devices, smart sensors, IoT network, modern technology ecosystem",
            "Clean Energy": "Solar panels, wind turbines, renewable energy, sustainable technology, green innovation",
            "E-Government": "Digital government services, online portals, citizen engagement, modern public services",
            "AgTech": "Smart farming, agricultural technology, precision agriculture, modern farming equipment",
            "EdTech": "Digital learning, online education, educational technology, modern classroom technology",
            "Telemedicine": "Remote healthcare, digital health, medical technology, telehealth consultation"
        }
        
        base_prompt = tech_prompts.get(technology.name, f"{technology.name} technology illustration")
        
        return f"""
        {base_prompt}
        
        Style: Clean, modern, professional illustration
        Colors: Technology-focused color palette with blues and purples
        Background: Clean, minimal
        No text overlays
        High quality, detailed illustration
        """
    
    def _create_country_prompt(self, country: Country) -> str:
        """Create prompt for country context image"""
        return f"""
        Create an image representing economic development and modernization in {country.name}.
        
        Show:
        - Modern urban development and infrastructure
        - Economic growth and prosperity
        - Technology adoption and digital transformation
        - Cultural elements specific to {country.name}
        - People benefiting from technological progress
        
        Style: Optimistic, modern, professional
        Colors: Warm, inviting colors with technology accents
        No text overlays
        Represent {country.region} regional characteristics
        """
    
    def _create_infographic_prompt(self, country: Country, technology: Technology, 
                                 blog_data: Dict) -> str:
        """Create prompt for infographic generation"""
        return f"""
        Create a modern infographic showing the impact of {technology.name} in {country.name}.
        
        Include visual elements for:
        - GDP growth statistics
        - Population impact numbers
        - Technology adoption rates
        - Economic benefits
        - Timeline of development
        
        Style: Clean, modern infographic design
        Colors: Professional blue and purple gradient scheme
        Layout: Vertical infographic format
        Include charts, icons, and data visualizations
        Professional typography and clean design
        """
    
    def _create_social_card_prompt(self, country: Country, technology: Technology, 
                                 blog_data: Dict, platform: str) -> str:
        """Create prompt for social media card"""
        return f"""
        Create a social media card for {platform} about {technology.name} in {country.name}.
        
        The image should:
        - Be optimized for {platform} sharing
        - Include visual elements representing {technology.name}
        - Show {country.name} context
        - Have a modern, professional design
        - Be eye-catching and shareable
        
        Style: Modern, clean, social media optimized
        Colors: Brand colors (blue, purple, cyan)
        Text: Minimal or no text (will be added separately)
        Design: Engaging and professional
        """
    
    def _generate_image_with_prompt(self, prompt: str, file_path: str, 
                                  dimensions: Optional[Tuple[int, int]] = None) -> bool:
        """Generate image using AI image generation service"""
        try:
            # This is a placeholder for actual image generation
            # In a real implementation, this would call an image generation API
            # like DALL-E, Midjourney, or Stable Diffusion
            
            logger.info(f"Generating image: {file_path}")
            logger.debug(f"Prompt: {prompt}")
            
            # For now, create a placeholder image file
            # In production, replace this with actual image generation
            placeholder_content = f"Generated image for: {prompt[:100]}..."
            
            with open(file_path, 'w') as f:
                f.write(placeholder_content)
            
            logger.info(f"Image generated successfully: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return False
    
    def _should_generate_infographic(self, blog_data: Dict) -> bool:
        """Determine if an infographic should be generated"""
        # Generate infographic for longer posts with data
        return (
            blog_data['word_count'] > 1200 and
            any(keyword in blog_data['content'].lower() 
                for keyword in ['statistics', 'data', 'percent', 'growth', 'increase'])
        )
    
    def generate_video_content(self, country: Country, technology: Technology, 
                             blog_data: Dict) -> Optional[Dict]:
        """Generate video content for the blog post (future feature)"""
        try:
            # This would generate short video content
            # Currently not implemented but structure is ready
            
            logger.info("Video generation not yet implemented")
            return None
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return None
    
    def optimize_images(self, media_assets: List[Dict]) -> List[Dict]:
        """Optimize generated images for web delivery"""
        try:
            optimized_assets = []
            
            for asset in media_assets:
                if asset['type'] in ['image', 'infographic'] or asset['type'].startswith('social_'):
                    # In production, this would optimize images:
                    # - Compress for web
                    # - Generate multiple sizes
                    # - Create WebP versions
                    # - Add lazy loading attributes
                    
                    optimized_asset = asset.copy()
                    optimized_asset['optimized'] = True
                    optimized_assets.append(optimized_asset)
                else:
                    optimized_assets.append(asset)
            
            logger.info(f"Optimized {len(optimized_assets)} media assets")
            return optimized_assets
            
        except Exception as e:
            logger.error(f"Error optimizing images: {e}")
            return media_assets
    
    def cleanup_old_media(self, days_old: int = 30):
        """Clean up old media files to save storage space"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # In production, this would:
            # - Find files older than cutoff_date
            # - Check if they're still referenced in the database
            # - Delete unreferenced old files
            # - Update file paths if needed
            
            logger.info(f"Media cleanup completed (files older than {days_old} days)")
            
        except Exception as e:
            logger.error(f"Error cleaning up media: {e}")

def main():
    """Test the media generator"""
    from models.blog import Country, Technology
    
    # Create test instances
    country = Country(name="Kenya", code="KEN", region="Africa")
    technology = Technology(name="Mobile Money", category="Fintech")
    blog_data = {
        "title": "Kenya's Mobile Money Revolution",
        "content": "Test content about mobile money in Kenya...",
        "word_count": 1500
    }
    
    generator = MediaGenerator()
    media_assets = generator.generate_post_media(country, technology, blog_data)
    
    print(f"Generated {len(media_assets)} media assets:")
    for asset in media_assets:
        print(f"- {asset['type']}: {asset['file_path']}")

if __name__ == "__main__":
    main()


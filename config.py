"""Configuration settings for the Job Analyzer."""
import os
from typing import List

# Default search categories if none provided
DEFAULT_SEARCH_CATEGORIES = [
    'strategy',
    'project',
    'consultant',
    'business',
    'product',
    'marketing'
]

class Config:
    """Configuration class for the Job Analyzer."""
    
    def __init__(self):
        # API Configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        # Resume Configuration
        self.resume_path = os.getenv('RESUME_PATH', 'resume.txt')
        if not os.path.exists(self.resume_path):
            raise FileNotFoundError(f"Resume file not found at {self.resume_path}")
            
        # Search Configuration
        self.search_categories = os.getenv('SEARCH_CATEGORIES', '').split(',')
        if not self.search_categories or self.search_categories == ['']:
            self.search_categories = DEFAULT_SEARCH_CATEGORIES
            
        # Scraping Configuration
        self.base_url = "https://www.arbeitnow.com"
        self.max_retries = 3
        self.max_pages = int(os.getenv('MAX_PAGES', '2'))
        
        # Output Configuration
        self.output_dir = os.getenv('OUTPUT_DIR', 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Logging Configuration
        self.logs_dir = os.getenv('LOGS_DIR', 'logs')
        os.makedirs(self.logs_dir, exist_ok=True)

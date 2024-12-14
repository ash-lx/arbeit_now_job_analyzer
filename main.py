import argparse
import pandas as pd
import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import logging
import os
from openai import OpenAI
import json
from config import Config


class IntegratedJobAnalyzer:
    """
    An integrated job analysis system that combines web scraping and AI-powered
    job matching capabilities to help users find relevant job opportunities.
    """

    def __init__(self, config: Config):
        """
        Initialize the job analyzer with configuration settings.
        
        Args:
            config (Config): Configuration object containing all necessary settings
        """
        self.config = config
        self.base_url = config.base_url
        self.jobs_data = []
        self.search_categories = config.search_categories
        self.filename = os.path.join(
            config.output_dir,
            f'Analyzed_Jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )

        # Setup OpenAI
        try:
            self.client = OpenAI(api_key=config.openai_api_key)
            print("OpenAI client initialized successfully")
        except Exception as e:
            print(f"Error initializing OpenAI client: {str(e)}")
            raise

        # Load resume
        try:
            with open(config.resume_path, 'r', encoding='utf-8') as file:
                self.resume = file.read()
            print("Resume loaded successfully")
        except Exception as e:
            print(f"Error loading resume: {str(e)}")
            raise

        # Setup logging
        logging.basicConfig(
            filename=os.path.join(
                config.logs_dir,
                f'analyzer_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
            ),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # Setup Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        logging.info("Chrome driver initialized successfully")

    def analyze_with_gpt(self, job_data: dict) -> dict:
        """
        Analyze job details using GPT to determine match with resume.
        
        Args:
            job_data (dict): Dictionary containing job details
            
        Returns:
            dict: Analysis results including match score and recommendations
        """
        try:
            print(f"\nAnalyzing job with GPT: {job_data['title']}")

            system_prompt = """You are an expert ATS system and career advisor analyzing job descriptions and resumes.
            You must respond ONLY with a valid JSON object in the exact format shown below:
            {
                "match_score": <number between 0-100>,
                "german_required": <"Yes" or "No">,
                "key_matches": <array of strings>,
                "missing_skills": <array of strings>,
                "recommendation": <string>
            }
            Do not include any other text or explanation outside the JSON object."""

            user_prompt = f"""
            JOB TITLE: {job_data['title']}

            RESUME:
            {self.resume}

            JOB DESCRIPTION:
            {job_data['description']}

            Analyze based on:
            1. Skills Match (30%): Technical and soft skills alignment
            2. Experience Relevance (30%): Years and type of experience
            3. Role Alignment (25%): Job responsibility match
            4. Education/Qualifications (15%): Required qualifications match

            German Language:
            - "Yes" only if German explicitly required
            - "No" if preferred/optional/not mentioned
            - "No" if job is in German but doesn't specify requirement

            Respond ONLY with a JSON object matching the format specified in the system prompt.
            Do not include any text before or after the JSON object."""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )

            response_text = response.choices[0].message.content.strip()

            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                cleaned_response = response_text.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()
                result = json.loads(cleaned_response)

            required_fields = ['match_score', 'german_required',
                             'key_matches', 'missing_skills', 'recommendation']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")

            analyzed_job = {
                'search_category': job_data['search_category'],
                'title': job_data['title'],
                'company': job_data['company'],
                'location': job_data['location'],
                'url': job_data['url'],
                'match_score': result['match_score'],
                'german_required': result['german_required'],
                'key_matches': '; '.join(result['key_matches']),
                'missing_skills': '; '.join(result['missing_skills']),
                'recommendation': result['recommendation']
            }

            print(f"Analysis complete - Score: {result['match_score']}, German Required: {result['german_required']}")
            return analyzed_job

        except Exception as e:
            print(f"GPT analysis failed for {job_data['title']}: {str(e)}")
            return self.create_fallback_analysis(job_data)

    def create_fallback_analysis(self, job_data):
        """Create a fallback analysis when GPT analysis fails."""
        return {
            'search_category': job_data['search_category'],
            'title': job_data['title'],
            'company': job_data['company'],
            'location': job_data['location'],
            'url': job_data['url'],
            'match_score': 0,
            'german_required': 'No',
            'key_matches': 'Analysis failed',
            'missing_skills': 'Analysis failed',
            'recommendation': 'Analysis failed - please review manually'
        }

    def extract_job_description(self, url: str, max_retries: int = 3) -> str:
        """
        Extract job description from the provided URL.
        
        Args:
            url (str): Job posting URL
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            str: Job description text
        """
        for attempt in range(max_retries):
            try:
                print(f"Fetching job description: {url}")
                self.driver.get(url)

                description_element = self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div[itemprop="description"]'))
                )

                description_html = description_element.get_attribute('innerHTML')
                soup = BeautifulSoup(description_html, 'html.parser')
                description = soup.get_text(separator='\n', strip=True)

                print("Description fetched successfully")
                return description

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    logging.error(f"Failed to get description for {url}: {str(e)}")
                    return "Failed to fetch description"
                time.sleep(random.uniform(2, 4))

    def extract_basic_job_info(self, job_element, search_category):
        """Extract basic job information without description."""
        try:
            title_element = job_element.find_element(
                By.CSS_SELECTOR, 'h2[itemprop="title"]')
            title = title_element.text.strip()
            url_element = title_element.find_element(
                By.CSS_SELECTOR, 'a[itemprop="url"]')
            url = url_element.get_attribute('href')

            company_element = job_element.find_element(
                By.CSS_SELECTOR, 'a[itemprop="hiringOrganization"]')
            company = company_element.text.strip()

            location_element = job_element.find_element(
                By.CSS_SELECTOR, 'span.text-gray-600')
            location = location_element.text.strip()

            return {
                'search_category': search_category,
                'title': title,
                'company': company,
                'location': location,
                'url': url,
                'description': None
            }
        except Exception as e:
            logging.error(f"Error extracting basic job info: {e}")
            return None

    def scrape_page(self, page_number: int, search_category: str) -> list:
        """
        First pass: Scrape basic job information from page.
        
        Args:
            page_number (int): Page number to scrape
            search_category (str): Job category to search for
            
        Returns:
            list: List of jobs with basic information
        """
        try:
            url = f"{self.base_url}/?search={search_category}&tags=&sort_by=newest&page={page_number}"
            print(f"\nScraping URL: {url}")

            self.driver.get(url)
            time.sleep(2)

            job_listings = self.driver.find_elements(
                By.CSS_SELECTOR, 'li.list-none.hover\\:shadow-sm')
            print(f"Found {len(job_listings)} job listings")

            page_jobs = []
            for job_listing in job_listings:
                job_info = self.extract_basic_job_info(
                    job_listing, search_category)
                if job_info:
                    page_jobs.append(job_info)

            print(f"Extracted basic info for {len(page_jobs)} jobs from page {page_number}")
            return page_jobs

        except Exception as e:
            logging.error(f"Error scraping page {page_number}: {e}")
            return []

    def remove_duplicates(self, jobs: list) -> list:
        """Remove duplicate jobs based on URL."""
        unique_jobs = []
        seen_urls = set()

        for job in jobs:
            if job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)

        print(f"Removed {len(jobs) - len(unique_jobs)} duplicate jobs")
        return unique_jobs

    def process_jobs(self):
        """Complete job processing pipeline."""
        all_jobs = []

        # First pass: Collect all basic job information
        for category in self.search_categories:
            print(f"\n{'='*50}")
            print(f"Processing category: {category}")
            print(f"{'='*50}")

            for page in range(1, self.config.max_pages + 1):
                print(f"\nProcessing page {page} for {category}")
                page_jobs = self.scrape_page(page, category)
                if not page_jobs:
                    break

                all_jobs.extend(page_jobs)
                time.sleep(random.uniform(1, 2))

        # Remove duplicates before detailed analysis
        print("\nRemoving duplicate job listings...")
        unique_jobs = self.remove_duplicates(all_jobs)
        print(f"\nCollected {len(unique_jobs)} unique jobs across all categories")

        # Second pass: Add descriptions and analyze
        analyzed_jobs = []
        print("\nStarting to fetch job descriptions and analyze...")
        for i, job in enumerate(unique_jobs, 1):
            try:
                print(f"\nProcessing job {i}/{len(unique_jobs)}: {job['title']}")

                # Get description
                description = self.extract_job_description(job['url'])
                if not description:
                    continue

                job['description'] = description

                # Analyze with GPT
                analyzed_job = self.analyze_with_gpt(job)
                if analyzed_job:
                    analyzed_jobs.append(analyzed_job)

                time.sleep(random.uniform(1, 2))

            except Exception as e:
                print(f"Error processing job {job['title']}: {str(e)}")
                continue

        # Save results
        if analyzed_jobs:
            df = pd.DataFrame(analyzed_jobs)
            df.insert(0, 'S.No', range(1, len(df) + 1))
            df.to_csv(self.filename, index=False, encoding='utf-8')
          print(f"\nResults saved to {self.filename}")
            print("\nAnalysis Summary:")
            print(f"Total jobs analyzed: {len(df)}")
            print(f"Average match score: {df['match_score'].mean():.2f}")
            print(f"Jobs requiring German: {(df['german_required'] == 'Yes').sum()}")

            # Summary by category
            print("\nCategory-wise Summary:")
            category_summary = df.groupby('search_category').agg({
                'S.No': 'count',
                'match_score': 'mean',
                'german_required': lambda x: (x == 'Yes').sum()
            }).round(2)
            print(category_summary)

            print("\nTop 5 Matches Overall:")
            print(df[['search_category', 'title', 'company', 'match_score', 'german_required', 'key_matches']]
                  .sort_values('match_score', ascending=False)
                  .head(5))

    def __del__(self):
        """Cleanup resources."""
        try:
            self.driver.quit()
        except:
            pass


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Job Analysis Tool')
    parser.add_argument('--resume', type=str, help='Path to resume file')
    parser.add_argument('--categories', type=str, help='Comma-separated list of job categories')
    parser.add_argument('--max-pages', type=int, help='Maximum number of pages to scrape per category')
    parser.add_argument('--output-dir', type=str, help='Directory for output files')
    return parser.parse_args()


def main():
    """Main entry point for the job analyzer."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set environment variables from command line arguments if provided
    if args.resume:
        os.environ['RESUME_PATH'] = args.resume
    if args.categories:
        os.environ['SEARCH_CATEGORIES'] = args.categories
    if args.max_pages:
        os.environ['MAX_PAGES'] = str(args.max_pages)
    if args.output_dir:
        os.environ['OUTPUT_DIR'] = args.output_dir

    try:
        # Initialize configuration
        config = Config()
        
        # Initialize and run analyzer
        analyzer = IntegratedJobAnalyzer(config=config)
        analyzer.process_jobs()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        logging.error(f"Fatal error: {str(e)}")
    finally:
        if 'analyzer' in locals():
            analyzer.driver.quit()


if __name__ == "__main__":
    main()

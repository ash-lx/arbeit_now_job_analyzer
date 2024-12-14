# arbeit_now_job_analyzer
The smart job matching tool that understands both you and the market -> Built for https://www.arbeitnow.com

# AI-Powered Job Analyzer

An intelligent job analysis tool that combines web scraping and AI to help match your resume with job postings. The tool scrapes job listings from Arbeitnow.com and uses GPT to analyze job fit based on your resume.

## Features

- Automated job scraping from Arbeitnow.com
- AI-powered job matching using GPT
- Customizable job categories
- Detailed analysis of skills match and requirements
- German language requirement detection
- Comprehensive output in CSV format
- Category-wise analysis and summaries

## Prerequisites

- Python 3.8+
- Chrome browser installed
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/job-analyzer.git
cd job-analyzer
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with the following:
```
OPENAI_API_KEY=your_api_key_here
RESUME_PATH=path/to/your/resume.txt
OUTPUT_DIR=output
LOGS_DIR=logs
MAX_PAGES=2
```

## Usage

1. Basic usage:
```bash
python main.py
```

2. With command line arguments:
```bash
python main.py --resume path/to/resume.txt --categories "strategy,consulting" --max-pages 3
```

3. Environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `RESUME_PATH`: Path to your resume file (default: resume.txt)
- `SEARCH_CATEGORIES`: Comma-separated list of job categories
- `MAX_PAGES`: Maximum pages to scrape per category
- `OUTPUT_DIR`: Directory for output files
- `LOGS_DIR`: Directory for log files

## Output

The tool generates:
1. A CSV file with analyzed jobs including:
   - Match score
   - Key matching skills
   - Missing skills
   - Recommendations
   - German language requirements
2. Summary statistics
3. Category-wise analysis
4. Top matching jobs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes only. Please respect websites' terms of service and implement appropriate rate limiting when scraping.

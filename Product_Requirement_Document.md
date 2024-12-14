# AI Job Analyzer PRD (for www.arbeitnow.com)
### The smart job matching tool that understands both you and the market

## Why This Matters
Job hunting isn't just about matching keywords. It's about understanding the full context - your skills, the company's needs, and those unspoken requirements that make or break a fit. For international job seekers especially, this includes understanding language requirements and cultural contexts that aren't always obvious in job descriptions.

## Core Problem
- Manual job searching is time-consuming and inefficient
- People miss opportunities because they can't process hundreds of job descriptions
- Job seekers struggle to objectively assess their fit for roles
- Language requirements (especially German) are often buried in job descriptions
- No easy way to track and compare opportunities across multiple job categories

## Solution
An intelligent job analyzer that:
1. Automatically scrapes targeted job postings
2. Uses AI to match your resume against opportunities
3. Provides clear, actionable insights about job fit
4. Surfaces hidden requirements and potential gaps
5. Tracks opportunities across multiple categories

## Key Features

### Smart Scraping
- Multi-category job collection from Arbeitnow.com
- Automatic duplicate removal
- Configurable search depth per category
- Rate-limited to respect website resources

### AI Analysis
- Resume-to-job matching using GPT
- Weighted scoring across:
  - Skills Match (30%)
  - Experience Relevance (30%)
  - Role Alignment (25%)
  - Education/Qualifications (15%)
- German language requirement detection
- Key matching skills identification
- Missing skills analysis
- Personalized recommendations

### Output & Insights
- Comprehensive CSV reports
- Category-wise analysis
- Match score summaries
- Top opportunities ranking
- Language requirement flags

## Success Metrics
1. Analysis accuracy (validated through user feedback)
2. Time saved vs manual search
3. Match score correlation with interview success
4. User-reported job application success rate

## Technical Requirements
- Python 3.8+
- OpenAI API access
- Chrome browser
- 2GB+ RAM
- Stable internet connection

## Timeline
Phase 1 (Week 1-2): Core scraping and analysis
Phase 2 (Week 3-4): Testing and refinement
Phase 3 (Week 5): Documentation and open source release

## Future Enhancements
1. Support for additional job sites
2. Custom scoring weights
3. Interview preparation suggestions
4. Salary range analysis
5. Company culture matching

Remember: This isn't just another job search tool. It's about giving job seekers the insights they need to make confident decisions about their careers, while respecting both their time and the complexity of job matching.

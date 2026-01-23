

def scrape(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    """
    
    Project Scope / documentation:
    
    I want to build a tool that will automate the process of looking at job adds each day as I
    feel that I am waisting a lot of time doing this manually. The tool should be able to:
    1. Scrape job adds from multiple job boards (e.g., Indeed, LinkedIn, Glassdoor).
    2. Filter job adds based on my preferences (e.g., location, salary, job title, company).
    3. Store the jobs in a spreadsheet like google sheets so I can pull from it later
    4. User a LLM to compare the job add to my linkedin profile and give me a match rating per job add this will
         help me prioritize which jobs to apply for first. The ones with low rating means I have to re work my Resume
         or they may be scams.
    5. Ill do a data compare from my data base spread sheet to my job applied sheet to keep track of what I applied for
        all ready so I don't do things multiple times.
    
    Here is a high level breakdwon of the larger blocks that I'll need to code for this project
    I also like to utalize a LLM for this process as I not work with those before I don't think this project
    will be a good use of a AI agent quite yet but I can use it to help with some of the tasks.
    
    1. Data Sources
    LinkedIn Profile
    Export your profile as CSV (LinkedIn has this feature) or use the API if you have access.
    Extract: job history, skills, recommendations, certifications, education.
    
    Job Listings
    Target sites: LinkedIn Jobs, Indeed, Glassdoor, or niche game-dev boards.
    Extract: title, company, location, description, URL, date posted.
    
    2. Preprocessing
    Normalize job titles (e.g., “Technical Artist” vs “Tech Artist”).
    Clean job descriptions (remove HTML, extra whitespace).
    Normalize your LinkedIn data (skills as lowercase, split multi-word skills).
    
    3. Relevance Scoring
    Two main approaches:
    A. Keyword-based scoring (simple)
    score = sum(job_description.count(keyword) for keyword in keywords)
    
    B. Semantic similarity using embeddings (better)
    Use OpenAI embeddings or sentence-transformers.
    Compute vector for each job description and your profile/skills.
    Cosine similarity → score between 0–1.
    
    Example workflow:
    Concatenate your skills + recent job history as “profile text”.
    For each job description: compute similarity score.
    Normalize scores to 0–1 and store in Score column.
    
    4. Output
    Store in Google Sheets: Title | Company | Location | Score | URL | Notes | Date Checked.
    Optional: add conditional formatting in Sheets to highlight high scores.
    Optional: track historical scores to see if jobs get updated.
    
    5. Automation
    Schedule script daily or weekly with cron (Linux/Mac) or Task Scheduler (Windows).
    
    Each run:
    Pull new job listings.
    Score relevance.
    Update Google Sheet.
    
    6. Optional LLM Enhancements
    Summarize job description: “Key responsibilities, must-have skills, preferred skills.”
    Tailor application notes: Generate a short note linking your experience to the job.
    Highlight gaps: Identify skills listed in the job description that you don’t have.
    
    7. Modular Python Structure
    project/
    │
    ├─ data/
    │   ├─ linkedin_export.csv
    │   └─ job_listings.json
    │
    ├─ utils/
    │   ├─ scrape_jobs.py         # scraping logic
    │   ├─ parse_linkedin.py      # extract profile & skills
    │   ├─ score_jobs.py          # keyword or embedding scoring
    │   ├─ gsheet_upload.py       # push results to Google Sheets
    │   └─ summarize_jobs.py      # optional LLM summaries
    │
    ├─ config.py                 # API keys, keywords, thresholds
    └─ main.py                   # orchestrates the workflow
    
    
    This gives you:
    Control (you decide scoring, thresholds, sites).
    Scalability (add more sites, more scoring methods).
    AI Assistance (LLM or embeddings used where they make sense, not everywhere).
    """
    print_hi('PyCharm')

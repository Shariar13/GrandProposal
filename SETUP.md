# Grant Proposal Generator - Setup Instructions

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

Create a `.env` file in the project root (same directory as manage.py):

```bash
# Copy the example file
cp .env.example .env
```

Then edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-API-KEY-HERE
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=400000
OPENAI_TEMPERATURE=0.7
```

**Important:** Never commit your `.env` file to git. It's already in `.gitignore`.

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Run the Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ in your browser.

## Features

- ✅ Comprehensive RAG system (arXiv, OpenAlex, Semantic Scholar + Web Scraping)
- ✅ AI-powered proposal generation with GPT-4
- ✅ Multi-format export (DOCX, PDF, LaTeX, Markdown, TXT, JSON)
- ✅ Professional UI with rich text editing
- ✅ Dynamic funding call discovery
- ✅ Citation management and bibliography generation
- ✅ Version control for proposals
- ✅ User analytics and tracking

## Troubleshooting

### NLTK Data Error
If you get "Resource punkt_tab not found", the system will automatically download it. Just restart the server.

### OpenAI API Key Error
Make sure you've created a `.env` file with your API key. Check that the file is in the same directory as `manage.py`.

### Database Errors
Run migrations:
```bash
python manage.py migrate
```

## Project Structure

```
GrandProposal/
├── home/                          # Main application
│   ├── views_comprehensive.py     # Main views with all features
│   ├── enhanced_rag_with_web.py   # RAG system combining APIs + web
│   ├── web_scraper.py             # Web scraping (Scholar, news, etc.)
│   ├── export_engine.py           # Multi-format export
│   ├── dynamic_proposal_discovery.py  # Funding call discovery
│   └── professional_visuals_generator.py  # Charts and graphs
├── templates/                     # HTML templates
│   ├── base_new.html             # Base template with design system
│   ├── dashboard.html            # Main dashboard
│   ├── my_proposals_comprehensive.html  # Proposal list
│   └── proposal_detail_comprehensive.html  # Proposal editor
├── authentication/               # User authentication
├── static/                       # Static files (CSS, JS, images)
├── .env                         # Your configuration (DO NOT COMMIT)
├── .env.example                 # Example configuration
├── requirements.txt             # Python dependencies
└── manage.py                    # Django management script
```

## Support

For issues and questions, please check the GitHub repository.

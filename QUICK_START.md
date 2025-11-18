# 🚀 Quick Start Guide

## Get Your Grant Proposal Generator Running in 5 Minutes!

### Prerequisites
- Python 3.10 or higher
- Virtual environment activated
- Your OpenAI API key (already in `.env` file)

---

## Step 1: Install Dependencies

```bash
# Activate your virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install python-dotenv for environment variables
pip install python-dotenv

# Install core dependencies (if not already installed)
pip install Django==5.2.6 openai pillow requests
```

---

## Step 2: Update Django Settings

Add this line **at the very top** of `GrantProposal/settings.py` (before any other imports):

```python
from dotenv import load_dotenv
load_dotenv()
```

It should look like this:

```python
from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
from django.contrib.messages import constants as messages
import os
# ... rest of the file
```

---

## Step 3: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Step 4: Populate Proposal Types

This creates all 10 funding body templates (Horizon Europe, NSF, NIH, etc.):

```bash
python manage.py populate_proposal_types
```

You should see:
```
✓ Created Horizon Europe
✓ Created Europol
✓ Created NSF
✓ Created NIH
✓ Created ERC
✓ Created Marie Curie
✓ Created Wellcome Trust
✓ Created Gates Foundation
✓ Created DARPA
✓ Created UKRI

✅ Successfully populated all proposal types!
```

---

## Step 5: Create a Superuser (Optional but Recommended)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

---

## Step 6: Run the Development Server

```bash
python manage.py runserver
```

---

## Step 7: Access the Application

Open your browser and visit:

- **Home Page**: http://127.0.0.1:8000/
- **Dashboard** (after login): http://127.0.0.1:8000/dashboard/
- **Admin Panel**: http://127.0.0.1:8000/admin/

---

## First Time User Flow

### 1. Register an Account
- Visit http://127.0.0.1:8000/
- Click "Get Started Free"
- Fill in your details
- You'll need to provide: username, email, password, first name, last name, university

### 2. Create Your First Proposal
- After login, you'll see the dashboard with 10 funding body options
- Click on any funding body (e.g., "Horizon Europe")
- Fill in:
  - **Research Title**: e.g., "Advanced Deep Learning for Deepfake Detection"
  - **Keywords**: e.g., "deep learning, computer vision, deepfake"
  - **Description**: Detailed description of your research (minimum 10 words recommended)
- Click "Generate Proposal"

### 3. Watch the Magic!
The system will:
1. 🔍 Search academic databases (arXiv, OpenAlex, Semantic Scholar)
2. 📚 Retrieve 100-150 relevant papers with citations
3. 🤖 Generate complete proposal using GPT-4
4. ✅ Display your proposal with perfect citations

### 4. Save and Export
- Review your generated proposal
- Click "Save" to store it in your account
- Click "Export" to download in various formats

---

## Troubleshooting

### Error: "No module named 'dotenv'"
```bash
pip install python-dotenv
```

### Error: "OpenAI API key not found"
Make sure you added the `load_dotenv()` line at the top of `settings.py`

### Error: "ProposalType matching query does not exist"
Run the populate command:
```bash
python manage.py populate_proposal_types
```

### Error: Template not found
Make sure all template files exist in the `templates/` directory

### RAG search is slow
This is normal! The system searches 3 academic databases and analyzes 100+ papers. It takes 30-90 seconds.

---

## What's Included

### Proposal Types (10)
1. **Horizon Europe** - EU's premier research funding (30-70 pages)
2. **Europol** - Law enforcement research (15-40 pages)
3. **NSF** - US National Science Foundation (10-15 pages)
4. **NIH** - US National Institutes of Health (12 pages)
5. **ERC** - European Research Council (15 pages)
6. **Marie Curie** - EU mobility program (10 pages)
7. **Wellcome Trust** - UK health research (8-20 pages)
8. **Gates Foundation** - Global health (10-25 pages)
9. **DARPA** - US defense research (15-25 pages)
10. **UKRI** - UK Research and Innovation (8-15 pages)

### Features
- ✅ AI-powered proposal generation with GPT-4
- ✅ Multi-source academic search (arXiv, OpenAlex, Semantic Scholar)
- ✅ Perfect citation generation (APA + BibTeX)
- ✅ No hallucinations - only real papers
- ✅ Professional academic UI
- ✅ User profiles and analytics
- ✅ Proposal versioning
- ✅ Multi-format export (TXT, JSON, soon PDF/DOCX)
- ✅ Admin panel for management

---

## Admin Panel

Access at: http://127.0.0.1:8000/admin/

You can:
- View all users and their proposals
- Edit proposal types and templates
- View analytics
- Manage all content

---

## Testing the System

### Quick Test
1. Register a new user
2. Go to dashboard
3. Click "Horizon Europe"
4. Enter:
   - Title: "AI for Climate Change"
   - Keywords: "artificial intelligence, climate modeling, machine learning"
   - Description: "Develop advanced AI models to predict climate change impacts and support mitigation strategies through improved weather forecasting and environmental monitoring."
5. Click "Generate Proposal"
6. Wait 1-2 minutes
7. View your generated proposal!

---

## Next Steps

### Customize Proposal Templates
Go to Admin Panel → Proposal Templates to edit:
- Section names
- Word count requirements
- Generation prompts
- Requirements

### Add More Funding Bodies
In Admin Panel → Proposal Types, you can:
- Add custom funding bodies
- Create custom section templates
- Set specific requirements

### Export Improvements
Coming soon:
- PDF export with proper formatting
- DOCX export with styles
- LaTeX export for academic journals

---

## Need Help?

1. Check `TRANSFORMATION_SUMMARY.md` for detailed documentation
2. Review code comments in:
   - `home/enhanced_rag_system.py` - RAG logic
   - `home/enhanced_proposal_generator.py` - AI generation
   - `home/views_enhanced.py` - Request handling
3. Check Django error messages for specifics

---

## Production Deployment (Future)

When ready to deploy:
1. Set `DEBUG = False` in settings.py
2. Configure proper `SECRET_KEY`
3. Set up PostgreSQL database
4. Use Gunicorn or uWSGI
5. Configure Nginx
6. Set up HTTPS
7. Configure proper email backend
8. Set up cloud storage for media files

---

## You're All Set! 🎉

Your professional grant proposal generator is ready to use!

Start creating winning proposals with AI-powered research and perfect citations.

**Happy Grant Writing!** 🚀

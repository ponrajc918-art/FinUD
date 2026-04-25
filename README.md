# FinUD - Financial level Understanding

A full-stack AI-powered web application for financial decision intelligence, built with Flask + vanilla JS.

## Features

| Module | Description |
|--------|-------------|
| 📊 Loan Analysis | ML-based approval/rejection with risk scores + AI explanations |
| 👥 Staff Performance | Target vs achieved analysis with AI coaching suggestions |
| 🎯 Goal Planner | Investment recommendations based on customer profiles |
| 🚨 Fraud Detection | Auto-runs on upload: duplicates, outliers, abnormal income |
| 💬 AI Chatbot | Floating assistant powered by Claude API |
| ✦ AI Engine | Explains all decisions in plain English |

## Tech Stack

- **Backend**: Flask, Pandas, NumPy, Scikit-learn
- **Frontend**: HTML5, CSS3, Vanilla JS, Chart.js
- **AI**: Anthropic Claude API (claude-sonnet-4-20250514)
- **Deploy**: Render (render.yaml included)

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Generate sample datasets (optional)
python generate_samples.py

# Run locally
python app.py
# App runs at http://localhost:5000
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key for AI explanations |
| `PORT` | Server port (default: 5000) |

The app works **without** an API key — it falls back to pre-written financial explanations.

## Deployment (Render)

1. Push to GitHub
2. Create new Web Service on [render.com](https://render.com)
3. Connect repo → Render auto-detects `render.yaml`
4. Add `ANTHROPIC_API_KEY` in Environment Variables
5. Deploy

## CSV Format

### Loan Dataset (sample_loan.csv)
```
loan_id, age, income, loan_amount, credit_score, employment_years, loan_status
```

### Staff Dataset (sample_staff.csv)
```
staff_id, name, department, target, achieved, quarter
```

### Customer Dataset (sample_customer.csv)
```
customer_id, age, income, balance, risk_appetite, occupation
```

> The system auto-detects column names — exact names not required.

## Project Structure

```
finai/
├── app.py              # Flask backend (all API endpoints)
├── templates/
│   └── index.html      # Single-page frontend (SPA)
├── requirements.txt    # Python dependencies
├── generate_samples.py # Sample data generator
├── render.yaml         # Render deployment config
├── Procfile            # Gunicorn start command
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload CSV dataset |
| `/api/stats` | GET | Dataset statistics |
| `/api/dashboard` | GET | KPI data |
| `/api/loan/analyze` | POST | Run loan analysis |
| `/api/staff/analyze` | POST | Run staff analysis |
| `/api/goals/analyze` | POST | Generate investment plans |
| `/api/fraud/<type>` | GET | Get fraud detection results |
| `/api/chat` | POST | AI chatbot |

## Screenshots
# My Project HOME page
<img width="1916" height="966" alt="image" src="https://github.com/user-attachments/assets/38410197-934e-42a6-a433-579bd9dd1250" />
# datasets upload page
<img width="1919" height="973" alt="image" src="https://github.com/user-attachments/assets/90ba241b-49bc-44c7-9cee-28d01393ee0d" />
## screen recording for my working 

https://github.com/user-attachments/assets/5ba736b0-6e4c-4792-921a-ff462b4fcb3e






---

Website link for FinAI :
https://finud.onrender.com/

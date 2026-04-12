# FinAI — Financial Decision Intelligence Dashboard

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
<img width="1918" height="1079" alt="Screenshot 2026-04-10 235309" src="https://github.com/user-attachments/assets/9dc5c7d4-9707-4e0e-b2e8-9304cbaee8b4" />

<img width="1918" height="1079" alt="Screenshot 2026-04-10 235309" src="https://github.com/user-attachments/assets/9dc5c7d4-9707-4e0e-b2e8-9304cbaee8b4" />

<img width="1919" height="1013" alt="Screenshot 2026-04-10 235256" src="https://github.com/user-attachments/assets/082e7de9-0dde-4086-b30b-21f47b8d3736" />

<img width="1919" height="1043" alt="Screenshot 2026-04-10 235245" src="https://github.com/user-attachments/assets/0e7cc203-94e9-4c79-8b67-d0bc14ee12a0" />

<img width="1919" height="1073" alt="Screenshot 2026-04-10 235348" src="https://github.com/user-attachments/assets/8e2a9606-55f8-4d5e-aec9-85184ee6740d" />



---

Built for Final Year Project | Portfolio-ready | Render-deployable

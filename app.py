from flask import Flask, request, jsonify, render_template, session
import pandas as pd
import numpy as np
import json
import os
import requests
from io import StringIO
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.secret_key = 'finai_secret_2024'

# In-memory data store
DATA_STORE = {
    'loan': None,
    'staff': None,
    'customer': None,
    'fraud_results': {}
}

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

def call_claude(prompt, system="You are a financial intelligence AI assistant. Be concise and professional."):
    if not ANTHROPIC_API_KEY:
        return generate_fallback_response(prompt)
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 800,
                "system": system,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        data = response.json()
        if 'content' in data:
            return data['content'][0]['text']
        return "AI analysis unavailable at this time."
    except Exception as e:
        return generate_fallback_response(prompt)

def generate_fallback_response(prompt):
    p = prompt.lower()
    if 'loan' in p and ('approv' in p or 'reject' in p):
        return "Based on the applicant's financial profile, the loan decision reflects their credit history, income stability, and debt-to-income ratio. Key factors include consistent repayment capacity and risk assessment metrics."
    if 'fraud' in p or 'duplicate' in p or 'outlier' in p:
        return "Anomaly detected based on statistical deviation from normal patterns. This entry shows characteristics inconsistent with the dataset's expected distribution."
    if 'staff' in p or 'performance' in p:
        return "Staff performance analysis indicates areas for improvement. Focus on target alignment, training initiatives, and incentive programs to boost achievement rates."
    if 'invest' in p or 'goal' in p:
        return "Based on the customer's financial profile, a balanced investment approach with diversified assets is recommended to achieve long-term financial goals."
    if 'risk' in p:
        return "Risk assessment is based on multiple financial indicators including credit score, income stability, loan-to-value ratio, and repayment history."
    return "I'm your Financial Intelligence Assistant. I can help with loan analysis, risk assessment, staff performance, investment planning, and fraud detection. Please ask me anything about the loaded datasets or banking concepts."

# ─── Routes ─────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_dataset():
    dataset_type = request.form.get('type')
    file = request.files.get('file')
    if not file or not dataset_type:
        return jsonify({'error': 'Missing file or type'}), 400
    try:
        content = file.read().decode('utf-8')
        df = pd.read_csv(StringIO(content))
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        DATA_STORE[dataset_type] = df        
        fraud = run_fraud_detection(df, dataset_type)
        DATA_STORE['fraud_results'][dataset_type] = fraud
        return jsonify({
            'success': True,
            'rows': len(df),
            'columns': list(df.columns),
            'preview': df.head(5).to_dict(orient='records'),
            'fraud_summary': {
                'duplicates': len(fraud.get('duplicates', [])),
                'outliers': len(fraud.get('outliers', [])),
                'abnormal': len(fraud.get('abnormal', []))
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = {}
    for key, df in DATA_STORE.items():
        if key == 'fraud_results':
            continue
        if df is not None:
            stats[key] = {'rows': len(df), 'columns': len(df.columns)}
    return jsonify(stats)

# ─── Loan Module ─────────────────────────────────────────────────────────────

@app.route('/api/loan/analyze', methods=['POST'])
def analyze_loans():
    df = DATA_STORE.get('loan')
    if df is None:
        return jsonify({'error': 'No loan dataset uploaded'}), 400
    try:
        results = []
        col = df.columns.tolist()

        for idx, row in df.head(200).iterrows():
            row_dict = row.to_dict()
            score, decision, reason = predict_loan(row_dict, col)
                    # Rule-based explanation
            reasons = []

            if row_dict.get('credit_score', 700) < 600:
                reasons.append("Low credit score")

            if row_dict.get('income', 0) < 30000:
                reasons.append("Low income")

            if row_dict.get('loan_amount', 0) > row_dict.get('income', 1) * 5:
                reasons.append("High loan burden")

            if row_dict.get('employment_years', 0) < 2:
                reasons.append("Low job stability")

            if row_dict.get('dependents', 0) > 3:
                reasons.append("High dependents")

            if row_dict.get('age', 30) < 21 or row_dict.get('age', 30) > 60:
                reasons.append("Risky age group")

            if decision == "Approved":
                explanation = "Approved due to stable financial profile"
            else:
                explanation = "Rejected due to: " + ", ".join(reasons)

            # Optional AI polish
            ai_explain = call_claude(explanation)
            results.append({
                'id': idx + 1,
                'data': {k: (round(v, 2) if isinstance(v, float) else v) for k, v in row_dict.items()},
                'decision': decision,
                'risk_score': score,
                'explanation': ai_explain
            })

        approved = sum(1 for r in results if r['decision'] == 'Approved')
        return jsonify({
            'results': results[:50],
            'summary': {
                'total': len(results),
                'approved': approved,
                'rejected': len(results) - approved,
                'avg_risk': round(np.mean([r['risk_score'] for r in results]), 1)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def predict_loan(row, cols):
    score = 50
    col_str = ' '.join(cols)

    # Income
    income_col = next((c for c in cols if 'income' in c or 'salary' in c), None)
    loan_col = next((c for c in cols if 'loan' in c and ('amount' in c or 'amt' in c)), None)
    credit_col = next((c for c in cols if 'credit' in c), None)
    age_col = next((c for c in cols if 'age' in c), None)
    emp_col = next((c for c in cols if 'employ' in c or 'exp' in c or 'year' in c), None)

    try:
        if income_col and row.get(income_col):
            income = float(row[income_col])
            if income > 80000: score += 15
            elif income > 50000: score += 8
            elif income < 20000: score -= 15
    except: pass

    try:
        if credit_col and row.get(credit_col):
            credit = float(row[credit_col])
            if credit > 750: score += 20
            elif credit > 650: score += 10
            elif credit < 600: score -= 20
    except: pass

    try:
        if income_col and loan_col and row.get(income_col) and row.get(loan_col):
            ratio = float(row[loan_col]) / max(float(row[income_col]), 1)
            if ratio < 3: score += 10
            elif ratio > 8: score -= 15
    except: pass

    try:
        if emp_col and row.get(emp_col):
            exp = float(row[emp_col])
            if exp >= 5: score += 10
            elif exp < 1: score -= 10
    except: pass

    try:
        if age_col and row.get(age_col):
            age = float(row[age_col])
            if 25 <= age <= 55: score += 5
            elif age < 22 or age > 65: score -= 5
    except: pass

    # Check any approval column in data
    approval_col = next((c for c in cols if 'approv' in c or 'status' in c or 'loan_status' in c), None)
    if approval_col and row.get(approval_col) is not None:
        val = str(row[approval_col]).lower()
        if val in ('1', 'yes', 'approved', 'y'):
            score = max(score, 60)
        elif val in ('0', 'no', 'rejected', 'n'):
            score = min(score, 45)

    score = max(10, min(95, score))
    decision = 'Approved' if score >= 55 else 'Rejected'
    risk = 100 - score
    return risk, decision, ''

# ─── Staff Module ─────────────────────────────────────────────────────────────

@app.route('/api/staff/analyze', methods=['POST'])
def analyze_staff():
    df = DATA_STORE.get('staff')
    if df is None:
        return jsonify({'error': 'No staff dataset uploaded'}), 400
    try:
        cols = df.columns.tolist()
        target_col = next((c for c in cols if 'target' in c), None)
        achieved_col = next((c for c in cols if 'achiev' in c or 'actual' in c or 'sales' in c or 'result' in c), None)
        name_col = next((c for c in cols if 'name' in c or 'staff' in c or 'employee' in c), None)
        id_col = next((c for c in cols if 'id' in c), name_col)

        if not target_col or not achieved_col:
            # Fallback: use first two numeric columns
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(num_cols) >= 2:
                target_col, achieved_col = num_cols[0], num_cols[1]
            else:
                return jsonify({'error': 'Cannot identify target/achieved columns'}), 400

        results = []
        for idx, row in df.iterrows():
            try:
                target = float(row[target_col]) if row[target_col] else 0
                achieved = float(row[achieved_col]) if row[achieved_col] else 0
                pct = round((achieved / target * 100) if target > 0 else 0, 1)
                if pct >= 100: level = 'Excellent'
                elif pct >= 80: level = 'Good'
                elif pct >= 60: level = 'Average'
                else: level = 'Needs Improvement'

                staff_id = row.get(id_col, idx + 1)
                staff_name = row.get(name_col, f'Staff {idx+1}') if name_col else f'Staff {idx+1}'

                results.append({
                    'id': str(staff_id),
                    'name': str(staff_name),
                    'target': round(target, 2),
                    'achieved': round(achieved, 2),
                    'percentage': pct,
                    'level': level,
                    'gap': round(target - achieved, 2)
                })
            except: continue

        top = sorted(results, key=lambda x: x['percentage'], reverse=True)[:3]
        bottom = sorted(results, key=lambda x: x['percentage'])[:3]

        ai_suggest = call_claude(
            f"Give 3 brief, actionable suggestions to improve staff performance. "
            f"Average achievement: {np.mean([r['percentage'] for r in results]):.1f}%. "
            f"Bottom performers need most help. Keep it practical and motivating."
        )

        return jsonify({
            'results': results[:50],
            'summary': {
                'total': len(results),
                'excellent': sum(1 for r in results if r['level'] == 'Excellent'),
                'good': sum(1 for r in results if r['level'] == 'Good'),
                'average': sum(1 for r in results if r['level'] == 'Average'),
                'needs_improvement': sum(1 for r in results if r['level'] == 'Needs Improvement'),
                'avg_achievement': round(np.mean([r['percentage'] for r in results]), 1)
            },
            'top_performers': top,
            'bottom_performers': bottom,
            'ai_suggestions': ai_suggest
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ─── Goal Planner ─────────────────────────────────────────────────────────────

@app.route('/api/goals/analyze', methods=['POST'])
def analyze_goals():
    df = DATA_STORE.get('customer')
    if df is None:
        return jsonify({'error': 'No customer dataset uploaded'}), 400
    try:
        cols = df.columns.tolist()
        age_col = next((c for c in cols if 'age' in c), None)
        income_col = next((c for c in cols if 'income' in c or 'salary' in c), None)
        balance_col = next((c for c in cols if 'balance' in c or 'saving' in c or 'deposit' in c), None)
        risk_col = next((c for c in cols if 'risk' in c), None)
        id_col = next((c for c in cols if 'id' in c or 'customer' in c), None)

        results = []
        for idx, row in df.iterrows():
            try:
                age = float(row[age_col]) if age_col and row.get(age_col) else 35
                income = float(row[income_col]) if income_col and row.get(income_col) else 50000
                balance = float(row[balance_col]) if balance_col and row.get(balance_col) else 10000
                risk_appetite = str(row.get(risk_col, '')).lower() if risk_col else 'medium'

                plan = suggest_investment(age, income, balance, risk_appetite)
                cust_id = row.get(id_col, idx + 1)

                results.append({
                    'id': str(cust_id),
                    'age': int(age),
                    'income': round(income, 2),
                    'balance': round(balance, 2),
                    'plan': plan['name'],
                    'allocation': plan['allocation'],
                    'reason': plan['reason'],
                    'expected_return': plan['expected_return']
                })
            except: continue

        plan_counts = {}
        for r in results:
            plan_counts[r['plan']] = plan_counts.get(r['plan'], 0) + 1

        return jsonify({
            'results': results[:50],
            'summary': {
                'total': len(results),
                'plan_distribution': plan_counts,
                'avg_income': round(np.mean([r['income'] for r in results]), 2) if results else 0,
                'avg_balance': round(np.mean([r['balance'] for r in results]), 2) if results else 0
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def suggest_investment(age, income, balance, risk_appetite):
    plans = {
        'Conservative': {
            'name': 'Conservative Growth',
            'allocation': {'Fixed Deposits': 50, 'Bonds': 30, 'Blue-chip Stocks': 20},
            'reason': 'Safe, steady returns ideal for preservation of capital with minimal risk exposure.',
            'expected_return': '6-8% p.a.'
        },
        'Balanced': {
            'name': 'Balanced Portfolio',
            'allocation': {'Mutual Funds': 40, 'Stocks': 35, 'Fixed Income': 25},
            'reason': 'Balanced mix of growth and stability, suitable for medium-term wealth building.',
            'expected_return': '10-14% p.a.'
        },
        'Growth': {
            'name': 'Aggressive Growth',
            'allocation': {'Equity Funds': 60, 'Stocks': 30, 'REITs': 10},
            'reason': 'High growth potential through equity exposure, ideal for long investment horizons.',
            'expected_return': '15-20% p.a.'
        },
        'Retirement': {
            'name': 'Retirement Security',
            'allocation': {'Pension Funds': 45, 'Bonds': 35, 'Gold': 20},
            'reason': 'Capital protection focused on secure retirement income streams.',
            'expected_return': '5-7% p.a.'
        }
    }

    if age >= 55 or 'low' in risk_appetite:
        return plans['Conservative'] if age >= 55 else plans['Conservative']
    elif age >= 45:
        return plans['Retirement']
    elif income > 80000 and balance > 50000 and 'high' in risk_appetite:
        return plans['Growth']
    else:
        return plans['Balanced']

# ─── Fraud Detection ─────────────────────────────────────────────────────────

def run_fraud_detection(df, dataset_type):
    results = {'duplicates': [], 'outliers': [], 'abnormal': []}
    try:
        # Duplicates
        dup_mask = df.duplicated(keep='first')
        for idx in df[dup_mask].index:
            results['duplicates'].append({
                'row': int(idx) + 1,
                'column': 'All Columns',
                'id': str(df.iloc[idx, 0]) if len(df.columns) > 0 else str(idx),
                'reason': 'Exact duplicate row detected'
            })

        # Outliers (IQR method)
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        for col in num_cols[:6]:
            Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            IQR = Q3 - Q1
            if IQR == 0: continue
            lo, hi = Q1 - 3 * IQR, Q3 + 3 * IQR
            outlier_rows = df[(df[col] < lo) | (df[col] > hi)]
            for idx, row in outlier_rows.iterrows():
                results['outliers'].append({
                    'row': int(idx) + 1,
                    'column': col,
                    'value': round(float(row[col]), 2),
                    'id': str(df.iloc[idx, 0]),
                    'reason': f'Value {round(float(row[col]),2)} is a statistical outlier (3×IQR rule)'
                })

        # Abnormal income patterns
        income_col = next((c for c in df.columns if 'income' in c or 'salary' in c), None)
        if income_col:
            mean_inc = df[income_col].mean()
            std_inc = df[income_col].std()
            abnormal = df[df[income_col] > mean_inc + 4 * std_inc]
            for idx, row in abnormal.iterrows():
                results['abnormal'].append({
                    'row': int(idx) + 1,
                    'column': income_col,
                    'value': round(float(row[income_col]), 2),
                    'id': str(df.iloc[idx, 0]),
                    'reason': f'Income {round(float(row[income_col]),2)} exceeds 4 standard deviations from mean'
                })
    except Exception as e:
        pass
    return results
# 🔥 NEW: Age vs Income anomaly
age_col = next((c for c in df.columns if 'age' in c), None)
income_col = next((c for c in df.columns if 'income' in c), None)

if age_col and income_col:
    for idx, row in df.iterrows():
        try:
            age = float(row[age_col])
            income = float(row[income_col])

            if age < 25 and income > 150000:
                results['abnormal'].append({
                    'row': int(idx) + 1,
                    'column': income_col,
                    'value': round(income, 2),
                    'id': str(df.iloc[idx, 0]),
                    'reason': 'Income too high for age (suspicious pattern)'
                })
        except:
            continue

@app.route('/api/fraud/<dataset_type>', methods=['GET'])
def get_fraud(dataset_type):
    fraud = DATA_STORE['fraud_results'].get(dataset_type, {})
    all_flags = []
    for ftype, items in fraud.items():
        for item in items:
            item['type'] = ftype
            all_flags.append(item)

    if all_flags:
        ai_summary = call_claude(
            f"Summarize these fraud/anomaly findings in 3 sentences for a financial analyst. "
            f"Found: {len(fraud.get('duplicates',[]))} duplicates, "
            f"{len(fraud.get('outliers',[]))} outliers, "
            f"{len(fraud.get('abnormal',[]))} abnormal income patterns in {dataset_type} dataset."
        )
    else:
        ai_summary = "No fraud or anomalies detected in this dataset. The data appears clean and consistent."

    return jsonify({
        'flags': all_flags[:100],
        'summary': {
            'duplicates': len(fraud.get('duplicates', [])),
            'outliers': len(fraud.get('outliers', [])),
            'abnormal': len(fraud.get('abnormal', []))
        },
        'ai_summary': ai_summary
    })

# ─── Chatbot ─────────────────────────────────────────────────────────────────

@app.route('/api/chat', methods=['POST'])
def chat():
    msg = request.json.get('message', '')
    context_parts = []
    for key, df in DATA_STORE.items():
        if key == 'fraud_results': continue
        if df is not None:
            context_parts.append(f"{key} dataset: {len(df)} rows, columns: {', '.join(df.columns[:8].tolist())}")

    system = """You are FinAI Assistant, an intelligent banking and financial intelligence chatbot.
You help users understand loan decisions, risk scores, staff performance, investment plans, and fraud detection.
Be concise (2-4 sentences), professional, and helpful. Use simple language."""

    prompt = f"Context: {'; '.join(context_parts) if context_parts else 'No datasets loaded yet'}.\nUser question: {msg}"
    msg = msg.lower()

    # 🔥 DATA CONTEXT
    loan_df = DATA_STORE.get('loan')
    staff_df = DATA_STORE.get('staff')
    customer_df = DATA_STORE.get('customer')

    # =========================
    # 🔥 INTELLIGENT RESPONSES
    # =========================

    # Loan queries
    if "loan" in msg or "approve" in msg or "reject" in msg:
        if loan_df is not None:
            total = len(loan_df)
            avg_income = round(loan_df['income'].mean(), 2) if 'income' in loan_df else 0
            reply = f"There are {total} loan applications loaded. Average applicant income is {avg_income}. Loan decisions are based on income, credit score, and risk factors."
        else:
            reply = "No loan dataset loaded yet."

    # Risk queries
    elif "risk" in msg:
        reply = "Risk is calculated using credit score, income level, loan burden, employment stability, and dependents."

    # Staff queries
    elif "staff" in msg or "performance" in msg:
        if staff_df is not None:
            avg_perf = round((staff_df.iloc[:,1] / staff_df.iloc[:,0]).mean() * 100, 1)
            reply = f"Staff average performance is {avg_perf}%. Improving training and customer engagement can boost results."
        else:
            reply = "No staff dataset loaded."

    # Investment / goal
    elif "invest" in msg or "goal" in msg:
        reply = "Investment plans are suggested based on income, age, and risk appetite. Balanced and growth portfolios are commonly recommended."

    # Fraud queries
    elif "fraud" in msg or "anomaly" in msg:
        reply = "Fraud detection checks duplicates, abnormal income patterns, and statistical outliers in datasets."

    # Default
    else:
        reply = "I can help with loan analysis, risk evaluation, staff performance, investment planning, and fraud detection. Please ask a specific question."

    return jsonify({'reply': reply})
    return f"Based on your query: '{prompt[:50]}...', here is a financial insight. Please refine your query for more precise analysis."
# ─── Dashboard KPIs ──────────────────────────────────────────────────────────

@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    kpis = {
        'loan_total': 0, 'loan_approved': 0, 'loan_rejected': 0,
        'staff_total': 0, 'customer_total': 0,
        'fraud_total': 0, 'datasets_loaded': 0,
        'loan_chart': [], 'fraud_chart': []
    }
    for key, df in DATA_STORE.items():
        if key == 'fraud_results': continue
        if df is not None:
            kpis['datasets_loaded'] += 1
            if key == 'loan': kpis['loan_total'] = len(df)
            if key == 'staff': kpis['staff_total'] = len(df)
            if key == 'customer': kpis['customer_total'] = len(df)

    for key, fraud in DATA_STORE['fraud_results'].items():
        kpis['fraud_total'] += len(fraud.get('duplicates', [])) + len(fraud.get('outliers', [])) + len(fraud.get('abnormal', []))

    return jsonify(kpis)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

import os
import csv
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

CRM_FILE = "c:/Users/Promise/Desktop/outreach/data/campaign_crm.csv"
ACCOUNTS_FILE = "c:/Users/Promise/Desktop/outreach/email_accounts.txt"

def load_crm_data():
    if not os.path.exists(CRM_FILE):
        return []
    leads = []
    with open(CRM_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)
    return leads

def load_accounts():
    accounts = []
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) > 0:
                accounts.append(parts[0].strip())
    return accounts

def get_daily_limit():
    manager_path = "c:/Users/Promise/Desktop/outreach/campaign_manager.py"
    if os.path.exists(manager_path):
        with open(manager_path, "r", encoding="utf-8") as f:
            for line in f:
                if "DAILY_LIMIT_PER_ACCOUNT" in line and "=" in line:
                    try:
                        value_part = line.split("=")[1].split("#")[0].strip()
                        return int(value_part)
                    except:
                        pass
    return 15  # Fallback default

# Beautiful Dark Glassmorphic Dashboard HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Outreach CRM Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: rgba(255, 255, 255, 0.03);
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-glow: rgba(99, 102, 241, 0.15);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --success: #10b981;
            --warning: #f59e0b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2.5rem;
            display: flex;
            justify-content: center;
        }

        .container {
            width: 100%;
            max-width: 1200px;
        }

        /* Header Style */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
        }

        h1 {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #fff 0%, #6366f1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .refresh-btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
        }

        .refresh-btn:hover {
            background: var(--primary-hover);
            transform: translateY(-1px);
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }

        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .stat-card:hover {
            transform: translateY(-2px);
            border-color: rgba(99, 102, 241, 0.3);
        }

        .stat-card h3 {
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }

        .stat-card .value {
            font-size: 2.25rem;
            font-weight: 700;
            color: var(--text-primary);
        }

        /* Table Dashboard Layout */
        .dashboard-layout {
            display: grid;
            grid-template-columns: 1fr;
            gap: 2rem;
        }

        .section-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 2rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }

        th, td {
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
        }

        th {
            color: var(--text-secondary);
            font-weight: 500;
            font-size: 0.875rem;
        }

        td {
            font-size: 0.95rem;
        }

        tr:last-child td {
            border-bottom: none;
        }

        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge-step-1 {
            background: rgba(99, 102, 241, 0.15);
            color: var(--primary);
        }

        .badge-step-2 {
            background: rgba(245, 158, 11, 0.15);
            color: var(--warning);
        }

        .badge-active {
            background: rgba(16, 185, 129, 0.15);
            color: var(--success);
        }

        .url-link {
            color: var(--primary);
            text-decoration: none;
        }

        .url-link:hover {
            text-decoration: underline;
        }

        /* Progress Bar styles */
        .progress-container {
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            height: 8px;
            margin-top: 0.75rem;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--primary) 0%, var(--success) 100%);
            border-radius: 10px;
            transition: width 0.4s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Campaign Control Panel</h1>
            </div>
            <button class="refresh-btn" onclick="window.location.reload()">Refresh Data</button>
        </header>

        <!-- Stats Counter -->
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total imported Leads</h3>
                <div class="value">{{ stats.total }}</div>
                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.5rem;">Remaining Queue: {{ stats.remaining }}</div>
            </div>
            <div class="stat-card">
                <h3>Sent Today</h3>
                <div class="value" style="color: var(--primary)">{{ stats.total_sent_today }}</div>
                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.5rem;">Career Sent: {{ stats.total_sent_career }}</div>
            </div>
            <div class="stat-card">
                <h3>Weekly Progress (Combined)</h3>
                <div class="value" style="color: var(--success)">{{ stats.total_sent_week }} <span style="font-size: 1rem; color: var(--text-secondary)">/ {{ stats.total_target_week }}</span></div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {{ stats.weekly_progress_pct }}%"></div>
                </div>
            </div>
            <div class="stat-card">
                <h3>Replies & Conversion</h3>
                <div class="value" style="color: var(--warning)">{{ stats.replies }}</div>
                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.5rem;">Reply Rate: {{ stats.reply_rate }}%</div>
            </div>
            <div class="stat-card">
                <h3>Bounces & Unsubs</h3>
                <div class="value" style="color: #ef4444">{{ stats.bounced }}</div>
                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.5rem;">Unsubscribed: {{ stats.unsubscribed }}</div>
            </div>
        </div>

        <div class="dashboard-layout">
            <!-- Account Stats -->
            <div class="section-card">
                <div class="section-title">Sender Accounts Activity</div>
                <table>
                    <thead>
                        <tr>
                            <th>Email Account</th>
                            <th>Sent Today</th>
                            <th>Sent This Week</th>
                            <th>Target This Week</th>
                            <th>Total Sent</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for email, counts in account_stats.items() %}
                        <tr>
                            <td style="font-weight: 500;">{{ email }}</td>
                            <td><span class="badge" style="background: rgba(99, 102, 241, 0.1); color: var(--primary);">{{ counts.today }}</span></td>
                            <td><span class="badge badge-active">{{ counts.week }}</span></td>
                            <td><span class="badge" style="background: rgba(255, 255, 255, 0.05); color: var(--text-secondary);">{{ counts.target_week }}</span></td>
                            <td><span class="badge" style="background: rgba(16, 185, 129, 0.15); color: var(--success);">{{ counts.total }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <!-- Recent Activity -->
            <div class="section-card" style="margin-top: 2rem;">
                <div class="section-title">Recently Emailed Leads</div>
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Lead Email</th>
                                <th>Website</th>
                                <th>Current Status</th>
                                <th>Last Sent Date</th>
                                <th>Assigned Account</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for lead in recent_leads %}
                            <tr>
                                <td style="font-weight: 500;">{{ lead.Name }}</td>
                                <td>{{ lead.Email }}</td>
                                <td><a class="url-link" href="{{ lead.Website }}" target="_blank">{{ lead.Website }}</a></td>
                                <td>
                                    {% if lead.Step == '1' %}
                                    <span class="badge badge-step-1">Step 1 Sent</span>
                                    {% elif lead.Step == '2' %}
                                    <span class="badge badge-step-2">Follow-up Sent</span>
                                    {% else %}
                                    <span class="badge">{{ lead.Step }}</span>
                                    {% endif %}
                                </td>
                                <td style="color: var(--text-secondary);">{{ lead.Last_Sent_Date }}</td>
                                <td style="font-size: 0.85rem;">{{ lead.Assigned_Sender }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    leads = load_crm_data()
    accounts = load_accounts()

    # Calculate sends per account
    daily_limit = get_daily_limit()
    weekly_target = daily_limit * 7

    account_stats = {
        email: {
            "total": 0,
            "today": 0,
            "week": 0,
            "target_week": weekly_target
        } for email in accounts
    }
    
    current_date = datetime.now().date()
    start_of_week = current_date - timedelta(days=7)

    for lead in leads:
        sender = lead.get("Assigned_Sender", "").strip()
        last_sent_str = lead.get("Last_Sent_Date", "").strip()
        if not sender:
            continue
        if sender not in account_stats:
            account_stats[sender] = {
                "total": 0,
                "today": 0,
                "week": 0,
                "target_week": weekly_target
            }
        
        account_stats[sender]["total"] += 1

        if last_sent_str:
            try:
                sent_date = datetime.strptime(last_sent_str, "%Y-%m-%d").date()
                if sent_date == current_date:
                    account_stats[sender]["today"] += 1
                if sent_date >= start_of_week:
                    account_stats[sender]["week"] += 1
            except Exception:
                pass

    # Calculate overall metrics
    total_leads = len(leads)
    step1_count = sum(1 for l in leads if int(l["Step"]) >= 1)
    step2_count = sum(1 for l in leads if int(l["Step"]) >= 2)
    remaining = sum(1 for l in leads if int(l["Step"]) == 0)
    
    replies_count = sum(1 for l in leads if l.get("Status", "").strip().lower() in ["replied", "unsubscribed"])
    bounced_count = sum(1 for l in leads if l.get("Status", "").strip().lower() == "bounced")
    unsub_count = sum(1 for l in leads if l.get("Status", "").strip().lower() == "unsubscribed")
    reply_rate = round((replies_count / step1_count) * 100, 1) if step1_count > 0 else 0.0

    total_sent_today = sum(acc["today"] for acc in account_stats.values())
    total_sent_week = sum(acc["week"] for acc in account_stats.values())
    total_target_week = len(accounts) * weekly_target
    total_sent_career = sum(acc["total"] for acc in account_stats.values())
    weekly_progress_pct = min(100.0, round((total_sent_week / total_target_week) * 100, 1)) if total_target_week > 0 else 0.0

    stats = {
        "total": total_leads,
        "step1": step1_count,
        "step2": step2_count,
        "remaining": remaining,
        "replies": replies_count,
        "bounced": bounced_count,
        "unsubscribed": unsub_count,
        "reply_rate": reply_rate,
        "total_sent_today": total_sent_today,
        "total_sent_week": total_sent_week,
        "total_target_week": total_target_week,
        "weekly_progress_pct": weekly_progress_pct,
        "total_sent_career": total_sent_career
    }

    # Get recent emailed leads (Step > 0) sorted by date and position in CRM descending
    emailed_leads_with_idx = [(l, i) for i, l in enumerate(leads) if int(l.get("Step", "0")) > 0]
    # Sort descending: latest date first, then highest row index (latest sent) first
    emailed_leads_with_idx.sort(key=lambda x: (x[0].get("Last_Sent_Date", ""), x[1]), reverse=True)
    recent_leads = [x[0] for x in emailed_leads_with_idx[:10]]  # Display only the 10 absolute latest sent leads

    return render_template_string(
        DASHBOARD_HTML, 
        stats=stats, 
        account_stats=account_stats, 
        recent_leads=recent_leads
    )

if __name__ == "__main__":
    print("Launching Local Control Dashboard...")
    print("Open http://127.0.0.1:5000 in your browser to view.")
    # Run Flask on local port 5000
    app.run(host="127.0.0.1", port=5000, debug=False)

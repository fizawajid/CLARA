# 🚀 Quick Start Guide - ABSA Features

## ✅ System Status

**ABSA Dashboard Implementation: COMPLETE**

All aspect-based sentiment analysis features are now integrated into your web dashboard and ready to use!

---

## 🎯 How to Start the System

### Option 1: Easy Start (Streamlit Only)

If your API is already running at `http://localhost:8000`:

**Windows:**
```bash
# Double-click this file:
start_streamlit.bat

# OR run in terminal:
.venv\Scripts\python -m streamlit run src\ui\app.py
```

**The app will open at:** http://localhost:8501

---

### Option 2: Start Both Services

If you need to start both API and Streamlit:

**Terminal 1 - API Server:**
```bash
python -m uvicorn src.api.main:app --reload
```
*API runs at: http://localhost:8000*

**Terminal 2 - Streamlit Dashboard:**
```bash
.venv\Scripts\python -m streamlit run src\ui\app.py
```
*Dashboard runs at: http://localhost:8501*

---

### Option 3: Unified Startup Script

Start both services with one command:

```bash
python scripts/start_app.py
```

This will:
- Start the FastAPI backend
- Wait for API to be ready
- Start the Streamlit UI
- Display both URLs

---

## 🎯 Where to Find ABSA Features

Once the dashboard is running at http://localhost:8501:

### **1. Login First**

Navigate to: **🔐 Login** (sidebar)
- Use existing credentials OR register a new account

---

### **2. Upload & Analyze Feedback**

#### **Upload:**
- Go to: **📤 Upload** (sidebar)
- Enter feedback text (or upload CSV/JSON file)
- Click "Upload Feedback"

#### **Analyze:**
- Go to: **🔍 Analysis** (sidebar)
- Select your uploaded feedback batch
- Click "🔍 Analyze Feedback"
- **ABSA is enabled by default!**
- Wait for analysis to complete (~10-30 seconds)

---

### **3. View ABSA Results** (3 Places)

#### **A. In Analysis Results Page** (Immediate)

After analysis completes, you'll see 5 tabs:

```
[ 📊 Overview ] [ 😊 Emotions ] [ 🎯 Aspects ] [ 🏷️ Topics ] [ 📝 Report ]
                                      ↑
                                  CLICK HERE
```

**What you'll see:**
- ✅ Total aspects detected
- ✅ Mention counts per aspect
- ✅ Stacked bar chart showing sentiment distribution
- ✅ Detailed cards for each aspect with:
  - Priority indicators (🔴 HIGH, 🟡 MEDIUM, 🟢 LOW)
  - Sentiment progress bars (positive/neutral/negative %)
  - Dominant sentiment
- ✅ Recommendations (strengths & improvements)

---

#### **B. On Dashboard** (Quick Overview)

Go to: **📊 Dashboard** (sidebar)

**Two places to check:**

**1. Latest Analysis Summary** (top section):
```
┌─────────────────┬─────────────────┬──────────────────────┐
│ Sentiment       │ Topic Overview  │ Aspect Highlights NEW│
│ Distribution    │                 │                      │
├─────────────────┼─────────────────┼──────────────────────┤
│ 😊 Positive: 15 │ Topic 0:        │ 🟢 PRODUCT: 5 ment.  │
│ 😐 Neutral: 8   │ quality, fast   │ 🔴 PRICE: 3 mentions │
│ 😞 Negative: 3  │                 │                      │
└─────────────────┴─────────────────┴──────────────────────┘
```

**2. Aspect Analytics Overview** (bottom section):
```
🎯 Aspect Analytics Overview

Last 30 Days - Aspect Performance

┌────────────────────────────┬────────────────────────────┐
│ ✅ Top Performing Aspects: │ ⚠️ Aspects Needing Attn:   │
├────────────────────────────┼────────────────────────────┤
│ - PRICE: 90% positive      │ - USABILITY: 67% negative  │
│ - PERFORMANCE: 85% positive│ - DESIGN: 50% negative     │
│ - PRODUCT: 75% positive    │ - DELIVERY: 33% negative   │
└────────────────────────────┴────────────────────────────┘

        [ 📊 View Detailed Aspect Analytics ]
```

Click the button to go to the full page →

---

#### **C. Dedicated Aspect Analytics Page** (Comprehensive)

Go to: **🎯 Aspects** (sidebar - Page 7)

**What you'll see:**

1. **Time Range Selector** - Choose 7/14/30/60/90 days
2. **Overview Metrics** - 4 KPIs at the top
3. **Sentiment Distribution Chart** - Interactive stacked bars
4. **Performance Matrix** - Scatter plot (positive % vs mentions)
5. **Recommendations** - Strengths & improvements
6. **Detailed Breakdown** - Filterable/sortable aspect cards
7. **Export Options** - Download JSON report

---

## 📊 Example Workflow

Let's walk through a complete example:

### Step 1: Upload Sample Feedback

Go to **📤 Upload**, enter:

```
The product quality is excellent and shipping was fast!
```
```
Great value for money, but the interface is confusing.
```
```
Terrible delivery experience, package arrived damaged.
```

Click "Upload Feedback"

---

### Step 2: Analyze

Go to **🔍 Analysis**
- Select your feedback batch
- Click "🔍 Analyze Feedback"
- Wait ~15 seconds

---

### Step 3: View Results in Aspects Tab

Click **🎯 Aspects** tab

**You'll see something like:**

```
📊 Aspect Overview
Total Aspects: 6  |  Total Mentions: 7  |  High Priority: 1

📈 Aspect Sentiment Distribution
[Stacked bar chart showing:]

PRODUCT    ████████ (1 positive, 0 neutral, 0 negative)
DELIVERY   ████▓▓▓▓ (1 positive, 0 neutral, 1 negative)
PRICE      ████████ (1 positive, 0 neutral, 0 negative)
INTERFACE  ▓▓▓▓▓▓▓▓ (0 positive, 0 neutral, 1 negative)
...

🔍 Detailed Aspect Breakdown

▼ 🔴 DELIVERY (1 mentions) - Priority: HIGH

  Sentiment Breakdown:
  😊 Positive: 1 (50.0%)  ██████████ 50%
  😐 Neutral: 0 (0.0%)    ▯▯▯▯▯▯▯▯▯▯ 0%
  😞 Negative: 1 (50.0%)  ██████████ 50%

  Total: 2 | Priority: HIGH | 😐 Mixed Sentiment

💡 Recommendations

✅ Top Strengths:
- PRODUCT
- PRICE
- SHIPPING

⚠️ Areas Needing Attention:
- INTERFACE
- DELIVERY
```

---

### Step 4: Check Dashboard

Go to **📊 Dashboard**

See your aspect highlights and 30-day summary!

---

### Step 5: Explore Full Analytics

Click **📊 View Detailed Aspect Analytics** or go to **🎯 Aspects** page

- Explore the performance matrix
- Filter by HIGH priority to see critical issues
- Download the JSON report for sharing

---

## 🎨 Understanding the Visuals

### **Priority Indicators:**

- 🔴 **HIGH** = Negative sentiment, needs immediate attention
- 🟡 **MEDIUM** = Mixed sentiment, monitor closely
- 🟢 **LOW** = Positive sentiment, strength to maintain

### **Sentiment Colors:**

- **Green bars** = Positive mentions
- **Gray bars** = Neutral mentions
- **Red bars** = Negative mentions

### **Charts:**

**Stacked Bar Chart:**
- X-axis: Aspect names (PRODUCT, PRICE, etc.)
- Y-axis: Mention count
- Stack colors: Green (positive), Gray (neutral), Red (negative)

**Performance Matrix (Scatter Plot):**
- X-axis: Positive sentiment %
- Y-axis: Total mentions
- Bubble color: Priority (red/orange/green)
- Bubble size: Mention frequency

**Interpretation:**
- **Top-Right quadrant**: High positive %, many mentions = **Your strengths!**
- **Bottom-Left quadrant**: Low positive %, few but negative mentions = **Critical issues!**

---

## 💡 What ABSA Tells You

### **Before ABSA:**
"Customers gave negative feedback" ← **Not actionable**

### **After ABSA:**
"DELIVERY has 75% negative sentiment (6 mentions) - HIGH priority" ← **Specific & Actionable!**

**Action items:**
1. Fix delivery issues immediately (HIGH priority)
2. Maintain product quality (80% positive)
3. Consider price reduction (mixed feedback)

---

## 🔧 Troubleshooting

### **Issue: Can't see Aspects tab**

**Cause:** ABSA might be disabled or no aspects detected

**Solution:**
1. Make sure analysis completed successfully
2. Check if feedback has specific aspects (product, price, service, etc.)
3. Try uploading more diverse feedback

---

### **Issue: "No aspect data available"**

**Cause:** No analyses have been run yet

**Solution:**
1. Upload feedback first
2. Run analysis with ABSA enabled (it's on by default)
3. Wait for completion
4. Refresh the page

---

### **Issue: Aspect Analytics page shows error**

**Cause:** Not logged in or API not responding

**Solution:**
1. Make sure you're logged in
2. Check API is running at http://localhost:8000
3. Verify you have completed at least one analysis
4. Check the **⚙️ System** page for API status

---

## 📚 Additional Resources

- **Full Documentation:** `ABSA_DASHBOARD_FEATURES.md`
- **Visual Guide:** `ABSA_VISUAL_GUIDE.md`
- **Test Suite:** Run `python test_dashboard_absa.py`

---

## 🎯 Quick Reference - ABSA Locations

| Feature | Location | What You'll See |
|---------|----------|-----------------|
| **Full Results** | Analysis → 🎯 Aspects tab | Complete breakdown after analysis |
| **Quick View** | Dashboard → Latest Analysis | Top 2 aspects |
| **30-Day Summary** | Dashboard → Aspect Analytics | Aggregate performance |
| **Comprehensive** | 🎯 Aspects page (sidebar) | All charts, filters, export |

---

## ✅ System is Ready!

**Current Status:**
- ✅ API Server: http://localhost:8000
- ✅ Streamlit Dashboard: http://localhost:8501
- ✅ ABSA Features: Fully Integrated

**Next Step:**
Open http://localhost:8501 in your browser and start exploring! 🚀

---

**Happy Analyzing! 🎯**

*For questions or issues, check the documentation files or run the test suite.*

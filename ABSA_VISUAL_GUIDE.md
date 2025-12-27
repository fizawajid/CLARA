# 🎯 ABSA Visual Guide - What You'll See in the Dashboard

This guide shows you exactly what the ABSA features look like in your web dashboard.

---

## 1. 📊 Dashboard - Latest Analysis Summary

### Location: Main Dashboard → "Latest Analysis Summary" Section

**What you'll see:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  📊 Latest Analysis Summary                                              │
├────────────────────┬────────────────────┬────────────────────────────────┤
│ Sentiment          │ Topic Overview     │ Aspect Highlights         NEW! │
│ Distribution       │                    │                                │
├────────────────────┼────────────────────┼────────────────────────────────┤
│ 😊 Positive: 15    │ Topic 0:           │ 🟢 PRODUCT: 5 mentions         │
│ 😐 Neutral: 8      │ quality, fast      │ 🔴 PRICE: 3 mentions           │
│ 😞 Negative: 3     │ (10 docs)          │                                │
└────────────────────┴────────────────────┴────────────────────────────────┘
```

**Key Elements:**
- **3rd column** is new and shows top 2 aspects
- **Priority indicators**: 🔴 (HIGH) 🟡 (MEDIUM) 🟢 (LOW)
- **Mention counts** show how often each aspect appears

---

## 2. 🎯 Aspect Analytics Overview (Dashboard)

### Location: Dashboard → Bottom Section (NEW)

**What you'll see:**

```
═══════════════════════════════════════════════════════════════════════════
🎯 Aspect Analytics Overview

Last 30 Days - Aspect Performance

┌─────────────────────────────────┬─────────────────────────────────┐
│ ✅ Top Performing Aspects:      │ ⚠️ Aspects Needing Attention:  │
├─────────────────────────────────┼─────────────────────────────────┤
│ - PRICE: 90% positive           │ - USABILITY: 67% negative       │
│ - PERFORMANCE: 85% positive     │ - DESIGN: 50% negative          │
│ - PRODUCT: 75% positive         │ - DELIVERY: 33% negative        │
└─────────────────────────────────┴─────────────────────────────────┘

        [ 📊 View Detailed Aspect Analytics ]  ← Click to go to full page
═══════════════════════════════════════════════════════════════════════════
```

**Key Elements:**
- **Left column**: Your strengths (high positive sentiment)
- **Right column**: Issues to fix (high negative sentiment)
- **Button**: Links to dedicated Aspect Analytics page

---

## 3. 🎯 Aspects Tab (Analysis Results)

### Location: Analysis Page → After running analysis → "🎯 Aspects" Tab

**What you'll see:**

```
Tabs: [ 📊 Overview ] [ 😊 Emotions ] [ 🎯 Aspects ] [ 🏷️ Topics ] [ 📝 Report ]
                                          ↑ NEW TAB

═══════════════════════════════════════════════════════════════════════════
🎯 Aspect-Based Sentiment Analysis

📊 Aspect Overview
┌──────────────────┬──────────────────┬──────────────────┐
│ Total Aspects    │ Total Mentions   │ High Priority    │
│       7          │       17         │ Issues: 2  ⚠️    │
└──────────────────┴──────────────────┴──────────────────┘

───────────────────────────────────────────────────────────────────────────

📈 Aspect Sentiment Distribution

     [Interactive Stacked Bar Chart - Plotly]

     PRODUCT     ███████████░░░░░  (3 pos, 2 neu, 0 neg)
     PRICE       ███████████████   (3 pos, 0 neu, 0 neg)
     DELIVERY    ███░░░░░░░░░░░░   (1 pos, 0 neu, 2 neg)
     SERVICE     ██████░░░░░░░░░   (2 pos, 0 neu, 1 neg)

     Legend: █ Positive (green)  ░ Neutral (gray)  ░ Negative (red)

───────────────────────────────────────────────────────────────────────────

🔍 Detailed Aspect Breakdown

▼ 🔴 USABILITY (1 mentions) - Priority: HIGH  ← Auto-expanded (HIGH priority)
  ┌─────────────────────────────────────┬─────────────────┐
  │ Sentiment Breakdown:                │ Total: 1        │
  │                                     │ Priority: HIGH  │
  │ 😊 Positive: 0 (0.0%)               │ 😞 Mostly       │
  │ ▯▯▯▯▯▯▯▯▯▯ 0%                       │    Negative     │
  │                                     │                 │
  │ 😐 Neutral: 0 (0.0%)                │ Net Sentiment:  │
  │ ▯▯▯▯▯▯▯▯▯▯ 0%                       │ -100.0%         │
  │                                     │                 │
  │ 😞 Negative: 1 (100.0%)             │                 │
  │ ██████████ 100%                     │                 │
  └─────────────────────────────────────┴─────────────────┘

▶ 🟡 DESIGN (2 mentions) - Priority: MEDIUM  ← Click to expand

▶ 🟢 PRODUCT (3 mentions) - Priority: LOW

───────────────────────────────────────────────────────────────────────────

💡 Recommendations

✅ Top Strengths to Maintain:
- PRICE
- MONEY
- PERFORMANCE

⚠️ Areas Requiring Immediate Attention:
- USABILITY
- DESIGN
- DELIVERY

═══════════════════════════════════════════════════════════════════════════
```

**Key Elements:**
- **Overview metrics** at top
- **Interactive stacked bar chart** (Plotly - hover for details)
- **Expandable cards** for each aspect
- **Priority-based sorting** (HIGH first)
- **Progress bars** showing sentiment percentages
- **Recommendations** section at bottom

---

## 4. 📊 Dedicated Aspect Analytics Page

### Location: Pages → "07_🎯_Aspects"

### **Top Section:**

```
═══════════════════════════════════════════════════════════════════════════
🎯 Aspect Analytics
Detailed aspect-based sentiment analysis and insights across all feedback.
───────────────────────────────────────────────────────────────────────────

📅 Time Range

  [ Last 30 days ▼ ]   Showing aspect analytics for the last 30 days

───────────────────────────────────────────────────────────────────────────

📊 Overview Metrics

┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Total        │ Total        │ High Priority│ Avg Positive │
│ Aspects      │ Mentions     │ Issues       │ Sentiment    │
│              │              │              │              │
│     9        │    17        │    2  ⚠️     │   58.8%      │
└──────────────┴──────────────┴──────────────┴──────────────┘

═══════════════════════════════════════════════════════════════════════════
```

### **Sentiment Distribution Chart:**

```
═══════════════════════════════════════════════════════════════════════════
📈 Sentiment Distribution by Aspect

[Large Interactive Stacked Bar Chart - Plotly, 500px height]

Sorted by total mentions (highest first):

PRODUCT      ████████████░░░▓  (5 pos, 3 neu, 2 neg) | 10 total
PRICE        ██████████████▓▓  (8 pos, 2 neu, 2 neg) | 12 total
SERVICE      ████████░░▓▓▓▓▓▓  (4 pos, 1 neu, 3 neg) | 8 total
DELIVERY     ████░░░░▓▓▓▓▓▓▓▓  (2 pos, 1 neu, 5 neg) | 8 total
...

Legend (horizontal):  ████ Positive  ░░░░ Neutral  ▓▓▓▓ Negative

═══════════════════════════════════════════════════════════════════════════
```

### **Performance Matrix:**

```
═══════════════════════════════════════════════════════════════════════════
🎯 Aspect Performance Matrix

[Interactive Scatter Plot - Plotly]

      │
   12 │                  ●  PRICE (LOW)
      │
   10 │        ●  PRODUCT (LOW)
M  8  │
e     │                        ●  PERFORMANCE (LOW)
n  6  │
t     │   ●  DELIVERY (HIGH)
i  4  │        ●  DESIGN (MEDIUM)
o     │
n  2  │   ●  USABILITY (HIGH)
s     │
      └─────────────────────────────────────────────
        0%    20%   40%   60%   80%   100%
              Positive Sentiment %

Legend:  ● HIGH Priority (Red)  ● MEDIUM Priority (Orange)  ● LOW Priority (Green)

💡 Tip: Aspects in bottom-left (low positive %, low mentions but negative) need
        immediate attention. Top-right aspects are your strengths.

═══════════════════════════════════════════════════════════════════════════
```

### **Recommendations:**

```
═══════════════════════════════════════════════════════════════════════════
💡 Strategic Recommendations

┌─────────────────────────────────┬─────────────────────────────────┐
│ ✅ Top Strengths to Maintain &  │ ⚠️ Critical Areas Requiring     │
│    Promote                      │    Immediate Action             │
├─────────────────────────────────┼─────────────────────────────────┤
│ 1. PRICE                        │ 1. USABILITY                    │
│ 2. PERFORMANCE                  │ 2. DELIVERY                     │
│ 3. PRODUCT                      │ 3. DESIGN                       │
│ 4. MONEY                        │ 4. SERVICE                      │
│ 5. QUALITY                      │ 5. INTERFACE                    │
│                                 │                                 │
│ These aspects are performing    │ These aspects have the most     │
│ well. Consider highlighting     │ negative sentiment and should   │
│ them in marketing materials.    │ be prioritized for improvement. │
└─────────────────────────────────┴─────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════
```

### **Detailed Breakdown with Filters:**

```
═══════════════════════════════════════════════════════════════════════════
🔍 Detailed Aspect Breakdown

Filters:
  [ All ▼ ]           [ Priority ▼ ]  ← Filter and sort options
  Filter by Priority  Sort by

───────────────────────────────────────────────────────────────────────────

▼ 🔴 DELIVERY (8 mentions) - Priority: HIGH  ← Expanded

  ┌──────────────────────────────────────────┬──────────────┐
  │ Sentiment Breakdown:                     │ Total: 8     │
  │                                          │ Priority:HIGH│
  │ 😊 Positive: 2 mentions (25.0%)          │              │
  │ ██▯▯▯▯▯▯▯▯ 25%                           │ 😞 Mostly    │
  │                                          │    Negative  │
  │ 😐 Neutral: 1 mentions (12.5%)           │              │
  │ █▯▯▯▯▯▯▯▯▯ 12.5%                         │ Net Score:   │
  │                                          │ -37.5%       │
  │ 😞 Negative: 5 mentions (62.5%)          │              │
  │ ██████▯▯▯▯ 62.5%                         │              │
  └──────────────────────────────────────────┴──────────────┘

▼ 🔴 USABILITY (1 mentions) - Priority: HIGH

  [Similar card structure...]

▶ 🟡 DESIGN (2 mentions) - Priority: MEDIUM  ← Collapsed

▶ 🟢 PRODUCT (3 mentions) - Priority: LOW

───────────────────────────────────────────────────────────────────────────

📉 Export & Actions

[ 📊 Download Aspect Report (JSON) ] [ 🔄 Refresh Data ] [ 📤 Upload More Feedback ]

═══════════════════════════════════════════════════════════════════════════
```

---

## 🎨 Color Coding Reference

### **Sentiment Colors:**
- 🟩 **Positive**: Green (#4CAF50)
- ⬜ **Neutral**: Gray (#9E9E9E)
- 🟥 **Negative**: Red (#F44336)

### **Priority Indicators:**
- 🔴 **HIGH**: Critical issues, negative sentiment
- 🟡 **MEDIUM**: Moderate attention needed
- 🟢 **LOW**: Performing well, positive sentiment

### **Chart Colors:**
All Plotly charts use the same consistent color scheme for easy recognition.

---

## 📱 Interactive Elements

### **Clickable/Interactive:**
1. **Stacked bar charts** - Hover for exact counts
2. **Scatter plot** - Hover for aspect details
3. **Expander cards** - Click to expand/collapse
4. **Filter dropdowns** - Change priority/sort order
5. **Time range selector** - Change analysis period
6. **Quick action buttons** - Navigate to other pages

---

## 💡 How to Read the Visualizations

### **Stacked Bar Chart:**
```
PRICE  ███████████████   ← All green = 100% positive = Great!
DELIVERY  ███░░░▓▓▓▓▓▓   ← Mixed = Need to investigate
```

### **Performance Matrix:**
```
High Mentions    │  ● Strength    ● Strength
     ↑           │     (Promote)     (Maintain)
                 │
Low Mentions     │  ● Critical    ● Opportunity
                 └──────────────────────────────→
                   Low Positive%   High Positive%
```

### **Progress Bars:**
- **Green bar at 80%** = 80% of mentions were positive
- **Red bar at 60%** = 60% of mentions were negative
- Look for large red bars in HIGH priority aspects = **urgent action needed**

---

## 🚀 Quick Start Guide

1. **Start both servers:**
   ```bash
   python -m uvicorn src.api.main:app --reload
   streamlit run src/ui/app.py
   ```

2. **Log in** to the web app

3. **Upload feedback** (text, CSV, or JSON)

4. **Run analysis** - ABSA is enabled by default

5. **View results** in any of these places:
   - Analysis Results → 🎯 Aspects tab
   - Dashboard → Aspect highlights + 30-day summary
   - Dedicated Aspect Analytics page

---

## ✅ What Makes Good ABSA Results?

### **Good Signs:**
- ✅ Most aspects have 🟢 LOW priority
- ✅ Strengths list is longer than improvements list
- ✅ Positive sentiment > 60% across aspects
- ✅ No HIGH priority issues

### **Warning Signs:**
- ⚠️ Multiple 🔴 HIGH priority aspects
- ⚠️ Negative sentiment > 40% on key aspects
- ⚠️ Empty strengths list
- ⚠️ Low mention counts (need more data)

---

**Ready to explore? Start analyzing your feedback with ABSA! 🎯**

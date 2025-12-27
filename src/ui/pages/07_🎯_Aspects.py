"""
Aspect Analytics Page - Detailed Aspect-Based Sentiment Analysis
"""

import streamlit as st
from src.ui.utils.session_state import initialize_session_state
from src.ui.components.api_client import get_api_client
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any

# Initialize session
initialize_session_state()

# Page header
st.title("🎯 Aspect Analytics")
st.markdown("Detailed aspect-based sentiment analysis and insights across all your feedback.")
st.markdown("---")

# Check authentication
if not st.session_state.get('access_token'):
    st.warning("⚠️ Please log in to view aspect analytics.")
    if st.button("Go to Login"):
        st.switch_page("pages/01_🔐_Login.py")
    st.stop()

# Get API client
api_client = get_api_client()

# ====================
# Time Range Selection
# ====================
st.subheader("📅 Time Range")

col1, col2 = st.columns([1, 3])

with col1:
    days = st.selectbox(
        "Select Period",
        options=[7, 14, 30, 60, 90],
        index=2,  # Default to 30 days
        format_func=lambda x: f"Last {x} days"
    )

with col2:
    st.caption(f"Showing aspect analytics for the last **{days} days**")

st.markdown("---")

# ====================
# Fetch Aspect Summary
# ====================
try:
    with st.spinner("Loading aspect analytics..."):
        aspect_summary = api_client.get_aspect_summary(days=days)

    if not aspect_summary or 'aspects' not in aspect_summary:
        st.info("No aspect data available for the selected period. Upload and analyze feedback with ABSA enabled to see insights here.")
        st.stop()

    aspects = aspect_summary['aspects']
    recommendations = aspect_summary.get('recommendations', {})

    if not aspects:
        st.info("No aspects detected in the selected time period. Try uploading more feedback or selecting a longer time range.")
        st.stop()

    # ====================
    # Overview Metrics
    # ====================
    st.subheader("📊 Overview Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Aspects", len(aspects))

    with col2:
        total_mentions = sum(sum(a.get('sentiment_breakdown', {}).values()) for a in aspects)
        st.metric("Total Mentions", f"{total_mentions:,}")

    with col3:
        # Count high priority aspects
        high_priority = sum(1 for a in aspects if a.get('priority', 'LOW') == 'HIGH')
        st.metric(
            "High Priority Issues",
            high_priority,
            delta=None if high_priority == 0 else f"-{high_priority}",
            delta_color="inverse"
        )

    with col4:
        # Average positive sentiment across all aspects
        total_positive = sum(a.get('sentiment_breakdown', {}).get('positive', 0) for a in aspects)
        avg_positive_pct = (total_positive / total_mentions * 100) if total_mentions > 0 else 0
        st.metric("Avg Positive Sentiment", f"{avg_positive_pct:.1f}%")

    st.markdown("---")

    # ====================
    # Sentiment Distribution by Aspect (Stacked Bar Chart)
    # ====================
    st.subheader("📈 Sentiment Distribution by Aspect")

    # Prepare data
    aspect_names = []
    positive_counts = []
    neutral_counts = []
    negative_counts = []

    # Sort aspects by total mentions (descending)
    sorted_aspects = sorted(
        aspects,
        key=lambda x: sum(x.get('sentiment_breakdown', {}).values()),
        reverse=True
    )

    for aspect in sorted_aspects:
        aspect_names.append(aspect['aspect'].upper())
        sentiment = aspect.get('sentiment_breakdown', {})
        positive_counts.append(sentiment.get('positive', 0))
        neutral_counts.append(sentiment.get('neutral', 0))
        negative_counts.append(sentiment.get('negative', 0))

    # Create stacked bar chart
    fig = go.Figure(data=[
        go.Bar(
            name='Positive',
            x=aspect_names,
            y=positive_counts,
            marker_color='#4CAF50',
            text=positive_counts,
            textposition='inside'
        ),
        go.Bar(
            name='Neutral',
            x=aspect_names,
            y=neutral_counts,
            marker_color='#9E9E9E',
            text=neutral_counts,
            textposition='inside'
        ),
        go.Bar(
            name='Negative',
            x=aspect_names,
            y=negative_counts,
            marker_color='#F44336',
            text=negative_counts,
            textposition='inside'
        )
    ])

    fig.update_layout(
        barmode='stack',
        title='Sentiment Breakdown by Aspect',
        xaxis_title='Aspect',
        yaxis_title='Mention Count',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ====================
    # Aspect Performance Matrix
    # ====================
    st.subheader("🎯 Aspect Performance Matrix")

    # Calculate sentiment percentage for each aspect
    aspect_performance = []
    for aspect in aspects:
        sentiment = aspect.get('sentiment_breakdown', {})
        total = sum(sentiment.values())

        if total > 0:
            pos_pct = (sentiment.get('positive', 0) / total) * 100
            neg_pct = (sentiment.get('negative', 0) / total) * 100
            neu_pct = (sentiment.get('neutral', 0) / total) * 100
        else:
            pos_pct = neg_pct = neu_pct = 0

        aspect_performance.append({
            'aspect': aspect['aspect'].upper(),
            'positive': pos_pct,
            'neutral': neu_pct,
            'negative': neg_pct,
            'mentions': total,
            'priority': aspect.get('priority', 'LOW')
        })

    # Create scatter plot (Mentions vs Positive %)
    fig2 = go.Figure()

    # Color by priority
    colors = {'HIGH': '#F44336', 'MEDIUM': '#FF9800', 'LOW': '#4CAF50'}

    for priority in ['HIGH', 'MEDIUM', 'LOW']:
        priority_aspects = [a for a in aspect_performance if a['priority'] == priority]

        if priority_aspects:
            fig2.add_trace(go.Scatter(
                x=[a['positive'] for a in priority_aspects],
                y=[a['mentions'] for a in priority_aspects],
                mode='markers+text',
                name=f'{priority} Priority',
                marker=dict(
                    size=[a['mentions']/2 + 10 for a in priority_aspects],
                    color=colors[priority],
                    line=dict(width=2, color='white')
                ),
                text=[a['aspect'] for a in priority_aspects],
                textposition='top center',
                textfont=dict(size=10)
            ))

    fig2.update_layout(
        title='Aspect Performance: Positive Sentiment vs Mention Frequency',
        xaxis_title='Positive Sentiment (%)',
        yaxis_title='Total Mentions',
        height=500,
        showlegend=True,
        hovermode='closest'
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.caption("**💡 Tip:** Aspects in the bottom-left (low positive %, low mentions but negative) need immediate attention. Top-right aspects are your strengths.")

    st.markdown("---")

    # ====================
    # Recommendations
    # ====================
    if recommendations:
        st.subheader("💡 Strategic Recommendations")

        col1, col2 = st.columns(2)

        with col1:
            if recommendations.get('strengths'):
                st.success("**✅ Top Strengths to Maintain & Promote**")
                for i, strength in enumerate(recommendations['strengths'][:5], 1):
                    st.markdown(f"{i}. **{strength.upper()}**")
                st.caption("These aspects are performing well. Consider highlighting them in marketing materials.")

        with col2:
            if recommendations.get('improvements'):
                st.error("**⚠️ Critical Areas Requiring Immediate Action**")
                for i, improvement in enumerate(recommendations['improvements'][:5], 1):
                    st.markdown(f"{i}. **{improvement.upper()}**")
                st.caption("These aspects have the most negative sentiment and should be prioritized for improvement.")

        st.markdown("---")

    # ====================
    # Detailed Aspect Breakdown
    # ====================
    st.subheader("🔍 Detailed Aspect Breakdown")

    # Filter options
    col1, col2 = st.columns([1, 3])

    with col1:
        priority_filter = st.selectbox(
            "Filter by Priority",
            options=['All', 'HIGH', 'MEDIUM', 'LOW'],
            index=0
        )

    with col2:
        sort_by = st.selectbox(
            "Sort by",
            options=['Priority', 'Mentions (High to Low)', 'Mentions (Low to High)', 'Positive %', 'Negative %'],
            index=0
        )

    # Apply filters
    filtered_aspects = aspects

    if priority_filter != 'All':
        filtered_aspects = [a for a in filtered_aspects if a.get('priority', 'LOW') == priority_filter]

    # Apply sorting
    if sort_by == 'Priority':
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        filtered_aspects = sorted(filtered_aspects, key=lambda x: (priority_order.get(x.get('priority', 'LOW'), 3), -sum(x.get('sentiment_breakdown', {}).values())))
    elif sort_by == 'Mentions (High to Low)':
        filtered_aspects = sorted(filtered_aspects, key=lambda x: sum(x.get('sentiment_breakdown', {}).values()), reverse=True)
    elif sort_by == 'Mentions (Low to High)':
        filtered_aspects = sorted(filtered_aspects, key=lambda x: sum(x.get('sentiment_breakdown', {}).values()))
    elif sort_by == 'Positive %':
        filtered_aspects = sorted(filtered_aspects, key=lambda x: (
            x.get('sentiment_breakdown', {}).get('positive', 0) / sum(x.get('sentiment_breakdown', {}).values()) if sum(x.get('sentiment_breakdown', {}).values()) > 0 else 0
        ), reverse=True)
    elif sort_by == 'Negative %':
        filtered_aspects = sorted(filtered_aspects, key=lambda x: (
            x.get('sentiment_breakdown', {}).get('negative', 0) / sum(x.get('sentiment_breakdown', {}).values()) if sum(x.get('sentiment_breakdown', {}).values()) > 0 else 0
        ), reverse=True)

    # Display filtered aspects
    for aspect in filtered_aspects:
        aspect_name = aspect['aspect']
        priority = aspect.get('priority', 'LOW')
        sentiment = aspect.get('sentiment_breakdown', {})

        # Priority emoji
        priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}

        # Calculate totals
        total = sum(sentiment.values())

        if total > 0:
            pos_pct = (sentiment.get('positive', 0) / total) * 100
            neu_pct = (sentiment.get('neutral', 0) / total) * 100
            neg_pct = (sentiment.get('negative', 0) / total) * 100
        else:
            pos_pct = neu_pct = neg_pct = 0

        # Create expander
        with st.expander(
            f"{priority_emoji[priority]} **{aspect_name.upper()}** ({total} mentions) - {priority} Priority",
            expanded=(priority == 'HIGH')
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("**Sentiment Breakdown:**")

                # Positive
                st.markdown(f"😊 **Positive:** {sentiment.get('positive', 0)} mentions ({pos_pct:.1f}%)")
                st.progress(pos_pct / 100)

                # Neutral
                st.markdown(f"😐 **Neutral:** {sentiment.get('neutral', 0)} mentions ({neu_pct:.1f}%)")
                st.progress(neu_pct / 100)

                # Negative
                st.markdown(f"😞 **Negative:** {sentiment.get('negative', 0)} mentions ({neg_pct:.1f}%)")
                st.progress(neg_pct / 100)

            with col2:
                st.metric("Total Mentions", total)
                st.metric("Priority", priority)

                # Dominant sentiment
                if pos_pct > neg_pct and pos_pct > neu_pct:
                    st.success("😊 Mostly Positive")
                elif neg_pct > pos_pct and neg_pct > neu_pct:
                    st.error("😞 Mostly Negative")
                else:
                    st.info("😐 Mostly Neutral")

                # Net sentiment score
                net_score = pos_pct - neg_pct
                st.metric("Net Sentiment", f"{net_score:+.1f}%")

    st.markdown("---")

    # ====================
    # Aspect Trends (if multiple time periods)
    # ====================
    st.subheader("📉 Export & Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Download Aspect Report (JSON)", use_container_width=True):
            import json
            json_str = json.dumps(aspect_summary, indent=2)
            st.download_button(
                label="💾 Download",
                data=json_str,
                file_name=f"aspect_analytics_{days}days.json",
                mime="application/json",
                use_container_width=True
            )

    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    with col3:
        if st.button("📤 Upload More Feedback", use_container_width=True):
            st.switch_page("pages/02_📤_Upload.py")

except Exception as e:
    st.error(f"❌ Error loading aspect analytics: {str(e)}")
    st.info("Make sure you have:")
    st.markdown("- Logged in successfully")
    st.markdown("- Uploaded feedback data")
    st.markdown("- Analyzed feedback with ABSA enabled")
    st.markdown("- The API server is running")

    if st.button("Check System Status"):
        st.switch_page("pages/06_⚙️_System.py")

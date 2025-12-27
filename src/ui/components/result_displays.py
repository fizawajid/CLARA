"""
Result Display Components for Analysis Results
"""

import streamlit as st
from typing import Dict, Any, List
from src.ui.utils.formatters import (
    format_emotion_label,
    format_emotion_emoji,
    format_emotion_color,
    format_large_number,
    format_topic_label,
    truncate_text
)


def display_overview(analysis_results: Dict[str, Any]):
    """
    Display analysis overview with key metrics

    Args:
        analysis_results: Complete analysis results dictionary
    """
    st.subheader("📊 Overview")

    # Extract data
    feedback_id = analysis_results.get('feedback_id', 'N/A')
    emotions = analysis_results.get('emotions', {})
    topics = analysis_results.get('topics', {})

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        dominant_emotion = emotions.get('dominant_emotion', 'neutral')
        emoji = format_emotion_emoji(dominant_emotion)
        label = format_emotion_label(dominant_emotion)
        st.metric(
            "Dominant Emotion",
            f"{emoji} {label}"
        )

    with col2:
        num_topics = topics.get('num_topics', 0)
        st.metric("Topics Discovered", num_topics)

    with col3:
        distribution = emotions.get('emotion_distribution', {})
        joy_count = distribution.get('joy', 0)
        st.metric("Joyful Feedback", joy_count)

    with col4:
        diversity = emotions.get('emotion_diversity', 0)
        st.metric("Emotional Diversity", f"{diversity:.2f}", help="Range from 0 (uniform) to 1 (diverse)")

    # Feedback ID
    st.caption(f"**Feedback Batch ID:** `{feedback_id}`")


def display_emotion_analysis(emotion_data: Dict[str, Any]):
    """
    Display detailed emotion analysis results

    Args:
        emotion_data: Emotion analysis dictionary
    """
    st.subheader("😊 Emotion Analysis")

    # Average emotion scores
    st.markdown("### Average Emotion Scores")

    avg_scores = emotion_data.get('average_scores', {})

    # Create 3 rows with 2 emotions each
    emotions = ['joy', 'sadness', 'anger', 'fear', 'surprise', 'neutral']

    for i in range(0, 6, 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(emotions):
                emotion = emotions[i + j]
                score = avg_scores.get(emotion, 0)
                emoji = format_emotion_emoji(emotion)
                label = format_emotion_label(emotion)
                color = format_emotion_color(emotion)

                with col:
                    st.markdown(f"**{emoji} {label}**")
                    st.progress(score)
                    st.caption(f"{score:.1%}")

    # Distribution
    st.markdown("### Emotion Distribution")

    distribution = emotion_data.get('emotion_distribution', {})
    dominant_emotion = emotion_data.get('dominant_emotion', 'neutral')

    # Create 3 rows with 2 emotions each
    for i in range(0, 6, 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(emotions):
                emotion = emotions[i + j]
                count = distribution.get(emotion, 0)
                emoji = format_emotion_emoji(emotion)
                label = format_emotion_label(emotion)

                with col:
                    is_dominant = (emotion == dominant_emotion)
                    if is_dominant:
                        st.success(f"{emoji} **{label}:** {count} ⭐")
                    else:
                        st.info(f"{emoji} **{label}:** {count}")

    # Percentage breakdown
    total = sum(distribution.values())

    if total > 0:
        percentages = [f"{format_emotion_label(e)}: {(distribution.get(e, 0) / total) * 100:.1f}%"
                      for e in emotions]
        st.caption(" | ".join(percentages))


def display_topic_modeling(topics_data: Dict[str, Any]):
    """
    Display topic modeling results

    Args:
        topics_data: Topic modeling dictionary
    """
    st.subheader("🏷️ Topic Modeling")

    num_topics = topics_data.get('num_topics', 0)
    topics_list = topics_data.get('topics', [])
    outliers = topics_data.get('outliers', 0)

    if num_topics == 0:
        st.warning("No topics were discovered in this dataset.")
        return

    st.markdown(f"**{num_topics} topics discovered** (excluding {outliers} outliers)")

    # Display each topic
    for topic in topics_list:
        topic_id = topic.get('topic_id', -1)

        # Skip outliers topic
        if topic_id == -1:
            continue

        keywords = topic.get('keywords', [])
        scores = topic.get('scores', [])
        count = topic.get('count', 0)

        # Topic card
        with st.expander(f"📌 {format_topic_label(topic_id, keywords)}", expanded=(topic_id < 3)):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("**Top Keywords:**")

                # Display keywords with scores
                keyword_data = []
                for i, (keyword, score) in enumerate(zip(keywords[:10], scores[:10])):
                    keyword_data.append({
                        'Rank': i + 1,
                        'Keyword': keyword,
                        'Relevance': f"{score:.3f}"
                    })

                st.dataframe(keyword_data, use_container_width=True, hide_index=True)

            with col2:
                st.metric("Documents", count)
                st.caption(f"Topic {topic_id}")

            # Representative documents (if available)
            rep_docs = topic.get('representative_docs', [])
            if rep_docs:
                st.markdown("**Representative Feedback:**")
                for i, doc in enumerate(rep_docs[:3]):
                    st.info(f"💬 {truncate_text(doc, 200)}")


def display_report(report_data: Dict[str, Any]):
    """
    Display generated report

    Args:
        report_data: Report dictionary
    """
    st.subheader("📝 Generated Report")

    # Key insights
    if 'key_insights' in report_data and report_data['key_insights']:
        st.markdown("### 🔑 Key Insights")
        for insight in report_data['key_insights']:
            st.markdown(f"- {insight}")

    # Recommendations
    if 'recommendations' in report_data and report_data['recommendations']:
        st.markdown("### 💡 Recommendations")
        for i, recommendation in enumerate(report_data['recommendations'], 1):
            st.markdown(f"{i}. {recommendation}")

    # Summary
    if 'summary' in report_data and report_data['summary']:
        st.markdown("### 📄 Executive Summary")
        st.markdown(report_data['summary'])

    # Full report (if available)
    if 'full_report' in report_data:
        with st.expander("View Full Report"):
            st.markdown(report_data['full_report'])


def display_complete_results(analysis_results: Dict[str, Any]):
    """
    Display complete analysis results with tabs

    Args:
        analysis_results: Complete analysis results dictionary
    """
    # Check if aspects are available
    has_aspects = 'aspects' in analysis_results and analysis_results.get('aspects')

    # Tabs for different result sections
    if has_aspects:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview",
            "😊 Emotions",
            "🎯 Aspects",
            "🏷️ Topics",
            "📝 Report"
        ])
    else:
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Overview",
            "😊 Emotions",
            "🏷️ Topics",
            "📝 Report"
        ])

    with tab1:
        display_overview(analysis_results)

    with tab2:
        emotions = analysis_results.get('emotions', {})
        if emotions:
            display_emotion_analysis(emotions)
        else:
            st.warning("No emotion analysis data available.")

    if has_aspects:
        with tab3:
            display_aspect_analysis(analysis_results)

        with tab4:
            topics = analysis_results.get('topics', {})
            if topics:
                display_topic_modeling(topics)
            else:
                st.warning("No topic modeling data available.")

        with tab5:
            report = analysis_results.get('report', {})
            if report:
                display_report(report)
            else:
                st.warning("No report data available.")
    else:
        with tab3:
            topics = analysis_results.get('topics', {})
            if topics:
                display_topic_modeling(topics)
            else:
                st.warning("No topic modeling data available.")

        with tab4:
            report = analysis_results.get('report', {})
            if report:
                display_report(report)
            else:
                st.warning("No report data available.")


def display_analysis_error(error_message: str):
    """
    Display analysis error message

    Args:
        error_message: Error message string
    """
    st.error(f"❌ Analysis Error: {error_message}")

    st.markdown("""
    **Troubleshooting:**
    - Ensure the feedback batch exists
    - Check if the API server is running
    - Try analyzing a smaller dataset
    - Check the system logs for details
    """)


def display_loading_stages(stage: str = "Initializing"):
    """
    Display analysis loading stages

    Args:
        stage: Current processing stage
    """
    stages = {
        "Initializing": 0,
        "Data Ingestion": 25,
        "Emotion Analysis": 50,
        "Topic Modeling": 75,
        "Synthesis": 90,
        "Complete": 100
    }

    progress = stages.get(stage, 0)

    st.progress(progress / 100)
    st.caption(f"**Current Stage:** {stage}")


def display_aspect_analysis(aspect_data: Dict[str, Any]):
    """
    Display aspect-based sentiment analysis results

    Args:
        aspect_data: Aspect analysis dictionary
    """
    st.subheader("🎯 Aspect-Based Sentiment Analysis")

    # Handle different data structures
    # Case 1: aspect_data is the full result with 'aspects' key
    if isinstance(aspect_data, dict) and 'aspects' in aspect_data:
        aspects_obj = aspect_data.get('aspects', {})

        # Check if aspects_obj is a dict with 'aspects' key (nested structure)
        if isinstance(aspects_obj, dict) and 'aspects' in aspects_obj:
            aspects = aspects_obj.get('aspects', [])
            recommendations = aspects_obj.get('recommendations', {})
        # Check if aspects_obj is directly a list
        elif isinstance(aspects_obj, list):
            aspects = aspects_obj
            recommendations = aspect_data.get('recommendations', {})
        else:
            st.info("No aspect analysis data available. ABSA may be disabled or no aspects were detected.")
            return
    else:
        st.info("No aspect analysis data available. ABSA may be disabled or no aspects were detected.")
        return

    # Validate aspects is a list of dicts
    if not aspects or not isinstance(aspects, list):
        st.warning("No specific aspects were identified in this feedback.")
        return

    # Check if first item is a dict (valid structure)
    if aspects and not isinstance(aspects[0], dict):
        st.warning(f"Invalid aspect data format. Expected list of dictionaries, got list of {type(aspects[0]).__name__}")
        return

    # Overview metrics
    st.markdown("### 📊 Aspect Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Aspects", len(aspects))

    with col2:
        total_mentions = sum(a.get('mention_count', 0) for a in aspects)
        st.metric("Total Mentions", total_mentions)

    with col3:
        # Count high priority (negative) aspects
        high_priority = sum(1 for a in aspects if a.get('priority', 'LOW') == 'HIGH')
        st.metric("High Priority Issues", high_priority,
                 delta=None if high_priority == 0 else f"-{high_priority}",
                 delta_color="inverse")

    st.markdown("---")

    # Sentiment breakdown chart
    st.markdown("### 📈 Aspect Sentiment Distribution")

    # Prepare data for visualization
    import plotly.graph_objects as go

    aspect_names = []
    positive_counts = []
    neutral_counts = []
    negative_counts = []

    for aspect in aspects:
        aspect_names.append(aspect['aspect'].upper())
        sentiment = aspect.get('sentiment_breakdown', {})
        positive_counts.append(sentiment.get('positive', 0))
        neutral_counts.append(sentiment.get('neutral', 0))
        negative_counts.append(sentiment.get('negative', 0))

    # Create stacked bar chart
    fig = go.Figure(data=[
        go.Bar(name='Positive', x=aspect_names, y=positive_counts, marker_color='#4CAF50'),
        go.Bar(name='Neutral', x=aspect_names, y=neutral_counts, marker_color='#9E9E9E'),
        go.Bar(name='Negative', x=aspect_names, y=negative_counts, marker_color='#F44336')
    ])

    fig.update_layout(
        barmode='stack',
        title='Sentiment by Aspect',
        xaxis_title='Aspect',
        yaxis_title='Mention Count',
        height=400,
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Detailed aspect cards
    st.markdown("### 🔍 Detailed Aspect Breakdown")

    # Sort by priority (HIGH first) then by mention count
    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    sorted_aspects = sorted(
        aspects,
        key=lambda x: (priority_order.get(x.get('priority', 'LOW'), 3), -x.get('mention_count', 0))
    )

    for aspect in sorted_aspects:
        aspect_name = aspect['aspect']
        mentions = aspect.get('mention_count', 0)
        priority = aspect.get('priority', 'LOW')
        sentiment = aspect.get('sentiment_breakdown', {})

        # Priority emoji and color
        priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
        priority_color = {'HIGH': 'red', 'MEDIUM': 'orange', 'LOW': 'green'}

        # Calculate sentiment percentages
        total = sentiment.get('positive', 0) + sentiment.get('neutral', 0) + sentiment.get('negative', 0)

        if total > 0:
            pos_pct = (sentiment.get('positive', 0) / total) * 100
            neu_pct = (sentiment.get('neutral', 0) / total) * 100
            neg_pct = (sentiment.get('negative', 0) / total) * 100
        else:
            pos_pct = neu_pct = neg_pct = 0

        # Create expander for each aspect
        with st.expander(
            f"{priority_emoji[priority]} **{aspect_name.upper()}** ({mentions} mentions) - Priority: {priority}",
            expanded=(priority == 'HIGH')
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("**Sentiment Breakdown:**")

                # Sentiment progress bars
                st.markdown(f"😊 **Positive:** {sentiment.get('positive', 0)} mentions ({pos_pct:.1f}%)")
                st.progress(pos_pct / 100)

                st.markdown(f"😐 **Neutral:** {sentiment.get('neutral', 0)} mentions ({neu_pct:.1f}%)")
                st.progress(neu_pct / 100)

                st.markdown(f"😞 **Negative:** {sentiment.get('negative', 0)} mentions ({neg_pct:.1f}%)")
                st.progress(neg_pct / 100)

            with col2:
                st.metric("Total Mentions", mentions)
                st.metric("Priority Level", priority)

                # Dominant sentiment
                if pos_pct > neg_pct and pos_pct > neu_pct:
                    st.success("😊 Mostly Positive")
                elif neg_pct > pos_pct and neg_pct > neu_pct:
                    st.error("😞 Mostly Negative")
                else:
                    st.info("😐 Mostly Neutral")

    # Recommendations section
    if recommendations and isinstance(recommendations, dict):
        st.markdown("---")
        st.markdown("### 💡 Recommendations")

        if recommendations.get('strengths'):
            st.success("**✅ Top Strengths to Maintain:**")
            for strength in recommendations['strengths'][:3]:
                st.markdown(f"- {strength.upper()}")

        if recommendations.get('improvements'):
            st.error("**⚠️ Areas Requiring Immediate Attention:**")
            for improvement in recommendations['improvements'][:3]:
                st.markdown(f"- {improvement.upper()}")


def create_download_section(analysis_results: Dict[str, Any], feedback_id: str):
    """
    Create download section for results

    Args:
        analysis_results: Analysis results
        feedback_id: Feedback batch ID
    """
    st.markdown("---")
    st.subheader("📥 Download Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        # JSON download
        import json
        json_str = json.dumps(analysis_results, indent=2)

        st.download_button(
            label="📄 Download JSON",
            data=json_str,
            file_name=f"analysis_{feedback_id}.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:
        # CSV download placeholder (will be implemented with exporters)
        st.button(
            "📊 Export to CSV",
            use_container_width=True,
            disabled=True,
            help="CSV export coming soon"
        )

    with col3:
        # PDF download placeholder
        st.button(
            "📑 Generate PDF",
            use_container_width=True,
            disabled=True,
            help="PDF export coming soon"
        )

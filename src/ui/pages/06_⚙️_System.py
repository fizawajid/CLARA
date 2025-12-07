"""
System Page - Health Status and Configuration (FIXED)
"""

import streamlit as st
from src.ui.utils.session_state import initialize_session_state, update_system_stats, get_cached_stats
from src.ui.utils.formatters import format_large_number, format_timestamp
from datetime import datetime

# Initialize session
initialize_session_state()

# Page header
st.title("⚙️ System Health & Configuration")
st.markdown("Monitor system status and view configuration details.")
st.markdown("---")

# Auto-refresh toggle
col1, col2 = st.columns([3, 1])

with col2:
    auto_refresh = st.checkbox("Auto-refresh", value=False, help="Refresh every 10 seconds")

if auto_refresh:
    import time
    time.sleep(10)
    st.rerun()

# ====================
# Health Status
# ====================
st.subheader("🏥 Health Status")

try:
    api_client = st.session_state.api_client

    # Fetch health status
    with st.spinner("Checking system health..."):
        health = api_client.get_health()

    # Display status
    col1, col2, col3 = st.columns(3)

    with col1:
        status = health.get('status', 'unknown')
        if status == 'healthy':
            st.success(f"✅ **API Status:** {status.upper()}")
        else:
            st.error(f"❌ **API Status:** {status.upper()}")

    with col2:
        embed_status = health.get('embedding_service', 'unknown')
        if embed_status == 'operational':
            st.success(f"✅ **Embeddings:** {embed_status.upper()}")
        else:
            st.warning(f"⚠️ **Embeddings:** {embed_status.upper()}")

    with col3:
        vector_status = health.get('vector_store', 'unknown')
        if vector_status == 'operational':
            st.success(f"✅ **Vector Store:** {vector_status.upper()}")
        else:
            st.warning(f"⚠️ **Vector Store:** {vector_status.upper()}")

    # Document count - handle both string and int
    doc_count_raw = health.get('document_count', 0)
    
    # Convert to int if it's a string
    try:
        if isinstance(doc_count_raw, str):
            doc_count = int(doc_count_raw)
        else:
            doc_count = doc_count_raw
    except (ValueError, TypeError):
        doc_count = 0
    
    st.metric("Total Documents in Vector Store", format_large_number(doc_count))

    # Last updated
    st.caption(f"Last checked: {format_timestamp(datetime.now().isoformat(), '%Y-%m-%d %H:%M:%S')}")

except Exception as e:
    st.error(f"❌ Unable to connect to API")
    st.code(str(e))
    
    st.markdown("""
    **Troubleshooting:**
    - Ensure the API server is running on http://localhost:8000
    - Check if all dependencies are installed
    - Verify network connectivity
    - Check the terminal for API error messages
    """)
    
    # Show more details
    with st.expander("🔍 Error Details"):
        st.exception(e)

st.markdown("---")

# ====================
# System Statistics
# ====================
st.subheader("📊 System Statistics")

try:
    # Try to get cached stats first
    stats = get_cached_stats(max_age_seconds=60)

    if stats is None:
        # Fetch fresh stats
        with st.spinner("Fetching statistics..."):
            response = api_client.get_statistics()
            
            # Extract statistics from response
            if response.get('success'):
                stats = response.get('statistics', {})
            else:
                stats = {}
            
            update_system_stats(stats)

    # Display statistics
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Session Statistics**")
        st.metric("Uploaded Batches", len(st.session_state.uploaded_feedback_ids))
        st.metric("Analyses Performed", len(st.session_state.analysis_history))

    with col2:
        st.markdown("**Database Statistics**")
        if isinstance(stats, dict) and stats:
            total_docs = stats.get('total_documents', 0)
            st.metric("Total Documents", format_large_number(total_docs))
            
            collection_name = stats.get('collection_name', 'N/A')
            st.caption(f"Collection: {collection_name}")
        else:
            st.caption("Statistics not available")

except Exception as e:
    st.warning(f"Unable to fetch statistics: {str(e)}")

st.markdown("---")

# ====================
# System Information
# ====================
st.subheader("ℹ️ System Information")

try:
    info = api_client.get_info()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**API Configuration**")
        
        api_info = info.get('api', {})
        st.code(f"""
Title: {api_info.get('title', 'N/A')}
Version: {api_info.get('version', 'N/A')}
Description: {api_info.get('description', 'N/A')}
        """.strip(), language="text")

    with col2:
        st.markdown("**Model Information**")
        
        embed_info = info.get('embedding_service', {})
        st.code(f"""
Model: {embed_info.get('model_name', 'N/A')}
Dimension: {embed_info.get('embedding_dimension', 'N/A')}
Max Sequence: {embed_info.get('max_seq_length', 'N/A')}
        """.strip(), language="text")

    # Vector Store info
    vector_info = info.get('vector_store', {})
    if vector_info:
        st.markdown("**Vector Store Configuration**")
        st.code(f"""
Collection: {vector_info.get('collection_name', 'N/A')}
Documents: {format_large_number(vector_info.get('document_count', 0))}
Directory: {vector_info.get('persist_directory', 'N/A')}
        """.strip(), language="text")

    # Configuration
    config_info = info.get('configuration', {})
    if config_info:
        st.markdown("**NLP Configuration**")
        st.code(f"""
Log Level: {config_info.get('log_level', 'N/A')}
Agent Timeout: {config_info.get('agent_timeout', 'N/A')}s
Max Topics: {config_info.get('max_topics', 'N/A')}
        """.strip(), language="text")

except Exception as e:
    st.warning(f"Unable to fetch system information: {str(e)}")
    
    with st.expander("🔍 Error Details"):
        st.exception(e)

st.markdown("---")

# ====================
# Actions
# ====================
st.subheader("🔧 Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Refresh Status", use_container_width=True):
        # Clear cache and refresh
        st.session_state.system_stats = None
        st.session_state.last_stats_fetch = None
        st.rerun()

with col2:
    if st.button("🗑️ Clear Session Data", use_container_width=True):
        if st.session_state.get('confirm_clear', False):
            from src.ui.utils.session_state import clear_all_data
            clear_all_data()
            st.success("✅ Session data cleared!")
            st.session_state.confirm_clear = False
            st.rerun()
        else:
            st.session_state.confirm_clear = True
            st.warning("⚠️ Click again to confirm")

with col3:
    st.link_button("📊 View API Docs", "http://localhost:8000/docs", use_container_width=True)

# Reset confirm state if user navigates away
if st.session_state.get('confirm_clear', False):
    if st.button("❌ Cancel Clear", key="cancel_clear"):
        st.session_state.confirm_clear = False
        st.rerun()

st.markdown("---")

# ====================
# Connection Info
# ====================
st.subheader("🔌 Connection Information")

st.code("""
API Base URL: http://localhost:8000
Streamlit UI: http://localhost:8501

API Endpoints:
- Health: GET /health
- Info: GET /info
- Upload: POST /api/v1/upload
- Analyze: POST /api/v1/analyze
- Process: POST /api/v1/process
- Feedback: GET /api/v1/feedback/{id}
- Statistics: GET /api/v1/statistics

Interactive API Docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
""".strip(), language="text")

# Test Connection Button
if st.button("🧪 Test API Connection", type="secondary"):
    with st.spinner("Testing connection..."):
        try:
            health = api_client.get_health()
            if health.get('status') == 'healthy':
                st.success("✅ API connection successful!")
                st.json(health)
            else:
                st.warning("⚠️ API responded but may have issues")
                st.json(health)
        except Exception as e:
            st.error("❌ API connection failed")
            st.code(str(e))

st.markdown("---")

# Footer
st.caption("CLARA NLP v1.0.0 - Multi-Agent Feedback Analysis System")

# Debug section
with st.expander("🔧 Debug Information"):
    st.markdown("**Session State:**")
    st.json({
        "uploaded_feedback_count": len(st.session_state.uploaded_feedback_ids),
        "analysis_count": len(st.session_state.analysis_history),
        "has_current_analysis": st.session_state.current_analysis is not None,
        "api_client_initialized": st.session_state.api_client is not None
    })
    
    st.markdown("**API Client Base URL:**")
    st.code(st.session_state.api_client.base_url)
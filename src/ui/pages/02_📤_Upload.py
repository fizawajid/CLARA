"""
Upload Page - Feedback Submission Interface (FIXED)
"""

import streamlit as st
import time
from src.ui.utils.session_state import initialize_session_state, add_uploaded_feedback, clear_upload_data
from src.ui.components.upload_handlers import (
    handle_text_input,
    handle_csv_upload,
    handle_json_upload,
    process_csv_data,
    process_json_data,
    display_validation_results,
    display_feedback_preview,
    create_upload_summary,
    detect_feedback_column
)
from src.ui.utils.formatters import format_large_number

# Initialize session
initialize_session_state()

# Page header
st.title("📤 Upload Feedback")
st.markdown("Submit customer feedback for analysis using one of the methods below.")
st.markdown("---")

# Tab interface for different upload methods
tab1, tab2, tab3 = st.tabs(["📝 Manual Text", "📊 CSV File", "📄 JSON File"])

# ====================
# TAB 1: Manual Text Entry
# ====================
with tab1:
    st.subheader("Enter Feedback Manually")
    st.markdown("Enter one piece of feedback per line.")

    text_input = st.text_area(
        "Feedback Text",
        height=300,
        placeholder="Example:\nGreat product, very satisfied!\nThe shipping was slow but the quality is good.\nNeeds improvement in customer service.",
        help="Each line will be treated as a separate feedback entry"
    )

    col1, col2 = st.columns([3, 1])

    with col2:
        process_text = st.button("Process Text", type="primary", use_container_width=True)

    if process_text and text_input:
        with st.spinner("Processing text input..."):
            feedback_list, metadata_list, validation_results = handle_text_input(text_input)

            if validation_results['valid']:
                st.success(f"✅ Processed {validation_results['valid_count']} feedback entries")

                # Display validation results
                display_validation_results(validation_results)

                # Preview
                display_feedback_preview(feedback_list, metadata_list)

                # Store in session state
                st.session_state.upload_data = {
                    'feedback': feedback_list,
                    'metadata': metadata_list,
                    'validated': True,
                    'method': 'text'
                }

            else:
                st.error("No valid feedback found. Please check your input.")

    # Upload button (if data is validated)
    if st.session_state.upload_data.get('validated') and st.session_state.upload_data.get('method') == 'text':
        st.markdown("---")
        st.markdown("### Ready to Upload")

        feedback_list = st.session_state.upload_data['feedback']
        metadata_list = st.session_state.upload_data['metadata']

        st.markdown(create_upload_summary(
            len(feedback_list),
            any(metadata_list),
            list(metadata_list[0].keys()) if metadata_list and metadata_list[0] else None
        ))

        if st.button("📤 Upload to System", key="text_upload", type="primary", use_container_width=True):
            try:
                api_client = st.session_state.api_client

                with st.spinner("Uploading feedback..."):
                    response = api_client.upload_feedback(
                        feedback=feedback_list,
                        metadata=metadata_list if any(metadata_list) else None
                    )

                    if response.get('status') == 'success':
                        feedback_id = response.get('feedback_id')
                        count = response.get('count')
                        timestamp = response.get('timestamp')

                        # Add to session state
                        add_uploaded_feedback(feedback_id, count, timestamp)

                        st.success(f"✅ Successfully uploaded {count} feedback items!")
                        st.info(f"**Feedback ID:** `{feedback_id}`")
                        st.caption(f"Go to the **Analysis** page to process this feedback.")

                        # Clear upload data
                        clear_upload_data()

                        st.balloons()

                    else:
                        st.error("Upload failed. Please try again.")

            except Exception as e:
                st.error(f"Error uploading feedback: {str(e)}")

# ====================
# TAB 2: CSV Upload
# ====================
with tab2:
    st.subheader("Upload CSV File")
    st.markdown("Upload a CSV file containing feedback data.")

    # File uploader
    csv_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Maximum file size: 200MB"
    )

    if csv_file:
        # Encoding selector
        encoding = st.selectbox(
            "File Encoding",
            options=['utf-8', 'latin-1', 'cp1252', 'iso-8859-1'],
            index=0,
            help="Select the character encoding of your CSV file"
        )

        # Process CSV
        with st.spinner("Reading CSV file..."):
            success, error_msg, df = handle_csv_upload(csv_file, encoding)

        if not success:
            st.error(f"❌ {error_msg}")
        else:
            st.success(f"✅ CSV loaded successfully: {len(df)} rows, {len(df.columns)} columns")

            # Column selection
            st.markdown("### Select Feedback Column")

            detected_column = detect_feedback_column(df)

            feedback_column = st.selectbox(
                "Which column contains the feedback text?",
                options=df.columns.tolist(),
                index=df.columns.tolist().index(detected_column),
                help="The column containing customer feedback"
            )

            # Metadata options
            st.markdown("### Metadata Options")

            include_metadata = st.checkbox(
                "Include additional columns as metadata",
                value=True,
                help="Include other columns as metadata for each feedback"
            )

            metadata_columns = None

            if include_metadata:
                other_columns = [col for col in df.columns if col != feedback_column]

                if other_columns:
                    metadata_columns = st.multiselect(
                        "Select metadata columns",
                        options=other_columns,
                        default=other_columns,
                        help="Columns to include as metadata"
                    )

            # Process button
            if st.button("Process CSV Data", type="primary"):
                with st.spinner("Processing CSV data..."):
                    feedback_list, metadata_list, validation_results = process_csv_data(
                        df=df,
                        feedback_column=feedback_column,
                        include_metadata=include_metadata,
                        metadata_columns=metadata_columns
                    )

                    if validation_results['valid']:
                        st.success(f"✅ Processed {validation_results['valid_count']} feedback entries")

                        # Display validation results
                        display_validation_results(validation_results)

                        # Preview
                        display_feedback_preview(feedback_list, metadata_list)

                        # Store in session state
                        st.session_state.upload_data = {
                            'feedback': feedback_list,
                            'metadata': metadata_list,
                            'validated': True,
                            'method': 'csv'
                        }

                    else:
                        st.error("No valid feedback found in CSV file.")

    # Upload button (if data is processed)
    if st.session_state.upload_data.get('validated') and st.session_state.upload_data.get('method') == 'csv':
        st.markdown("---")
        st.markdown("### Ready to Upload")

        feedback_list = st.session_state.upload_data['feedback']
        metadata_list = st.session_state.upload_data['metadata']

        st.markdown(create_upload_summary(
            len(feedback_list),
            any(metadata_list),
            list(metadata_list[0].keys()) if metadata_list and metadata_list[0] else None
        ))

        if st.button("📤 Upload to System", key="csv_upload", type="primary", use_container_width=True):
            try:
                api_client = st.session_state.api_client

                with st.spinner("Uploading feedback..."):
                    response = api_client.upload_feedback(
                        feedback=feedback_list,
                        metadata=metadata_list if any(metadata_list) else None
                    )

                    if response.get('status') == 'success':
                        feedback_id = response.get('feedback_id')
                        count = response.get('count')
                        timestamp = response.get('timestamp')

                        # Add to session state
                        add_uploaded_feedback(feedback_id, count, timestamp)

                        st.success(f"✅ Successfully uploaded {count} feedback items!")
                        st.info(f"**Feedback ID:** `{feedback_id}`")
                        st.caption(f"Go to the **Analysis** page to process this feedback.")

                        # Clear upload data
                        clear_upload_data()

                        st.balloons()

                    else:
                        st.error("Upload failed. Please try again.")

            except Exception as e:
                st.error(f"Error uploading feedback: {str(e)}")

# ====================
# TAB 3: JSON Upload
# ====================
with tab3:
    st.subheader("Upload JSON File")
    st.markdown("Upload a JSON file containing feedback data as a list.")

    # Expected format
    with st.expander("📋 Expected JSON Format"):
        st.markdown("""
        **Option 1: List of strings**
        ```json
        [
            "Great product!",
            "Fast shipping",
            "Could be better"
        ]
        ```

        **Option 2: List of objects**
        ```json
        [
            {"text": "Great product!", "rating": 5, "source": "website"},
            {"text": "Fast shipping", "rating": 4, "source": "email"},
            {"text": "Could be better", "rating": 3, "source": "survey"}
        ]
        ```
        """)

    # File uploader
    json_file = st.file_uploader(
        "Choose a JSON file",
        type=['json'],
        help="Maximum file size: 200MB"
    )

    if json_file:
        # Encoding selector
        encoding = st.selectbox(
            "File Encoding",
            options=['utf-8', 'latin-1', 'cp1252'],
            index=0,
            help="Select the character encoding of your JSON file",
            key="json_encoding"
        )

        # Process JSON
        with st.spinner("Reading JSON file..."):
            success, error_msg, data = handle_json_upload(json_file, encoding)

        if not success:
            st.error(f"❌ {error_msg}")
        else:
            st.success(f"✅ JSON loaded successfully: {len(data)} items")

            # Process button
            if st.button("Process JSON Data", type="primary"):
                with st.spinner("Processing JSON data..."):
                    feedback_list, metadata_list, validation_results = process_json_data(data)

                    if validation_results['valid']:
                        st.success(f"✅ Processed {validation_results['valid_count']} feedback entries")

                        # Display validation results
                        display_validation_results(validation_results)

                        # Preview
                        display_feedback_preview(feedback_list, metadata_list)

                        # Store in session state
                        st.session_state.upload_data = {
                            'feedback': feedback_list,
                            'metadata': metadata_list,
                            'validated': True,
                            'method': 'json'
                        }

                    else:
                        st.error("No valid feedback found in JSON file.")

    # Upload button (if data is processed)
    if st.session_state.upload_data.get('validated') and st.session_state.upload_data.get('method') == 'json':
        st.markdown("---")
        st.markdown("### Ready to Upload")

        feedback_list = st.session_state.upload_data['feedback']
        metadata_list = st.session_state.upload_data['metadata']

        st.markdown(create_upload_summary(
            len(feedback_list),
            any(metadata_list),
            list(metadata_list[0].keys()) if metadata_list and metadata_list[0] else None
        ))

        if st.button("📤 Upload to System", key="json_upload", type="primary", use_container_width=True):
            try:
                api_client = st.session_state.api_client

                with st.spinner("Uploading feedback..."):
                    response = api_client.upload_feedback(
                        feedback=feedback_list,
                        metadata=metadata_list if any(metadata_list) else None
                    )

                    if response.get('status') == 'success':
                        feedback_id = response.get('feedback_id')
                        count = response.get('count')
                        timestamp = response.get('timestamp')

                        # Add to session state
                        add_uploaded_feedback(feedback_id, count, timestamp)

                        st.success(f"✅ Successfully uploaded {count} feedback items!")
                        st.info(f"**Feedback ID:** `{feedback_id}`")
                        st.caption(f"Go to the **Analysis** page to process this feedback.")

                        # Clear upload data
                        clear_upload_data()

                        st.balloons()

                    else:
                        st.error("Upload failed. Please try again.")

            except Exception as e:
                st.error(f"Error uploading feedback: {str(e)}")

# Footer help
st.markdown("---")
st.info("""
💡 **Tips:**
- Ensure each feedback entry has at least 3 words
- Remove any empty lines or entries
- CSV files should have a header row
- JSON files must be a valid list (array)
- Maximum file size is 200MB
- After uploading, go to the **Analysis** page to process your feedback
""")

# Debug info (can remove in production)
if st.checkbox("🔧 Show Debug Info"):
    st.json({
        "uploaded_feedback_count": len(st.session_state.uploaded_feedback_ids),
        "uploaded_feedback_ids": st.session_state.uploaded_feedback_ids,
        "upload_data_validated": st.session_state.upload_data.get('validated', False)
    })
"""
File upload component.
"""

import streamlit as st
from pathlib import Path
from ..utils.api_client import APIClient


def render_upload_section(api_client: APIClient, enable_t5: bool):
    """
    Render file upload section.
    
    Args:
        api_client: API client instance
        enable_t5: Whether T5 correction is enabled
    """
    st.header("📤 Upload Text File")
    
    uploaded_file = st.file_uploader(
        "Choose a .txt file",
        type=['txt'],
        help="Upload a text file containing spelling or grammar errors"
    )
    
    if uploaded_file is not None:
        # Display original text
        original_text = uploaded_file.read().decode('utf-8')
        
        st.subheader("📄 Original Text")
        st.text_area("Original", original_text, height=150, disabled=True, key="original")
        
        # Process button
        if st.button("🚀 Correct Text", type="primary"):
            with st.spinner("Processing your text..."):
                # Reset file pointer
                uploaded_file.seek(0)
                
                # Upload to API
                result = api_client.upload_file(
                    uploaded_file.read(),
                    uploaded_file.name,
                    enable_t5=enable_t5
                )
                
                if result:
                    # Show status message
                    if result.get('t5_enabled') and result.get('t5_applied'):
                        st.success("✅ Processing completed with T5 grammar correction!")
                    elif result.get('t5_enabled') and not result.get('t5_applied'):
                        st.warning("⚠️ Processing completed. T5 was enabled but could not be applied.")
                    else:
                        st.success("✅ Processing completed (SymSpell only)!")
                    
                    # Store in session state
                    st.session_state['file_id'] = result['file_id']
                    st.session_state['filename'] = uploaded_file.name
                    st.session_state['result'] = result
                    
                    # Display results
                    render_results(api_client, result, uploaded_file.name, original_text)


def render_results(
    api_client: APIClient,
    result: dict,
    filename: str,
    original_text: str
):
    """
    Render correction results.
    
    Args:
        api_client: API client instance
        result: Upload result from API
        filename: Original filename
        original_text: Original text content
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Intermediate (SymSpell)")
        intermediate_content = api_client.download_file(result['file_id'], 'intermediate')
        if intermediate_content:
            intermediate_text = intermediate_content.decode('utf-8')
            st.text_area(
                "After spell checking",
                intermediate_text,
                height=150,
                disabled=True,
                key="intermediate"
            )
            
            # Download button
            st.download_button(
                label="⬇️ Download Intermediate",
                data=intermediate_content,
                file_name=f"{Path(filename).stem}_intermediate.txt",
                mime="text/plain",
                key="btn_intermediate"
            )
    
    with col2:
        final_label = "✨ Final (T5 Grammar)" if result.get('t5_applied') else "✨ Final (SymSpell Only)"
        st.subheader(final_label)
        final_content = api_client.download_file(result['file_id'], 'final')
        if final_content:
            final_text = final_content.decode('utf-8')
            st.text_area(
                "After grammar correction" if result.get('t5_applied') else "Final result",
                final_text,
                height=150,
                disabled=True,
                key="final"
            )
            
            # Download button
            st.download_button(
                label="⬇️ Download Final",
                data=final_content,
                file_name=f"{Path(filename).stem}_final.txt",
                mime="text/plain",
                key="btn_final"
            )
    
    # Statistics
    st.markdown("---")
    st.subheader("📊 Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Original Length", len(original_text))
    with col2:
        if intermediate_content:
            st.metric("Intermediate Length", len(intermediate_text))
    with col3:
        if final_content:
            st.metric("Final Length", len(final_text))

"""
Streamlit interface for text correction service.

This interface provides:
- File upload for text files
- Automatic correction pipeline (SymSpell -> T5)
- Display of original, intermediate, and final texts
- Download buttons for corrected versions
"""

import streamlit as st
import requests
from pathlib import Path
import tempfile
import time

# API configuration
API_URL = "http://localhost:8000"


def check_api_health():
    """Check if the API is running and healthy."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def upload_file_to_api(file_content: bytes, filename: str, enable_t5: bool = True):
    """Upload file to API and get corrections."""
    files = {"file": (filename, file_content, "text/plain")}
    params = {"enable_t5": enable_t5}
    
    try:
        response = requests.post(f"{API_URL}/upload", files=files, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error uploading file: {e}")
        return None


def download_file_from_api(file_id: str, file_type: str):
    """Download intermediate or final file from API."""
    try:
        response = requests.get(f"{API_URL}/download/{file_id}/{file_type}")
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading file: {e}")
        return None


def main():
    st.set_page_config(
        page_title="Text Correction Tool",
        page_icon="✍️",
        layout="wide"
    )
    
    st.title("✍️ Text Correction Tool")
    st.markdown("""
    Upload a text file to correct spelling and grammar errors.
    
    **Process:**
    1. 📝 **SymSpell Correction** - Fast spell checking
    2. 🤖 **T5 Grammar Correction** - Advanced grammar and style improvements
    """)
    
    # Check API health
    with st.sidebar:
        st.header("⚙️ System Status")
        if check_api_health():
            st.success("✅ API is running")
        else:
            st.error("❌ API is not available")
            st.warning("Please start the API server: `python api.py`")
            st.stop()
        
        st.markdown("---")
        st.header("🎛️ Settings")
        
        # Feature flag for T5 correction
        enable_t5 = st.checkbox(
            "Enable T5 Grammar Correction",
            value=True,
            help="Enable or disable T5-based grammar correction. When disabled, only SymSpell spell checking will be applied."
        )
        
        if enable_t5:
            st.info("🤖 T5 grammar correction enabled")
        else:
            st.warning("⚠️ T5 grammar correction disabled (SymSpell only)")
        
        st.markdown("---")
        st.header("ℹ️ About")
        st.markdown("""
        This tool uses:
        - **SymSpell** for fast spell checking
        - **T5-small ONNX** for grammar correction (optional)
        - Runs completely offline
        """)
    
    # File upload section
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
        st.text_area("Original", original_text, height=150, disabled=True)
        
        # Process button
        if st.button("🚀 Correct Text", type="primary"):
            with st.spinner("Processing your text..."):
                # Reset file pointer
                uploaded_file.seek(0)
                
                # Upload to API with feature flag
                result = upload_file_to_api(uploaded_file.read(), uploaded_file.name, enable_t5=enable_t5)
                
                if result:
                    # Show T5 status
                    if result.get('t5_enabled') and result.get('t5_applied'):
                        st.success(f"✅ Processing completed with T5 grammar correction!")
                    elif result.get('t5_enabled') and not result.get('t5_applied'):
                        st.warning(f"⚠️ Processing completed. T5 was enabled but could not be applied.")
                    else:
                        st.success(f"✅ Processing completed (SymSpell only)!")
                    
                    # Store file_id in session state
                    st.session_state['file_id'] = result['file_id']
                    st.session_state['filename'] = uploaded_file.name
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📝 Intermediate (SymSpell)")
                        intermediate_content = download_file_from_api(result['file_id'], 'intermediate')
                        if intermediate_content:
                            intermediate_text = intermediate_content.decode('utf-8')
                            st.text_area("After spell checking", intermediate_text, height=150, disabled=True)
                            
                            # Download button
                            st.download_button(
                                label="⬇️ Download Intermediate",
                                data=intermediate_content,
                                file_name=f"{Path(uploaded_file.name).stem}_intermediate.txt",
                                mime="text/plain",
                                key="btn_intermediate"
                            )
                    
                    with col2:
                        final_label = "✨ Final (T5 Grammar)" if result.get('t5_applied') else "✨ Final (SymSpell Only)"
                        st.subheader(final_label)
                        final_content = download_file_from_api(result['file_id'], 'final')
                        if final_content:
                            final_text = final_content.decode('utf-8')
                            st.text_area("After grammar correction", final_text, height=150, disabled=True)
                            
                            # Download button
                            st.download_button(
                                label="⬇️ Download Final",
                                data=final_content,
                                file_name=f"{Path(uploaded_file.name).stem}_final.txt",
                                mime="text/plain",
                                key="btn_final"
                            )
                    
                    # Show statistics
                    st.markdown("---")
                    st.subheader("📊 Statistics")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Original Length", len(original_text))
                    with col2:
                        st.metric("Intermediate Length", len(intermediate_text))
                    with col3:
                        st.metric("Final Length", len(final_text))
    
    # If file_id exists in session state, show download buttons even without re-processing
    elif 'file_id' in st.session_state:
        st.info("Previous results available")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Intermediate Version")
            intermediate_content = download_file_from_api(st.session_state['file_id'], 'intermediate')
            if intermediate_content:
                st.download_button(
                    label="⬇️ Download Intermediate",
                    data=intermediate_content,
                    file_name=f"{Path(st.session_state['filename']).stem}_intermediate.txt",
                    mime="text/plain",
                    key="btn_intermediate_prev"
                )
        
        with col2:
            st.subheader("✨ Final Version")
            final_content = download_file_from_api(st.session_state['file_id'], 'final')
            if final_content:
                st.download_button(
                    label="⬇️ Download Final",
                    data=final_content,
                    file_name=f"{Path(st.session_state['filename']).stem}_final.txt",
                    mime="text/plain",
                    key="btn_final_prev"
                )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    Made with ❤️ using FastAPI & Streamlit | Offline Text Correction System
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

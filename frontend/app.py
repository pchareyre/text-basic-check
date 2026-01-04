"""
Main Streamlit application.

This module contains the main Streamlit UI with proper architecture:
- Component-based design
- Configuration management
- API client integration
"""

import streamlit as st
from .config import settings
from .utils.api_client import APIClient
from .components.sidebar import render_sidebar
from .components.upload import render_upload_section


def main():
    """Main application entry point."""
    
    # Page configuration
    st.set_page_config(
        page_title=settings.app_title,
        page_icon=settings.app_icon,
        layout=settings.layout,
        initial_sidebar_state=settings.sidebar_state
    )
    
    # Initialize API client
    api_client = APIClient()
    
    # Header
    st.title(f"{settings.app_icon} {settings.app_title}")
    st.markdown("""
    Upload a text file to correct spelling and grammar errors.
    
    **Process:**
    1. 📝 **SymSpell Correction** - Fast spell checking
    2. 🤖 **T5 Grammar Correction** - Advanced grammar and style improvements (optional)
    """)
    
    # Render sidebar and get settings
    enable_t5 = render_sidebar(api_client)
    
    # Render upload section
    render_upload_section(api_client, enable_t5)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    Made with ❤️ using FastAPI & Streamlit | Offline Text Correction System
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

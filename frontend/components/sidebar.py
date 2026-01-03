"""
Sidebar component for settings and status.
"""

import streamlit as st
from ..utils.api_client import APIClient


def render_sidebar(api_client: APIClient) -> bool:
    """
    Render sidebar with settings and status.
    
    Returns:
        enable_t5: Whether T5 correction is enabled
    """
    with st.sidebar:
        st.header("⚙️ System Status")
        
        # Check API health
        if api_client.check_health():
            st.success("✅ API is running")
        else:
            st.error("❌ API is not available")
            st.warning("Please start the API server:")
            st.code("python -m backend.run")
            st.stop()
        
        st.markdown("---")
        st.header("🎛️ Settings")
        
        # Feature flag for T5 correction
        enable_t5 = st.checkbox(
            "Enable T5 Grammar Correction",
            value=True,
            help="Enable or disable T5-based grammar correction. "
                 "When disabled, only SymSpell spell checking will be applied."
        )
        
        if enable_t5:
            st.info("🤖 T5 grammar correction enabled")
        else:
            st.warning("⚠️ T5 disabled (SymSpell only)")
        
        st.markdown("---")
        st.header("ℹ️ About")
        st.markdown("""
        This tool uses:
        - **SymSpell** for fast spell checking
        - **T5-small ONNX** for grammar correction (optional)
        - Runs completely offline
        """)
        
        st.markdown("---")
        st.caption("v1.0.0 | Made with ❤️")
    
    return enable_t5

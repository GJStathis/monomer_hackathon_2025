import streamlit as st

st.set_page_config(
    page_title="Monomer Hackathon 2025",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Monomer Hackathon 2025")

st.markdown("## AI-Powered Protocol Generation Platform")

st.markdown("""
Welcome to the **Monomer Hackathon 2025** platform! This application uses cutting-edge AI and bioinformatics 
to generate optimized growth protocols for microorganisms.
""")

st.info("""
**Available Pages:**
- 🏠 **Home** (this page) - Overview and introduction
- 🧬 **Protocol Explorer** - Generate AI-powered protocols for any organism
- 🧪 **Protocol Outputs** - View and analyze generated protocols
- 📊 **Protocol Results** - Experimental results and analytics
""")

st.markdown("---")

# Features section
st.markdown("### ✨ Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🧬 BLAST Analysis")
    st.markdown("""
    Automatically finds related organisms using 16S rRNA sequence similarity to inform protocol design.
    """)

with col2:
    st.markdown("#### 📚 Literature Mining")
    st.markdown("""
    Choose between two research agents:
    - **OpenAI o1-mini**: Fast reasoning model (default)
    - **FutureHouse AI**: Comprehensive research platform
    """)

with col3:
    st.markdown("#### 🤖 AI Protocol Generation")
    st.markdown("""
    OpenAI-powered agent generates detailed reagent recommendations with concentrations and units.
    """)

st.markdown("---")

# Getting started section
st.markdown("### 🚀 Getting Started")

st.markdown("""
1. Navigate to **🧬 Protocol Explorer** from the sidebar
2. Enter the scientific name of your target organism
3. Click **Generate Protocol** and wait for the AI to work its magic
4. Download your customized protocol as CSV
5. Review related organisms and reagent recommendations
""")

st.markdown("---")

# Technical details
with st.expander("🔧 Technical Details"):
    st.markdown("""
    **Technology Stack:**
    - **Backend:** FastAPI with Python
    - **Frontend:** Streamlit
    - **Database:** SQLite with SQLAlchemy ORM
    - **Bioinformatics:** NCBI BLAST API (Biopython)
    - **AI Services:** 
        - **Research Agents:**
            - OpenAI o1-mini (default) - Fast reasoning model
            - FutureHouse AI - Comprehensive research platform
        - OpenAI GPT-4o for protocol generation
    - **Caching:** Built-in caching for BLAST and literature results
    
    **API Endpoints:**
    - `GET /api/generate_protocol` - Generate a new protocol
    - `GET /api/health` - Health check
    - `GET /health` - Server health check
    
    **Data Persistence:**
    - All generated protocols are automatically saved to the database
    - Protocol history with timestamps
    - Related organisms cached for fast retrieval
    - Literature responses cached to reduce API calls
    """)

st.markdown("---")
st.caption("Built with Streamlit | Powered by BLAST, FutureHouse AI, and OpenAI")


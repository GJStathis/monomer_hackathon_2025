import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(
    page_title="Protocol Explorer",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 Protocol Explorer")
st.markdown("Generate optimized growth protocols for microorganisms using AI and bioinformatics")

# API endpoint configuration
API_BASE_URL = "http://localhost:8000/api"

# Create two columns for layout
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Input")
    
    # Organism name input
    organism_name = st.text_input(
        "Organism Name",
        placeholder="e.g., Vibrio natriegens, E. coli, Bacillus subtilis",
        help="Enter the scientific name of the organism you want to generate a protocol for"
    )
    
    # Optional: Absorbance data file path and research agent selection
    with st.expander("Advanced Options"):
        research_agent = st.selectbox(
            "Research Agent",
            options=["basic", "futurehouse"],
            index=0,
            help="Choose the research agent: 'basic' uses OpenAI o1-mini (faster, cheaper), 'futurehouse' uses FutureHouse API (more comprehensive)"
        )
        
        absorbance_path = st.text_input(
            "Absorbance Data Path (Optional)",
            placeholder="/path/to/absorbance_data.csv",
            help="Optional: Path to CSV file with absorbance data for analysis"
        )
    
    # Submit button
    submit_button = st.button("🚀 Generate Protocol", type="primary", use_container_width=True)
    
    # Information box
    st.info("""
    **How it works:**
    1. 🧬 BLAST analysis finds related organisms
    2. 📚 Research agent gathers scientific literature
       - **Basic**: Uses OpenAI o1-mini (faster, cost-effective)
       - **FutureHouse**: Uses FutureHouse AI (comprehensive research)
    3. 🤖 Protocol agent generates optimized reagent recommendations
    """)

with col2:
    st.header("Results")
    
    # Handle form submission
    if submit_button:
        if not organism_name:
            st.error("⚠️ Please enter an organism name")
        else:
            # Show loading state
            with st.spinner(f"🔬 Generating protocol for **{organism_name}**... This may take a few minutes."):
                try:
                    # Prepare API request
                    params = {
                        "organism_name": organism_name,
                        "research_agent": research_agent
                    }
                    if absorbance_path:
                        params["absorbance_csv_path"] = absorbance_path
                    
                    # Make API request
                    response = requests.get(
                        f"{API_BASE_URL}/generate_protocol",
                        params=params,
                        timeout=300  # 5 minute timeout for BLAST and AI processing
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Display success message
                        st.success(f"✅ {data['message']}")
                        
                        # Display organism information
                        st.subheader("📊 Organism Information")
                        st.write(f"**Target Organism:** {data['organism_name']}")
                        
                        # Display research agent used
                        agent_emoji = "🤖" if research_agent == "basic" else "🏛️"
                        agent_label = "OpenAI o1-mini" if research_agent == "basic" else "FutureHouse AI"
                        st.caption(f"{agent_emoji} Research Agent: **{agent_label}**")
                        
                        # Display related organisms
                        if data['related_organisms']:
                            with st.expander("🔗 Related Organisms Found", expanded=False):
                                for i, org in enumerate(data['related_organisms'], 1):
                                    st.write(f"{i}. {org}")
                        
                        # Display reagents as a table
                        st.subheader("🧪 Recommended Reagents")
                        
                        # Convert reagents to DataFrame
                        reagents_data = []
                        for reagent in data['reagents']:
                            reagents_data.append({
                                'Reagent Name': reagent['name'],
                                'Concentration': reagent['concentration'] if reagent['concentration'] is not None else 'N/A',
                                'Unit': reagent['unit']
                            })
                        
                        df = pd.DataFrame(reagents_data)
                        
                        # Display as table
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        # Download button for CSV
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Protocol as CSV",
                            data=csv,
                            file_name=f"{organism_name.replace(' ', '_')}_protocol.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        
                    else:
                        st.error(f"❌ Error: {response.status_code} - {response.text}")
                        
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. The protocol generation is taking longer than expected. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Connection error. Please make sure the API server is running at http://localhost:8000")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
    
    else:
        # Show placeholder when no results yet
        st.info("👆 Enter an organism name and click 'Generate Protocol' to begin")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    <p>Protocol Explorer | Powered by BLAST, FutureHouse AI, and OpenAI</p>
</div>
""", unsafe_allow_html=True)


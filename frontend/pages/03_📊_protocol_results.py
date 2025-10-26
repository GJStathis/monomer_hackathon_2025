import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import io

st.set_page_config(
    page_title="Protocol Results",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Protocol Results")
st.markdown("Refine protocols with experimental absorbance data")

# API endpoint configuration
API_BASE_URL = "http://localhost:8000/api"

# Create two columns for layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Select & Refine Protocol")
    
    # Fetch organisms
    try:
        organisms_response = requests.get(f"{API_BASE_URL}/organisms", timeout=10)
        if organisms_response.status_code == 200:
            organisms_data = organisms_response.json()
            organisms = organisms_data.get('organisms', [])
            
            if not organisms:
                st.warning("⚠️ No protocols found in the database. Generate some protocols first!")
                st.stop()
            
            # Organism selector
            selected_organism = st.selectbox(
                "Organism",
                options=organisms,
                help="Select an organism to refine its protocol"
            )
            
            # Fetch protocols for selected organism
            if selected_organism:
                protocols_response = requests.get(
                    f"{API_BASE_URL}/protocols/by-organism",
                    params={"organism": selected_organism},
                    timeout=10
                )
                
                if protocols_response.status_code == 200:
                    protocols_data = protocols_response.json()
                    trackers = protocols_data.get('trackers', [])
                    
                    if trackers:
                        # Create display options for the selectbox
                        tracker_options = {}
                        for tracker in trackers:
                            # Parse the datetime string
                            created_at = datetime.fromisoformat(tracker['created_at'].replace('Z', '+00:00'))
                            display_text = f"{created_at.strftime('%Y-%m-%d %H:%M:%S')} (ID: {tracker['id']})"
                            tracker_options[display_text] = tracker['id']
                        
                        # Protocol selector
                        selected_display = st.selectbox(
                            "Protocol (Timestamp)",
                            options=list(tracker_options.keys()),
                            help="Select a protocol to refine"
                        )
                        
                        selected_tracker_id = tracker_options[selected_display]
                        
                        st.markdown("---")
                        st.subheader("Upload Absorbance Data")
                        
                        # File upload option
                        upload_method = st.radio(
                            "Input Method",
                            ["Upload CSV File", "Enter File Path"],
                            help="Choose how to provide the absorbance data"
                        )
                        
                        absorbance_file_path = None
                        
                        if upload_method == "Upload CSV File":
                            uploaded_file = st.file_uploader(
                                "Choose absorbance CSV file",
                                type=['csv'],
                                help="Upload a CSV file with absorbance data (96-well plate format)"
                            )
                            
                            if uploaded_file is not None:
                                # Save the uploaded file temporarily
                                temp_file_path = f"/tmp/uploaded_absorbance_{selected_tracker_id}.csv"
                                with open(temp_file_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                absorbance_file_path = temp_file_path
                                
                                st.success(f"✅ File uploaded: {uploaded_file.name}")
                                
                                # Preview the data
                                with st.expander("Preview Data"):
                                    df_preview = pd.read_csv(uploaded_file, index_col=0)
                                    st.write(f"Shape: {df_preview.shape[0]} timepoints × {df_preview.shape[1]} wells")
                                    st.dataframe(df_preview.head(10), use_container_width=True)
                                    # Reset file pointer
                                    uploaded_file.seek(0)
                        else:
                            absorbance_file_path = st.text_input(
                                "File Path",
                                placeholder="/path/to/absorbance_data.csv",
                                help="Enter the full path to the absorbance data CSV file"
                            )
                        
                        # Research agent selector
                        research_agent = st.selectbox(
                            "Research Agent",
                            options=["basic", "futurehouse"],
                            index=0,
                            help="Choose the research agent: 'basic' uses OpenAI o1-mini (faster), 'futurehouse' uses FutureHouse API"
                        )
                        
                        # Refine button
                        refine_button = st.button(
                            "🔬 Refine Protocol with Data",
                            type="primary",
                            use_container_width=True,
                            disabled=not absorbance_file_path
                        )
                        
                        if refine_button and absorbance_file_path:
                            st.session_state['refine_tracker_id'] = selected_tracker_id
                            st.session_state['absorbance_path'] = absorbance_file_path
                            st.session_state['research_agent'] = research_agent
                            st.session_state['refine_protocol'] = True
                    else:
                        st.warning(f"No protocols found for {selected_organism}")
                else:
                    st.error(f"Error fetching protocols: {protocols_response.status_code}")
        else:
            st.error(f"Error fetching organisms: {organisms_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("🔌 Connection error. Please make sure the API server is running at http://localhost:8000")
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
    
    # Information box
    st.info("""
    **Protocol Refinement:**
    - Select an existing protocol
    - Upload absorbance data (CSV)
    - AI refines the protocol based on growth patterns
    - Original protocol is updated with new recommendations
    """)

with col2:
    st.header("Refined Protocol")
    
    # Check if we should refine a protocol
    if st.session_state.get('refine_protocol', False):
        tracker_id = st.session_state['refine_tracker_id']
        absorbance_path = st.session_state['absorbance_path']
        research_agent = st.session_state['research_agent']
        
        try:
            with st.spinner("🔬 Refining protocol with absorbance data... This may take a few minutes."):
                # Call the refine endpoint
                refine_response = requests.put(
                    f"{API_BASE_URL}/protocols/{tracker_id}/refine",
                    params={
                        "absorbance_csv_path": absorbance_path,
                        "research_agent": research_agent
                    },
                    timeout=300  # 5 minute timeout
                )
                
                if refine_response.status_code == 200:
                    protocol_data = refine_response.json()
                    
                    # Display success message
                    st.success(f"✅ Protocol refined successfully!")
                    
                    # Show metadata
                    st.subheader("📋 Protocol Information")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Organism", protocol_data['organism_name'])
                    with col_b:
                        created_at = datetime.fromisoformat(protocol_data['created_at'].replace('Z', '+00:00'))
                        st.metric("Original Date", created_at.strftime('%Y-%m-%d %H:%M:%S'))
                    
                    col_c, col_d = st.columns(2)
                    with col_c:
                        st.metric("Protocol ID", f"#{protocol_data['tracker_id']}")
                    with col_d:
                        agent_label = "OpenAI o1-mini" if research_agent == "basic" else "FutureHouse AI"
                        st.metric("Research Agent", agent_label)
                    
                    st.success("🔄 Protocol updated with absorbance data insights")
                    
                    # Display reagents
                    st.subheader("🧪 Refined Reagents")
                    
                    # Convert reagents to DataFrame
                    reagents_data = []
                    for reagent in protocol_data['reagents']:
                        reagents_data.append({
                            'Reagent Name': reagent['name'],
                            'Concentration': reagent['concentration'] if reagent['concentration'] is not None else 'N/A',
                            'Unit': reagent['unit']
                        })
                    
                    df = pd.DataFrame(reagents_data)
                    
                    # Display as table
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Statistics
                    st.subheader("📊 Statistics")
                    col_stat1, col_stat2 = st.columns(2)
                    with col_stat1:
                        st.metric("Total Reagents", len(df))
                    with col_stat2:
                        reagents_with_conc = sum(1 for r in protocol_data['reagents'] if r['concentration'] is not None)
                        st.metric("With Concentration", reagents_with_conc)
                    
                    # Download button
                    st.markdown("---")
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Refined Protocol as CSV",
                        data=csv,
                        file_name=f"{protocol_data['organism_name'].replace(' ', '_')}_refined_protocol_{tracker_id}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                    # Reset the refine flag
                    st.session_state['refine_protocol'] = False
                    
                elif refine_response.status_code == 404:
                    st.error("❌ Protocol not found")
                else:
                    st.error(f"❌ Error refining protocol: {refine_response.status_code} - {refine_response.text}")
                    
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Protocol refinement is taking longer than expected. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection error. Please make sure the API server is running")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    else:
        # Show placeholder
        st.info("👈 Select a protocol, upload absorbance data, and click 'Refine Protocol' to improve recommendations")
        
        # Show explanation
        st.markdown("### 💡 How Protocol Refinement Works")
        st.markdown("""
        1. **Select Existing Protocol**: Choose a protocol you've already generated
        2. **Upload Absorbance Data**: Provide experimental growth data (CSV format)
        3. **AI Analysis**: The system analyzes:
           - Growth patterns across wells
           - Best performing conditions
           - Worst performing conditions
           - Statistical growth metrics
        4. **Refined Recommendations**: AI generates improved reagent recommendations
        5. **Protocol Update**: The selected protocol is updated (not replaced)
        
        **CSV Format**: 96-well plate format with time points as rows and wells (A1-H12) as columns.
        """)
        
        # Show sample format
        with st.expander("📋 Example CSV Format"):
            st.code("""
,A1,A2,A3,...,H12
0,0.117,0.129,0.124,...,0.096
29,0.116,0.128,0.124,...,0.096
59,0.116,0.128,0.124,...,0.096
...
            """, language="csv")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    <p>Protocol Results | Refine protocols with experimental data</p>
</div>
""", unsafe_allow_html=True)


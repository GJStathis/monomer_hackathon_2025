import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(
    page_title="Protocol Outputs",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Protocol Outputs")
st.markdown("View and analyze previously generated protocols")

# API endpoint configuration
API_BASE_URL = "http://localhost:8000/api"

# Create two columns for layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Select Protocol")
    
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
                help="Select an organism to view its protocols"
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
                        
                        # Timestamp/ID selector
                        selected_display = st.selectbox(
                            "Protocol (Timestamp)",
                            options=list(tracker_options.keys()),
                            help="Select a protocol by its creation timestamp"
                        )
                        
                        selected_tracker_id = tracker_options[selected_display]
                        
                        # Load protocol button
                        if st.button("📊 Load Protocol", type="primary", use_container_width=True):
                            st.session_state['selected_tracker_id'] = selected_tracker_id
                            st.session_state['load_protocol'] = True
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
    **About Protocol Outputs:**
    - View all previously generated protocols
    - Filter by organism
    - Select by timestamp
    - Export protocols as CSV
    """)

with col2:
    st.header("Protocol Details")
    
    # Check if we should load a protocol
    if st.session_state.get('load_protocol', False) and 'selected_tracker_id' in st.session_state:
        tracker_id = st.session_state['selected_tracker_id']
        
        try:
            with st.spinner("Loading protocol details..."):
                # Fetch protocol details
                detail_response = requests.get(
                    f"{API_BASE_URL}/protocols/{tracker_id}",
                    timeout=10
                )
                
                if detail_response.status_code == 200:
                    protocol_data = detail_response.json()
                    
                    # Display protocol information
                    st.success(f"✅ Protocol loaded successfully!")
                    
                    # Show metadata
                    st.subheader("📋 Protocol Information")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Organism", protocol_data['organism_name'])
                    with col_b:
                        created_at = datetime.fromisoformat(protocol_data['created_at'].replace('Z', '+00:00'))
                        st.metric("Created", created_at.strftime('%Y-%m-%d %H:%M:%S'))
                    
                    st.metric("Protocol ID", f"#{protocol_data['tracker_id']}")
                    
                    # Display reagents
                    st.subheader("🧪 Reagents")
                    
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
                        label="📥 Download Protocol as CSV",
                        data=csv,
                        file_name=f"{protocol_data['organism_name'].replace(' ', '_')}_protocol_{tracker_id}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                    # Reset the load flag
                    st.session_state['load_protocol'] = False
                    
                elif detail_response.status_code == 404:
                    st.error("❌ Protocol not found")
                else:
                    st.error(f"❌ Error loading protocol: {detail_response.status_code}")
                    
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection error. Please make sure the API server is running")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
    else:
        # Show placeholder
        st.info("👈 Select an organism and timestamp, then click 'Load Protocol' to view details")
        
        # Show sample visualization
        st.markdown("### 💡 Quick Stats")
        st.markdown("""
        This page allows you to:
        - Browse all generated protocols
        - View reagent compositions
        - Compare protocols across different timestamps
        - Export data for further analysis
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    <p>Protocol Outputs | Data stored in local SQLite database</p>
</div>
""", unsafe_allow_html=True)


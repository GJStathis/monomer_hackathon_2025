import streamlit as st
import requests
from datetime import datetime

st.set_page_config(
    page_title="Protocol Exporter",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Protocol Exporter")
st.markdown("Export protocols to OpenTrons robotics format")

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
                help="Select an organism to export its protocol"
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
                            help="Select a protocol to export to robotics format"
                        )
                        
                        selected_tracker_id = tracker_options[selected_display]
                        
                        st.markdown("---")
                        
                        # Export button
                        export_button = st.button(
                            "🤖 Export Protocol",
                            type="primary",
                            use_container_width=True
                        )
                        
                        if export_button:
                            st.session_state['export_tracker_id'] = selected_tracker_id
                            st.session_state['export_organism'] = selected_organism
                            st.session_state['export_protocol'] = True
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
    **Protocol Export:**
    - Select an existing protocol
    - Export to OpenTrons robotics format
    - Copy the script for direct use in your robot
    - Compatible with OpenTrons OT-2 and OT-3
    """)

with col2:
    st.header("Robotics Protocol")
    
    # Check if we should export a protocol
    if st.session_state.get('export_protocol', False) and 'export_tracker_id' in st.session_state:
        tracker_id = st.session_state['export_tracker_id']
        organism = st.session_state['export_organism']
        
        try:
            with st.spinner("🤖 Generating robotics protocol... Please wait."):
                # Call the robotics endpoint
                robotics_response = requests.get(
                    f"{API_BASE_URL}/protocols/{tracker_id}/robotics",
                    timeout=60
                )
                
                if robotics_response.status_code == 200:
                    robotics_data = robotics_response.json()
                    protocol_text = robotics_data.get('protocol_text', '')
                    protocol_script = robotics_data.get('protocol_script', '')
                    
                    # Display success message
                    st.success(f"✅ Robotics protocol generated successfully!")
                    
                    # Show metadata
                    st.subheader("📋 Protocol Information")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Organism", organism)
                    with col_b:
                        st.metric("Protocol ID", f"#{tracker_id}")
                    
                    st.markdown("---")
                    
                    # Create tabs for protocol text and script
                    tab1, tab2 = st.tabs(["📄 Full Protocol", "🐍 Python Script"])
                    
                    with tab1:
                        st.subheader("🤖 Complete OpenTrons Protocol")
                        
                        # Add instructions
                        st.markdown("""
                        <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                            <p style='margin: 0; color: #31333F;'>
                                <strong>📋 Full Protocol:</strong> This includes labware setup, solution preparation instructions, and the Python script.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display full protocol as markdown
                        st.markdown(protocol_text)
                        
                        # Download button for full protocol
                        st.download_button(
                            label="💾 Download Full Protocol (.md)",
                            data=protocol_text,
                            file_name=f"opentrons_protocol_full_{organism.replace(' ', '_')}_{tracker_id}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    
                    with tab2:
                        st.subheader("🐍 Python Script Only")
                        
                        # Add copy instructions
                        st.markdown("""
                        <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                            <p style='margin: 0; color: #31333F;'>
                                <strong>📋 Instructions:</strong> Click the copy button in the top-right corner of the code block below to copy the Python script.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if protocol_script:
                            # Display Python script with syntax highlighting
                            st.code(protocol_script, language="python", line_numbers=True)
                            
                            # Statistics
                            st.markdown("---")
                            st.subheader("📊 Script Statistics")
                            col_stat1, col_stat2, col_stat3 = st.columns(3)
                            with col_stat1:
                                lines = protocol_script.count('\n') + 1
                                st.metric("Lines of Code", lines)
                            with col_stat2:
                                chars = len(protocol_script)
                                st.metric("Characters", f"{chars:,}")
                            with col_stat3:
                                words = len(protocol_script.split())
                                st.metric("Words", words)
                            
                            # Download button for script only
                            st.markdown("---")
                            st.download_button(
                                label="💾 Download Python Script (.py)",
                                data=protocol_script,
                                file_name=f"opentrons_protocol_{organism.replace(' ', '_')}_{tracker_id}.py",
                                mime="text/x-python",
                                use_container_width=True
                            )
                        else:
                            st.warning("⚠️ No Python script extracted from the protocol. The full protocol is available in the 'Full Protocol' tab.")
                    
                    st.markdown("---")
                    
                    # Additional info
                    with st.expander("ℹ️ How to Use This Protocol"):
                        st.markdown("""
                        ### Using the Protocol on OpenTrons
                        
                        1. **Download the Script**
                           - Click the "Download Protocol Script" button above
                           - Save the `.py` file to your computer
                        
                        2. **Upload to OpenTrons App**
                           - Open the OpenTrons App on your computer
                           - Click "Upload Protocol"
                           - Select the downloaded `.py` file
                        
                        3. **Configure Labware**
                           - Review the labware setup in the app
                           - Ensure you have the required tips, plates, and reagents
                           - Position labware according to the deck layout
                        
                        4. **Run Protocol**
                           - Calibrate your robot if needed
                           - Click "Run" to start the protocol
                           - Monitor the robot during execution
                        
                        5. **Safety Notes**
                           - Always verify the protocol before running
                           - Ensure all reagents are properly labeled
                           - Have emergency stop button accessible
                        """)
                    
                    # Reset the export flag
                    st.session_state['export_protocol'] = False
                    
                elif robotics_response.status_code == 404:
                    st.error("❌ Protocol not found")
                else:
                    st.error(f"❌ Error generating robotics protocol: {robotics_response.status_code} - {robotics_response.text}")
                    
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection error. Please make sure the API server is running")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    else:
        # Show placeholder
        st.info("👈 Select a protocol and click 'Export Protocol' to generate robotics script")
        
        # Show explanation
        st.markdown("### 💡 About Protocol Export")
        st.markdown("""
        This tool converts your biological growth protocols into executable Python scripts
        for OpenTrons liquid handling robots.
        
        **What You Get:**
        - 🤖 **OpenTrons-compatible Python script**
        - 📦 **Automated labware setup**
        - 💧 **Precise liquid handling instructions**
        - 📊 **Complete reagent preparation protocol**
        
        **Supported Platforms:**
        - OpenTrons OT-2
        - OpenTrons OT-3
        - Compatible with OpenTrons API v2.x
        
        **Features:**
        - Automatic pipette selection
        - 96-well plate support
        - Stock solution handling
        - Volume optimization
        - Error checking and validation
        """)
        
        # Show sample code
        with st.expander("📋 Example Output"):
            st.code("""
from opentrons import protocol_api

metadata = {
    'protocolName': 'Growth Media Preparation',
    'author': 'Protocol Agent',
    'description': 'Automated protocol for E. coli growth media'
}

def run(protocol: protocol_api.ProtocolContext):
    # Load labware
    tiprack = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 2)
    
    # Load pipettes
    p300 = protocol.load_instrument('p300_single', 'right', tip_racks=[tiprack])
    
    # Transfer reagents
    p300.transfer(100, source, plate['A1'])
    ...
            """, language="python")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    <p>Protocol Exporter | Convert biological protocols to robotic automation</p>
</div>
""", unsafe_allow_html=True)


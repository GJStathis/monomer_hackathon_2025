import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Cost Dashboard",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Cost Dashboard")

st.markdown("### Sample Cost Analysis")

# Generate sample data
np.random.seed(42)
dates = pd.date_range(start='2025-01-01', end='2025-10-25', freq='W')
costs = np.cumsum(np.random.uniform(50, 200, len(dates)))

# Create a DataFrame
df = pd.DataFrame({
    'Date': dates,
    'Cumulative Cost ($)': costs
})

# Create tabs for different views
tab1, tab2 = st.tabs(["📈 Cumulative Costs", "📊 Cost Breakdown"])

with tab1:
    st.markdown("#### Cumulative Cost Over Time")
    
    # Create an interactive plotly chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Cumulative Cost ($)'],
        mode='lines+markers',
        name='Cumulative Cost',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Cost ($)",
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Cost", f"${costs[-1]:,.2f}")
    with col2:
        st.metric("Average Weekly Cost", f"${np.mean(np.diff(costs)):,.2f}")
    with col3:
        st.metric("Number of Weeks", len(dates))

with tab2:
    st.markdown("#### Cost Breakdown by Category")
    
    # Sample cost breakdown data
    categories = ['Reagents', 'Equipment', 'Labor', 'Overhead', 'Other']
    category_costs = [35, 25, 20, 15, 5]
    
    # Create pie chart
    fig_pie = go.Figure(data=[go.Pie(
        labels=categories,
        values=category_costs,
        hole=0.3,
        marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
    )])
    
    fig_pie.update_layout(
        title="Cost Distribution by Category (%)",
        height=500
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Display breakdown table
    st.markdown("#### Detailed Breakdown")
    breakdown_df = pd.DataFrame({
        'Category': categories,
        'Percentage': [f"{c}%" for c in category_costs],
        'Estimated Cost ($)': [f"${costs[-1] * c / 100:,.2f}" for c in category_costs]
    })
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("📊 Sample data for demonstration purposes")


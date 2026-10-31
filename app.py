import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="NGO Program: Monitoring, Evaluation & Impact",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    conn = sqlite3.connect('data/project_data.db')
    query = "SELECT * FROM me_reports"
    df = pd.read_sql(query, conn)
    conn.close()
    df['report_date'] = pd.to_datetime(df['report_date'])
    return df

df = load_data()

st.sidebar.header("🎛️ Program Control Panel")
selected_program = st.sidebar.selectbox("Filter Program", options=["All"] + list(df['program_name'].unique()))
selected_week = st.sidebar.slider("Select Program Week", int(df['week_number'].min()), int(df['week_number'].max()), int(df['week_number'].max()))

filtered_df = df[df['week_number'] == selected_week]
if selected_program != "All":
    filtered_df = filtered_df[filtered_df['program_name'] == selected_program]

st.title("📊 Public Health Program: Monitoring, Evaluation & Impact")
st.markdown("Bridging financial expenditure and biological outcomes for international health interventions across Kenya.")

col1, col2, col3, col4 = st.columns(4)

total_allocated = int(filtered_df['allocated_budget'].sum())
total_spent = int(filtered_df['spent_budget'].sum())
overall_burn_rate = (total_spent / total_allocated) * 100 if total_allocated > 0 else 0
total_reached = int(filtered_df['reached_beneficiaries'].sum())
avg_health_impact = round(filtered_df['health_impact_reduction_pct'].mean(), 1) if len(filtered_df) > 0 else 0

col1.metric("Total Budget Spent", f"KES {total_spent:,}", f"{overall_burn_rate:.1f}% Burn Rate")
col2.metric("Beneficiaries Reached", f"{total_reached:,}")
col3.metric("Avg Biological Impact / ROI", f"{avg_health_impact}% Gain")
col4.metric("Active Counties Tracked", f"{filtered_df['county'].nunique()}")

st.markdown("---")

row1_col1, row1_col2 = st.columns([1.2, 1])

with row1_col1:
    st.subheader(f"🗺️ County Performance & Intervention Map (Week {selected_week})")
    
    m = folium.Map(location=[0.0236, 37.9062], zoom_start=6, tiles="OpenStreetMap")
    
    for _, row in filtered_df.iterrows():
        status = row['project_status']
        color = 'green' if 'On Track' in status else ('red' if 'At Risk' in status else 'orange')
        radius = min(max(row['reached_beneficiaries'] / 40, 8), 30)
        
        popup_text = f"""
        <b>County:</b> {row['county']}<br>
        <b>Program:</b> {row['program_name']}<br>
        <b>Reached:</b> {row['reached_beneficiaries']:,}<br>
        <b>Spent:</b> KES {row['spent_budget']:,}<br>
        <b>Status:</b> {status}
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(m)
        
    st_folium(m, width=650, height=450, key="kenya_ngo_map")

with row1_col2:
    st.subheader("💰 Budget Allocation vs Actual Spend")
    budget_df = filtered_df.groupby('county')[['allocated_budget', 'spent_budget']].sum().reset_index()
    
    fig_budget = px.bar(
        budget_df, x='county', y=['allocated_budget', 'spent_budget'],
        barmode='group', labels={'value': 'Amount (KES)', 'county': 'County'},
        color_discrete_map={'allocated_budget': '#3498db', 'spent_budget': '#e74c3c'}
    )
    st.plotly_chart(fig_budget, use_container_width=True, key="budget_chart")

st.markdown("---")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("📄 Automated Donor Impact Summary")
    st.info(f"""
    **Reporting Period:** Week {selected_week}  
    **Program Focus:** {selected_program}  
    * **Intervention Reach:** {total_reached:,} beneficiaries engaged across target counties.
    * **Financial Efficiency:** KES {total_spent:,} utilized out of allocated budget ({overall_burn_rate:.1f}% burn rate).
    * **Biological / Health Outcome:** Demonstrated an average **{avg_health_impact}% improvement** in target disease reduction / clinical safety index.
    * **Status Assessment:** Program operations are scaling successfully with active field monitoring in underperforming regions.
    """)

with row2_col2:
    st.subheader("📋 County Performance & Status Log")
    log_df = filtered_df[['county', 'program_name', 'reached_beneficiaries', 'cost_per_beneficiary', 'health_impact_reduction_pct', 'project_status']]
    st.dataframe(log_df, use_container_width=True)
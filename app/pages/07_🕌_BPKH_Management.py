# 1. ADD NEW PAGE: app/pages/07_🕌_BPKH_Management.py
# ============================================================================

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.bpkh_service import BPKHService
from components.bpkh_charts import BPKHCharts
from utils.formatters import format_currency, format_percentage
from database.bpkh_data import BPKHDataManager

st.set_page_config(
    page_title="BPKH Management",
    page_icon="🕌",
    layout="wide"
)

# Initialize services
@st.cache_resource
def init_bpkh_service():
    return BPKHService()

@st.cache_resource  
def init_charts():
    return BPKHCharts()

@st.cache_resource
def init_data_manager():
    return BPKHDataManager()

def main():
    # Page header
    st.title("🕌 BPKH Management Platform")
    st.markdown("**Badan Pengelola Keuangan Haji • Institutional Grade Dashboard**")
    
    # Initialize components
    bpkh_service = init_bpkh_service()
    charts = init_charts()
    data_manager = init_data_manager()
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1f2937/ffffff?text=BPKH")
        
        dashboard_type = st.selectbox(
            "🎛️ Dashboard Type",
            ["📊 Executive Dashboard", "📈 Performance Analysis", 
             "🛡️ Risk & Compliance", "🔮 Forecasting"]
        )
        
        # Data refresh button
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.success("Data refreshed!")
    
    # Load real BPKH data
    data = data_manager.get_historical_data()
    current_metrics = bpkh_service.calculate_current_metrics(data)
    
    # Route to appropriate dashboard
    if dashboard_type == "📊 Executive Dashboard":
        render_executive_dashboard(current_metrics, charts, data)
    elif dashboard_type == "📈 Performance Analysis":
        render_performance_analysis(current_metrics, charts, data)
    elif dashboard_type == "🛡️ Risk & Compliance":
        render_risk_compliance(current_metrics, charts, data)
    elif dashboard_type == "🔮 Forecasting":
        render_forecasting(current_metrics, charts, data)

def render_executive_dashboard(metrics, charts, data):
    # KPI Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Dana Haji", 
                 format_currency(metrics['dana_haji_current']), 
                 format_percentage(metrics['dana_haji_growth']))
    
    with col2:
        st.metric("📈 Investasi Portfolio",
                 format_currency(metrics['investasi_current']),
                 format_percentage(metrics['investasi_growth']))
    
    with col3:
        st.metric("👥 Pendaftar Baru 2024",
                 f"{metrics['pendaftar_current']:,}",
                 format_percentage(metrics['pendaftar_growth']))
    
    with col4:
        st.metric("🏦 Rasio Likuiditas",
                 f"{metrics['rasio_likuiditas']:.2f}",
                 "Target: 2.00 ✅")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(charts.create_trend_chart(data), use_container_width=True)
    
    with col2:
        st.plotly_chart(charts.create_allocation_pie(metrics), use_container_width=True)
    
    # Waiting list statistics
    charts.render_waiting_list_stats(metrics)

def render_performance_analysis(metrics, charts, data):
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 ROI Investasi 2024", format_percentage(metrics['roi_investasi']))
    with col2:
        st.metric("💼 ROI Penempatan 2024", format_percentage(metrics['roi_penempatan']))
    with col3:
        st.metric("💰 Total Return 2024", format_currency(metrics['total_return']))
    with col4:
        st.metric("📊 Cost-Income Ratio", format_percentage(metrics['cost_income_ratio']))
    
    # Performance charts
    st.plotly_chart(charts.create_performance_chart(data), use_container_width=True)

def render_risk_compliance(metrics, charts, data):
    # Risk metrics
    charts.render_liquidity_management(data)
    charts.render_compliance_status(metrics)

def render_forecasting(metrics, charts, data):
    # Forecasting scenarios
    charts.render_scenario_analysis(metrics)
    charts.render_strategic_priorities()

if __name__ == "__main__":
    main()


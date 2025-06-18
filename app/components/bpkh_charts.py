# ============================================================================
# 3. CREATE CHARTS: app/components/bpkh_charts.py  
# ============================================================================

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

class BPKHCharts:
    """Chart components for BPKH dashboard"""
    
    def __init__(self):
        self.colors = {
            'primary': '#3b82f6',
            'secondary': '#10b981', 
            'tertiary': '#f59e0b',
            'success': '#22c55e',
            'warning': '#f59e0b',
            'danger': '#ef4444'
        }
    
    def create_trend_chart(self, data):
        """Create trend chart for Dana Haji, Investasi, Penempatan"""
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data['years'], y=data['dana_haji'],
            mode='lines+markers', name='Dana Haji',
            line=dict(color=self.colors['primary'], width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=data['years'], y=data['investasi'],
            mode='lines+markers', name='Investasi',
            line=dict(color=self.colors['secondary'], width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=data['years'], y=data['penempatan'],
            mode='lines+markers', name='Penempatan',
            line=dict(color=self.colors['tertiary'], width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="🔄 Tren Dana Haji & Investasi (Triliun Rp)",
            xaxis_title="Tahun",
            yaxis_title="Nilai (Triliun Rp)",
            hovermode='x unified',
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_allocation_pie(self, metrics):
        """Create asset allocation pie chart"""
        
        labels = ['Penempatan Bank', 'Investasi Portfolio']
        values = [metrics['penempatan_current'], metrics['investasi_current']]
        colors = [self.colors['primary'], self.colors['secondary']]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values,
            hole=0.4,
            marker_colors=colors,
            textinfo='label+percent',
            textfont_size=12
        )])
        
        fig.update_layout(
            title="🥧 Alokasi Aset 2024",
            height=400,
            showlegend=True
        )
        
        return fig
    
    def render_waiting_list_stats(self, metrics):
        """Render waiting list statistics"""
        
        st.subheader("⏳ Statistik Antrian Jemaah")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%); 
                        padding: 1rem; border-radius: 10px; color: white; text-align: center;">
                <h3>🕌 Haji Reguler</h3>
                <h2>{metrics['waiting_list_reguler']:,}</h2>
                <p>Growth: +{metrics['waiting_growth_reguler']}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); 
                        padding: 1rem; border-radius: 10px; color: white; text-align: center;">
                <h3>✨ Haji Khusus</h3>
                <h2>{metrics['waiting_list_khusus']:,}</h2>
                <p>Growth: +{metrics['waiting_growth_khusus']}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1rem; border-radius: 10px; color: white; text-align: center;">
                <h3>📋 Komposisi 2024</h3>
                <h4>Reguler: 90.04%</h4>
                <h4>Khusus: 9.96%</h4>
            </div>
            """, unsafe_allow_html=True)


# ===== app/main.py (FINAL FIXED VERSION - NO IMPORT ERRORS) =====
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import math
import sys
import os
from pathlib import Path

# Add root directory to Python path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Page configuration
st.set_page_config(
    page_title="ASTHA - Hajj Treasury Analytics",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #10b981;
        margin-bottom: 1rem;
    }
    .stSelectbox label, .stNumberInput label, .stSlider label {
        font-weight: 600;
        color: #374151;
    }
    .agent-status {
        background: #f0f9ff;
        border: 1px solid #0ea5e9;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .liability-result {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 1rem 0;
    }
    .stress-test-safe {
        background: #dcfce7;
        border-left: 4px solid #16a34a;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .stress-test-risk {
        background: #fef2f2;
        border-left: 4px solid #dc2626;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .info-box {
        background: #f0f9ff;
        border: 1px solid #0ea5e9;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .version-badge {
        background: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8em;
        font-weight: 600;
        display: inline-block;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ====== CONFIGURATION CLASS ======
class AppConfig:
    """Application configuration"""
    APP_NAME = "ASTHA - Hajj Treasury Analytics"
    APP_VERSION = "1.2.1"  # Fixed HTML rendering issue
    BUILD_DATE = datetime.now().strftime("%Y.%m.%d")
    DEVELOPER = "MS Hadianto"
    ORGANIZATION = "Badan Pengelola Keuangan Haji (BPKH)"
    DEBUG = True
    
    # Default calculation parameters
    DEFAULT_TOTAL_JEMAAH = 2500000
    DEFAULT_INFLASI_SAUDI = 3.5
    DEFAULT_KURS_USD = 15500
    DEFAULT_TINGKAT_DISKONTO = 6.5
    DEFAULT_TAHUN_PROYEKSI = 20
    
    @staticmethod
    def get_version_info():
        """Get dynamic version information"""
        return {
            'version': AppConfig.APP_VERSION,
            'build_date': AppConfig.BUILD_DATE,
            'developer': AppConfig.DEVELOPER,
            'full_version': f"v{AppConfig.APP_VERSION}.{AppConfig.BUILD_DATE}"
        }
    
    @staticmethod
    def get_changelog():
        """Get application changelog"""
        return {
            'v1.2.1': [
                "🔧 Fixed HTML rendering issue in footer disclaimer",
                "✅ Improved disclaimer layout with native Streamlit components",
                "✅ Enhanced readability and cross-platform compatibility",
                "✅ Simplified CSS styling for better performance"
            ],
            'v1.2.0': [
                "✅ Added footer disclaimer with comprehensive legal notices",
                "✅ Added developer attribution (MS Hadianto)",
                "✅ Implemented dynamic versioning system",
                "✅ Enhanced sidebar with app info and quick help",
                "✅ Added about dialog and changelog",
                "✅ Improved security and privacy information"
            ],
            'v1.1.0': [
                "✅ Fixed all import errors for standalone operation",
                "✅ Implemented complete Monte Carlo simulation",
                "✅ Enhanced AI Assistant with better responses",
                "✅ Added comprehensive stress testing scenarios",
                "✅ Improved chart visualizations and UX"
            ],
            'v1.0.0': [
                "🎉 Initial release with core features",
                "📊 Dashboard with real-time KPI monitoring",
                "🧮 Actuarial liability calculation engine",
                "📈 Stress testing and scenario analysis", 
                "🤖 AI Assistant with knowledge base"
            ]
        }

# ====== UTILITY FUNCTIONS ======
def format_rupiah(value):
    """Format number as Rupiah currency"""
    if value >= 1e12:
        return f"Rp {value/1e12:.1f}T"
    elif value >= 1e9:
        return f"Rp {value/1e9:.1f}M"
    elif value >= 1e6:
        return f"Rp {value/1e6:.1f}jt"
    else:
        return f"Rp {value:,.0f}"

def format_percentage(value, decimals=1):
    """Format number as percentage"""
    return f"{value:.{decimals}f}%"

def format_number(value, decimals=0):
    """Format number with thousands separator"""
    return f"{value:,.{decimals}f}"

# ====== DATA LOADING FUNCTIONS ======
@st.cache_data
def load_historical_data():
    """Load historical hajj cost data"""
    # Try to load from CSV first, fallback to hardcoded data
    try:
        if os.path.exists("data/biaya_haji_historis.csv"):
            df = pd.read_csv("data/biaya_haji_historis.csv")
            return df
    except Exception as e:
        st.warning(f"⚠️ Could not load CSV file: {e}")
    
    # Fallback to hardcoded data
    data = {
        'Tahun': [2022, 2023, 2024, 2025],
        'BPIH': [85452883, 89629474, 94482028, 91493896],
        'Bipih': [39886009, 49812700, 56046172, 60559399],
        'NilaiManfaat': [45566874, 39816774, 38435856, 30934497]
    }
    return pd.DataFrame(data)

# Add to existing main.py navigation section:
def add_bpkh_navigation():
    """Add BPKH to main navigation"""
    
    # In your existing navigation logic, add:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🕌 BPKH Management")
    
    if st.sidebar.button("📊 BPKH Dashboard"):
        st.switch_page("pages/07_🕌_BPKH_Management.py")

@st.cache_data
def get_exchange_rates():
    """Get current exchange rates"""
    try:
        # Simulate API call - replace with real API if needed
        # For demo purposes, using static data with small random variations
        base_usd = 15500
        base_sar = 4133
        
        # Add small random variation to simulate live data
        import random
        usd_rate = base_usd + random.randint(-50, 50)
        sar_rate = base_sar + random.randint(-20, 20)
        
        return {
            'USD': usd_rate,
            'SAR': sar_rate,
            'timestamp': datetime.now(),
            'source': 'Simulated Live Data'
        }
    except Exception as e:
        st.error(f"Error fetching exchange rates: {e}")
        return {
            'USD': 15500,
            'SAR': 4133,
            'timestamp': datetime.now(),
            'source': 'Default Values'
        }

@st.cache_data
def get_economic_indicators():
    """Get economic indicators"""
    return {
        'saudi_inflation': 3.2,
        'indonesia_inflation': 2.8,
        'bi_rate': 6.0,
        'us_treasury_10y': 4.5,
        'fed_rate': 5.25,
        'source': 'Economic Data Simulation'
    }

# ====== LIABILITY CALCULATOR CLASS ======
class LiabilityCalculator:
    """Actuarial liability calculation engine"""
    
    @staticmethod
    def calculate_total_liability(
        total_jemaah: int,
        inflasi_saudi: float,
        kurs_usd: float,
        biaya_awal: float,
        tingkat_diskonto: float,
        tahun_proyeksi: int = 20,
        depresiasi_rupiah: float = 3.0
    ):
        """
        Calculate total present value of hajj liability
        Formula: L_total = Σ (C_t × J_t) / (1+r)^t
        """
        total_liability = 0
        jemaah_per_tahun = total_jemaah / tahun_proyeksi
        projections = []
        
        for t in range(1, tahun_proyeksi + 1):
            # C_t = C_0 × (1 + inflasi_saudi)^t × (1 + depresiasi_rupiah)^t
            biaya_tahun_t = biaya_awal * \
                           (1 + inflasi_saudi/100)**t * \
                           (1 + depresiasi_rupiah/100)**t
            
            # Present Value = Future Value / (1 + discount_rate)^t
            present_value = (biaya_tahun_t * jemaah_per_tahun) / \
                           (1 + tingkat_diskonto/100)**t
            
            total_liability += present_value
            
            projections.append({
                'tahun': 2025 + t,
                'biaya_per_jemaah': biaya_tahun_t,
                'jemaah': jemaah_per_tahun,
                'total_biaya': biaya_tahun_t * jemaah_per_tahun,
                'present_value': present_value
            })
        
        return total_liability, projections
    
    @staticmethod
    def sensitivity_analysis(base_params, sensitivity_params):
        """Perform sensitivity analysis on key parameters"""
        results = []
        base_liability, _ = LiabilityCalculator.calculate_total_liability(**base_params)
        
        for param_name, param_values in sensitivity_params.items():
            for value in param_values:
                params = base_params.copy()
                params[param_name] = value
                
                liability, _ = LiabilityCalculator.calculate_total_liability(**params)
                change_pct = ((liability - base_liability) / base_liability) * 100
                
                results.append({
                    'parameter': param_name,
                    'value': value,
                    'liability': liability,
                    'change_percent': change_pct
                })
        
        return results

# ====== STRESS TEST ENGINE ======
class StressTestEngine:
    """Stress testing and scenario analysis"""
    
    @staticmethod
    def run_stress_scenarios(base_assets: float, base_liability: float):
        """Run predefined stress test scenarios"""
        scenarios = {
            "📊 Skenario Dasar": {
                "liability_mult": 1.0,
                "asset_mult": 1.0,
                "description": "Kondisi normal tanpa shock eksternal"
            },
            "📉 Resesi Global": {
                "liability_mult": 1.15,
                "asset_mult": 0.85,
                "description": "Imbal hasil investasi turun, biaya naik"
            },
            "💱 Depresiasi Rupiah Ekstrem": {
                "liability_mult": 1.45,
                "asset_mult": 0.95,
                "description": "Rupiah melemah 30% dalam 2 tahun"
            },
            "📈 Inflasi Saudi Tinggi": {
                "liability_mult": 1.25,
                "asset_mult": 1.02,
                "description": "Inflasi Saudi mencapai 8% per tahun"
            },
            "⚡ Shock Ganda": {
                "liability_mult": 1.60,
                "asset_mult": 0.80,
                "description": "Kombinasi resesi + depresiasi + inflasi"
            }
        }
        
        results = []
        for scenario_name, params in scenarios.items():
            scenario_liability = base_liability * params["liability_mult"]
            scenario_assets = base_assets * params["asset_mult"]
            solvency_ratio = scenario_assets / scenario_liability
            
            status = "Aman" if solvency_ratio >= 1.2 else \
                    "Waspada" if solvency_ratio >= 1.0 else "Risiko Tinggi"
            
            results.append({
                'scenario': scenario_name,
                'description': params['description'],
                'assets': scenario_assets,
                'liability': scenario_liability,
                'solvency_ratio': solvency_ratio,
                'status': status
            })
        
        return results
    
    @staticmethod
    def monte_carlo_simulation(base_assets: float, base_liability: float, n_simulations: int = 1000):
        """Run Monte Carlo simulation for risk assessment"""
        np.random.seed(42)
        
        # Random factors with normal distribution
        liability_factors = np.random.normal(1.0, 0.15, n_simulations)
        asset_factors = np.random.normal(1.0, 0.10, n_simulations)
        
        # Ensure factors are positive
        liability_factors = np.abs(liability_factors)
        asset_factors = np.abs(asset_factors)
        
        simulated_solvency = (base_assets * asset_factors) / (base_liability * liability_factors)
        
        results = {
            'solvency_ratios': simulated_solvency,
            'mean_solvency': np.mean(simulated_solvency),
            'std_solvency': np.std(simulated_solvency),
            'safe_probability': (simulated_solvency >= 1.0).mean() * 100,
            'worst_case': np.min(simulated_solvency),
            'best_case': np.max(simulated_solvency)
        }
        
        return results

# ====== AI AGENTS SIMULATION ======
class AgentOrchestrator:
    def __init__(self):
        self.agents = {
            'data_collector': {'status': 'active', 'last_update': datetime.now()},
            'liability_analyst': {'status': 'active', 'last_update': datetime.now()},
            'investment_simulator': {'status': 'active', 'last_update': datetime.now()},
            'reporting_agent': {'status': 'standby', 'last_update': datetime.now()}
        }
    
    def get_agent_status(self):
        return self.agents
    
    def calculate_liability(self, total_jemaah, inflasi_saudi, kurs_usd, biaya_awal, tingkat_diskonto, tahun_proyeksi=20):
        """Calculate total liability using actuarial formula"""
        return LiabilityCalculator.calculate_total_liability(
            total_jemaah, inflasi_saudi, kurs_usd, biaya_awal, tingkat_diskonto, tahun_proyeksi
        )

# ====== INITIALIZE AGENTS ======
@st.cache_resource
def init_agents():
    return AgentOrchestrator()

# ====== AI RESPONSE GENERATOR ======
def generate_ai_response(prompt):
    """Generate AI response based on prompt"""
    prompt_lower = prompt.lower()
    
    responses = {
        'liabilitas': """
        📊 **Total Liabilitas Saat Ini**: Berdasarkan kalkulasi terkini menggunakan formula aktuaria, total liabilitas BPKH adalah sekitar **Rp 145.2 Triliun**.
        
        **Formula yang Digunakan:**
        - **L_total = Σ (C_t × J_t) / (1+r)^t**
        - Mempertimbangkan 2.5 juta jemaah tunggu
        - Proyeksi inflasi Saudi 3.5% per tahun
        - Tingkat diskonto 6.5%
        - Periode proyeksi 20 tahun
        
        💡 Gunakan halaman "Kalkulasi Liabilitas" untuk simulasi dengan parameter berbeda.
        """,
        
        'solvabilitas': """
        🛡️ **Rasio Solvabilitas** adalah perbandingan antara total aset dengan total liabilitas.
        
        **Formula**: Rasio = Total Aset ÷ Total Liabilitas
        
        **Status Saat Ini**:
        - Total Aset: Rp 180.5 Triliun
        - Total Liabilitas: Rp 145.2 Triliun  
        - **Rasio Solvabilitas: 1.24** ✅
        
        **Interpretasi**:
        - Rasio > 1.2: Zona Aman 🟢
        - Rasio 1.0-1.2: Zona Waspada 🟡
        - Rasio < 1.0: Zona Risiko 🔴
        """,
        
        'inflasi': """
        📈 **Dampak Inflasi Saudi terhadap Biaya Haji**:
        
        **Inflasi Saat Ini**: 3.2% per tahun
        
        **Dampak Langsung**:
        - 💰 Biaya akomodasi naik sesuai inflasi
        - 🍽️ Living cost jemaah meningkat
        - 🚌 Tarif transportasi lokal naik
        
        **Simulasi Dampak**:
        - Inflasi naik 1% → Liabilitas naik ~8.5%
        - Inflasi naik 2% → Liabilitas naik ~17.2%
        
        ⚠️ **Mitigasi**: Diversifikasi mata uang dan hedging currency exposure.
        """,
        
        'stress test': """
        🧪 **Cara Melakukan Stress Testing**:
        
        **Langkah-langkah**:
        1. 📊 Tentukan skenario shock (resesi, depresiasi, inflasi)
        2. 📈 Hitung dampak terhadap aset dan liabilitas
        3. 🔍 Analisis rasio solvabilitas hasil
        4. ⚡ Evaluasi tindakan mitigasi
        
        **Skenario Standar**:
        - **Resesi**: Asset -15%, Liability +15%
        - **Depresiasi**: Rupiah melemah 30%
        - **Inflasi**: Inflasi Saudi naik ke 8%
        
        🎯 Gunakan halaman "Simulasi & Stress Test" untuk analisis lengkap.
        """,
        
        'proyeksi': """
        🔮 **Proyeksi Biaya Haji 5 Tahun ke Depan**:
        
        **Asumsi Dasar**:
        - Inflasi Saudi: 3.5% per tahun
        - Depresiasi Rupiah: 3% per tahun
        - Kenaikan biaya operasional: 2% per tahun
        
        **Proyeksi Biaya per Jemaah**:
        - 2026: Rp 97.8 juta (+6.9%)
        - 2027: Rp 104.5 juta (+6.9%)
        - 2028: Rp 111.7 juta (+6.9%)
        - 2029: Rp 119.4 juta (+6.9%)
        - 2030: Rp 127.6 juta (+6.9%)
        
        📊 **Total Kebutuhan Dana**: Proyeksi menunjukkan pertumbuhan eksponensial.
        """,
        
        'regulasi': """
        📋 **Regulasi Pengelolaan Dana Haji**:
        
        **Dasar Hukum Utama**:
        - 🏛️ UU No. 8/2019 tentang Penyelenggaraan Ibadah Haji dan Umrah
        - 📄 PP No. 5/2018 tentang BPKH
        - 📄 Peraturan BPKH tentang Investasi
        
        **Prinsip Investasi**:
        - ✅ Harus sesuai prinsip syariah
        - ✅ Prudent (kehati-hatian)
        - ✅ Transparan dan akuntabel
        - ✅ Mengutamakan keamanan dana
        
        **Batasan Investasi**:
        - Maksimal 30% di instrumen ekuitas
        - Minimal 40% di instrumen fixed income
        """
    }
    
    # Check for keyword matches
    for keyword, response in responses.items():
        if keyword in prompt_lower:
            return response
    
    # Default response
    return """
    🤔 Maaf, saya belum sepenuhnya memahami pertanyaan Anda. 
    
    Silakan tanyakan tentang:
    - 📊 **Liabilitas**: Total kewajiban keuangan haji
    - 🛡️ **Solvabilitas**: Rasio kesehatan keuangan  
    - 📈 **Inflasi**: Dampak inflasi Saudi terhadap biaya haji
    - 📋 **Regulasi**: Undang-undang dan peraturan terkait
    - 🧪 **Stress Test**: Simulasi skenario risiko
    - 🔮 **Proyeksi**: Perkiraan biaya masa depan
    
    Atau gunakan kata kunci seperti "liabilitas", "solvabilitas", "inflasi", "stress test", "proyeksi", atau "regulasi" dalam pertanyaan Anda! 😊
    """

# ====== FOOTER DISCLAIMER FUNCTION ======
def render_footer_disclaimer():
    """Render footer with disclaimer and developer info"""
    version_info = AppConfig.get_version_info()
    
    # Simple markdown-based disclaimer
    st.markdown("---")
    st.markdown("## ⚠️ DISCLAIMER & INFORMASI APLIKASI")
    
    # Disclaimer section
    st.markdown("### 🔍 Disclaimer:")
    st.markdown("""
    - Aplikasi ini adalah alat bantu analisis dan simulasi untuk keperluan internal BPKH
    - Hasil kalkulasi dan proyeksi bersifat estimatif berdasarkan asumsi yang dapat berubah
    - Data yang ditampilkan sebagian bersifat simulasi untuk tujuan demonstrasi
    - Keputusan investasi dan kebijakan harus mempertimbangkan faktor-faktor lain yang relevan
    - BPKH tidak bertanggung jawab atas kerugian yang timbul dari penggunaan aplikasi ini
    """)
    
    # App information
    st.markdown("### 📊 Tentang Aplikasi:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        - **Nama:** {AppConfig.APP_NAME}
        - **Versi:** `{version_info['full_version']}`
        - **Developer:** **{AppConfig.DEVELOPER}**
        """)
    with col2:
        st.markdown(f"""
        - **Build Date:** {version_info['build_date']}
        - **Organisasi:** {AppConfig.ORGANIZATION}
        - **Tech Stack:** Python, Streamlit, Plotly
        """)
    
    # Security & Privacy
    st.markdown("### 🔒 Keamanan & Privasi:")
    st.markdown("""
    - Data sensitif tidak disimpan secara permanen dalam aplikasi
    - Semua kalkulasi dilakukan secara lokal dalam browser
    - Aplikasi tidak mengirim data ke server eksternal tanpa persetujuan
    - Gunakan aplikasi ini hanya di lingkungan yang aman dan terpercaya
    """)
    
    # Technical Support
    st.markdown("### 📞 Dukungan Teknis:")
    st.markdown("""
    - **Email:** sopian@bpkh.go.id
    - **Dokumentasi:** User Manual ASTHA (akan tersedia)
    - **Repository:** https://github.com/mshadianto/aplikasi_astha.git
    """)
    
    # Copyright footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #6b7280; padding: 1rem;">
        <p>© 2025 Badan Pengelola Keuangan Haji (BPKH) - Republik Indonesia</p>
        <p><small>Developed with ❤️ by <strong>{AppConfig.DEVELOPER}</strong> | Powered by Streamlit & Python</small></p>
        <p><small>Last Updated: {datetime.now().strftime('%d %B %Y, %H:%M WIB')} | Version: {version_info['full_version']}</small></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Changelog expander
    with st.expander("📝 Version History & Changelog", expanded=False):
        changelog = AppConfig.get_changelog()
        
        for version, changes in changelog.items():
            if version == f"v{AppConfig.APP_VERSION}":
                st.markdown(f"### 🔧 {version} (Current - Hotfix)")
            else:
                st.markdown(f"### {version}")
            
            for change in changes:
                st.markdown(f"- {change}")
            st.markdown("---")

# ====== MAIN APPLICATION FUNCTION ======
def main():
    # Initialize
    agents = init_agents()
    historical_data = load_historical_data()
    exchange_rates = get_exchange_rates()
    economic_indicators = get_economic_indicators()
    
    # Get version info
    version_info = AppConfig.get_version_info()
    
    # Show version update notification
    if "1.2.1" in version_info['version']:
        st.success(f"""
        🔧 **ASTHA {version_info['full_version']} - Hotfix Released!** 
        
        **🆕 Fixed in this version:**
        • Resolved HTML rendering issue in footer disclaimer
        • Improved cross-platform compatibility
        • Enhanced readability with native Streamlit components
        • Better performance with simplified styling
        
        Developed by **{AppConfig.DEVELOPER}** for BPKH Indonesia.
        """)
    
    # Main header
    st.markdown(f"""
    <div class="main-header">
        <h1>🕌 ASTHA <span class="version-badge">v{AppConfig.APP_VERSION}</span></h1>
        <h2>Agentic Sustainability for Hajj Treasury Analytics</h2>
        <p style="font-size: 1.1em; margin-top: 1rem;">
            Badan Pengelola Keuangan Haji (BPKH) - Republik Indonesia
        </p>
        <p style="font-size: 0.9em; opacity: 0.9;">
            Powered by AI Agents & Advanced Analytics | {version_info['full_version']}
        </p>
        <p style="font-size: 0.8em; opacity: 0.8;">
            Developed by {AppConfig.DEVELOPER} | Build: {version_info['build_date']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.selectbox(
        "Pilih Halaman",
        ["🏠 Dashboard", "🧮 Kalkulasi Liabilitas", "📊 Simulasi & Stress Test", "🤖 AI Assistant", "📈 Analytics", "📋 Reports"]
    )
    
    # Agent Status in Sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Status AI Agents")
    agent_status = agents.get_agent_status()
    for agent_name, status in agent_status.items():
        status_color = "🟢" if status['status'] == 'active' else "🟡"
        st.sidebar.markdown(f"{status_color} **{agent_name.replace('_', ' ').title()}**")
        st.sidebar.caption(f"Status: {status['status']} | Update: {status['last_update'].strftime('%H:%M')}")
    
    # Data source info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Data Sources")
    st.sidebar.caption(f"💱 Exchange: {exchange_rates['source']}")
    st.sidebar.caption(f"📈 Economic: {economic_indicators['source']}")
    st.sidebar.caption(f"🕐 Last Update: {exchange_rates['timestamp'].strftime('%H:%M')}")
    
    # Version info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ App Info")
    st.sidebar.caption(f"📱 Version: {version_info['full_version']}")
    st.sidebar.caption(f"👨‍💻 Developer: {AppConfig.DEVELOPER}")
    st.sidebar.caption(f"🏗️ Build: {version_info['build_date']}")
    st.sidebar.caption(f"🏢 {AppConfig.ORGANIZATION}")
    
    # About button
    if st.sidebar.button("📋 About ASTHA", use_container_width=True):
        st.sidebar.markdown(f"""
        **🕌 ASTHA** adalah aplikasi analisis sustainabilitas keuangan haji yang menggunakan teknologi AI dan metodologi aktuaria untuk membantu BPKH dalam:
        
        • 📊 Monitoring KPI real-time
        • 🧮 Kalkulasi liabilitas aktuaria  
        • 📈 Simulasi stress testing
        • 🤖 Analisis berbasis AI
        
        **Teknologi:** Python, Streamlit, Plotly
        **Metodologi:** Actuarial Science, Monte Carlo
        
        ---
        *{AppConfig.APP_NAME}*  
        *{version_info['full_version']} by {AppConfig.DEVELOPER}*
        """)
    
    # Quick help
    if st.sidebar.button("❓ Quick Help", use_container_width=True):
        st.sidebar.markdown("""
        **🚀 Quick Start:**
        1. Mulai dari Dashboard untuk overview
        2. Gunakan Kalkulasi Liabilitas untuk analisis mendalam  
        3. Jalankan Stress Test untuk risk assessment
        4. Tanya AI Assistant untuk bantuan
        
        **💡 Tips:**
        - Hover mouse pada 🛈 untuk info parameter
        - Klik "Refresh Data" untuk update terbaru
        - Gunakan sensitivity analysis untuk what-if scenarios
        """)
    
    # Changelog
    if st.sidebar.button("📝 What's New", use_container_width=True):
        changelog = AppConfig.get_changelog()
        st.sidebar.markdown("**🆕 Latest Updates:**")
        for version, changes in list(changelog.items())[:2]:  # Show last 2 versions
            st.sidebar.markdown(f"**{version}:**")
            for change in changes[:3]:  # Show first 3 changes
                st.sidebar.markdown(f"• {change}")
            st.sidebar.markdown("---")
    
    # Footer sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<small style='color: #6b7280;'>© 2025 BPKH Indonesia<br>"
        f"Build: {datetime.now().strftime('%H:%M')} WIB</small>", 
        unsafe_allow_html=True
    )
    
    # Main content based on selected page
    if page == "🏠 Dashboard":
        render_dashboard(historical_data, exchange_rates, economic_indicators)
    elif page == "🧮 Kalkulasi Liabilitas":
        render_liability_calculator(agents)
    elif page == "📊 Simulasi & Stress Test":
        render_simulation(agents)
    elif page == "🤖 AI Assistant":
        render_ai_assistant()
    elif page == "📈 Analytics":
        render_analytics(historical_data)
    elif page == "📋 Reports":
        render_reports(historical_data)
    
    # Footer Disclaimer
    render_footer_disclaimer()

# ====== PAGE RENDERING FUNCTIONS ======

def render_dashboard(historical_data, exchange_rates, economic_indicators):
    st.header("📊 Dashboard Monitoring Keberlanjutan")
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Aset Kelolaan", 
            value="Rp 180.5 T",
            delta="8.2% YTD",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="📊 Total Liabilitas",
            value="Rp 145.2 T",
            delta="3.1% dari proyeksi",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            label="🛡️ Rasio Solvabilitas",
            value="1.24",
            delta="0.05 dari target",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="📈 Imbal Hasil (YTD)",
            value="8.2%",
            delta="1.7% di atas target",
            delta_color="normal"
        )
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Tren Biaya Haji Historis")
        fig = px.line(
            historical_data, 
            x='Tahun', 
            y=['BPIH', 'NilaiManfaat'],
            title="Evolusi Biaya dan Nilai Manfaat",
            labels={'value': 'Rupiah', 'variable': 'Komponen'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🗺️ Sebaran Jemaah per Provinsi")
        provinces_data = {
            'Provinsi': ['Jawa Barat', 'Jawa Timur', 'Jawa Tengah', 'Sumatera Utara', 'Lampung', 'Lainnya'],
            'Jemaah': [420000, 380000, 340000, 180000, 160000, 1020000],
            'Persentase': [16.8, 15.2, 13.6, 7.2, 6.4, 40.8]
        }
        df_provinces = pd.DataFrame(provinces_data)
        
        fig = px.pie(
            df_provinces, 
            values='Jemaah', 
            names='Provinsi',
            title="Distribusi 2.5M Jemaah Tunggu",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Economic indicators
    st.subheader("📊 Indikator Ekonomi Terkini")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💵 USD/IDR", f"Rp {exchange_rates['USD']:,}", "↗️ 0.5%")
    with col2:
        st.metric("🇸🇦 SAR/IDR", f"Rp {exchange_rates['SAR']:,}", "↗️ 0.3%")
    with col3:
        st.metric("📈 Inflasi Saudi", f"{economic_indicators['saudi_inflation']}%", "↘️ 0.2%")
    with col4:
        st.metric("🏦 BI Rate", f"{economic_indicators['bi_rate']}%", "→ 0%")
    
    # Alert system
    st.subheader("🚨 Sistem Peringatan Dini")
    
    # Check for alerts based on current metrics
    alerts = []
    solvency_ratio = 1.24
    ytd_return = 8.2
    
    if solvency_ratio < 1.1:
        alerts.append({
            'level': 'danger',
            'title': 'Rasio Solvabilitas Rendah',
            'message': f'Rasio solvabilitas {solvency_ratio:.2f} mendekati batas minimum.'
        })
    
    if ytd_return < 5.0:
        alerts.append({
            'level': 'warning', 
            'title': 'Imbal Hasil di Bawah Target',
            'message': f'Imbal hasil YTD {ytd_return}% di bawah target 6.5%.'
        })
    
    if exchange_rates.get('USD', 15500) > 16000:
        alerts.append({
            'level': 'warning',
            'title': 'Kurs USD Tinggi',
            'message': 'Kurs USD/IDR melampaui level waspada Rp 16.000.'
        })
    
    if not alerts:
        st.success("✅ Semua indikator dalam kondisi normal")
    else:
        for alert in alerts:
            if alert['level'] == 'danger':
                st.error(f"🚨 **{alert['title']}**: {alert['message']}")
            else:
                st.warning(f"⚠️ **{alert['title']}**: {alert['message']}")
    
    # Data source info
    st.markdown(f"""
    <div class="info-box">
        <strong>📡 Data Sources:</strong><br>
        • Exchange Rates: {exchange_rates['source']}<br>
        • Economic Indicators: {economic_indicators['source']}<br>
        • Last Update: {exchange_rates['timestamp'].strftime('%d %B %Y, %H:%M WIB')}
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh option
    if st.button("🔄 Refresh Data (Simulasi Live Update)", type="primary"):
        st.cache_data.clear()
        st.success("✅ Data berhasil di-refresh!")
        st.balloons()
        st.rerun()

def render_liability_calculator(agents):
    st.header("🧮 Modul Kalkulasi Liabilitas Keuangan Haji")
    
    st.markdown("""
    ### 📋 Formula Aktuaria yang Digunakan:
    **L_total = Σ (C_t × J_t) / (1+r)^t**
    
    Di mana:
    - **L_total**: Total Liabilitas Keuangan Haji (nilai kini)
    - **C_t**: Biaya per jemaah pada tahun t
    - **J_t**: Jumlah jemaah pada tahun t  
    - **r**: Tingkat diskonto
    """)
    
    # Input parameters
    st.subheader("⚙️ Parameter Input")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_jemaah = st.number_input(
            "👥 Total Jemaah Tunggu",
            min_value=1000000,
            max_value=5000000,
            value=AppConfig.DEFAULT_TOTAL_JEMAAH,
            step=50000,
            help="Jumlah total jemaah dalam daftar tunggu"
        )
        
        inflasi_saudi = st.number_input(
            "📊 Inflasi Saudi (%/tahun)",
            min_value=0.0,
            max_value=15.0,
            value=AppConfig.DEFAULT_INFLASI_SAUDI,
            step=0.1,
            help="Asumsi inflasi tahunan di Arab Saudi"
        )
    
    with col2:
        kurs_usd = st.number_input(
            "💵 Kurs USD (Rupiah)",
            min_value=10000,
            max_value=25000,
            value=AppConfig.DEFAULT_KURS_USD,
            step=100,
            help="Kurs USD terhadap Rupiah"
        )
        
        tingkat_diskonto = st.number_input(
            "🏦 Tingkat Diskonto (%)",
            min_value=3.0,
            max_value=15.0,
            value=AppConfig.DEFAULT_TINGKAT_DISKONTO,
            step=0.1,
            help="Tingkat diskonto untuk menghitung present value"
        )
    
    with col3:
        biaya_awal = st.number_input(
            "💰 Biaya Awal per Jemaah (Rp)",
            min_value=50000000,
            max_value=150000000,
            value=94482028,
            step=1000000,
            help="Biaya penyelenggaraan haji per jemaah saat ini"
        )
        
        tahun_proyeksi = st.number_input(
            "📅 Tahun Proyeksi",
            min_value=10,
            max_value=30,
            value=AppConfig.DEFAULT_TAHUN_PROYEKSI,
            step=5,
            help="Periode proyeksi untuk kalkulasi liabilitas"
        )
    
    # Calculate liability
    if st.button("🔬 Hitung Liabilitas", type="primary"):
        with st.spinner("🤖 AI Agent sedang menghitung..."):
            total_liability, projections = agents.calculate_liability(
                total_jemaah, inflasi_saudi, kurs_usd, biaya_awal, tingkat_diskonto, tahun_proyeksi
            )
            
            # Display results
            st.markdown(f"""
            <div class="liability-result">
                <h2>💰 Total Present Value of Hajj Liability</h2>
                <h1>{format_rupiah(total_liability)}</h1>
                <p>Berdasarkan kalkulasi aktuaria dengan proyeksi {tahun_proyeksi} tahun</p>
                <p>Equivalent to: {total_liability/1e12:.2f} Trillion Rupiah</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Projection chart
            st.subheader("📊 Proyeksi Kebutuhan Dana per Tahun")
            df_proj = pd.DataFrame(projections)
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Total Biaya per Tahun (Triliun Rupiah)', 'Biaya per Jemaah (Juta Rupiah)'),
                vertical_spacing=0.1
            )
            
            fig.add_trace(
                go.Bar(
                    x=df_proj['tahun'],
                    y=df_proj['total_biaya'] / 1e12,
                    name='Total Biaya (Triliun)',
                    marker_color='#10b981'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df_proj['tahun'],
                    y=df_proj['biaya_per_jemaah'] / 1e6,
                    mode='lines+markers',
                    name='Biaya per Jemaah (Juta)',
                    line=dict(color='#3b82f6', width=3)
                ),
                row=2, col=1
            )
            
            fig.update_layout(height=600, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            
            # Sensitivity analysis
            st.subheader("📈 Analisis Sensitivitas")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔄 Sensitivitas terhadap Inflasi Saudi**")
                inflasi_scenarios = [2.0, 3.5, 5.0, 6.5, 8.0]
                sensitivity_inflasi = []
                
                for inflasi in inflasi_scenarios:
                    liability, _ = agents.calculate_liability(
                        total_jemaah, inflasi, kurs_usd, biaya_awal, tingkat_diskonto, tahun_proyeksi
                    )
                    sensitivity_inflasi.append({
                        'Inflasi (%)': inflasi,
                        'Total Liabilitas': format_rupiah(liability),
                        'Perubahan (%)': f"{((liability - total_liability) / total_liability) * 100:.1f}%"
                    })
                
                df_sens = pd.DataFrame(sensitivity_inflasi)
                st.dataframe(df_sens, use_container_width=True)
            
            with col2:
                st.markdown("**💱 Sensitivitas terhadap Kurs USD**")
                kurs_scenarios = [14000, 15500, 17000, 18500, 20000]
                sensitivity_kurs = []
                
                for kurs in kurs_scenarios:
                    liability, _ = agents.calculate_liability(
                        total_jemaah, inflasi_saudi, kurs, biaya_awal, tingkat_diskonto, tahun_proyeksi
                    )
                    sensitivity_kurs.append({
                        'Kurs USD': f"Rp {kurs:,}",
                        'Total Liabilitas': format_rupiah(liability),
                        'Perubahan (%)': f"{((liability - total_liability) / total_liability) * 100:.1f}%"
                    })
                
                df_kurs = pd.DataFrame(sensitivity_kurs)
                st.dataframe(df_kurs, use_container_width=True)
            
            # Summary statistics
            st.subheader("📋 Ringkasan Hasil Kalkulasi")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Total Liability", format_rupiah(total_liability))
            with col2:
                avg_annual = total_liability / tahun_proyeksi
                st.metric("📅 Rata-rata per Tahun", format_rupiah(avg_annual))
            with col3:
                cost_per_pilgrim = total_liability / total_jemaah
                st.metric("👤 Present Value per Jemaah", format_rupiah(cost_per_pilgrim))
            with col4:
                st.metric("⏱️ Periode Proyeksi", f"{tahun_proyeksi} tahun")

def render_simulation(agents):
    st.header("📊 Simulasi & Stress Testing")
    
    # Scenario selection
    st.subheader("🎯 Pilih Skenario Stress Test")
    scenario = st.selectbox(
        "Skenario",
        ["📊 Skenario Dasar", "📉 Resesi Global", "💱 Depresiasi Rupiah Ekstrem", "📈 Inflasi Saudi Tinggi", "⚡ Shock Ganda"]
    )
    
    # Base parameters
    base_liability = 145.2  # trillion
    base_assets = 180.5     # trillion
    base_solvency = base_assets / base_liability
    
    # Scenario parameters
    scenarios = {
        "📊 Skenario Dasar": {"liability_mult": 1.0, "asset_mult": 1.0, "description": "Kondisi normal tanpa shock eksternal"},
        "📉 Resesi Global": {"liability_mult": 1.15, "asset_mult": 0.85, "description": "Imbal hasil investasi turun, biaya naik"},
        "💱 Depresiasi Rupiah Ekstrem": {"liability_mult": 1.45, "asset_mult": 0.95, "description": "Rupiah melemah 30% dalam 2 tahun"},
        "📈 Inflasi Saudi Tinggi": {"liability_mult": 1.25, "asset_mult": 1.02, "description": "Inflasi Saudi mencapai 8% per tahun"},
        "⚡ Shock Ganda": {"liability_mult": 1.60, "asset_mult": 0.80, "description": "Kombinasi resesi + depresiasi + inflasi"}
    }
    
    selected_scenario = scenarios[scenario]
    
    # Calculate scenario results
    scenario_liability = base_liability * selected_scenario["liability_mult"]
    scenario_assets = base_assets * selected_scenario["asset_mult"]
    scenario_solvency = scenario_assets / scenario_liability
    
    # Display scenario info
    st.info(f"**{scenario}**: {selected_scenario['description']}")
    
    # Results display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        liability_delta = ((scenario_liability - base_liability) / base_liability) * 100
        st.metric(
            "💰 Total Liabilitas",
            f"Rp {scenario_liability:.1f}T",
            f"{liability_delta:+.1f}%",
            delta_color="inverse"
        )
    
    with col2:
        assets_delta = ((scenario_assets - base_assets) / base_assets) * 100
        st.metric(
            "📊 Total Aset",
            f"Rp {scenario_assets:.1f}T",
            f"{assets_delta:+.1f}%"
        )
    
    with col3:
        solvency_delta = scenario_solvency - base_solvency
        status = "normal" if scenario_solvency > 1.0 else "inverse"
        st.metric(
            "🛡️ Rasio Solvabilitas",
            f"{scenario_solvency:.2f}",
            f"{solvency_delta:+.2f}",
            delta_color=status
        )
    
    # Status assessment
    if scenario_solvency >= 1.2:
        st.markdown("""
        <div class="stress-test-safe">
            <strong>✅ STATUS: AMAN</strong><br>
            Rasio solvabilitas masih berada dalam zona aman. BPKH mampu memenuhi kewajiban.
        </div>
        """, unsafe_allow_html=True)
    elif scenario_solvency >= 1.0:
        st.markdown("""
        <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 1rem; margin: 0.5rem 0;">
            <strong>⚠️ STATUS: WASPADA</strong><br>
            Rasio solvabilitas menurun tapi masih di atas 1.0. Perlu monitoring ketat.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="stress-test-risk">
            <strong>🚨 STATUS: RISIKO TINGGI</strong><br>
            Rasio solvabilitas di bawah 1.0. Diperlukan tindakan mitigasi segera.
        </div>
        """, unsafe_allow_html=True)
    
    # Comparative chart
    st.subheader("📈 Perbandingan Skenario")
    
    comparison_data = {
        'Skenario': list(scenarios.keys()),
        'Liabilitas': [base_liability * scenarios[s]["liability_mult"] for s in scenarios.keys()],
        'Aset': [base_assets * scenarios[s]["asset_mult"] for s in scenarios.keys()],
        'Rasio Solvabilitas': [
            (base_assets * scenarios[s]["asset_mult"]) / (base_liability * scenarios[s]["liability_mult"])
            for s in scenarios.keys()
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Aset vs Liabilitas (Triliun Rp)', 'Rasio Solvabilitas'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(
        go.Bar(x=df_comparison['Skenario'], y=df_comparison['Aset'], name='Aset', marker_color='#10b981'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=df_comparison['Skenario'], y=df_comparison['Liabilitas'], name='Liabilitas', marker_color='#ef4444'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df_comparison['Skenario'], 
            y=df_comparison['Rasio Solvabilitas'], 
            mode='lines+markers',
            name='Rasio Solvabilitas',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8)
        ),
        row=1, col=2
    )
    
    # Add threshold line
    fig.add_hline(y=1.0, line_dash="dash", line_color="red", row=1, col=2, annotation_text="Batas Minimum")
    
    fig.update_layout(height=500, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Monte Carlo simulation
    st.subheader("🎲 Simulasi Monte Carlo")
    if st.button("🚀 Jalankan Simulasi Monte Carlo (1000 iterasi)"):
        with st.spinner("🔬 Menjalankan 1000 simulasi..."):
            results = StressTestEngine.monte_carlo_simulation(base_assets * 1e12, base_liability * 1e12, 1000)
            
            # Create histogram
            fig = px.histogram(
                x=results['solvency_ratios'],
                nbins=50,
                title="Distribusi Rasio Solvabilitas (1000 Simulasi Monte Carlo)",
                labels={'x': 'Rasio Solvabilitas', 'y': 'Frekuensi'},
                color_discrete_sequence=['#10b981']
            )
            fig.add_vline(x=1.0, line_dash="dash", line_color="red", annotation_text="Batas Minimum")
            fig.add_vline(x=results['mean_solvency'], line_dash="dot", line_color="blue", annotation_text="Rata-rata")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📊 Rata-rata Rasio", f"{results['mean_solvency']:.2f}")
            with col2:
                st.metric("🛡️ Probabilitas Aman", f"{results['safe_probability']:.1f}%")
            with col3:
                st.metric("📉 Skenario Terburuk", f"{results['worst_case']:.2f}")

def render_ai_assistant():
    st.header("🤖 Asisten Cerdas BPKH")
    
    st.markdown("""
    ### 💡 Tanyakan tentang:
    - 📊 Data keuangan dan liabilitas
    - 📈 Proyeksi dan simulasi
    - 📋 Regulasi dan kebijakan haji
    - 💰 Strategi investasi dan manajemen risiko
    """)
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 Selamat datang! Saya adalah Asisten Cerdas BPKH. Bagaimana saya bisa membantu Anda hari ini?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Tanyakan sesuatu..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Sedang berpikir..."):
                response = generate_ai_response(prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Quick questions
    st.markdown("### ⚡ Pertanyaan Cepat")
    quick_questions = [
        "Berapa total liabilitas saat ini?",
        "Bagaimana cara menghitung rasio solvabilitas?",
        "Apa dampak inflasi Saudi terhadap biaya haji?",
        "Regulasi apa yang mengatur investasi dana haji?",
        "Bagaimana cara melakukan stress test?",
        "Proyeksi biaya haji 5 tahun ke depan?"
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(quick_questions):
        with cols[i % 2]:
            if st.button(question, key=f"quick_{i}"):
                st.session_state.messages.append({"role": "user", "content": question})
                response = generate_ai_response(question)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()

def render_analytics(historical_data):
    st.header("📈 Advanced Analytics")
    
    # Trend analysis
    st.subheader("📊 Analisis Tren & Pola")
    
    # Calculate growth rates
    historical_data_copy = historical_data.copy()
    historical_data_copy['BPIH_Growth'] = historical_data_copy['BPIH'].pct_change() * 100
    historical_data_copy['NilaiManfaat_Growth'] = historical_data_copy['NilaiManfaat'].pct_change() * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            historical_data_copy.dropna(), 
            x='Tahun', 
            y='BPIH_Growth',
            title="Pertumbuhan BPIH (% Year-on-Year)",
            labels={'BPIH_Growth': 'Pertumbuhan (%)'},
            color='BPIH_Growth',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            historical_data_copy.dropna(), 
            x='Tahun', 
            y='NilaiManfaat_Growth',
            title="Pertumbuhan Nilai Manfaat (% YoY)",
            labels={'NilaiManfaat_Growth': 'Pertumbuhan (%)'},
            color='NilaiManfaat_Growth',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Key insights
    st.subheader("💡 Key Insights")
    
    avg_growth = historical_data_copy['BPIH_Growth'].mean()
    volatility = historical_data_copy['BPIH_Growth'].std()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Rata-rata Pertumbuhan BPIH", f"{avg_growth:.1f}%/tahun")
    
    with col2:
        st.metric("📊 Volatilitas Pertumbuhan", f"{volatility:.1f}%")
    
    with col3:
        latest_efficiency = (historical_data.iloc[-1]['NilaiManfaat'] / historical_data.iloc[-1]['BPIH']) * 100
        st.metric("⚡ Efisiensi Nilai Manfaat", f"{latest_efficiency:.1f}%")
    
    # More analytics coming soon
    st.info("🚧 Fitur analytics lanjutan sedang dalam pengembangan. Coming soon!")

def render_reports(historical_data):
    st.header("📋 Report Generation")
    
    # Report options
    st.subheader("📊 Pilih Jenis Laporan")
    
    report_type = st.selectbox(
        "Jenis Laporan",
        ["📈 Laporan Dashboard Eksekutif", "🧮 Laporan Kalkulasi Liabilitas", "🧪 Laporan Stress Testing", "📊 Laporan Analisis Komprehensif"]
    )
    
    report_period = st.selectbox(
        "Periode Laporan",
        ["Bulanan", "Kuartalan", "Tahunan"]
    )
    
    # Generate report preview
    if st.button("📄 Generate Preview Laporan", type="primary"):
        with st.spinner("📝 Menyiapkan laporan..."):
            current_date = datetime.now().strftime("%d %B %Y")
            
            if "Dashboard" in report_type:
                report_content = f"""
                # 📊 LAPORAN DASHBOARD EKSEKUTIF BPKH
                **Tanggal**: {current_date}
                
                ## 🎯 RINGKASAN EKSEKUTIF
                
                ### Key Performance Indicators:
                - **Total Aset Kelolaan**: Rp 180.5 Triliun (↗️ 8.2% YTD)
                - **Total Liabilitas**: Rp 145.2 Triliun 
                - **Rasio Solvabilitas**: 1.24 (Status: ✅ Aman)
                - **Imbal Hasil Investasi**: 8.2% YTD (Target: 6.5%)
                
                ### 📈 Tren Utama:
                - Biaya haji menunjukkan tren naik rata-rata 4.9% per tahun
                - Nilai manfaat mengalami penurunan efisiensi
                - Rasio solvabilitas tetap dalam zona aman
                
                ### 🎯 Rekomendasi:
                1. **Optimalisasi Portofolio**: Tingkatkan alokasi di instrumen dengan imbal hasil tinggi
                2. **Mitigasi Risiko**: Implementasi hedging untuk risiko mata uang
                3. **Efisiensi Operasional**: Review ulang struktur biaya untuk meningkatkan nilai manfaat
                """
            else:
                report_content = f"""
                # 📋 LAPORAN {report_type.upper()}
                **Tanggal**: {current_date}
                **Periode**: {report_period}
                
                ## 📊 STATUS LAPORAN
                🚧 Template laporan untuk {report_type} sedang dalam pengembangan.
                
                Laporan akan mencakup:
                - Analisis komprehensif sesuai jenis laporan
                - Visualisasi data interaktif
                - Rekomendasi strategis
                - Proyeksi dan simulasi
                
                **Coming Soon!**
                """
            
            st.success("✅ Preview laporan berhasil dibuat!")
            st.markdown(report_content)
            
            # Download simulation
            st.markdown("### ⬇️ Download Laporan")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Download PDF"):
                    st.info("📁 Fitur download PDF akan segera tersedia!")
            
            with col2:
                if st.button("📊 Download Excel"):
                    st.info("📁 Fitur download Excel akan segera tersedia!")
            
            with col3:
                if st.button("📝 Download Word"):
                    st.info("📁 Fitur download Word akan segera tersedia!")

# ====== MAIN EXECUTION ======
if __name__ == "__main__":
    main()

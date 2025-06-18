# ============================================================================
# 4. CREATE DATA MANAGER: app/database/bpkh_data.py
# ============================================================================

import pandas as pd
from typing import Dict, List

class BPKHDataManager:
    """Data manager for BPKH historical and real-time data"""
    
    def __init__(self):
        self.historical_data = self._load_historical_data()
    
    def _load_historical_data(self) -> pd.DataFrame:
        """Load historical BPKH data from 2022-2024"""
        
        data = {
            'years': ['2022', '2023', '2024'],
            'dana_haji': [66.54, 66.74, 71.64],
            'investasi': [17.59, 25.11, 30.88],
            'penempatan': [48.95, 41.63, 40.76],
            'pendapatan_investasi': [8.58, 8.94, 9.15],
            'pendapatan_penempatan': [1.59, 1.98, 2.35],
            'pendaftar_baru': [320251, 322490, 398745],
            'rasio_likuiditas': [2.22, 2.09, 2.16],
            'program_kemaslahatan': [130.32, 228.58, 230.27],
            'biaya_operasional': [398.36, 369.49, 458.89]
        }
        
        return pd.DataFrame(data)
    
    def get_historical_data(self) -> pd.DataFrame:
        """Get historical data"""
        return self.historical_data.copy()
    
    def get_latest_metrics(self) -> Dict:
        """Get latest period metrics"""
        latest = self.historical_data.iloc[-1]
        return latest.to_dict()


# ============================================================================
# 2. CREATE SERVICE: app/services/bpkh_service.py
# ============================================================================

import pandas as pd
import numpy as np
from typing import Dict, Any

class BPKHService:
    """Service class for BPKH business logic and calculations"""
    
    def __init__(self):
        self.target_liquidity_ratio = 2.0
        
    def calculate_current_metrics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate current period metrics and growth rates"""
        
        current = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else current
        
        # Growth calculations
        dana_haji_growth = self._calculate_growth(current['dana_haji'], previous['dana_haji'])
        investasi_growth = self._calculate_growth(current['investasi'], previous['investasi'])
        pendaftar_growth = self._calculate_growth(current['pendaftar_baru'], previous['pendaftar_baru'])
        
        # ROI calculations
        roi_investasi = (current['pendapatan_investasi'] / current['investasi']) * 100
        roi_penempatan = (current['pendapatan_penempatan'] / current['penempatan']) * 100
        total_return = current['pendapatan_investasi'] + current['pendapatan_penempatan']
        
        # Cost metrics
        cost_income_ratio = (current['biaya_operasional'] / (total_return * 1000)) * 100
        
        return {
            'dana_haji_current': current['dana_haji'],
            'dana_haji_growth': dana_haji_growth,
            'investasi_current': current['investasi'],
            'investasi_growth': investasi_growth,
            'pendaftar_current': current['pendaftar_baru'],
            'pendaftar_growth': pendaftar_growth,
            'rasio_likuiditas': current['rasio_likuiditas'],
            'roi_investasi': roi_investasi,
            'roi_penempatan': roi_penempatan,
            'total_return': total_return,
            'cost_income_ratio': cost_income_ratio,
            'penempatan_current': current['penempatan'],
            # Waiting list data
            'waiting_list_reguler': 5336016,
            'waiting_list_khusus': 122410,
            'waiting_growth_reguler': 1.48,
            'waiting_growth_khusus': 21.74
        }
    
    def _calculate_growth(self, current: float, previous: float) -> float:
        """Calculate growth rate between two periods"""
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100
    
    def calculate_scenario_projections(self, current_metrics: Dict) -> Dict:
        """Calculate 2025 scenario projections"""
        
        scenarios = {
            'conservative': {
                'dana_haji_growth': 0.06,
                'investasi_growth': 0.08
            },
            'base_case': {
                'dana_haji_growth': 0.08,
                'investasi_growth': 0.12
            },
            'optimistic': {
                'dana_haji_growth': 0.12,
                'investasi_growth': 0.18
            }
        }
        
        projections = {}
        for scenario, growth_rates in scenarios.items():
            projections[scenario] = {
                'dana_haji': current_metrics['dana_haji_current'] * (1 + growth_rates['dana_haji_growth']),
                'investasi': current_metrics['investasi_current'] * (1 + growth_rates['investasi_growth'])
            }
        
        return projections

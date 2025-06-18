# ===== utils/formatters.py =====
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

def format_currency(amount: float, currency: str = "IDR") -> str:
    """Format currency with appropriate suffix"""
    if currency == "IDR":
        if amount >= 1000:  # Triliun
            return f"Rp {amount:.2f}T"
        elif amount >= 1:  # Miliar
            return f"Rp {amount*1000:.0f}M"
        else:
            return f"Rp {amount*1000000:.0f}K"
    return f"{amount:,.2f}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage with sign"""
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{decimals}f}%"

def format_number(number: int) -> str:
    """Format large numbers with commas"""
    return f"{number:,}"

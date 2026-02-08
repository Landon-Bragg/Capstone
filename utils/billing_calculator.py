from datetime import datetime
from config import Config

def get_season(month):
    """Determine season based on month"""
    if month in [6, 7, 8]:  # June, July, August
        return 'summer'
    elif month in [12, 1, 2]:  # December, January, February
        return 'winter'
    else:
        return 'spring_fall'

def calculate_usage_charge(usage_ccf, month):
    """
    Calculate usage charge based on tiered pricing and seasonal multipliers
    
    Args:
        usage_ccf (float): Total usage in CCF (hundred cubic feet)
        month (int): Month number (1-12)
    
    Returns:
        dict: Breakdown of charges
    """
    pricing = Config.PRICING
    tiers = pricing['tiers']
    
    # Get seasonal multiplier
    season = get_season(month)
    seasonal_multiplier = pricing['seasonal_multipliers'][season]
    
    # Calculate tiered charges
    remaining_usage = usage_ccf
    tier_charges = []
    total_charge = 0
    
    for tier in tiers:
        if remaining_usage <= 0:
            break
        
        tier_min = tier['min']
        tier_max = tier['max']
        tier_rate = tier['rate']
        
        # Calculate usage in this tier
        tier_usage = min(remaining_usage, tier_max - tier_min)
        tier_charge = tier_usage * tier_rate
        
        tier_charges.append({
            'tier': f"{tier_min}-{tier_max if tier_max != float('inf') else '+'} CCF",
            'usage': round(tier_usage, 2),
            'rate': tier_rate,
            'charge': round(tier_charge, 2)
        })
        
        total_charge += tier_charge
        remaining_usage -= tier_usage
    
    # Apply seasonal multiplier
    base_charge = total_charge
    seasonal_adjustment = total_charge * (seasonal_multiplier - 1)
    total_charge *= seasonal_multiplier
    
    return {
        'base_charge': round(base_charge, 2),
        'seasonal_multiplier': seasonal_multiplier,
        'season': season,
        'seasonal_adjustment': round(seasonal_adjustment, 2),
        'usage_charge': round(total_charge, 2),
        'tier_breakdown': tier_charges
    }

def calculate_total_bill(usage_ccf, month):
    """
    Calculate complete bill including fees
    
    Args:
        usage_ccf (float): Total usage in CCF
        month (int): Month number (1-12)
    
    Returns:
        dict: Complete bill breakdown
    """
    pricing = Config.PRICING
    
    # Calculate usage charge
    usage_breakdown = calculate_usage_charge(usage_ccf, month)
    
    # Add fees
    base_service_fee = pricing['fees']['base_service']
    infrastructure_fee = pricing['fees']['infrastructure']
    total_fees = base_service_fee + infrastructure_fee
    
    # Calculate total
    total_amount = usage_breakdown['usage_charge'] + total_fees
    
    return {
        'total_usage': round(usage_ccf, 2),
        'usage_charge': usage_breakdown['usage_charge'],
        'base_service_fee': base_service_fee,
        'infrastructure_fee': infrastructure_fee,
        'total_fees': total_fees,
        'total_amount': round(total_amount, 2),
        'breakdown': usage_breakdown
    }

def generate_bill_summary(bill_data):
    """
    Generate human-readable bill summary
    
    Args:
        bill_data (dict): Bill data from calculate_total_bill
    
    Returns:
        str: Formatted bill summary
    """
    breakdown = bill_data['breakdown']
    
    summary = f"""
HYDROSPARK WATER BILL SUMMARY
================================

Total Water Usage: {bill_data['total_usage']} CCF

USAGE CHARGES ({breakdown['season'].upper()})
Season Multiplier: {breakdown['seasonal_multiplier']}x
"""
    
    for tier in breakdown['tier_breakdown']:
        summary += f"\n  {tier['tier']}: {tier['usage']} CCF × ${tier['rate']}/CCF = ${tier['charge']}"
    
    if breakdown['seasonal_adjustment'] != 0:
        summary += f"\n  Seasonal Adjustment: ${breakdown['seasonal_adjustment']}"
    
    summary += f"""

FEES & CHARGES
  Base Service Fee: ${bill_data['base_service_fee']}
  Infrastructure Fee: ${bill_data['infrastructure_fee']}

TOTAL AMOUNT DUE: ${bill_data['total_amount']}
================================
"""
    
    return summary

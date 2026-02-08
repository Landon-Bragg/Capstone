import numpy as np
from datetime import datetime, timedelta
from config import Config

def detect_anomalies(customer_usage_data, threshold_sigma=None):
    """
    Detect anomalies in water usage using statistical analysis
    
    Args:
        customer_usage_data (list): List of usage records [{date, usage_ccf}, ...]
        threshold_sigma (float): Number of standard deviations for threshold
    
    Returns:
        list: Anomalies detected [{date, usage, avg, std, sigma}, ...]
    """
    if threshold_sigma is None:
        threshold_sigma = Config.ANOMALY_THRESHOLD_SIGMA
    
    if len(customer_usage_data) < 30:  # Need at least 30 days for meaningful statistics
        return []
    
    # Extract usage values
    usage_values = [record['usage_ccf'] for record in customer_usage_data]
    
    # Calculate statistics
    mean_usage = np.mean(usage_values)
    std_usage = np.std(usage_values)
    
    # Avoid division by zero
    if std_usage == 0:
        return []
    
    # Detect anomalies
    anomalies = []
    for record in customer_usage_data:
        usage = record['usage_ccf']
        sigma_value = (usage - mean_usage) / std_usage
        
        # Flag if usage is more than threshold_sigma standard deviations above mean
        if sigma_value > threshold_sigma:
            anomalies.append({
                'date': record['date'],
                'usage_ccf': usage,
                'average_usage': round(mean_usage, 2),
                'std_deviation': round(std_usage, 2),
                'sigma_value': round(sigma_value, 2),
                'deviation_percent': round(((usage - mean_usage) / mean_usage) * 100, 1)
            })
    
    return anomalies

def get_recent_anomalies(customer_usage_data, days=30):
    """
    Get anomalies from the last N days
    
    Args:
        customer_usage_data (list): List of usage records
        days (int): Number of days to look back
    
    Returns:
        list: Recent anomalies
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Filter recent data
    recent_data = [
        record for record in customer_usage_data
        if isinstance(record['date'], datetime) and record['date'] >= cutoff_date
        or isinstance(record['date'], str) and datetime.fromisoformat(record['date']) >= cutoff_date
    ]
    
    return detect_anomalies(recent_data)

def analyze_usage_pattern(customer_usage_data):
    """
    Analyze usage patterns to provide insights
    
    Args:
        customer_usage_data (list): List of usage records
    
    Returns:
        dict: Usage pattern analysis
    """
    if len(customer_usage_data) < 7:
        return {'error': 'Insufficient data for pattern analysis'}
    
    usage_values = [record['usage_ccf'] for record in customer_usage_data]
    
    # Calculate statistics
    stats = {
        'mean': round(np.mean(usage_values), 2),
        'median': round(np.median(usage_values), 2),
        'std_dev': round(np.std(usage_values), 2),
        'min': round(np.min(usage_values), 2),
        'max': round(np.max(usage_values), 2),
        'total': round(np.sum(usage_values), 2),
        'count': len(usage_values)
    }
    
    # Calculate percentiles
    stats['percentile_25'] = round(np.percentile(usage_values, 25), 2)
    stats['percentile_75'] = round(np.percentile(usage_values, 75), 2)
    stats['percentile_90'] = round(np.percentile(usage_values, 90), 2)
    
    # Determine usage trend (last 30 days vs previous 30 days)
    if len(usage_values) >= 60:
        recent_30 = usage_values[-30:]
        previous_30 = usage_values[-60:-30]
        
        recent_avg = np.mean(recent_30)
        previous_avg = np.mean(previous_30)
        
        trend_change = ((recent_avg - previous_avg) / previous_avg) * 100
        
        stats['trend'] = {
            'recent_avg': round(recent_avg, 2),
            'previous_avg': round(previous_avg, 2),
            'change_percent': round(trend_change, 1),
            'direction': 'increasing' if trend_change > 5 else 'decreasing' if trend_change < -5 else 'stable'
        }
    
    return stats

def get_anomaly_summary(anomalies):
    """
    Generate summary report for anomalies
    
    Args:
        anomalies (list): List of anomaly records
    
    Returns:
        dict: Summary statistics
    """
    if not anomalies:
        return {
            'total_anomalies': 0,
            'avg_deviation_percent': 0,
            'max_deviation_percent': 0,
            'severity': 'none'
        }
    
    deviation_percents = [a['deviation_percent'] for a in anomalies]
    avg_deviation = np.mean(deviation_percents)
    max_deviation = np.max(deviation_percents)
    
    # Determine severity
    if max_deviation > 200:
        severity = 'critical'
    elif max_deviation > 100:
        severity = 'high'
    elif max_deviation > 50:
        severity = 'medium'
    else:
        severity = 'low'
    
    return {
        'total_anomalies': len(anomalies),
        'avg_deviation_percent': round(avg_deviation, 1),
        'max_deviation_percent': round(max_deviation, 1),
        'severity': severity,
        'most_recent': anomalies[-1] if anomalies else None
    }

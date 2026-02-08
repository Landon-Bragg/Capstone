import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

def forecast_usage(customer_usage_data, forecast_days=30):
    """
    Forecast future water usage based on historical patterns
    
    Args:
        customer_usage_data (list): List of usage records [{date, usage_ccf}, ...]
        forecast_days (int): Number of days to forecast
    
    Returns:
        dict: Forecast data including predictions and confidence intervals
    """
    if len(customer_usage_data) < 60:  # Need at least 60 days for meaningful forecast
        return {
            'error': 'Insufficient historical data for forecasting',
            'required_days': 60,
            'available_days': len(customer_usage_data)
        }
    
    # Sort by date
    sorted_data = sorted(customer_usage_data, key=lambda x: x['date'])
    
    # Calculate day-of-week patterns
    day_of_week_usage = defaultdict(list)
    for record in sorted_data[-90:]:  # Use last 90 days
        date = record['date']
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        day_of_week = date.weekday()
        day_of_week_usage[day_of_week].append(record['usage_ccf'])
    
    # Calculate average usage per day of week
    day_patterns = {}
    for day in range(7):
        if day in day_of_week_usage and day_of_week_usage[day]:
            day_patterns[day] = {
                'mean': np.mean(day_of_week_usage[day]),
                'std': np.std(day_of_week_usage[day])
            }
        else:
            # Use overall mean if no data for this day
            overall_mean = np.mean([r['usage_ccf'] for r in sorted_data[-90:]])
            overall_std = np.std([r['usage_ccf'] for r in sorted_data[-90:]])
            day_patterns[day] = {
                'mean': overall_mean,
                'std': overall_std
            }
    
    # Calculate monthly trend
    recent_usage = [r['usage_ccf'] for r in sorted_data[-30:]]
    previous_usage = [r['usage_ccf'] for r in sorted_data[-60:-30]]
    
    recent_avg = np.mean(recent_usage)
    previous_avg = np.mean(previous_usage)
    trend_factor = recent_avg / previous_avg if previous_avg > 0 else 1.0
    
    # Generate forecast
    last_date = sorted_data[-1]['date']
    if isinstance(last_date, str):
        last_date = datetime.fromisoformat(last_date)
    
    forecast = []
    for i in range(1, forecast_days + 1):
        forecast_date = last_date + timedelta(days=i)
        day_of_week = forecast_date.weekday()
        
        # Base prediction on day-of-week pattern
        base_prediction = day_patterns[day_of_week]['mean']
        
        # Apply trend
        prediction = base_prediction * trend_factor
        
        # Calculate confidence interval (95%)
        std = day_patterns[day_of_week]['std']
        lower_bound = max(0, prediction - 1.96 * std)
        upper_bound = prediction + 1.96 * std
        
        forecast.append({
            'date': forecast_date.isoformat(),
            'predicted_usage': round(prediction, 2),
            'lower_bound': round(lower_bound, 2),
            'upper_bound': round(upper_bound, 2),
            'confidence': 95
        })
    
    # Calculate forecast summary
    total_predicted = sum(f['predicted_usage'] for f in forecast)
    
    return {
        'forecast': forecast,
        'summary': {
            'total_predicted_usage': round(total_predicted, 2),
            'avg_daily_prediction': round(total_predicted / forecast_days, 2),
            'forecast_days': forecast_days,
            'trend_factor': round(trend_factor, 3),
            'trend_direction': 'increasing' if trend_factor > 1.05 else 'decreasing' if trend_factor < 0.95 else 'stable'
        },
        'historical_context': {
            'recent_30_day_avg': round(recent_avg, 2),
            'previous_30_day_avg': round(previous_avg, 2),
            'data_points_used': len(sorted_data)
        }
    }

def forecast_monthly_bill(customer_usage_data, month, year):
    """
    Forecast the bill amount for a future month
    
    Args:
        customer_usage_data (list): Historical usage data
        month (int): Target month (1-12)
        year (int): Target year
    
    Returns:
        dict: Forecasted bill information
    """
    from utils.billing_calculator import calculate_total_bill
    from calendar import monthrange
    
    # Get number of days in the target month
    days_in_month = monthrange(year, month)[1]
    
    # Forecast usage for the month
    forecast_result = forecast_usage(customer_usage_data, forecast_days=days_in_month)
    
    if 'error' in forecast_result:
        return forecast_result
    
    # Calculate total predicted usage
    total_usage = forecast_result['summary']['total_predicted_usage']
    
    # Calculate bill
    bill_data = calculate_total_bill(total_usage, month)
    
    # Add forecast context
    bill_data['forecast_info'] = {
        'month': month,
        'year': year,
        'days_in_month': days_in_month,
        'is_forecast': True,
        'confidence': 95,
        'trend': forecast_result['summary']['trend_direction']
    }
    
    return bill_data

def get_usage_insights(customer_usage_data):
    """
    Generate insights about usage patterns
    
    Args:
        customer_usage_data (list): Historical usage data
    
    Returns:
        dict: Usage insights and recommendations
    """
    if len(customer_usage_data) < 30:
        return {'error': 'Insufficient data for insights'}
    
    sorted_data = sorted(customer_usage_data, key=lambda x: x['date'])
    usage_values = [r['usage_ccf'] for r in sorted_data]
    
    # Day of week analysis
    day_of_week_usage = defaultdict(list)
    for record in sorted_data:
        date = record['date']
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        day_of_week = date.weekday()
        day_of_week_usage[day_of_week].append(record['usage_ccf'])
    
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_averages = {}
    for day in range(7):
        if day in day_of_week_usage and day_of_week_usage[day]:
            day_averages[day_names[day]] = round(np.mean(day_of_week_usage[day]), 2)
    
    # Find highest and lowest usage days
    if day_averages:
        highest_day = max(day_averages, key=day_averages.get)
        lowest_day = min(day_averages, key=day_averages.get)
    else:
        highest_day = lowest_day = 'Unknown'
    
    # Calculate variability
    std_dev = np.std(usage_values)
    mean_usage = np.mean(usage_values)
    coefficient_of_variation = (std_dev / mean_usage) * 100 if mean_usage > 0 else 0
    
    # Determine usage consistency
    if coefficient_of_variation < 20:
        consistency = 'Very Consistent'
    elif coefficient_of_variation < 40:
        consistency = 'Moderately Consistent'
    else:
        consistency = 'Highly Variable'
    
    return {
        'day_of_week_patterns': day_averages,
        'highest_usage_day': highest_day,
        'lowest_usage_day': lowest_day,
        'usage_consistency': consistency,
        'coefficient_of_variation': round(coefficient_of_variation, 1),
        'avg_daily_usage': round(mean_usage, 2),
        'recommendations': generate_recommendations(mean_usage, coefficient_of_variation)
    }

def generate_recommendations(avg_usage, variability):
    """Generate usage recommendations based on patterns"""
    recommendations = []
    
    if avg_usage > 0.5:
        recommendations.append("Your daily usage is above average. Consider checking for leaks or reducing shower times.")
    
    if variability > 50:
        recommendations.append("Your usage varies significantly. This could indicate irregular usage patterns or potential leaks.")
    
    if not recommendations:
        recommendations.append("Your usage patterns look normal. Keep up the water conservation efforts!")
    
    return recommendations

from typing import Dict, List, Tuple
from datetime import datetime, timedelta

# Airport information
AIRPORTS = {
    'ORD': {'name': "Chicago O'Hare International Airport", 'city': 'Chicago'},
    'MDW': {'name': 'Chicago Midway International Airport', 'city': 'Chicago'},
    'JFK': {'name': 'John F. Kennedy International Airport', 'city': 'New York'},
    'EWR': {'name': 'Newark Liberty International Airport', 'city': 'Newark'},
    'ISP': {'name': 'Long Island MacArthur Airport', 'city': 'Islip'}
}

ORIGIN_AIRPORTS = ['ORD', 'MDW']
DESTINATION_AIRPORTS = ['JFK', 'EWR', 'ISP']

def get_airport_pairs() -> List[Tuple[str, str]]:
    """Generate all possible origin-destination airport pairs."""
    pairs = []
    for origin in ORIGIN_AIRPORTS:
        for dest in DESTINATION_AIRPORTS:
            pairs.append((origin, dest))
    return pairs

def get_tomorrow_date() -> str:
    """Get tomorrow's date in YYYY-MM-DD format."""
    tomorrow = datetime.now() + timedelta(days=1)
    return tomorrow.strftime('%Y-%m-%d')

def format_price(price: str) -> float:
    """Convert price string to float."""
    try:
        return float(price.replace('$', '').replace(',', '').strip())
    except (ValueError, AttributeError):
        return float('inf')

def format_time(time_str: str) -> str:
    """Format time string to consistent format."""
    try:
        time_obj = datetime.strptime(time_str, '%I:%M %p')
        return time_obj.strftime('%H:%M')
    except ValueError:
        return time_str

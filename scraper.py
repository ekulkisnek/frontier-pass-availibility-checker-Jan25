import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, List
import time
from datetime import datetime
import random
from utils import format_price, format_time

class FrontierScraper:
    def __init__(self):
        self.base_url = "https://flights.flyfrontier.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()

    def _get_flight_data(self, origin: str, destination: str, date: str) -> List[Dict]:
        """
        Scrape flight data from Frontier Airlines website.
        Returns a list of dictionaries containing flight information.
        """
        flights = []
        try:
            # Construct search URL
            url = f"{self.base_url}/api/flights/search"
            params = {
                'origin': origin,
                'destination': destination,
                'date': date,
                'passengers': 1,
                'tripType': 'ONE_WAY'
            }
            
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Extract flight information
            for flight in data.get('flights', []):
                flight_info = {
                    'origin': origin,
                    'destination': destination,
                    'departure_time': format_time(flight.get('departureTime')),
                    'arrival_time': format_time(flight.get('arrivalTime')),
                    'price': format_price(flight.get('price', {}).get('amount')),
                    'available_seats': flight.get('availableSeats'),
                    'flight_number': flight.get('flightNumber')
                }
                flights.append(flight_info)
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            print(f"Error scraping {origin} to {destination}: {str(e)}")
            
        return flights

    def search_multiple_routes(self, routes: List[tuple], date: str) -> pd.DataFrame:
        """
        Search multiple routes and return results as a DataFrame.
        """
        all_flights = []
        
        for origin, destination in routes:
            flights = self._get_flight_data(origin, destination, date)
            all_flights.extend(flights)
        
        if not all_flights:
            return pd.DataFrame()
            
        df = pd.DataFrame(all_flights)
        df['search_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return df

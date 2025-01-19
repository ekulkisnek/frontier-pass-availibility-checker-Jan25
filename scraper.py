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
        self.base_url = "https://booking.flyfrontier.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()

    def _get_flight_data(self, origin: str, destination: str, date: str) -> List[Dict]:
        """
        Scrape flight data from Frontier Airlines website.
        Returns a list of dictionaries containing flight information.
        """
        flights = []
        try:
            # Construct search URL for the booking website
            url = f"{self.base_url}/Flight/Search"
            params = {
                'from': origin,
                'to': destination,
                'depart': date,
                'return': '',
                'adult': '1',
                'child': '0',
                'senior': '0',
                'infant': '0',
                'promo': '',
                'currency': 'USD'
            }

            # Add delay to avoid rate limiting
            time.sleep(random.uniform(2, 4))

            # Make the request
            response = self.session.get(url, params=params, headers=self.headers)
            response.raise_for_status()

            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find flight elements - updated selectors for Frontier's actual website structure
            flight_elements = soup.select('.flightItem')

            for flight in flight_elements:
                try:
                    # Extract flight information using proper selectors
                    price_element = flight.select_one('.fare-button__price')
                    departure_element = flight.select_one('.flight-time__departure')
                    arrival_element = flight.select_one('.flight-time__arrival')
                    flight_num_element = flight.select_one('.flight-details__number')

                    if not all([price_element, departure_element, arrival_element, flight_num_element]):
                        continue

                    flight_info = {
                        'origin': origin,
                        'destination': destination,
                        'departure_time': departure_element.text.strip(),
                        'arrival_time': arrival_element.text.strip(),
                        'price': format_price(price_element.text),
                        'flight_number': flight_num_element.text.strip()
                    }
                    flights.append(flight_info)
                except (AttributeError, ValueError) as e:
                    print(f"Error parsing flight element: {str(e)}")
                    continue

        except Exception as e:
            print(f"Error scraping {origin} to {destination}: {str(e)}")
            return []

        return flights

    def search_multiple_routes(self, routes: List[tuple], date: str) -> pd.DataFrame:
        """
        Search multiple routes and return results as a DataFrame.
        """
        all_flights = []

        for origin, destination in routes:
            flights = self._get_flight_data(origin, destination, date)
            if flights:  # Only add if we got real flight data
                all_flights.extend(flights)

        if not all_flights:
            return pd.DataFrame()

        df = pd.DataFrame(all_flights)
        df['search_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return df
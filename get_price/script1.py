from sqlalchemy.orm import sessionmaker
from db_schema import Price_1hr, engine
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('API_KEY')

API_ENDPOINT = "https://marketdata.tradermade.com/api/v1/timeseries?currency=XAUUSD&api_key="+str(api_key)+"&start_date=2024-10-01-00:00&end_date=2024-10-31-16:21&format=records&interval=hourly"

Session = sessionmaker(bind=engine)
session = Session()

def fetch_1hrprice():
    try:
        response = requests.get(API_ENDPOINT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def insert_data_to_db(data):
    try:
        quotes = data.get('quotes', [])

        for quote in quotes:
            datetime_obj = datetime.strptime(quote['date'], '%Y-%m-%d %H:%M:%S')
            time_only = datetime_obj.time() 
            prices = Price_1hr(
                time_in_ms=str(time_only),
                candle_start_price=quote["open"],
                candle_close_price=quote["close"],
                candle_max_price=quote["high"],
                candle_min_price=quote["low"]
            )
            session.add(prices)

        session.commit()
        print("Data inserted successfully!")

    except Exception as e:
        session.rollback()
        print(f"Error inserting data: {e}")
    finally:
        session.close()


if __name__ == "__main__":

    data = fetch_1hrprice()

    base_currency = data.get('base_currency')
    quote_currency = data.get('quote_currency')
    print(base_currency, quote_currency)

    start_date = data.get('start_date')
    end_date = data.get('end_date')
    print(f"start_date: {start_date}, end_date: {end_date}")

    req_time = data.get('request_time')
    print(req_time)
        
    if data:
        insert_data_to_db(data)

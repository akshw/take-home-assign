from sqlalchemy.orm import sessionmaker
from db_schema import Price_15min, engine
import requests
from datetime import datetime
import time
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('API_KEY')

Session = sessionmaker(bind=engine)
session = Session()

def fetch_date():
    try:
        response = requests.get('https://marketdata.tradermade.com/api/v1/timeseries?currency=XAUUSD&api_key='+str(api_key)+'&start_date=2024-11-01&end_date=2024-11-22&format=records')
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []


def pass_date(dates):
    all_data = []
    i = 0
    while i < len(dates):
        if i + 4 < len(dates):  
            startdate = dates[i]    
            enddate = dates[i + 4]
            print(f"Fetch req  {i//5 + 1}: {startdate} to {enddate}")
        else:
            start_date = dates[i]
            end_date = dates[-1]
            print(f"Fetch: {startdate} to {enddate}")
        
        data = fetch_15minprice(startdate, enddate)
        if data and 'quotes' in data:
            all_data.extend(data['quotes'])
            print(f"Received {len(data['quotes'])} quotes")

        i += 5

        time.sleep(1)

    if all_data:
        return {
        'quotes': all_data,
        'start_date': dates[0],
        'end_date': dates[-1],
        }
    return {}



def fetch_15minprice(startdate, enddate):
    try:
        response = requests.get('https://marketdata.tradermade.com/api/v1/timeseries?currency=XAUUSD&api_key='+str(api_key)+'&start_date='+str(startdate)+'-00:00&end_date='+str(enddate)+'-16:21&format=records&interval=minute&period=15')
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
            prices = Price_15min(
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
    date_response = fetch_date()
    dates = []

    quotes = date_response.get('quotes', [])

    for quote in quotes:
        datetime_obj = datetime.strptime(quote['date'], '%Y-%m-%d')
        date_only = datetime_obj.strftime('%Y-%m-%d')
        dates.append(date_only)
    
    print(dates)
    data = pass_date(dates)

    if data:

        start_date = data.get('start_date')
        end_date = data.get('end_date')
        print(f"start_date: {start_date}, end_date: {end_date}")

    quotes = data.get('quotes', [])

    if data:
        insert_data_to_db(data)

    

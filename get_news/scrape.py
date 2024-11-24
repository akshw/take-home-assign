from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import random
from sqlalchemy.orm import sessionmaker
from db_schema import News, engine
import pandas as pd


df = pd.DataFrame(columns=["news_time", "news_impact", "news_name"])

Session = sessionmaker(bind=engine)
session = Session()

def create_driver():
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
    ]
    user_agent = random.choice(user_agent_list)

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("window-size=1900,1080")
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f'user-agent={user_agent}')

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("WebDriver created successfully")
        return driver
    except Exception as e:
        print(f"Failed to create WebDriver: {str(e)}")
        raise


def parse_data(driver, url):

    global df

    try:
        driver.get(url)
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "calendar__table"))
        )

        rows = table.find_elements(By.XPATH, "//tr[not(@class='calendar__header--desktop') and not(@class='calendar__header--mobile') and not(@class='calendar__row--day-breaker')]")
        
        data = []
        for row in rows:
            try:
                title = row.find_element(By.CLASS_NAME, "calendar__event-title").text.strip()
                time = row.find_element(By.CLASS_NAME, "calendar__time").find_element(By.TAG_NAME, "span").text.strip()
                impact = row.find_element(By.CLASS_NAME, "calendar__impact").find_element(By.TAG_NAME, "span").get_attribute("title").replace(" Expected", "").strip()
                
                if title and time and impact:
                    data.append({
                        'time': time,
                        'impact': impact,
                        'title': title
                    })
                new_row = pd.DataFrame([[time, impact, title]], columns=df.columns)
                df = pd.concat([new_row, df], ignore_index=True)

            except NoSuchElementException:
                continue
            except Exception as e:
                continue
        
        df.to_csv("scraped_news.csv", index=False)    
        
        print("Successfully extracted events")
        return data

    except TimeoutException:
        print("Timeout waiting for calendar table to load")
    except Exception as e:
        print(f"Error parsing data: {str(e)}")
    finally:
        driver.quit()

def insert_data_to_db(extracted_data):
    try:
        for item in extracted_data:
            print(f"Time={item['time']}, Impact={item['impact']}, Title={item['title']}")
            news = News(
                time_of_news=item['time'],
                severity_of_news=item['impact'],
                name_of_news=item['title']
            )
            session.add(news)

        session.commit()
        print("Data inserted successfully!")

    except Exception as e:
        session.rollback()
        print(f"Error inserting data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    try:
        date = input("Enter date in this formate (nov23.2024): ")
        print(date)
        driver = create_driver()
        
        url = 'https://www.forexfactory.com/calendar?day='+str(date)
        
        extracted_data = parse_data(driver, url)

    except Exception as e:
        print(f"Script execution failed: {str(e)}")
        if 'driver' in locals():
            driver.quit()

    if extracted_data:
        insert_data_to_db(extracted_data)            
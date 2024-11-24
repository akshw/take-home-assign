from sqlalchemy import create_engine, Column, BigInteger, Float, String, Integer
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql+psycopg2://ak:ak@localhost:5433/price_db"

engine = create_engine(DATABASE_URL)

Base = declarative_base()

class XAUUSD_Price(Base):
    __abstract__ = True 

    id = Column(Integer, primary_key=True, autoincrement=True)
    time_in_ms = Column(String, nullable=False) 
    candle_start_price = Column(Float, nullable=False)
    candle_close_price = Column(Float, nullable=False)
    candle_max_price = Column(Float, nullable=False)
    candle_min_price = Column(Float, nullable=False)

class Price_1hr(XAUUSD_Price):
    __tablename__ = "XAUUSD_prices_1hr"

class Price_15min(XAUUSD_Price):
    __tablename__ = "XAUUSD_prices_15min"

def create_schema():
    Base.metadata.create_all(engine)
    print("Schema created successfully!")

if __name__ == "__main__":
    create_schema()

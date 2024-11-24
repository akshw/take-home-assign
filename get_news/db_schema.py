from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql+psycopg2://ak:ak@localhost:5434/news_db"

engine = create_engine(DATABASE_URL)

Base = declarative_base()

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time_of_news = Column(String, nullable=False) 
    severity_of_news = Column(String, nullable=False)
    name_of_news = Column(String, nullable=False)

    

def create_schema():
    Base.metadata.create_all(engine)
    print("Schema created successfully!")

if __name__ == "__main__":
    create_schema()

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class UserRating(Base):
    __tablename__ = "user_ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    movie_id = Column(Integer, index=True)
    rating = Column(Float, index=True)

# Create tables
Base.metadata.create_all(bind=engine)

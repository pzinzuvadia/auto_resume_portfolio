import os
from datetime import datetime
import ssl
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import QueuePool

# Get database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///portfolio_generator.db")

# For PostgreSQL, we need to ensure SSL is handled properly
connect_args = {}
if DATABASE_URL.startswith('postgresql'):
    # Configure SSL context for PostgreSQL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args = {
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        "sslmode": "require"
    }

# Create SQLAlchemy engine with connection pooling and retry settings
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800  # Recycle connections after 30 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """User model for storing user information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to portfolios
    portfolios = relationship("Portfolio", back_populates="user")

class Portfolio(Base):
    """Portfolio model for storing generated portfolios."""
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255))
    theme = Column(String(100))
    html_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_favorite = Column(Boolean, default=False)
    
    # Relationship to user
    user = relationship("User", back_populates="portfolios")
    
    # Relationship to resume
    resume = relationship("Resume", back_populates="portfolio", uselist=False)

class Resume(Base):
    """Resume model for storing uploaded resume information."""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    filename = Column(String(255))
    content_text = Column(Text)
    extracted_name = Column(String(255))
    extracted_email = Column(String(255))
    extracted_phone = Column(String(255))
    sections_json = Column(Text)  # JSON string of extracted sections
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to portfolio
    portfolio = relationship("Portfolio", back_populates="resume")

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
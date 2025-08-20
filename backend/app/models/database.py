from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./novels.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Novel(Base):
    __tablename__ = "novels"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    description = Column(Text)
    author = Column(String(200))
    status = Column(String(50), default="ongoing")  # ongoing, completed, paused
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    chapters = relationship("Chapter", back_populates="novel", cascade="all, delete-orphan")
    glossary_terms = relationship("GlossaryTerm", back_populates="novel", cascade="all, delete-orphan")

class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(500))
    url = Column(String(1000), unique=True, nullable=False)
    original_content = Column(Text, nullable=False)
    refined_content = Column(Text)
    is_processed = Column(Boolean, default=False)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    novel = relationship("Novel", back_populates="chapters")

class GlossaryTerm(Base):
    __tablename__ = "glossary_terms"
    
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    original_term = Column(String(200), nullable=False)
    preferred_term = Column(String(200), nullable=False)
    term_type = Column(String(50), nullable=False)  # character, place, skill, item, etc.
    context = Column(Text)  # Additional context for the term
    frequency = Column(Integer, default=1)  # How often this term appears
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    novel = relationship("Novel", back_populates="glossary_terms")

class ProcessingLog(Base):
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    processing_type = Column(String(50), nullable=False)  # extraction, refinement, manual_edit
    changes_made = Column(Text)  # JSON string of changes made
    processing_time = Column(Integer)  # Time taken in seconds
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime, default=func.now())

# Database initialization
async def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
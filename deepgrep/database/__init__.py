"""Database module with PostgreSQL support."""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class SearchHistory(Base):
    """Search history model."""
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    pattern = Column(String(500), nullable=False)
    search_type = Column(String(50), default="regex")  # regex or semantic
    matches_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    files = Column(Text)  # JSON string of file paths

    # Create index for faster queries
    __table_args__ = (
        Index('idx_pattern_timestamp', 'pattern', 'timestamp'),
        Index('idx_search_type_timestamp', 'search_type', 'timestamp'),
    )


class Document(Base):
    """Document storage model."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    title = Column(String(500))
    source = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(Text)  # JSON string of metadata

    __table_args__ = (
        Index('idx_title', 'title'),
        Index('idx_source', 'source'),
    )


class DatabaseManager:
    """Manager for database operations."""

    def __init__(self, database_url: str = None):
        """
        Initialize database connection.

        Args:
            database_url: PostgreSQL connection string
                         Format: postgresql://user:password@host:port/dbname
        """
        if database_url is None:
            database_url = os.getenv(
                "DATABASE_URL",
                "sqlite:///./deepgrep.db"  # Fallback to SQLite
            )

        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()

    def add_search_history(self, pattern: str, matches_count: int, search_type: str = "regex", files: list = None):
        """Add a search history entry."""
        session = self.get_session()
        try:
            import json
            entry = SearchHistory(
                pattern=pattern,
                search_type=search_type,
                matches_count=matches_count,
                files=json.dumps(files) if files else "[]"
            )
            session.add(entry)
            session.commit()
            return entry.id
        finally:
            session.close()

    def get_search_history(self, limit: int = 50, search_type: str = None):
        """Get search history entries."""
        session = self.get_session()
        try:
            query = session.query(SearchHistory)
            if search_type:
                query = query.filter(SearchHistory.search_type == search_type)
            query = query.order_by(SearchHistory.timestamp.desc())
            query = query.limit(limit)
            return query.all()
        finally:
            session.close()

    def add_document(self, content: str, title: str = None, source: str = None, metadata: dict = None):
        """Add a document."""
        session = self.get_session()
        try:
            import json
            doc = Document(
                content=content,
                title=title,
                source=source,
                metadata=json.dumps(metadata) if metadata else "{}"
            )
            session.add(doc)
            session.commit()
            return doc.id
        finally:
            session.close()

    def get_documents(self, limit: int = 100, offset: int = 0):
        """Get documents with pagination."""
        session = self.get_session()
        try:
            query = session.query(Document)
            query = query.order_by(Document.created_at.desc())
            query = query.offset(offset).limit(limit)
            return query.all()
        finally:
            session.close()

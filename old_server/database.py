from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base, relationship
from datetime import datetime

# Configuration
DATABASE_URL = "mysql+pymysql://dylanteehan:Metrics.123@dylanteehan.mysql.pythonanywhere-services.com/dylanteehan$MetricsDB"

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

# Models
class Monitor(Base):
    __tablename__ = 'monitors'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)  # This will store the monitor type (System, BTC, XRP, etc)
    metric_types = relationship("MetricType", back_populates="monitor", cascade="all, delete-orphan")

class MetricType(Base):
    __tablename__ = 'metric_types'

    id = Column(Integer, primary_key=True)
    monitor_id = Column(Integer, ForeignKey('monitors.id'), nullable=False)
    name = Column(String(255), nullable=False)
    unit = Column(String(50))
    monitor = relationship("Monitor", back_populates="metric_types")
    metric_values = relationship("MetricValue", back_populates="metric_type", cascade="all, delete-orphan")

class MetricValue(Base):
    __tablename__ = 'metric_values'

    id = Column(Integer, primary_key=True)
    metric_type_id = Column(Integer, ForeignKey('metric_types.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    value = Column(Float, nullable=False)
    metric_type = relationship("MetricType", back_populates="metric_values")

# Create tables
# Base.metadata.create_all(bind=engine)
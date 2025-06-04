from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class BruteforceTask(Base):
    __tablename__ = "bruteforce_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True, nullable=False)
    hash_type = Column(String, nullable=False)
    target_hash = Column(String, nullable=False)
    charset = Column(String, nullable=False)
    max_length = Column(Integer, nullable=False)
    status = Column(String, default="PENDING")
    result = Column(String, nullable=True)
    progress = Column(Integer, default=0)
    current_combination = Column(String, nullable=True)
    combinations_per_second = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    elapsed_time = Column(String, nullable=True)
    user_id = Column(String, nullable=True)  # Для аутентификации 
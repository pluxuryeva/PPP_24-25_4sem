from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BruteforceRequest(BaseModel):
    hash_type: str = "md5"  # md5, sha1, sha256, rar, zip
    target_hash: str
    charset: Optional[str] = None
    max_length: int = 6
    task_id: Optional[str] = None  # Опциональный ID для WebSocket совместимости


class BruteforceResponse(BaseModel):
    task_id: str
    message: str


class TaskStatus(BaseModel):
    task_id: str
    status: str
    hash_type: str
    progress: int
    current_combination: Optional[str] = None
    combinations_per_second: int
    result: Optional[str] = None
    elapsed_time: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class WebSocketMessage(BaseModel):
    status: str
    task_id: str
    hash_type: Optional[str] = None
    charset_length: Optional[int] = None
    max_length: Optional[int] = None
    progress: Optional[int] = None
    current_combination: Optional[str] = None
    combinations_per_second: Optional[int] = None
    result: Optional[str] = None
    elapsed_time: Optional[str] = None 
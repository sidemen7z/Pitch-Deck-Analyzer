from beanie import Document as BeanieDocument, init_beanie
from pydantic import Field
from typing import Optional, Dict
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

from app.config import settings


class Document(BeanieDocument):
    """Documents collection"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    file_size_bytes: int
    file_type: str
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_status: str
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    overall_confidence: Optional[float] = None
    
    class Settings:
        name = "documents"


class ExtractedData(BeanieDocument):
    """Extracted data collection"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    data_json: Dict
    schema_version: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "extracted_data"


class ProcessingAudit(BeanieDocument):
    """Processing audit log collection"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    stage: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: str
    error_details: Optional[str] = None
    metadata: Optional[Dict] = None
    
    class Settings:
        name = "processing_audit"


# MongoDB client
client: Optional[AsyncIOMotorClient] = None


async def init_db():
    """Initialize MongoDB connection and Beanie"""
    global client
    client = AsyncIOMotorClient(settings.mongodb_url)
    
    await init_beanie(
        database=client.get_default_database(),
        document_models=[Document, ExtractedData, ProcessingAudit]
    )


async def close_db():
    """Close MongoDB connection"""
    if client:
        client.close()

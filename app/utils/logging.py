import logging
from datetime import datetime
from typing import Optional, Dict

from app.config import settings
from app.models.database import ProcessingAudit

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class AuditLogger:
    """Audit logger for processing operations"""
    
    @staticmethod
    async def log_operation(
        document_id: str,
        stage: str,
        status: str,
        error_details: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Log a processing operation to the audit collection"""
        try:
            audit_entry = ProcessingAudit(
                document_id=document_id,
                stage=stage,
                started_at=datetime.utcnow(),
                status=status,
                error_details=error_details,
                metadata=metadata
            )
            await audit_entry.insert()
            logger.info(f"Audit log: {stage} - {status} for document {document_id}")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    @staticmethod
    async def log_start(document_id: str, stage: str, metadata: Optional[Dict] = None):
        """Log the start of a processing stage"""
        await AuditLogger.log_operation(document_id, stage, "started", metadata=metadata)
    
    @staticmethod
    async def log_complete(document_id: str, stage: str, metadata: Optional[Dict] = None):
        """Log the completion of a processing stage"""
        await AuditLogger.log_operation(document_id, stage, "completed", metadata=metadata)
    
    @staticmethod
    async def log_error(document_id: str, stage: str, error: str, metadata: Optional[Dict] = None):
        """Log an error in a processing stage"""
        await AuditLogger.log_operation(document_id, stage, "failed", error_details=error, metadata=metadata)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)

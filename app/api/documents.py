from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List
import uuid
import os
import aiofiles

from app.services.document_parser import DocumentParser
from app.services.processor import DocumentProcessor
from app.models.database import Document as DBDocument, ExtractedData
from app.models.schemas import ProcessingStatus
from app.utils.logging import AuditLogger, get_logger
from app.config import settings

router = APIRouter(prefix="/api/documents", tags=["documents"])
logger = get_logger(__name__)


@router.post("/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload a pitch deck for processing"""
    try:
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file
        is_valid, error_msg = DocumentParser.validate_file(file.filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Save file to disk
        file_path = os.path.join(settings.upload_dir, f"{document_id}_{file.filename}")
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Save to database
        db_doc = DBDocument(
            id=document_id,
            filename=file.filename,
            file_size_bytes=file_size,
            file_type=os.path.splitext(file.filename)[1].lower().replace('.', ''),
            processing_status=ProcessingStatus.QUEUED.value
        )
        await db_doc.insert()
        
        # Log audit
        await AuditLogger.log_start(document_id, "upload", {
            "filename": file.filename,
            "size": file_size
        })
        
        # Start background processing
        background_tasks.add_task(DocumentProcessor.process_document, document_id, file_path)
        
        logger.info(f"Document uploaded: {document_id}")
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "status": ProcessingStatus.QUEUED.value,
            "message": "Document uploaded successfully and queued for processing"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_documents():
    """List all documents"""
    try:
        documents = await DBDocument.find_all().to_list()
        return {
            "documents": [
                {
                    "document_id": doc.id,
                    "filename": doc.filename,
                    "upload_date": doc.upload_timestamp.isoformat(),
                    "status": doc.processing_status,
                    "confidence": doc.overall_confidence
                }
                for doc in documents
            ]
        }
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}")
async def get_document(document_id: str):
    """Get document details"""
    try:
        doc = await DBDocument.find_one(DBDocument.id == document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get extracted data if available
        extracted_data = None
        if doc.processing_status == ProcessingStatus.COMPLETED.value:
            data = await ExtractedData.find_one(ExtractedData.document_id == document_id)
            if data:
                extracted_data = data.data_json
        
        return {
            "document_id": doc.id,
            "filename": doc.filename,
            "upload_date": doc.upload_timestamp.isoformat(),
            "status": doc.processing_status,
            "confidence": doc.overall_confidence,
            "error": doc.error_message,
            "extracted_data": extracted_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

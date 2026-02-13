from app.models.database import Document as DBDocument, ExtractedData
from app.models.schemas import ProcessingStatus
from app.services.document_parser import DocumentParser
from app.services.content_classifier import ContentClassifier
from app.services.information_extractor import InformationExtractor
from app.utils.logging import AuditLogger, get_logger
from app.config import settings
import os

logger = get_logger(__name__)


class DocumentProcessor:
    """Process pitch deck documents through the pipeline"""
    
    @staticmethod
    async def process_document(document_id: str, file_path: str):
        """Process a document through the complete pipeline"""
        try:
            # Update status to processing
            doc = await DBDocument.find_one(DBDocument.id == document_id)
            if not doc:
                logger.error(f"Document {document_id} not found")
                return
            
            doc.processing_status = ProcessingStatus.PROCESSING.value
            await doc.save()
            await AuditLogger.log_start(document_id, "processing")
            
            # Step 1: Parse document
            logger.info(f"Parsing document {document_id}")
            with open(file_path, 'rb') as f:
                content = f.read()
            
            parsed_doc = await DocumentParser.parse(content, doc.filename)
            await AuditLogger.log_complete(document_id, "parsing")
            
            # Step 2: Classify content
            logger.info(f"Classifying document {document_id}")
            classified_doc = await ContentClassifier.classify(parsed_doc)
            await AuditLogger.log_complete(document_id, "classification")
            
            # Step 3: Extract information
            logger.info(f"Extracting information from {document_id}")
            extracted_info = await InformationExtractor.extract(classified_doc)
            await AuditLogger.log_complete(document_id, "extraction")
            
            # Step 4: Calculate overall confidence
            confidence_scores = []
            if extracted_info.company.confidence:
                confidence_scores.extend(extracted_info.company.confidence.values())
            if extracted_info.financials.confidence:
                confidence_scores.extend(extracted_info.financials.confidence.values())
            if extracted_info.market.confidence:
                confidence_scores.extend(extracted_info.market.confidence.values())
            
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
            
            # Step 5: Save extracted data
            extracted_data = ExtractedData(
                document_id=document_id,
                data_json=extracted_info.dict(),
                schema_version=settings.system_version
            )
            await extracted_data.insert()
            
            # Step 6: Update document status
            doc.processing_status = ProcessingStatus.COMPLETED.value
            doc.overall_confidence = overall_confidence
            await doc.save()
            
            await AuditLogger.log_complete(document_id, "processing", {
                "confidence": overall_confidence
            })
            
            logger.info(f"Document {document_id} processed successfully")
            
        except Exception as e:
            logger.error(f"Processing error for {document_id}: {e}")
            
            # Update document status to failed
            doc = await DBDocument.find_one(DBDocument.id == document_id)
            if doc:
                doc.processing_status = ProcessingStatus.FAILED.value
                doc.error_message = str(e)
                await doc.save()
            
            await AuditLogger.log_error(document_id, "processing", str(e))

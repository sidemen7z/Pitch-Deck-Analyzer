"""
Enhanced Document Processor - Complete Pipeline
Implements the 7-phase accuracy-first architecture
"""
from app.models.database import Document as DBDocument, ExtractedData
from app.models.schemas import ProcessingStatus
from app.services.enhanced_parser import EnhancedDocumentParser
from app.services.enhanced_classifier import EnhancedContentClassifier
from app.services.enhanced_extractor import EnhancedInformationExtractor
from app.services.investment_analyzer import InvestmentAnalyzer
from app.utils.logging import AuditLogger, get_logger
from app.config import settings

logger = get_logger(__name__)


class EnhancedDocumentProcessor:
    """Production-grade document processor with full pipeline"""
    
    @staticmethod
    async def process_document(document_id: str, file_path: str):
        """Process document through the complete 7-phase pipeline"""
        try:
            # Update status
            doc = await DBDocument.find_one(DBDocument.id == document_id)
            if not doc:
                logger.error(f"Document {document_id} not found")
                return
            
            doc.processing_status = ProcessingStatus.PROCESSING.value
            await doc.save()
            await AuditLogger.log_start(document_id, "enhanced_processing")
            
            # PHASE 1: Document Ingestion & Extraction
            logger.info(f"[Phase 1] Parsing document {document_id}")
            with open(file_path, 'rb') as f:
                content = f.read()
            
            parsed_doc = await EnhancedDocumentParser.parse(content, doc.filename)
            await AuditLogger.log_complete(document_id, "phase1_parsing", {
                "method": parsed_doc["extraction_method"],
                "slides": parsed_doc["total_slides"]
            })
            
            # PHASE 4: Section Classification & Labeling
            logger.info(f"[Phase 4] Classifying sections for {document_id}")
            classified_doc = await EnhancedContentClassifier.classify_slides(parsed_doc)
            await AuditLogger.log_complete(document_id, "phase4_classification", {
                "sections_found": len([s for s in classified_doc.get("section_map", {}).values() if s])
            })
            
            # PHASE 5: Field-Level Structured Extraction
            logger.info(f"[Phase 5] Extracting structured data from {document_id}")
            extracted_info = await EnhancedInformationExtractor.extract_structured_data(
                parsed_doc, classified_doc
            )
            await AuditLogger.log_complete(document_id, "phase5_extraction", {
                "confidence": extracted_info["overall_confidence"]
            })
            
            # PHASE 6: Investment Signals & Insight Generation
            logger.info(f"[Phase 6] Analyzing investment potential for {document_id}")
            investment_analysis = await InvestmentAnalyzer.analyze_investment_potential(
                extracted_info
            )
            await AuditLogger.log_complete(document_id, "phase6_analysis")
            
            # Combine all results
            final_output = {
                "document_metadata": {
                    "document_id": document_id,
                    "filename": doc.filename,
                    "total_slides": parsed_doc["total_slides"],
                    "extraction_method": parsed_doc["extraction_method"]
                },
                "classification": classified_doc,
                "extracted_data": extracted_info["extracted_data"],
                "investment_analysis": investment_analysis["analysis"],
                "confidence": {
                    "overall": extracted_info["overall_confidence"],
                    "extraction_timestamp": extracted_info["extraction_timestamp"]
                }
            }
            
            # Save to database
            extracted_data = ExtractedData(
                document_id=document_id,
                data_json=final_output,
                schema_version=settings.system_version
            )
            await extracted_data.insert()
            
            # Update document status
            doc.processing_status = ProcessingStatus.COMPLETED.value
            doc.overall_confidence = extracted_info["overall_confidence"]
            await doc.save()
            
            await AuditLogger.log_complete(document_id, "enhanced_processing", {
                "confidence": extracted_info["overall_confidence"],
                "phases_completed": 6
            })
            
            logger.info(f"✅ Document {document_id} processed successfully with enhanced pipeline")
            
        except Exception as e:
            logger.error(f"Enhanced processing error for {document_id}: {e}")
            
            # Update document status to failed
            doc = await DBDocument.find_one(DBDocument.id == document_id)
            if doc:
                doc.processing_status = ProcessingStatus.FAILED.value
                doc.error_message = str(e)
                await doc.save()
            
            await AuditLogger.log_error(document_id, "enhanced_processing", str(e))

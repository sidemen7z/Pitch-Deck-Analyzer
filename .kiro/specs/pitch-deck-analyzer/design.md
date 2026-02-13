# Design Document: Pitch Deck Analyzer

## Overview

The Pitch Deck Analyzer is an AI-powered NLP system that processes startup pitch decks (PDF/PPT) and extracts structured investment information. The system uses a pipeline architecture with specialized components for document parsing, content classification, information extraction, summarization, and confidence scoring. The extracted data is presented through a web-based dashboard for visualization and analysis.

### Key Design Decisions

1. **Pipeline Architecture**: Sequential processing stages allow for modular development and testing of each component
2. **Confidence Scoring Throughout**: Every extraction step produces confidence scores to enable data quality assessment
3. **Schema-Driven Extraction**: Predefined JSON schema ensures consistent output structure across all documents
4. **Async Processing**: Document processing runs asynchronously to handle multiple uploads and long-running operations
5. **LLM-Based Extraction**: Use large language models (GPT-4, Claude) for content understanding and extraction rather than rule-based systems

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Dashboard (Web UI)                    │
│  - Upload Interface  - Visualization  - Comparison Views    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                       │
│  - Request Validation  - Rate Limiting  - Response Formatting│
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Processing Pipeline                        │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Document   │───▶│   Content    │───▶│ Information  │ │
│  │    Parser    │    │  Classifier  │    │  Extractor   │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                    │                    │         │
│         ▼                    ▼                    ▼         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │  Confidence  │    │ Summarizer   │    │   Structured │ │
│  │   Scorer     │    │              │    │    Output    │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Storage Layer                      │
│  - Document Store  - Metadata DB  - Processing Queue        │
└─────────────────────────────────────────────────────────────┘
```

### Processing Flow

1. **Upload**: User uploads PDF/PPT through dashboard
2. **Validation**: API validates file format, size, and integrity
3. **Queue**: Document added to processing queue with unique ID
4. **Parse**: Document Parser extracts text, images, and structure
5. **Classify**: Content Classifier identifies pitch deck sections
6. **Extract**: Information Extractor pulls key investment data
7. **Summarize**: Summarizer generates executive and section summaries
8. **Score**: Confidence Scorer assigns confidence levels to all extractions
9. **Format**: Structured Output Generator creates JSON and CSV outputs
10. **Store**: Results saved to database with metadata
11. **Display**: Dashboard retrieves and visualizes results

## Components and Interfaces

### 1. Document Parser

**Purpose**: Extract raw content from PDF and PowerPoint files

**Interface**:
```typescript
interface DocumentParser {
  parse(file: File): Promise<ParsedDocument>
  validateFile(file: File): ValidationResult
}

interface ParsedDocument {
  documentId: string
  pages: Page[]
  metadata: DocumentMetadata
  rawText: string
}

interface Page {
  pageNumber: number
  text: string
  images: Image[]
  layout: LayoutInfo
}
```

**Implementation Approach**:
- Use `pdf-parse` or `pdfjs` for PDF extraction
- Use `officegen` or `python-pptx` for PowerPoint extraction
- Extract text with positional information to preserve structure
- Extract images with OCR capability for text in images (using Tesseract)
- Preserve slide/page ordering and hierarchy

### 2. Content Classifier

**Purpose**: Identify and categorize pitch deck sections

**Interface**:
```typescript
interface ContentClassifier {
  classify(document: ParsedDocument): Promise<ClassifiedDocument>
}

interface ClassifiedDocument {
  documentId: string
  sections: ClassifiedSection[]
  overallConfidence: number
}

interface ClassifiedSection {
  sectionType: SectionType
  pageNumbers: number[]
  content: string
  confidence: number
}

enum SectionType {
  PROBLEM = "problem",
  SOLUTION = "solution",
  MARKET = "market",
  BUSINESS_MODEL = "business_model",
  TEAM = "team",
  TRACTION = "traction",
  FINANCIALS = "financials",
  COMPETITION = "competition",
  ASK = "ask",
  UNCLASSIFIED = "unclassified"
}
```

**Implementation Approach**:
- Use LLM (GPT-4 or Claude) with few-shot prompting to classify sections
- Provide examples of each section type in the prompt
- Use sliding window approach for long documents
- Aggregate classification results with confidence scores
- Handle multi-page sections by grouping consecutive pages with same classification

### 3. Information Extractor

**Purpose**: Extract structured investment data from classified sections

**Interface**:
```typescript
interface InformationExtractor {
  extract(classifiedDoc: ClassifiedDocument): Promise<ExtractedInformation>
}

interface ExtractedInformation {
  documentId: string
  company: CompanyInfo
  team: TeamInfo[]
  financials: FinancialInfo
  market: MarketInfo
  traction: TractionInfo
  ask: FundingAsk
  extractionTimestamp: string
}

interface CompanyInfo {
  name: string | null
  foundingDate: string | null  // ISO 8601
  location: string | null
  industry: string | null
  confidence: FieldConfidence
}

interface FieldConfidence {
  [fieldName: string]: number  // 0-1 confidence per field
}
```

**Implementation Approach**:
- Use structured output from LLM (JSON mode in GPT-4 or Claude)
- Define extraction schema with all expected fields
- Use section-specific prompts for targeted extraction
- Implement field-level confidence scoring based on:
  - LLM's stated confidence
  - Presence of supporting context
  - Consistency across multiple mentions
- Normalize extracted data (dates to ISO 8601, currencies with symbols)

### 4. Summarizer

**Purpose**: Generate concise summaries of pitch deck content

**Interface**:
```typescript
interface Summarizer {
  generateExecutiveSummary(extractedInfo: ExtractedInformation, 
                          classifiedDoc: ClassifiedDocument): Promise<Summary>
  generateSectionSummaries(classifiedDoc: ClassifiedDocument): Promise<SectionSummary[]>
}

interface Summary {
  executiveSummary: string  // Max 200 words
  keyHighlights: string[]
  confidence: number
}

interface SectionSummary {
  sectionType: SectionType
  summary: string
  confidence: number
}
```

**Implementation Approach**:
- Use LLM with specific word count constraints
- For executive summary: prioritize problem, solution, market size, traction, ask
- For section summaries: extract 2-3 key points per section
- Preserve numerical data exactly as extracted
- Calculate confidence based on source data quality

### 5. Confidence Scorer

**Purpose**: Assign confidence levels to all extracted information

**Interface**:
```typescript
interface ConfidenceScorer {
  scoreExtraction(extractedInfo: ExtractedInformation, 
                  source: ClassifiedDocument): ScoredInformation
  calculateOverallConfidence(scores: FieldConfidence[]): number
}

interface ScoredInformation extends ExtractedInformation {
  overallConfidence: number
  confidenceBreakdown: ConfidenceBreakdown
}

interface ConfidenceBreakdown {
  highConfidence: string[]    // Fields with score > 0.8
  mediumConfidence: string[]  // Fields with score 0.5-0.8
  lowConfidence: string[]     // Fields with score < 0.5
}
```

**Implementation Approach**:
- Aggregate confidence from multiple sources:
  - LLM-provided confidence scores
  - Classification confidence of source section
  - Presence of multiple supporting data points
  - Consistency of extracted values
- Weight overall confidence by importance of fields
- Flag low-confidence extractions for manual review

### 6. Structured Output Generator

**Purpose**: Format extracted data into JSON and CSV

**Interface**:
```typescript
interface StructuredOutputGenerator {
  generateJSON(scoredInfo: ScoredInformation): Promise<JSONOutput>
  generateCSV(scoredInfo: ScoredInformation): Promise<CSVOutput>
  validateOutput(output: JSONOutput): ValidationResult
}

interface JSONOutput {
  schema_version: string
  document_id: string
  processing_timestamp: string
  data: ExtractedInformation
  metadata: ProcessingMetadata
}

interface CSVOutput {
  headers: string[]
  rows: string[][]
}
```

**JSON Schema**:
```json
{
  "schema_version": "1.0.0",
  "document_id": "string",
  "processing_timestamp": "ISO 8601 datetime",
  "data": {
    "company": {
      "name": "string | null",
      "founding_date": "YYYY-MM-DD | null",
      "location": "string | null",
      "industry": "string | null"
    },
    "team": [
      {
        "name": "string",
        "title": "string",
        "background": "string",
        "confidence": "number"
      }
    ],
    "financials": {
      "revenue": "number | null",
      "currency": "string",
      "burn_rate": "number | null",
      "runway_months": "number | null",
      "funding_raised": "number | null",
      "confidence": "object"
    },
    "market": {
      "market_size": "number | null",
      "target_customer": "string | null",
      "growth_rate": "number | null",
      "confidence": "object"
    },
    "traction": {
      "user_count": "number | null",
      "growth_rate": "number | null",
      "key_milestones": ["string"],
      "confidence": "object"
    },
    "ask": {
      "amount": "number | null",
      "currency": "string",
      "use_of_funds": "string | null",
      "confidence": "object"
    }
  },
  "summaries": {
    "executive": "string",
    "sections": "object"
  },
  "confidence": {
    "overall": "number",
    "breakdown": "object"
  },
  "metadata": {
    "system_version": "string",
    "processing_time_seconds": "number",
    "file_size_bytes": "number"
  }
}
```

**CSV Format**:
- One row per document with flattened key metrics
- Consistent column headers: `document_id, company_name, industry, founding_date, revenue, market_size, user_count, funding_ask, overall_confidence`
- Nested objects flattened with dot notation

**Implementation Approach**:
- Validate JSON against schema before returning
- Handle null values consistently in both formats
- Include confidence scores in both outputs
- Add metadata for traceability

### 7. Dashboard

**Purpose**: Web interface for visualization and analysis

**Interface**:
```typescript
interface Dashboard {
  uploadDocument(file: File): Promise<UploadResponse>
  getDocumentList(filters: FilterOptions): Promise<DocumentSummary[]>
  getDocumentDetails(documentId: string): Promise<DocumentDetails>
  compareDocuments(documentIds: string[]): Promise<ComparisonView>
  exportData(documentId: string, format: ExportFormat): Promise<Blob>
}

interface FilterOptions {
  industry?: string[]
  fundingStage?: string[]
  minConfidence?: number
  dateRange?: DateRange
}

interface DocumentSummary {
  documentId: string
  companyName: string
  industry: string
  uploadDate: string
  overallConfidence: number
  processingStatus: ProcessingStatus
}

enum ProcessingStatus {
  QUEUED = "queued",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed"
}
```

**UI Components**:
1. **Upload Page**: Drag-and-drop file upload with progress indicator
2. **Document List**: Sortable/filterable table of processed documents
3. **Document Detail View**: 
   - Executive summary at top
   - Tabbed sections for each category
   - Confidence indicators (color-coded: green >0.8, yellow 0.5-0.8, red <0.5)
   - Raw section text expandable
4. **Comparison View**: Side-by-side comparison of 2-4 documents
5. **Export Options**: Download JSON or CSV

**Implementation Approach**:
- Use React or Vue.js for frontend
- Use REST API for backend communication
- Implement real-time status updates via WebSocket or polling
- Use charts (Chart.js or D3.js) for metric visualization
- Implement responsive design for mobile access

## Data Models

### Database Schema

**Documents Table**:
```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  filename VARCHAR(255) NOT NULL,
  file_size_bytes INTEGER NOT NULL,
  file_type VARCHAR(10) NOT NULL,
  upload_timestamp TIMESTAMP NOT NULL,
  processing_status VARCHAR(20) NOT NULL,
  processing_started_at TIMESTAMP,
  processing_completed_at TIMESTAMP,
  error_message TEXT,
  overall_confidence DECIMAL(3,2)
);
```

**Extracted Data Table**:
```sql
CREATE TABLE extracted_data (
  id UUID PRIMARY KEY,
  document_id UUID REFERENCES documents(id),
  data_json JSONB NOT NULL,
  schema_version VARCHAR(10) NOT NULL,
  created_at TIMESTAMP NOT NULL
);
```

**Processing Audit Log**:
```sql
CREATE TABLE processing_audit (
  id UUID PRIMARY KEY,
  document_id UUID REFERENCES documents(id),
  stage VARCHAR(50) NOT NULL,
  started_at TIMESTAMP NOT NULL,
  completed_at TIMESTAMP,
  status VARCHAR(20) NOT NULL,
  error_details TEXT,
  metadata JSONB
);
```

### File Storage

- **Raw Documents**: Store uploaded files in object storage (S3, Azure Blob)
- **Processed Outputs**: Store JSON/CSV outputs in object storage
- **Retention Policy**: Keep raw files for 90 days, processed outputs indefinitely

## Error Handling

### Error Categories

1. **Validation Errors** (4xx):
   - Invalid file format
   - File too large
   - Corrupted file
   - Missing required parameters

2. **Processing Errors** (5xx):
   - Document parsing failure
   - LLM API timeout or failure
   - Database connection error
   - Insufficient system resources

3. **Partial Success**:
   - Classification succeeds but extraction fails
   - Some fields extracted, others missing
   - Low confidence across all extractions

### Error Handling Strategy

```typescript
interface ErrorResponse {
  error: {
    code: string
    message: string
    details?: any
    retryable: boolean
  }
  partialResults?: any
}
```

**Handling Approach**:
- Return descriptive error messages to users
- Log detailed error information for debugging
- For partial failures, return available results with warnings
- Implement retry logic for transient failures (LLM timeouts)
- Provide fallback to raw text extraction if classification fails

### Validation Rules

1. **File Upload**:
   - Max size: 50MB
   - Allowed formats: PDF, PPT, PPTX
   - File integrity check (not corrupted)

2. **JSON Output**:
   - Validate against schema before saving
   - Ensure all required fields present (even if null)
   - Confidence scores in range [0, 1]

3. **Data Extraction**:
   - Dates in ISO 8601 format
   - Numerical values are valid numbers
   - Currency codes are valid ISO 4217 codes

## Testing Strategy

### Unit Testing

- Test each component independently with mock inputs
- Test error handling for each component
- Test data validation and normalization functions
- Test confidence scoring calculations
- Test JSON schema validation
- Test CSV generation with various data combinations

### Integration Testing

- Test complete pipeline with sample pitch decks
- Test API endpoints with various request types
- Test database operations (CRUD)
- Test file upload and storage
- Test dashboard UI interactions

### Property-Based Testing

Property-based tests will validate universal correctness properties across randomized inputs. Each test will run a minimum of 100 iterations and reference the corresponding design property.

**Test Configuration**:
- Use `fast-check` (JavaScript/TypeScript) or `Hypothesis` (Python)
- Minimum 100 iterations per property test
- Tag format: `Feature: pitch-deck-analyzer, Property {N}: {property_text}`

**Coverage**:
- Properties will be derived from acceptance criteria in the requirements
- Focus on data consistency, format validation, and confidence scoring
- Test with generated documents, extracted data, and edge cases



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Document Upload Returns Unique Identifiers

*For any* valid document upload (PDF or PPT under 50MB), the system should return a unique document identifier, and no two uploads should receive the same identifier.

**Validates: Requirements 1.5**

### Property 2: Unclassified Sections Have Low Confidence

*For any* classified document, all sections labeled as "unclassified" should have a confidence score below 0.6.

**Validates: Requirements 2.2**

### Property 3: Duplicate Section Types Are Numbered Sequentially

*For any* classified document with multiple sections of the same type, the sections should be numbered sequentially starting from 1.

**Validates: Requirements 2.3**

### Property 4: Confidence Scores Are Within Valid Range

*For any* extracted data point or classified section, the confidence score should be a number between 0 and 1 (inclusive).

**Validates: Requirements 2.4, 5.1**

### Property 5: Extracted Information Contains Required Fields

*For any* processed pitch deck, the extracted information output should contain all required field structures (company, team, financials, market, traction, ask) even if individual field values are null.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

### Property 6: Missing Data Is Represented As Null

*For any* extracted information field that cannot be found in the source document, the field value should be null (not undefined, not missing from output).

**Validates: Requirements 3.7**

### Property 7: Executive Summary Word Count Constraint

*For any* processed pitch deck, the generated executive summary should contain no more than 200 words.

**Validates: Requirements 4.1**

### Property 8: Section Summaries Match Classified Sections

*For any* processed pitch deck, the number of section summaries generated should equal the number of classified sections in the document.

**Validates: Requirements 4.2**

### Property 9: Numerical Data Preservation In Summaries

*For any* numerical value mentioned in a summary, that value should match exactly with the corresponding value in the extracted data (no rounding or modification).

**Validates: Requirements 4.4**

### Property 10: Confidence Flags Match Score Ranges

*For any* extracted data point, the confidence flag should correctly correspond to its score: "low confidence" for scores < 0.5, "medium confidence" for scores 0.5-0.8, and "high confidence" for scores > 0.8.

**Validates: Requirements 5.2, 5.3, 5.4**

### Property 11: Overall Confidence Is Weighted Average

*For any* processed document, the overall confidence score should equal the weighted average of all individual data point confidence scores.

**Validates: Requirements 5.5**

### Property 12: JSON Output Validates Against Schema

*For any* generated JSON output, the output should pass validation against the predefined JSON schema without errors.

**Validates: Requirements 6.1, 6.4**

### Property 13: CSV Output Has Consistent Headers

*For any* two CSV outputs generated by the system, they should have identical column headers in the same order.

**Validates: Requirements 6.5**

### Property 14: Output Contains Required Metadata

*For any* generated output (JSON or CSV), it should contain all required metadata fields: document_id, processing_timestamp, and system_version.

**Validates: Requirements 6.3**

### Property 15: Dashboard Filtering Returns Matching Documents Only

*For any* filter criteria applied on the dashboard (industry, funding stage, confidence level), all returned documents should match the specified criteria.

**Validates: Requirements 7.5**

### Property 16: Export Produces Valid Format

*For any* export operation from the dashboard, the exported file should be valid JSON or CSV that can be parsed without errors.

**Validates: Requirements 7.7**

### Property 17: Parsing Failures Return Error Messages

*For any* document that fails to parse, the system should return an error response with a descriptive message (not crash or hang).

**Validates: Requirements 8.1**

### Property 18: Classification Failure Returns Raw Text

*For any* document where classification produces no results, the system should return the raw extracted text along with a warning message.

**Validates: Requirements 8.2**

### Property 19: Partial Extraction Returns Available Data

*For any* document where extraction is incomplete, the system should return all successfully extracted fields with their confidence scores (not fail completely).

**Validates: Requirements 8.3**

### Property 20: Critical Errors Are Logged

*For any* critical error during processing, the system should write an entry to the audit log with error details and timestamp before returning an error response.

**Validates: Requirements 8.4**

### Property 21: Concurrent Processing Support

*For any* set of 10 documents submitted concurrently, the system should accept all requests and process them without rejecting any due to concurrency limits.

**Validates: Requirements 9.3**

### Property 22: Requests Are Queued Under Load

*For any* request submitted when the system is at capacity, the request should be added to a processing queue and return a queued status (not rejected).

**Validates: Requirements 9.4**

### Property 23: Idempotent Processing

*For any* document processed multiple times with identical input, the system should produce identical structured output (same extracted values, same confidence scores).

**Validates: Requirements 10.1**

### Property 24: Numerical Values Are Preserved Exactly

*For any* numerical value in the source document, if extracted, it should appear in the output with the exact same value (no rounding, no precision loss).

**Validates: Requirements 10.2**

### Property 25: Dates Are Normalized To ISO 8601

*For any* date value extracted from a document, the output should represent it in valid ISO 8601 format (YYYY-MM-DD).

**Validates: Requirements 10.3**

### Property 26: Currency Types Are Preserved

*For any* currency amount extracted, the output should include both the numerical value and a valid ISO 4217 currency code.

**Validates: Requirements 10.4**

### Property 27: All Operations Are Audit Logged

*For any* processing operation (upload, parse, classify, extract), an entry should be written to the audit log with the operation name, document ID, and ISO 8601 timestamp.

**Validates: Requirements 10.5**

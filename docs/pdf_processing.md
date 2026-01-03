# PDF Processing Module for Bias Detection

## Overview

The PDF Processing module (`utility/pdf_processor.py`) provides a complete pipeline for extracting text from Nepali PDFs and preparing sentences for bias detection analysis.

**Key Features:**
- ✓ PDF text extraction using PyMuPDF (fitz)
- ✓ Intelligent Nepali sentence segmentation
- ✓ LLM-based sentence refinement using Mistral
- ✓ Integration with bias detection API
- ✓ File upload support via API endpoints
- ✓ Error handling and logging

## Architecture

```
User Upload (PDF)
       ↓
PDFProcessor.process_pdf_from_bytes()
       ↓
[Extract Text] → [Clean Text] → [Split Sentences] → [Refine with LLM]
       ↓
List of Refined Sentences
       ↓
Bias Detection Model
       ↓
Bias Analysis Results
```

## Installation

### Required Dependencies

```bash
# PyMuPDF for PDF text extraction
pip install pymupdf

# Already included in module_a
# mistralai - Mistral LLM client
```

### Setup

1. Ensure `mistralai` is installed in your environment
2. Set `MISTRAL_API_KEY` environment variable
3. Module uses existing `MistralClient` from `module_a/llm_client.py`

## Usage

### 1. Basic Python Usage

```python
from utility.pdf_processor import PDFProcessor

# Initialize processor
processor = PDFProcessor()

# Process PDF from file path
result = processor.process_pdf(
    pdf_path="path/to/document.pdf",
    refine_with_llm=True
)

if result["success"]:
    sentences = result["sentences"]
    print(f"Extracted {result['total_sentences']} sentences")
    for sentence in sentences:
        print(f"- {sentence}")
```

### 2. Process from Bytes (File Uploads)

```python
# For API file uploads
processor = PDFProcessor()

pdf_bytes = await request.file.read()
result = processor.process_pdf_from_bytes(
    pdf_bytes=pdf_bytes,
    refine_with_llm=True
)
```

### 3. API Endpoints

#### A. Extract Sentences Only

**Endpoint:** `POST /api/v1/process-pdf`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/process-pdf" \
  -F "file=@nepali_document.pdf" \
  -F "refine_with_llm=true"
```

**Response:**
```json
{
  "success": true,
  "sentences": [
    "पहिलो वाक्य यहाँ छ।",
    "दोस्रो वाक्य यहाँ छ।",
    "तेस्रो वाक्य यहाँ छ।"
  ],
  "total_sentences": 3,
  "filename": "nepali_document.pdf",
  "raw_text": "पहिलो वाक्य यहाँ छ। दोस्रो वाक्य यहाँ छ। तेस्रो वाक्य यहाँ छ।"
}
```

#### B. Extract Sentences + Bias Detection

**Endpoint:** `POST /api/v1/process-pdf-to-bias`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/process-pdf-to-bias" \
  -F "file=@nepali_document.pdf" \
  -F "refine_with_llm=true" \
  -F "confidence_threshold=0.7"
```

**Response:**
```json
{
  "success": true,
  "total_sentences": 3,
  "biased_count": 1,
  "neutral_count": 2,
  "results": [
    {
      "sentence": "पहिलो वाक्य यहाँ छ।",
      "category": "neutral",
      "confidence": 0.95,
      "is_biased": false
    },
    {
      "sentence": "दोस्रो वाक्य यहाँ छ।",
      "category": "gender",
      "confidence": 0.82,
      "is_biased": true
    },
    {
      "sentence": "तेस्रो वाक्य यहाँ छ।",
      "category": "neutral",
      "confidence": 0.91,
      "is_biased": false
    }
  ],
  "filename": "nepali_document.pdf"
}
```

#### C. Service Health Check

**Endpoint:** `GET /api/v1/pdf-health`

**Response:**
```json
{
  "status": "healthy",
  "pdf_processor": "ready",
  "mistral_client": "connected",
  "features": {
    "pdf_extraction": true,
    "sentence_segmentation": true,
    "llm_refinement": true
  }
}
```

## API Schemas

### PDFProcessingResponse

```python
{
    "success": bool,
    "sentences": List[str],
    "total_sentences": int,
    "raw_text": Optional[str],
    "error": Optional[str],
    "filename": Optional[str]
}
```

### PDFToBiasDetectionResponse

```python
{
    "success": bool,
    "total_sentences": int,
    "biased_count": int,
    "neutral_count": int,
    "results": List[BiasResult],
    "error": Optional[str],
    "filename": Optional[str]
}
```

Where `BiasResult`:
```python
{
    "sentence": str,
    "category": str,
    "confidence": float,
    "is_biased": bool
}
```

## Processing Pipeline

### Step 1: Text Extraction
- Uses PyMuPDF (fitz) to extract text from PDF
- Handles multi-page documents
- Detects image-based PDFs (requires OCR)

### Step 2: Text Cleaning
- Removes extra whitespace
- Normalizes newlines
- Fixes formatting issues

### Step 3: Sentence Segmentation
- Uses regex patterns for Nepali sentence boundaries
- Recognizes: । (danda), . , ! , ?
- Filters out short fragments (< 5 characters)

### Step 4: LLM Refinement (Optional)
- Sends sentences to Mistral LLM
- Corrects mis-segmented sentences
- Removes duplicates
- Returns properly formatted JSON array

## Configuration

### Environment Variables

```bash
# Required for LLM refinement
export MISTRAL_API_KEY="your-api-key"

# Optional
export MISTRAL_MODEL="mistral-small"  # Default: mistral-small
export LOG_LEVEL="INFO"
```

### Processing Options

```python
# With LLM refinement (more accurate, slower)
result = processor.process_pdf(
    pdf_path="document.pdf",
    refine_with_llm=True  # Uses Mistral LLM
)

# Without LLM refinement (faster, regex-based)
result = processor.process_pdf(
    pdf_path="document.pdf",
    refine_with_llm=False  # Regex-based segmentation only
)
```

## Error Handling

The module handles various error scenarios:

```python
result = processor.process_pdf(pdf_path="file.pdf")

if not result["success"]:
    error = result["error"]
    # Possible errors:
    # - "No text could be extracted from the PDF"
    # - "Could not segment sentences from extracted text"
    # - "PDF might be image-based (requires OCR)"
    # - "File not found: path/to/file.pdf"
```

## Performance Considerations

### Execution Time Estimates

| Operation | Time | Notes |
|-----------|------|-------|
| PDF Text Extraction | ~100-500ms | Depends on PDF size |
| Sentence Segmentation | ~50-200ms | Regex-based |
| LLM Refinement | ~2-5s | API call to Mistral |
| Total (with LLM) | ~3-6s | Per document |
| Total (without LLM) | ~150-700ms | Regex only |

### Optimization Tips

1. **Disable LLM refinement** for faster processing when accuracy is less critical
2. **Batch multiple PDFs** to amortize API overhead
3. **Cache results** if processing same PDFs repeatedly

## Integration with Bias Detection

### Workflow

```
1. User uploads PDF
   ↓
2. Extract sentences using PDFProcessor
   ↓
3. Send sentences to Bias Detection model
   ↓
4. Classify each sentence (neutral/gender/caste/religion/etc.)
   ↓
5. Return analysis results to user
```

### Code Example

```python
from utility.pdf_processor import PDFProcessor
from api.routes.bias_detection import run_bias_detection

processor = PDFProcessor()

# Process PDF
pdf_result = processor.process_pdf(
    pdf_path="document.pdf",
    refine_with_llm=True
)

if pdf_result["success"]:
    sentences = pdf_result["sentences"]
    combined_text = " ".join(sentences)
    
    # Run bias detection
    bias_result = run_bias_detection(
        text=combined_text,
        confidence_threshold=0.7
    )
    
    print(f"Biased sentences: {bias_result.biased_count}")
    print(f"Neutral sentences: {bias_result.neutral_count}")
```

## Nepali Language Support

### Character Range Supported

The module recognizes Nepali character ranges:
- Consonants: अ-ह
- Vowels: ा-ौ
- Special characters: ँ-ॿ

### Sentence Boundaries

Recognized punctuation:
- `।` Danda (primary Nepali punctuation)
- `.` Period
- `!` Exclamation mark
- `?` Question mark

## Logging

Enable debug logging to track processing:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("utility.pdf_processor")

# Now see detailed logs
processor = PDFProcessor()
result = processor.process_pdf("document.pdf")
```

## Files Structure

```
utility/
├── __init__.py                 # Module initialization
├── pdf_processor.py            # Main PDFProcessor class
├── pdf_processor_examples.py   # Usage examples
└── docs/
    └── pdf_processing.md       # This file

api/
├── routes/
│   └── pdf_processing.py       # API endpoints
└── schemas.py                  # Pydantic models
```

## Troubleshooting

### Issue: "No text could be extracted from the PDF"

**Cause:** PDF is image-based (scanned document)
**Solution:** Requires OCR support (future enhancement)

### Issue: "LLM refinement failed"

**Cause:** Mistral API key missing or network error
**Solution:** Check `MISTRAL_API_KEY` environment variable

### Issue: Sentences are too short or fragmented

**Solution:** Sentences shorter than 5 characters are filtered. Adjust threshold in code if needed.

### Issue: Slow processing with LLM

**Solution:** 
- Disable LLM refinement (`refine_with_llm=False`) for speed
- Use smaller batch sizes
- Check network latency to Mistral API

## Future Enhancements

- [ ] OCR support for scanned PDFs
- [ ] Language detection and auto-switching
- [ ] Caching layer for repeated PDFs
- [ ] Batch processing optimization
- [ ] Support for other document formats (DOCX, TXT)
- [ ] Custom Nepali dictionary for better segmentation

## License

Part of Nepal Justice Weaver project

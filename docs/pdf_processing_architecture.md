# PDF Processing System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PDF Upload Component                                     │   │
│  │  • File input                                             │   │
│  │  • Drag & drop                                            │   │
│  │  • Progress indicator                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                      HTTP/FormData
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  POST /api/v1/process-pdf                                        │
│  └─► Extract sentences only                                      │
│                                                                   │
│  POST /api/v1/process-pdf-to-bias                                │
│  └─► Extract + Analyze bias (complete pipeline)                 │
│                                                                   │
│  GET /api/v1/pdf-health                                          │
│  └─► Service status check                                        │
│                                                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
         ▼                                   ▼
    ┌────────────┐                   ┌─────────────────┐
    │ PDF Bytes  │                   │ PDFProcessor    │
    │            │                   │ (utility/)      │
    └────────────┘                   └─────────────────┘
         │                                   │
         └───────────┬───────────────────────┘
                     │
                     ▼
         ┌─────────────────────────────┐
         │  Step 1: Extract Text       │
         │  PyMuPDF (fitz)             │
         │  • Read PDF pages           │
         │  • Extract raw text         │
         │  • Handle multi-page        │
         └────────────┬────────────────┘
                      │
                      ▼
         ┌─────────────────────────────┐
         │  Step 2: Clean Text         │
         │  Regex Processing           │
         │  • Remove extra whitespace  │
         │  • Normalize formatting     │
         └────────────┬────────────────┘
                      │
                      ▼
         ┌─────────────────────────────┐
         │  Step 3: Segment Sentences  │
         │  Nepali-aware Regex         │
         │  • Split on दण्ड (।)         │
         │  • Handle punctuation       │
         │  • Filter short fragments   │
         └────────────┬────────────────┘
                      │
                      ▼
         ┌─────────────────────────────┐
         │  Step 4: Refine (Optional)  │
         │  Mistral LLM API            │
         │  • Correct segmentation     │
         │  • Remove duplicates        │
         │  • JSON formatting          │
         └────────────┬────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
    ┌──────────────┐        ┌─────────────────┐
    │   Sentences  │        │  Return JSON    │
    │   List       │        │  Array          │
    └──────┬───────┘        └────────┬────────┘
           │                         │
           │            ┌────────────┴─────────────┐
           │            │                          │
           │            ▼                          ▼
           │      ┌─────────────────┐      ┌──────────────────┐
           │      │ Option A:       │      │ Option B:        │
           │      │ Return to       │      │ Pass to Bias     │
           │      │ User            │      │ Detection        │
           │      └─────────────────┘      └────────┬─────────┘
           │                                        │
           │                                        ▼
           │                              ┌──────────────────────┐
           │                              │  Bias Detection Model│
           │                              │  DistilBERT Nepali   │
           │                              │  (module_b)          │
           │                              ├──────────────────────┤
           │                              │ • Classify sentence  │
           │                              │ • 11 categories:     │
           │                              │  - neutral           │
           │                              │  - gender            │
           │                              │  - caste             │
           │                              │  - religion          │
           │                              │  - political         │
           │                              │  - age               │
           │                              │  - disability        │
           │                              │  - appearance        │
           │                              │  - social status     │
           │                              │  - religiosity       │
           │                              │  - ambiguity         │
           │                              └────────┬─────────────┘
           │                                       │
           └───────────┬───────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────────┐
        │       Response to User                │
        ├──────────────────────────────────────┤
        │ • Extracted sentences                │
        │ • Bias classification results        │
        │ • Confidence scores                  │
        │ • Biased/neutral counts              │
        │ • Processing metadata                │
        └──────────────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Frontend Display    │
            │  • Show results      │
            │  • Highlight biases  │
            │  • Display stats     │
            └──────────────────────┘
```

## Data Flow Diagram

```
INPUT: PDF File
   │
   ├─ Metadata
   │  ├─ Filename
   │  ├─ File size
   │  └─ Upload timestamp
   │
   └─ Binary content
      │
      ▼
   PDFProcessor.process_pdf_from_bytes()
      │
      ├─ extract_text_from_pdf()
      │  │ Uses: PyMuPDF.fitz.open()
      │  │ Output: Raw text string + page count
      │  └─ ~200-500ms
      │
      ├─ clean_text()
      │  │ Uses: Regex replacements
      │  │ Output: Normalized text string
      │  └─ ~50ms
      │
      ├─ split_into_sentences()
      │  │ Uses: Nepali-aware regex patterns
      │  │ Output: List[sentences]
      │  └─ ~50-150ms
      │
      └─ refine_sentences_with_llm() [OPTIONAL]
         │ Uses: Mistral API
         │ Input: JSON-formatted sentences
         │ Output: Refined List[sentences]
         └─ ~2-5s (includes API latency)
         
   ▼
OUTPUT 1 (Extract Only):
   {
       "success": true,
       "sentences": ["वाक्य १", "वाक्य २", ...],
       "total_sentences": 15,
       "raw_text": "फुल text...",
       "filename": "doc.pdf"
   }

OUTPUT 2 (Extract + Bias):
   {
       "success": true,
       "total_sentences": 15,
       "biased_count": 2,
       "neutral_count": 13,
       "results": [
           {
               "sentence": "वाक्य १",
               "category": "neutral",
               "confidence": 0.95,
               "is_biased": false
           },
           ...
       ],
       "filename": "doc.pdf"
   }
```

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    utility/ module                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PDFProcessor Class                                          │
│  ├─ __init__(mistral_api_key)                               │
│  │  └─ Initialize MistralClient                             │
│  │                                                            │
│  ├─ extract_text_from_pdf(pdf_path)                          │
│  │  ├─ fitz.open(pdf_path)                                   │
│  │  ├─ Iterate pages                                         │
│  │  ├─ get_text("text")                                      │
│  │  └─ Return: raw text                                      │
│  │                                                            │
│  ├─ clean_text(text)                                         │
│  │  ├─ Remove newlines                                       │
│  │  ├─ Normalize spaces                                      │
│  │  └─ Return: cleaned text                                  │
│  │                                                            │
│  ├─ split_into_sentences(text)                               │
│  │  ├─ Apply Nepali regex patterns                           │
│  │  ├─ Filter short fragments                               │
│  │  └─ Return: sentence list                                │
│  │                                                            │
│  ├─ refine_sentences_with_llm(sentences)                     │
│  │  ├─ Format as JSON                                        │
│  │  ├─ Send to Mistral API                                   │
│  │  ├─ Parse JSON response                                   │
│  │  └─ Return: refined sentences                             │
│  │                                                            │
│  ├─ process_pdf(pdf_path, refine_with_llm)                   │
│  │  └─ Complete pipeline (file path)                         │
│  │                                                            │
│  └─ process_pdf_from_bytes(pdf_bytes, refine_with_llm)       │
│     └─ Complete pipeline (bytes)                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    api/routes/ module                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  pdf_processing.py (FastAPI Routes)                          │
│  ├─ POST /api/v1/process-pdf                                │
│  │  ├─ Receive: file (UploadFile), refine_with_llm          │
│  │  ├─ Call: PDFProcessor.process_pdf_from_bytes()          │
│  │  └─ Return: PDFProcessingResponse                         │
│  │                                                            │
│  ├─ POST /api/v1/process-pdf-to-bias                         │
│  │  ├─ Receive: file, refine_with_llm, confidence_threshold  │
│  │  ├─ Call: PDFProcessor.process_pdf_from_bytes()          │
│  │  ├─ Call: run_bias_detection()                           │
│  │  └─ Return: PDFToBiasDetectionResponse                    │
│  │                                                            │
│  └─ GET /api/v1/pdf-health                                  │
│     ├─ Check: PDFProcessor availability                     │
│     ├─ Check: Mistral client status                         │
│     └─ Return: health status                                │
│                                                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  api/schemas.py (Pydantic Models)            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PDFProcessingRequest / Response                             │
│  PDFToBiasDetectionRequest / Response                        │
│  BiasResult (reused from bias_detection)                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│               External Dependencies                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PyMuPDF (fitz)                                              │
│  └─ PDF text extraction                                      │
│                                                               │
│  Mistral API Client                                          │
│  └─ LLM-based sentence refinement                            │
│                                                               │
│  FastAPI                                                      │
│  └─ API framework (from module_a)                            │
│                                                               │
│  Pydantic                                                     │
│  └─ Data validation                                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Processing Timeline

```
Timeline for Single PDF (~10 KB):

Time  Component                Duration    Cumulative
────────────────────────────────────────────────────
0ms   ├─ API receives upload  ~5ms        5ms
      │
5ms   ├─ Read bytes           ~10ms       15ms
      │
15ms  ├─ PyMuPDF extraction   ~200ms      215ms
      │
215ms ├─ Text cleaning        ~30ms       245ms
      │
245ms ├─ Sentence split       ~100ms      345ms
      │
345ms ├─ LLM refinement       ~3500ms     3845ms
      │   (if enabled)
      │
3845ms├─ Bias detection       ~500ms      4345ms
      │   (if enabled)
      │
4345ms└─ Return response      ~5ms        4350ms
       
Total Time:
├─ With LLM + Bias:  ~4.3 seconds
├─ With LLM only:    ~3.8 seconds
├─ Without LLM:      ~0.35 seconds
└─ Bias only:        ~0.5 seconds (sentence extraction)
```

## Error Handling Flow

```
API Request
   │
   ├─ Validate file
   │  ├─ Is PDF? → No → 400 Bad Request
   │  ├─ Is empty? → Yes → 400 Bad Request
   │  └─ Is valid? → Continue
   │
   └─ Process PDF
      ├─ Extract text
      │  ├─ File not found? → FileNotFoundError → 500
      │  ├─ Permission denied? → Exception → 500
      │  └─ Success? → Continue
      │
      ├─ Split sentences
      │  ├─ No sentences? → Warning in response → 200 (empty results)
      │  └─ Success? → Continue
      │
      └─ Refine with LLM (if enabled)
         ├─ API key missing? → Warning, use regex → 200 (fallback)
         ├─ Network error? → Warning, use regex → 200 (fallback)
         ├─ Invalid JSON? → Warning, use regex → 200 (fallback)
         └─ Success? → Return refined sentences → 200
```

## State Diagram

```
             ┌──────────────┐
             │   Idle       │
             └──────┬───────┘
                    │
        User uploads PDF
                    │
                    ▼
         ┌──────────────────┐
         │   Validating     │
         └──────┬───────────┘
                │
         ┌──────┴──────┐
         │             │
    Invalid         Valid
         │             │
         ▼             ▼
    ┌─────────┐  ┌──────────────────┐
    │  Error  │  │  Extracting      │
    └─────────┘  └──────┬───────────┘
                        │
                 ┌──────┴──────┐
                 │             │
             Success      No Text
                 │             │
                 ▼             ▼
            ┌──────────┐  ┌──────────┐
            │Splitting │  │  Error   │
            └──────┬───┘  └──────────┘
                   │
            ┌──────┴──────┐
            │             │
        Success      No Sentences
            │             │
            ▼             ▼
      ┌────────────┐  ┌──────────┐
      │Refining    │  │  Error   │
      │(Optional)  │  └──────────┘
      └──────┬─────┘
             │
      ┌──────┴──────┐
      │             │
   Success       Failed
      │             │
      ├─────┬───────┤
      │     │       │
      ▼     ▼       ▼
   ┌──────────────┐ ┌────────┐
   │ Formatting   │ │Fallback│
   │Response      │ │(Regex) │
   └──────┬───────┘ └───┬────┘
          │             │
          └──────┬──────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Bias Detection  │
        │ (if enabled)    │
        └────────┬────────┘
                 │
          ┌──────┴──────┐
          │             │
      Success        Error
          │             │
          ▼             ▼
    ┌────────────┐  ┌────────┐
    │Format      │  │Return  │
    │Response    │  │Error   │
    └────────┬───┘  └───┬────┘
             │          │
             └────┬─────┘
                  │
                  ▼
        ┌──────────────────┐
        │Send Response     │
        │to Client         │
        └──────────────────┘
```

## Integration Points

```
Frontend (Next.js)
       │
       ├─► /api/v1/process-pdf
       │   └─ Use for: Sentence extraction only
       │
       ├─► /api/v1/process-pdf-to-bias
       │   └─ Use for: Full analysis (PDF → Bias)
       │
       └─► /api/v1/pdf-health
           └─ Use for: Service status check

Internal Integration
       │
       ├─► PDFProcessor class
       │   └─ Use in: Custom workflows
       │
       └─► run_bias_detection() function
           └─ Use in: Direct bias analysis
```

---

This architecture provides:
✅ Scalable processing pipeline
✅ Clear separation of concerns
✅ Reusable components
✅ Error resilience
✅ Performance optimization options
✅ Easy integration points

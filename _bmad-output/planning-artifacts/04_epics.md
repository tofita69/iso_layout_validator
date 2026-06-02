# PROJECT EPICS & USER STORIES
## ISO Technical Drawing Validator System

**Document Version:** 1.0  
**Prepared by:** Scrum Master (Project Lead)  
**Based on:** PRD.md + architecture.md  
**Status:** ⏳ Draft (Pending Team Estimation)

---

## EPIC OVERVIEW (UPDATED WITH CHECKLIST REQUIREMENTS)

| Epic ID | Title | Priority | Complexity | Est. Weeks | Dependencies | Story Points |
|---------|-------|----------|-----------|-----------|--------------|--------------|
| **E0.5** | External Document Processing & Standards Registry | 🔴 P0 | Medium | 1 | None | 12 |
| **E1** | Data Ingestion & Preparation | 🔴 P0 | Medium | 3 | None | 26 |
| **E2** | Zone Detection & OCR (Drawing-Type Aware) | 🔴 P0 | High | 5 | E1 | 42 (+5 from classification) |
| **E3** | Data Extraction & Structuring (EXPANDED) | 🔴 P0 | High | 5 | E2 | 47 (+13 for material/weld/BOM/approval) |
| **E4** | Validation Rules Engine (EXPANDED) | 🔴 P0 | High | 6 | E3 | 60 (+26 for classification/standards/custom rules/workflow) |
| **E5** | Reporting & User Interface (EXPANDED) | 🟠 P1 | Medium | 3.5 | E4 | 25 (+5 for approval UI) |
| **E6** | RAG System (ISO Norms) | 🟠 P1 | Medium | 2 | E1 | 20 |
| **E7** | Expert Workflow & Feedback Loop | 🟠 P1 | Medium | 2 | E4, E5 | 15 |
| **E8** | Integration & Deployment | 🟠 P1 | High | 2 | E1-E7 | 18 |
| **E9** | Drawing Type Classification & Standards (NEW) | 🔴 P0 | High | 2 (overlap with E0.5 + E2/E4) | - | 21 |
| **PHASE 2** | Performance Optimization | 🟡 P2 | High | TBD | Post-MVP | TBD |

**Total MVP Duration:** ~26-28 weeks (6.5 months)  
**Total Story Points:** ~180-190 (was ~145)  
**Team Size Recommended:** 8-10 people (2-3 backend, 2 ML, 1-2 frontend, 1 DevOps, 1-2 QA, 1 rules architect)

---

## EPIC 1: DATA INGESTION & PREPARATION

**Goal:** Enable users to upload mechanical drawings; convert to standardized format for ML processing

**Business Value:**
- Unblock all downstream work (detection, extraction, validation)
- Enable batch processing for large projects
- Foundation for data versioning + audit trail

### User Stories

#### US1.1: Upload Drawing File via Web UI
**Description:**  
As a **design engineer**, I want to upload a drawing file (PDF or PNG) so that I can validate it against ISO standards.

**Acceptance Criteria:**
- User can drag-and-drop file into web interface
- Alternative: Click button to browse file system
- File type validation (PDF, PNG only)
- File size validation (max 50MB per file, or 500MB batch)
- Progress indicator during upload (for >10MB files)
- Clear error messages if validation fails
- Success notification with drawing_id

**Technical Notes:**
- Frontend: react-dropzone component
- Backend: FastAPI multipart form handler
- Validation: python-magic (MIME type check)

**Story Points:** 5 | **Priority:** P0 | **Owner:** Frontend + Backend

---

#### US1.2: Convert CATIA Drawing to PNG/Image
**Description:**  
As a **system**, I need to convert CATIA CATDrawing files to PNG/JPEG images so that the detection model can process them.

**Acceptance Criteria:**
- Accepted input: .CATDrawing (CATIA V5)
- Output: 1024x1024 normalized PNG
- Preserve aspect ratio (add borders if needed)
- Maintain readability (no quality loss >3dB PSNR)
- Support batch conversion (100 files in <5 min)
- Log conversion errors; skip problematic files
- Store both original + converted images in S3

**Technical Notes:**
- Use: python-pptx or libreoffice-headless for conversion
- Fallback: If CATDrawing unreadable, require user to export PDF manually
- Caching: Store converted image (key: drawing_id + MD5 hash)

**Story Points:** 8 | **Priority:** P0 | **Owner:** ML Engineer

---

#### US1.3: Normalize & Preprocess Images
**Description:**  
As a **detection module**, I need preprocessed images with optimal contrast and alignment so that YOLO inference accuracy is maximized.

**Acceptance Criteria:**
- Auto-rotation: Detect + correct skew (±30°)
- Contrast enhancement: Histogram equalization or CLAHE
- Noise reduction: Gaussian blur or morphological operations
- Deskew: Straighten tilted scans
- Output: Optimized 1024x1024 PNG
- Latency: <500ms per image
- Batch processing: 100 images in <60s

**Technical Notes:**
- Libraries: OpenCV, scikit-image
- Preserve original image for audit trail
- Store preprocessing metadata (rotation angle, contrast gain)

**Story Points:** 5 | **Priority:** P0 | **Owner:** ML Engineer

---

#### US1.4: Batch Upload & Management
**Description:**  
As a **project manager**, I want to upload 50+ drawings in a batch so that I can validate my entire project at once.

**Acceptance Criteria:**
- User selects multiple files (CSV manifest + folder)
- Project ID auto-assigned; drawings linked to project
- Batch job tracked (progress: N/100 files processed)
- Download report CSV (summary of all validations)
- Cancel batch mid-processing
- Retry failed files

**Technical Notes:**
- Manifest format: CSV with drawing_id, filename, reference
- Use Celery for parallel processing (max 10 concurrent)

**Story Points:** 5 | **Priority:** P1 | **Owner:** Frontend + Backend

---

#### US1.5: Dataset Versioning & Audit Trail
**Description:**  
As a **compliance officer**, I need immutable audit trail of all uploads so that I can track changes for ISO certification audits.

**Acceptance Criteria:**
- Every upload logged: timestamp, user, MD5 hash, file size, source
- Immutable database entries (no updates; only inserts + deletes with audit)
- Export audit log (JSON, CSV)
- Retention: 2 years minimum

**Technical Notes:**
- PostgreSQL: audit_log table with database triggers
- Encryption: AES-256 for sensitive data
- No update statements; only soft deletes

**Story Points:** 3 | **Priority:** P1 | **Owner:** Backend + DevOps

---

**Epic 1 Summary:**
- **Total Story Points:** 26
- **Duration:** 3 weeks
- **Team:** 2-3 people (1 backend, 1 frontend, 1 ML engineer)
- **Deliverables:** Upload API + UI + preprocessing pipeline

---

## EPIC 2: ZONE DETECTION & OCR

**Goal:** Train YOLO model to detect 8 drawing zones; fine-tune Donut for technical text OCR

**Business Value:**
- Enable extraction of structured data from drawings
- Foundation for validation rules
- Measurable quality metrics (mAP, CER)

### User Stories

#### US2.1: Prepare Training Dataset (50-100 Drawings)
**Description:**  
As a **data scientist**, I need annotated training data with bounding boxes so that I can train a high-accuracy detection model.

**Acceptance Criteria:**
- 100 drawings manually annotated with 8 zone types
- Format: COCO JSON + YOLO txt labels
- Quality: 2 annotators; >95% agreement (Cohen's kappa)
- Train/val/test split: 70/15/15
- Stored in DVC for versioning

**Technical Notes:**
- Annotation tool: CVAT or Roboflow
- Classes: title_block, notes, gdt_frames, dimensions, weld_symbols, surface_finish, revision_table, drawing_area
- Timeline: Negotiate with client; 2 weeks to gather + annotate

**Story Points:** 8 | **Priority:** P0 | **Owner:** Data Annotator + ML Engineer

---

#### US2.2: Train YOLO v11 Detection Model
**Description:**  
As a **ML engineer**, I need to train a YOLO model on annotated data so that it can detect drawing zones with >85% mAP50-95.

**Acceptance Criteria:**
- Model: YOLOv11n-obb (Oriented Bounding Box)
- Metrics: mAP50 ≥ 0.95, mAP50-95 ≥ 0.85
- Training time: <8 hours on single GPU (A100)
- Inference latency: <1000ms per image
- Output: model.pt saved to S3
- Version tracking: Tag model with date + metrics

**Technical Notes:**
- Hyperparameters: imgsz=1024, batch=16, epochs=30
- Augmentation: RandAugment, Mosaic, MixUp
- Optimizer: SGD + warmup
- Log metrics to W&B (Weights & Biases)

**Story Points:** 8 | **Priority:** P0 | **Owner:** ML Engineer

---

#### US2.3: Validate Model on Holdout Test Set
**Description:**  
As a **QA engineer**, I need to evaluate model performance on unseen data so that I can verify production readiness.

**Acceptance Criteria:**
- Test set: 15 drawings (unseen during training)
- Metrics computed: Precision, recall, mAP (by class)
- Confusion matrix generated
- Per-class performance table
- False positives analyzed; categorize as: hard negatives vs. labeling errors
- Report: Pass if all metrics ≥ acceptance threshold

**Technical Notes:**
- Test on CPU to simulate production environment
- Document corner cases (poor scans, handwritten notes)

**Story Points:** 5 | **Priority:** P0 | **Owner:** QA

---

#### US2.4: Fine-tune Donut for Technical Text OCR
**Description:**  
As a **ML engineer**, I need a fine-tuned OCR model so that it extracts technical text (dimensions, specs, notes) with >90% accuracy.

**Acceptance Criteria:**
- Base model: Donut (naver-clova-ix/donut-base)
- Fine-tune on 500 cropped zone images (from labeled drawings)
- Metrics: CER (Character Error Rate) <5%, WER (Word Error Rate) <8%
- Test on 100 unseen crops
- Output: Model pushed to HuggingFace Model Hub + versioned

**Technical Notes:**
- Dataset format: Image + ground truth text pairs
- Training: 3 epochs, learning rate 1e-4, batch=8
- Hardware: GPU (8GB VRAM sufficient)
- Augmentation: Rotation, blur, noise (simulate poor scans)

**Story Points:** 8 | **Priority:** P0 | **Owner:** ML Engineer

---

#### US2.5: Inference Pipeline & Model Serving
**Description:**  
As a **backend service**, I need a production-ready inference pipeline so that I can run detection + OCR on uploaded drawings asynchronously.

**Acceptance Criteria:**
- Load YOLO model from S3 cache (warm start)
- Run inference: input image → bboxes + classes + confidence
- Load Donut model; run OCR on each detected zone
- Output: JSON with zones, extracted text, confidence scores
- Error handling: Graceful degradation if model fails
- Metrics: Inference latency logged
- Model versioning: Track which version used for each draw

**Technical Notes:**
- Framework: FastAPI + async tasks
- GPU: Optional; graceful fallback to CPU (slower)
- Caching: Redis cache for models
- Scaling: Horizontal (multiple worker pods)

**Story Points:** 8 | **Priority:** P0 | **Owner:** Backend + ML Engineer

---

**Epic 2 Summary:**
- **Total Story Points:** 37
- **Duration:** 4 weeks
- **Team:** 3-4 people (2 ML engineers, 1 data annotator, 1 backend)
- **Deliverables:** Trained YOLO + Donut models, inference API
- **Go/No-Go Gate:** Model metrics must pass acceptance threshold before proceeding to Epic 3

---

## EPIC 3: DATA EXTRACTION & STRUCTURING

**Goal:** Parse detected zones into structured drawing metadata (cartridge, dimensions, GD&T, etc.)

**Business Value:**
- Enable automated compliance checking
- Feed validation rules with clean data
- Improve reporting accuracy

### User Stories

#### US3.1: Extract Cartouche (Title Block) Data
**Description:**  
As a **rule validator**, I need structured cartouche data (designation, reference, scale, index, mass, etc.) so that I can validate completeness and format.

**Acceptance Criteria:**
- Input: Cropped cartouche image + OCR text
- Extract fields:
  - Designation (e.g., "ADMISSION SHAFT")
  - Reference (e.g., "AS-001")
  - Revision Index (e.g., "A", "B")
  - Scale (e.g., "1:2")
  - Mass (kg) or "TBD"
  - Date
  - Author
  - Drawing area (mm²)
- Output: JSON with field confidence scores
- Accuracy: >95% on test set

**Technical Notes:**
- Parser: Regex + Donut OCR
- Fallback: Manual review UI if confidence <80%

**Story Points:** 5 | **Priority:** P0 | **Owner:** Backend + ML Engineer

---

#### US3.2: Extract Dimensions (Cotation)
**Description:**  
As a **rule validator**, I need structured dimension data (value, unit, tolerance, type) so that I can validate ISO conformance.

**Acceptance Criteria:**
- Extract from dimension zone annotations:
  - Nominal value (e.g., "Ø 10")
  - Unit (mm, inches)
  - Tolerance: upper (e.g., "+0.5") + lower (e.g., "-0.2")
  - Tolerance type (ISO 2768 code or ISO 13920 class)
  - Functional dimension: Y/N
  - Hors-tout dimension: Y/N
- Output: Array of {value, tolerance, type, confidence}
- Accuracy: >90%

**Technical Notes:**
- Regex patterns for dimension formats
- ISO 2768: Codes like "fH", "mK" (form + tolerance class)
- ISO 13920: Tolerance classes like "8/7f"

**Story Points:** 8 | **Priority:** P0 | **Owner:** Backend + ML Engineer

---

#### US3.3: Extract GD&T Symbols & Datums
**Description:**  
As a **rule validator**, I need to parse GD&T symbols and datum references so that I can validate geometric tolerance compliance.

**Acceptance Criteria:**
- Detect GD&T symbol frames (boxes with symbols)
- Symbols: Flatness, straightness, perpendicularity, parallelism, concentricity, runout, profile
- Extract: Tolerance value, datum letters, modifier (MMC, RFS)
- Output: Structured array of {symbol, value, datums, modifiers, confidence}
- Accuracy: >85% (hard problem; allow manual review for <70% confidence)

**Technical Notes:**
- Symbol recognition: Template matching or custom CNN
- Datum letters: OCR on datum boxes
- Fallback: Link to reference doc; allow expert to confirm

**Story Points:** 8 | **Priority:** P0 | **Owner:** ML Engineer

---

#### US3.4: Extract Weld Specifications
**Description:**  
As a **rule validator**, I need structured weld data (symbols, notes, CNE references) so that I can validate fabrication compliance.

**Acceptance Criteria:**
- Detect weld symbol frames
- Extract: Weld type, CND standard (ISO), NOTA reference
- Link to fabrication notes
- Output: {weld_type, standard, nota_ref, confidence}
- Accuracy: >80%

**Technical Notes:**
- Weld symbols: ISO 1101 + client-specific codes
- NOTA ↔ CNE cross-reference (lookup table)

**Story Points:** 5 | **Priority:** P0 | **Owner:** Backend

---

#### US3.5: Extract Surface Finish & Environment Criteria
**Description:**  
As a **rule validator**, I need surface finish specifications (Ra, Rz, environment criteria) so that I can validate manufacturing feasibility.

**Acceptance Criteria:**
- Extract: Ra (surface roughness), Rz, treatment (paint, anodize, etc.)
- Environment conditions: Temperature, humidity, corrosion risk
- Output: {finish_spec, environment, confidence}
- Accuracy: >80%

**Story Points:** 5 | **Priority:** P0 | **Owner:** Backend

---

#### US3.6: Link Extracted Data to Drawing Context
**Description:**  
As a **report generator**, I need to map extracted data back to image regions so that I can highlight violations in the UI.

**Acceptance Criteria:**
- For each extracted field, store: zone_id, bbox, confidence, raw_image_region
- Enable UI to highlight: "This dimension violates Rule X"
- Clickable annotations link to OCR confidence + raw text
- Support for multi-language notes (French, English, German)

**Story Points:** 3 | **Priority:** P1 | **Owner:** Frontend + Backend

---

**Epic 3 Summary:**
- **Total Story Points:** 34
- **Duration:** 3 weeks
- **Team:** 2-3 people (1-2 backend, 1 ML engineer)
- **Deliverables:** Extraction pipeline, structured data models, linking UI
- **Go/No-Go Gate:** >90% accuracy on cartouche + dimensions; <80% triggers manual review

---

## EPIC 4: VALIDATION RULES ENGINE

**Goal:** Codify ISO rules; execute validation; return pass/fail/review decisions

**Business Value:**
- Deliver core value: automated compliance checking
- Measurable pass/fail reports
- Compliance audit trail

### User Stories

#### US4.1: Codify ISO Rules (YAML Configuration)
**Description:**  
As a **rules architect**, I need to define all validation rules in a structured format so that I can maintain and update them without code changes.

**Acceptance Criteria:**
- Rules defined in YAML format:
  ```yaml
  rule_id: "cart_001"
  name: "Cartouche Required Fields"
  category: "cartouche"
  severity: CRITICAL
  condition: "(cartouche.designation != null) AND (cartouche.reference != null)"
  message: "Cartouche missing required fields"
  auto_fix: false  # Expert review needed
  ```
- 20+ rules across 7 categories
- Rules version-controlled in Git
- Support for rule overrides by project

**Story Points:** 8 | **Priority:** P0 | **Owner:** Rules Architect

---

#### US4.2: Build Rule Engine (Evaluation Logic)
**Description:**  
As a **validation service**, I need to evaluate rules against extracted data so that I can generate compliance reports.

**Acceptance Criteria:**
- Load rules from YAML
- For each drawing: evaluate all applicable rules
- Return: violations array with {rule_id, severity, message, affected_field, recommendation}
- Support rule dependencies (e.g., "Check mass only if index == A")
- Latency: <100ms per drawing
- Logging: Detailed trace of rule evaluation

**Technical Notes:**
- Parser: YAML loader
- Evaluation: Simple if/then logic (can upgrade to business rules engine later)
- Expression language: Python eval() with sandboxing

**Story Points:** 8 | **Priority:** P0 | **Owner:** Backend

---

#### US4.3: Severity Classification & Anomaly Detection
**Description:**  
As a **report generator**, I need to categorize violations by severity so that I can prioritize expert review.

**Acceptance Criteria:**
- Severity levels: CRITICAL, HIGH, MEDIUM, LOW
- CRITICAL: Prevent fabrication (e.g., missing cartouche)
- HIGH: Major compliance gap (e.g., tolerance type mismatch)
- MEDIUM: Minor issue (e.g., inconsistent units)
- LOW: Informational (e.g., OCR confidence low)
- Anomalies: Flag when:
  - Missing expected zone
  - Conflicting standards
  - Dimensional outliers (>3σ from training distribution)
  - Rare conditions (mass on intermediate, stabilization not flagged)
- Overall status: PASS (no CRITICAL/HIGH), FAIL (≥1 CRITICAL), REVIEW (HIGH only)

**Story Points:** 5 | **Priority:** P0 | **Owner:** Backend + ML Engineer

---

#### US4.4: Expert Decision Recording & Feedback
**Description:**  
As a **subject matter expert**, I need to approve/override system decisions so that I can refine rules for edge cases.

**Acceptance Criteria:**
- Expert dashboard: List flagged drawings (severity, rule)
- For each item: Show system decision + context
- Expert can: Approve, Override, Request More Info
- Record rationale + timestamp
- Weekly summary: "Rule X accuracy: 92%"
- Trigger retraining if accuracy drops >5%

**Story Points:** 8 | **Priority:** P1 | **Owner:** Backend + Frontend

---

#### US4.5: Rule Versioning & A/B Testing
**Description:**  
As a **product manager**, I need to roll out new rules gradually so that I can measure impact before full deployment.

**Acceptance Criteria:**
- Tag rules with version (v1.0, v1.1, etc.)
- A/B test: 10% of traffic on new rules
- Compare: Violation rate, expert override rate
- Metrics: "New rule reduces false positives by 15%"
- Rollback capability: Revert to prior rule set
- Audit: Track which rule version used for each drawing

**Story Points:** 5 | **Priority:** P1 | **Owner:** Backend + DevOps

---

**Epic 4 Summary:**
- **Total Story Points:** 34
- **Duration:** 4 weeks
- **Team:** 2-3 people (1 rules architect, 1-2 backend engineers)
- **Deliverables:** YAML rule set (20+), rule engine, expert dashboard
- **Go/No-Go Gate:** Expert agreement >90% on test set (50 drawings)

---

## EPIC 5: REPORTING & USER INTERFACE

**Goal:** Generate compliance reports (JSON, HTML, CSV); deliver intuitive web UI

**Business Value:**
- User-facing value; enables decision-making
- Compliance documentation for audits
- Visualization of violations

### User Stories

#### US5.1: Generate JSON Report
**Description:**  
As a **API client**, I need machine-readable validation results so that I can integrate them with other systems (DSM, MES, ERP).

**Acceptance Criteria:**
- Output: Structured JSON with:
  - Drawing metadata
  - Zones detected + confidence
  - Extracted data (cartouche, dimensions, specs)
  - Validation results (violations array)
  - Overall pass/fail status
  - Timestamp, model versions used
- Schema: JSON-Schema published (OpenAPI)
- Versioning: Backwards compatible with prior formats
- Compression: Gzip for large reports

**Story Points:** 5 | **Priority:** P0 | **Owner:** Backend

---

#### US5.2: Generate HTML Report with Visualization
**Description:**  
As a **design engineer**, I need a visual, interactive report so that I can understand violations and their locations on the drawing.

**Acceptance Criteria:**
- Report sections:
  1. Summary: Overall status, pass rate, violation count
  2. Zones: Detected zones with thumbnail + toggle visibility
  3. Violations: List view, filterable by severity/rule
  4. Recommendations: Suggested fixes + expert notes
- Interactivity:
  - Hover violation → highlight region on image
  - Click zone → zoom + show extracted text
  - Inline corrective note field (for expert input)
- Styling: Professional, responsive, print-friendly
- Export: Download as PDF

**Technical Notes:**
- Template: Jinja2 + Bootstrap CSS
- JavaScript: react-image-zoom library
- PDF export: weasyprint or Puppeteer

**Story Points:** 8 | **Priority:** P0 | **Owner:** Frontend + Backend

---

#### US5.3: Generate CSV Export (Bulk Analysis)
**Description:**  
As a **project manager**, I need to export validation results as CSV so that I can analyze trends across many drawings in Excel.

**Acceptance Criteria:**
- Columns: drawing_id, filename, status, violation_count, rule_violations (as JSON), pass_rate, timestamp
- Support batch export (100+ drawings in 1 file)
- Format: UTF-8, RFC 4180 compliant
- Compression: Optional .zip for large exports

**Story Points:** 3 | **Priority:** P1 | **Owner:** Backend

---

#### US5.4: Web UI - Upload Page
**Description:**  
As a **user**, I want to easily upload a drawing so that I can validate it.

**Acceptance Criteria:**
- Drag-and-drop zone with file preview
- Alternative: Browse button
- File type/size validation with clear error messages
- Progress bar for large files (>10MB)
- Success toast notification with drawing_id
- Link to status/report page

**Story Points:** 5 | **Priority:** P0 | **Owner:** Frontend

---

#### US5.5: Web UI - Report Page
**Description:**  
As a **design engineer**, I want to view my validation report with all details.

**Acceptance Criteria:**
- Tabbed interface: Summary | Zones | Violations | Details
- Summary tab:
  - Status (PASS / FAIL / REVIEW) with color coding
  - Violation breakdown by severity
  - Quick stats (zones detected, errors found)
- Violations tab:
  - List view with severity, rule, message
  - Filter: Severity, rule category, status
  - Sort: by severity, alphabetical
- Download buttons: JSON, HTML, CSV, PDF

**Story Points:** 8 | **Priority:** P0 | **Owner:** Frontend

---

#### US5.6: Web UI - Dashboard (Historical Tracking)
**Description:**  
As a **project manager**, I want to see all my validations in one place so that I can track project progress.

**Acceptance Criteria:**
- Show recent validations (last 30 days)
- Columns: Drawing name, status, date, violation count
- Filters: Status, date range, project
- Statistics: Pass rate (%), avg violations, trend chart
- Batch upload link

**Story Points:** 5 | **Priority:** P1 | **Owner:** Frontend

---

**Epic 5 Summary:**
- **Total Story Points:** 34
- **Duration:** 3 weeks
- **Team:** 2 people (1 frontend, 1 backend)
- **Deliverables:** Report generators (JSON, HTML, CSV), web UI (5 pages)

---

## EPIC 6: RAG SYSTEM (ISO NORMS KNOWLEDGE BASE)

**Goal:** Build conversational knowledge base for ISO standards queries; reduce need for manual norm lookup

**Business Value:**
- Expert support tool (reduce time on standard research)
- Compliance documentation
- User education

### User Stories

#### US6.1: Build ISO Norms Knowledge Base
**Description:**  
As a **knowledge curator**, I need to compile ISO standards into a searchable knowledge base so that users can query them.

**Acceptance Criteria:**
- Sources:
  - Veritas synthesis (30 weld standards)
  - ISO open documents (ISO 286-1, 1101, 5817, 13920, etc.)
  - Client checklists (codified as markdown)
  - Technical glossary (100+ terms)
- Format: Markdown files, 5K-20K tokens each
- Content: Definitions, examples, use cases
- Version control: Git; tracked updates

**Story Points:** 8 | **Priority:** P1 | **Owner:** Knowledge Curator

---

#### US6.2: Embed & Index Knowledge Base
**Description:**  
As a **RAG system**, I need to embed documents into vector space so that I can retrieve similar content for user queries.

**Acceptance Criteria:**
- Embedding model: sentence-transformers/all-MiniLM-L6-v2
- Vector DB: FAISS (local) or Pinecone (cloud)
- Index: 100+ documents
- Similarity search: Top-k retrieval (k=3-5)
- Latency: <500ms per query

**Technical Notes:**
- Use LangChain for abstraction
- Batch embedding: Process 100 docs in <5 minutes

**Story Points:** 5 | **Priority:** P1 | **Owner:** Backend + ML Engineer

---

#### US6.3: RAG Query API (Generate Answers)
**Description:**  
As a **user**, I want to ask a question about ISO standards and get a relevant answer.

**Acceptance Criteria:**
- Input: Natural language question (e.g., "Is M6 socket cap screw per ISO 4762?")
- Process:
  1. Embed question
  2. Retrieve top-k similar documents
  3. Feed to LLM (optional: GPT-4 for answer synthesis)
  4. Return: Answer + sources + confidence score
- Output: {answer, sources: [{doc, relevance_score}], confidence}
- Latency: <2s

**Story Points:** 8 | **Priority:** P1 | **Owner:** Backend + ML Engineer

---

#### US6.4: RAG Chat UI (Web Interface)
**Description:**  
As a **design engineer**, I want a chat interface to ask questions about ISO standards.

**Acceptance Criteria:**
- Chat bubble interface (question/answer)
- Input: Text box with send button
- Output: Formatted answer + source links (clickable)
- History: Show past questions (session)
- Suggestions: "Common questions" dropdown

**Story Points:** 5 | **Priority:** P1 | **Owner:** Frontend

---

**Epic 6 Summary:**
- **Total Story Points:** 26
- **Duration:** 2 weeks
- **Team:** 2 people (1 backend, 1 frontend)
- **Deliverables:** Knowledge base (100+ docs), RAG API, chat UI

---

## EPIC 7: EXPERT WORKFLOW & FEEDBACK LOOP

**Goal:** Manage expert review queue; record decisions; improve system via feedback

**Business Value:**
- Handle ambiguous cases safely (expert validation)
- Continuous improvement (feedback loop)
- Compliance via expert sign-off

### User Stories

#### US7.1: Expert Review Dashboard
**Description:**  
As a **subject matter expert**, I want to see drawings that need manual review so that I can make informed decisions.

**Acceptance Criteria:**
- Dashboard shows: List of drawings with status = REVIEW
- Columns: Drawing ID, rule violated, severity, submission date, status
- Filters: Severity, rule, date range, reviewer
- Sort: By severity (desc), date (desc)
- Detail page: Show flagged rule + system reasoning + context (related notes, OCR confidence)

**Story Points:** 5 | **Priority:** P1 | **Owner:** Frontend

---

#### US7.2: Expert Decision Interface
**Description:**  
As a **domain expert**, I want to record my decision (approve/override/request info) so that the system learns from my judgment.

**Acceptance Criteria:**
- Form: Radio buttons (Approve / Override / Request Info)
- Text field: Rationale (max 500 chars)
- Confidence scale: 1-5 stars
- Submit → Record to database with timestamp + user_id
- Success notification

**Story Points:** 3 | **Priority:** P1 | **Owner:** Frontend

---

#### US7.3: Feedback Analytics & Rule Refinement
**Description:**  
As a **product owner**, I need to track expert agreement rates so that I can identify rules needing refinement.

**Acceptance Criteria:**
- Weekly report: "Rule X accuracy: 92% (system ✓ = expert ✓ in 92% of cases)"
- Flag: Rules with <80% accuracy
- Action: Auto-notify rules architect; trigger retraining
- Trend: Show accuracy over time
- Segment: By drawing type, severity level

**Story Points:** 5 | **Priority:** P1 | **Owner:** Backend + Analytics

---

#### US7.4: Learning Loop - Retrain Model
**Description:**  
As a **ML engineer**, I need to incorporate expert feedback into model retraining so that the system continuously improves.

**Acceptance Criteria:**
- Trigger: Weekly batch (every Monday) or if accuracy drops >5%
- Process:
  1. Collect expert decisions from prior week
  2. Generate synthetic training data (augment)
  3. Retrain model on combined dataset (prior + new feedback)
  4. Validate on holdout set
  5. If metrics improve, deploy new model version
- Output: New model version + metrics report

**Story Points:** 8 | **Priority:** P1 | **Owner:** ML Engineer + DevOps

---

**Epic 7 Summary:**
- **Total Story Points:** 21
- **Duration:** 2 weeks
- **Team:** 2 people (1 frontend, 1 backend + analytics)
- **Deliverables:** Expert dashboard, feedback recording, analytics

---

## EPIC 8: INTEGRATION & DEPLOYMENT

**Goal:** Package system for production; set up CI/CD; deploy to cloud; integrate with external systems

**Business Value:**
- Live system; revenue-generating
- Automated testing + deployment reduces risk
- Integration unlocks value in adjacent systems

### User Stories

#### US8.1: Docker Containerization
**Description:**  
As a **DevOps engineer**, I need to package the system into Docker containers so that it can run consistently across environments.

**Acceptance Criteria:**
- Dockerfile for API service (FastAPI)
- Dockerfile for worker service (Celery)
- docker-compose.yml for local development (includes DB, cache, etc.)
- Image size: <2GB for production
- Security: Non-root user, minimal base image (python:3.11-slim)

**Story Points:** 5 | **Priority:** P1 | **Owner:** DevOps

---

#### US8.2: CI/CD Pipeline (GitHub Actions)
**Description:**  
As a **developer**, I need automated testing + building so that I can deploy changes safely.

**Acceptance Criteria:**
- Trigger: On PR + merge to main
- Steps:
  1. Lint (black, flake8, isort)
  2. Unit tests (pytest, >80% coverage)
  3. Integration tests (docker-compose)
  4. Security scan (Snyk, bandit)
  5. Build Docker image → push to ECR
  6. Deploy to staging → E2E tests
- Status: Fail fast if any step fails
- Notifications: Slack alerts for failures

**Story Points:** 8 | **Priority:** P1 | **Owner:** DevOps + Backend

---

#### US8.3: Infrastructure as Code (Terraform)
**Description:**  
As a **cloud architect**, I need to define infrastructure in code so that environments are reproducible and versioned.

**Acceptance Criteria:**
- Terraform modules for:
  - ECS cluster (API + worker services)
  - RDS (PostgreSQL, multi-AZ)
  - ElastiCache (Redis)
  - S3 (file storage)
  - VPC, security groups, IAM roles
- Environment configs: dev, staging, production
- Secrets: AWS Secrets Manager integration

**Story Points:** 8 | **Priority:** P1 | **Owner:** DevOps

---

#### US8.4: Production Deployment & Monitoring
**Description:**  
As a **operator**, I need to deploy to production safely with monitoring so that I can respond to issues quickly.

**Acceptance Criteria:**
- Deployment: Blue-green or canary (10% traffic initially)
- Monitoring:
  - API uptime (SLA: 99.5%)
  - Error rate (alert if >0.5%)
  - Latency (p99 <2.5s)
  - GPU utilization
  - Database connection pool
- Logging: ELK stack; searchable logs
- Alerting: PagerDuty / Slack integration

**Story Points:** 8 | **Priority:** P1 | **Owner:** DevOps + Backend

---

#### US8.5: CATIA Integration (Phase 2 Preview)
**Description:**  
As a **CATIA user**, I want to validate my drawing directly from CATIA so that I don't need to switch tools.

**Acceptance Criteria:**
- CATIA add-in / macro (VB.NET)
- Trigger: Right-click drawing → "Validate with ISO Validator"
- Workflow: Upload drawing → poll status → show results in CATIA notification
- Fallback: Link to web UI if results need detailed review

**Story Points:** 13 | **Priority:** P2 | **Owner:** Backend + DevOps | **Timeline:** Phase 2

---

#### US8.6: DSM Integration (Phase 2 Preview)
**Description:**  
As a **DSM user**, I want validation results linked to my design calculations so that I can track compliance.

**Acceptance Criteria:**
- API: Accept validation result + calculation reference
- Store: Link validation → calculation in DSM
- UI: Show "Drawing AS-001 validated ✓" in DSM interface
- Compliance: Audit trail of all validations

**Story Points:** 8 | **Priority:** P2 | **Owner:** Backend | **Timeline:** Phase 2

---

**Epic 8 Summary:**
- **Total Story Points:** 50 (excluding Phase 2 integrations: 21 P0 + 29 P2)
- **Duration:** 2 weeks (MVP), +2 weeks (Phase 2 integrations)
- **Team:** 2-3 people (1-2 DevOps, 1 backend)
- **Deliverables:** Docker images, CI/CD pipeline, Terraform configs, live deployment

---

## PHASE 2: PERFORMANCE OPTIMIZATION (Future Scope)

**Goal:** Scale system; improve accuracy; expand dataset

**Epics (TBD):**
- E9: Large-scale inference optimization (batch processing, model quantization)
- E10: Dataset expansion (500+ drawings, continuous feedback loop)
- E11: Advanced rule engine (machine-learned rule weighting)
- E12: Multi-language support (French, German, Spanish)
- E13: Mobile app (native iOS/Android)

---

## EPIC SEQUENCING & CRITICAL PATH

```
Sprint 0 (Week 1-2): Planning & Setup
  └─ Scope lock, team onboarding, infrastructure setup

Sprint 1 (Week 3-5): Data & Models (E1, E2)
  └─ Epic 1: Data ingestion pipeline
  └─ Epic 2: YOLO + Donut training (parallel)

Sprint 2 (Week 6-8): Core Extraction (E3)
  └─ Epic 3: Data extraction pipeline
  └─ Dependency: Needs E2 (trained models)

Sprint 3 (Week 9-12): Rules & Validation (E4)
  └─ Epic 4: Rule engine
  └─ Dependency: Needs E3 (structured data)

Sprint 4 (Week 13-15): Reporting & UI (E5)
  └─ Epic 5: Reports + web UI
  └─ Epic 6: RAG system (parallel)
  └─ Dependency: Needs E4 (validation results)

Sprint 5 (Week 16-18): Expert Workflow & Integration (E7, E8)
  └─ Epic 7: Expert dashboard
  └─ Epic 8: Deployment
  └─ Dependency: Needs E5 (UI framework)

Sprint 6 (Week 19-21): Testing & Production Launch
  └─ Full E2E testing
  └─ Performance tuning
  └─ Customer UAT
  └─ Production deployment

MVP Release: End of Week 21
Phase 2 Planning: Week 22+
```

---

## SUCCESS METRICS

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Model Accuracy** | mAP50-95 ≥ 0.85 | YOLO + Donut test metrics |
| **Rule Accuracy** | >90% expert agreement | Weekly feedback analytics |
| **System Availability** | 99.5% uptime | CloudWatch SLA |
| **User Adoption** | 80% of design team using system | Weekly DAU tracking |
| **Time Savings** | 5 hours/week per engineer | Survey + time tracking |
| **Compliance Pass Rate** | Stable >95% after tuning | Aggregate results |

---

**END OF EPICS DOCUMENT**

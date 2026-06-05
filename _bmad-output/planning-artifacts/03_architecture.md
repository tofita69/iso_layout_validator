# SOLUTION ARCHITECTURE DOCUMENT
## ISO Technical Drawing Validator System

**Document Version:** 1.0  
**Prepared by:** Solution Architect (Winston)  
**Based on:** requirements.md + PRD.md  
**Status:** ⏳ Draft (Pending Security Review)

---

## EXECUTIVE SUMMARY

The ISO Technical Drawing Validator is a cloud-native, AI-powered system that automates the detection and validation of mechanical engineering drawings. It uses proven computer vision (YOLOv11-obb) and OCR (Donut) models to extract drawing elements, validates them against codified ISO rules, and generates structured reports. A hybrid human-AI workflow ensures expert review for ambiguous cases.

**Architecture Principles:**
- **Modularity:** Decoupled services (detection, OCR, rules, reporting)
- **Scalability:** Stateless API; horizontal scaling; async processing
- **Reliability:** Graceful degradation; fallback mechanisms
- **Security:** Defense-in-depth; encryption; RBAC
- **Maintainability:** Clear interfaces; comprehensive logging; version-controlled models

---

## 1. HIGH-LEVEL SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  Web UI (React/Vue)  │  Mobile Browser  │  External API Clients│
└────────┬──────────────────────────────────────┬─────────────────┘
         │                                      │
         ▼                                      ▼
┌────────────────────────────────────┬────────────────────────────┐
│      API GATEWAY / LOAD BALANCER    │  CDN (Static Assets)     │
│   (Rate Limiting, Auth, Routing)    │                          │
└────────┬──────────────────────────────────────┴─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                            │
├──────────────────┬─────────────────┬──────────────┬─────────────┤
│  Drawing API     │  Rule Engine    │  Report Gen  │  RAG System │
│  (FastAPI)       │  (Rules Config) │  (Template)  │  (LangChain)│
└──────┬───────────┴─────────┬───────┴───────┬──────┴─────────────┘
       │                     │               │
       ▼                     ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI/ML INFERENCE LAYER                         │
├──────────────────┬──────────────────────────────────────────────┤
│ YOLO Detector    │  Donut OCR    │  Data Extractors             │
│ (Zone Detection) │  (Text Parse) │  (Struct. Parsing)           │
└──────┬───────────┴──────┬────────┴──────────────────┬───────────┘
       │                  │                          │
       └──────────────────┴──────────────────────────┘
              GPU Memory / Model Cache
              (Local or Cloud GPU)
              
┌─────────────────────────────────────────────────────────────────┐
│                    DATA & PERSISTENCE LAYER                      │
├──────────────────┬──────────────────┬───────────────────────────┤
│  PostgreSQL      │  Redis Cache     │  File Storage (S3/GCS)    │
│  (Drawings,      │  (Session,       │  (Uploads, Reports,       │
│   Results,       │   Model Cache)   │   Model Artifacts)        │
│   Audit Log)     │                  │                           │
└──────────────────┴──────────────────┴───────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  MONITORING & OPERATIONS                         │
├──────────────────┬──────────────────┬───────────────────────────┤
│  Prometheus      │  ELK Stack       │  Grafana Dashboards       │
│  (Metrics)       │  (Logs)          │  (Visualization)          │
└──────────────────┴──────────────────┴───────────────────────────┘
```

---

## 2. RECOMMENDED TECH STACK

### AI/ML Components
| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Zone Detection** | YOLOv11-obb (PyTorch) | 89% precision, 99% recall; OBB matches rectangular drawings perfectly; outperforms Florence-2 + SAM2 |
| **OCR** | Donut (fine-tuned) | 89.2% precision, 99.2% recall (From Drawings to Decisions paper); lower hallucination (10.8%) vs. Florence-2 (21.6%) |
| **Data Extraction** | Custom parser + Regex | Deterministic parsing for structured fields (cartouche, dimensions, etc.) |
| **RAG Framework** | LangChain + FAISS | Modular; supports vector DB + knowledge base search; integrates with LLM for answer generation |

### Backend Services
| Component | Technology | Justification |
|-----------|-----------|---------------|
| **API Framework** | FastAPI (Python) | Async; auto-OpenAPI docs; type hints; fits with ML stack |
| **Job Queue** | Celery + Redis | Async task processing; retry logic; priority queues |
| **Authentication** | OAuth2 (python-jose) | Standards-based; integrates with corporate SSO |
| **Web Framework** | React 18 | Component-based; fast; large ecosystem |
| **Styling** | Tailwind CSS | Utility-first; responsive; minimal CSS bloat |

### Data & Persistence
| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Primary DB** | PostgreSQL 14+ | ACID compliance; JSON support; proven reliability |
| **Cache** | Redis 7+ | Sub-millisecond latency; model cache; session store |
| **File Storage** | AWS S3 / GCS | Scalable; versioned; lifecycle policies |
| **Vector DB** | Pinecone or FAISS | RAG knowledge base embeddings |

### Infrastructure
| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Container** | Docker 24+ | Reproducible; isolation; ecosystem maturity |
| **Orchestration** | Kubernetes (managed) | Auto-scaling; self-healing; industry standard |
| **Cloud Provider** | AWS (or GCP/Azure) | GPU availability; managed services; security |
| **CI/CD** | GitHub Actions + ArgoCD | Git-native; simple; GitOps for deployment |
| **IaC** | Terraform | Cloud-agnostic; version-controlled infrastructure |

### Monitoring & Logging
| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Metrics** | Prometheus | Standard; time-series; alerting |
| **Logs** | ELK Stack (Elasticsearch + Logstash + Kibana) | Distributed logging; full-text search; dashboards |
| **APM** | Jaeger (optional) | Distributed tracing; latency visualization |

---

## 3. SERVICE BREAKDOWN

### Service A: Drawing Intake Service
**Responsibility:** Handle file upload, preprocessing, metadata extraction  
**Technology:** FastAPI + Celery  
**Key Endpoints:**
- `POST /api/v1/drawings` — Upload drawing; trigger async processing
- `GET /api/v1/drawings/{drawing_id}/status` — Poll processing status
- `GET /api/v1/drawings/{drawing_id}` — Retrieve drawing metadata

**Processing Steps:**
1. Validate file type (PDF, PNG)
2. Normalize image (rotation, denoise, enhance contrast)
3. Store original + processed image (S3)
4. Queue detection job (Celery)
5. Return job_id to client

**Error Handling:**
- File size > 50MB: Reject
- Invalid file type: Reject
- OCR failure: Log; mark region as "manual review needed"
- Timeout: Retry logic; max 3 attempts

---

### Service A.1: Drawing Classification Service (NEW)
**Responsibility:** Automatically classify drawing type (Pièce/Mécanosoudé/Sub-ensemble); route to correct validation rules  
**Technology:** Heuristic classifier + ensemble rules  
**Key Endpoints:**
- `POST /api/v1/classify_drawing` — Classify preprocessed image
- `GET /api/v1/classification_models/rules` — Retrieve classification rules

**Classification Logic:**
1. Detect specific markers for each drawing type:
   - **Pièce (076-A):** Single part, no weld symbols, material spec present
   - **Mécanosoudé (077-A):** Weld symbols detected, CNE/NOTA reference, assembly of parts
   - **Sub-ensemble (078-A):** BOM table detected, assembly instructions, part list
2. Use OCR confidence + zone patterns
3. Confidence threshold: >85% → Auto-classify; <85% → Route to manual review
4. Output: {type, confidence, markers_matched, audit_log}

**Routing:**
- Type A → Load 076-A rules (59 items)
- Type B → Load 077-A rules (55 items) + enable NOTA validation
- Type C → Load 078-A rules (56 items) + enable BOM validation

**Error Handling:**
- Ambiguous classification: Create "REVIEW_NEEDED" task for expert
- Confidence <50%: Require manual override before proceeding

---

### Service A.2: External Document Fetcher Service (NEW)
**Responsibility:** Fetch & cache external standards documents (NOTA, ISO references)  
**Technology:** Document registry (YAML) + file cache (S3)

**Documents Managed:**
- **ECM_Note Qualité en soudage_26337519-1-0_07-2025.pdf** (Weld specifications)
- ISO standard references (embedded in rules)
- Material nomenclature registry
- Treatment specification codes

**API Endpoints:**
- `GET /api/v1/documents/{doc_id}` — Fetch document
- `GET /api/v1/documents/version/{doc_id}` — Get document version history

**Caching:** Redis cache (TTL: 24 hours); S3 archive for audit trail

---

### Service A.3: Standards Registry Service (NEW)
**Responsibility:** Maintain registry of ISO standards, material codes, treatment specifications  
**Technology:** YAML registry + PostgreSQL

**Registry Contents:**
- ISO standard codes with versions & effective dates
- EN material nomenclature (material codes ↔ descriptions)
- Surface treatment codes (anodize, paint, galvanize, etc.)
- Weld symbol reference (ISO 1101)

**API Endpoints:**
- `GET /api/v1/standards/{standard_code}` — Look up standard
- `GET /api/v1/materials/{material_code}` — Validate material
- `POST /api/v1/standards/check_compatibility` — Check if two standards are compatible

---

### Service B: Zone Detection Service
**Responsibility:** Run YOLO model; output bounding boxes  
**Technology:** PyTorch + YOLOv11-obb  
**Infrastructure:** GPU (CUDA 11.8+ or ROCm)

**Model Specifications:**
- Input: 1024x1024 normalized image
- Output: Bboxes + classes + confidence scores (OBB format: 8 corner points)
- Classes: 8 types (cartouche, notes, gdt_frames, dimensions, weld_symbols, surface_finish, revision_table, drawing_area)
- Batch size: 8 (training); 1 (inference for latency)
- Latency: ~800ms (GPU A100); ~2000ms (GPU K80)

**Model Versioning:**
- Current: v1.0 (trained on 50 plans)
- Track version in output; audit trail logs model version used
- Weekly auto-retraining on new feedback data

---

### Service C: OCR & Text Extraction Service
**Responsibility:** Extract text from detected zones; parse structured data  
**Technology:** Donut (HuggingFace) + custom parsers

**Pipeline:**
1. Crop image to bounding box (from YOLO)
2. Apply fine-tuned Donut model
3. Post-process raw OCR (regex + domain rules):
   - Parse cartouche fields (regex patterns)
   - Parse dimensions (extract value + unit + tolerance)
   - Parse GD&T symbols (ISO 1101 symbol matching)
   - Parse weld specs (ISO codes)
4. Output structured JSON

**Example Output:**
```json
{
  "zone": "cartouche",
  "confidence": 0.94,
  "fields": {
    "designation": {"value": "ADMISSION SHAFT", "confidence": 0.98},
    "reference": {"value": "AS-001", "confidence": 0.96},
    "index": {"value": "A", "confidence": 0.99},
    "scale": {"value": "1:2", "confidence": 0.92},
    "date": {"value": "2026-05-07", "confidence": 0.95}
  }
}
```

---

### Service D: Rule Validation Engine
**Responsibility:** Apply codified rules; return pass/fail/review decisions  
**Technology:** Python + rule engine (simple if/then; can upgrade to Drools/business rules engine later)

**Rule Structure:**
```yaml
rules:
  - id: "cart_001"
    name: "Cartouche Completeness"
    severity: CRITICAL
    condition: "cartouche.fields.designation exists AND cartouche.fields.reference exists"
    message: "Cartouche missing required field: {field}"
    
  - id: "dim_001"
    name: "Dimensional Consistency"
    severity: HIGH
    condition: "dimensions.tolerance_upper >= dimensions.tolerance_lower"
    message: "Tolerance range invalid: upper < lower"
```

**Rule Categories (20+ rules):**
1. **Cartouche Rules (5):** Required fields, format, mass logic
2. **Dimensional Rules (4):** Functional vs. manufacturing, hors-tout format, consistency
3. **Tolerance Rules (3):** ISO 2768 vs. 13920 coherence
4. **GD&T Rules (3):** Symbol validity, datum definition, placement
5. **Weld Rules (3):** NOTA ↔ CNE alignment, CND levels
6. **Surface Finish Rules (2):** Environment criteria
7. **Structural Rules (2):** No overlaps, mass only on final

**Execution:**
- For each extracted zone: evaluate applicable rules
- Collect violations; assign severity + context
- Return overall status: PASS | FAIL | REVIEW

---

### Service E: Anomaly Detection Engine
**Responsibility:** Identify unexpected patterns; flag for expert review  
**Technology:** Heuristics + statistical baseline

**Anomalies:**
- Missing expected zone (cartouche not detected)
- Conflicting standards (both ISO 2768 + 13920 without justification)
- Dimensional outliers (tolerance > 3σ from training distribution)
- Rare conditions (mass on intermediate plan; stabilization not flagged)

**Output:** Anomaly list with confidence score; route to REVIEW queue

---

### Service F: Report Generation Service
**Responsibility:** Aggregate validation results; render HTML/JSON/CSV  
**Technology:** Jinja2 (templating) + Python

**Outputs:**
1. **JSON:** Structured schema (zones, extractions, violations, recommendations)
2. **HTML:** Interactive report with image overlays + clickable violations
3. **CSV:** Bulk export for spreadsheet analysis

**Rendering:**
- HTML template: base.html + modules (summary, violations, zones, history)
- Inject validation data; highlight violations by severity (color-coded)
- Embed thumbnail image; clickable links to zoom regions

---

### Service G: Expert Workflow Service
**Responsibility:** Manage queue; record decisions; feedback loop  
**Technology:** FastAPI + WebSocket (real-time updates)

**Dashboard:**
- List of REVIEW_NEEDED drawings (sortable, filterable)
- Detail view: Show flagged rule + system decision + context
- Decision UI: Approve / Override / Request more info
- Record: Decision + rationale + timestamp

**Feedback Integration:**
- Weekly aggregate: "Rule X accuracy: 92%"
- Trigger retraining if accuracy drops >5%
- Learning curve: System improves with expert corrections

---

### Service H: RAG (Retrieval-Augmented Generation) System
**Responsibility:** Knowledge base search; ISO standards Q&A  
**Technology:** LangChain + FAISS + OpenAI GPT-4 (optional)

**Knowledge Base:**
- Veritas synthesis (30 weld standards)
- ISO open references (ISO 286-1, 1101, 5817, 13920, etc.)
- Client checklists (codified as markdown)
- Technical glossary (bolt, screw, nut, datum, etc.)

**Pipeline:**
1. Embed documents using sentence-transformers
2. Store embeddings in FAISS (or Pinecone)
3. Query: User question → retrieval (top-k similar docs) → LLM answer
4. Answer includes: direct answer + source reference + confidence

**Example Query:**
```
Q: "Is M6 socket-head cap screw compliant with ISO 4762?"
A: "Yes. ISO 4762 specifies dimensions and properties for metric socket head cap screws.
   M6 is defined in ISO 4762 with nominal diameter 6mm, head height 5.7mm, etc.
   Source: ISO 4762:2004 (Table 1) | Confidence: 0.98"
```

---

## 4. BACKEND ARCHITECTURE

### API Design (OpenAPI 3.0)

**Base URL:** `https://validator.internal.company.com/api/v1`

#### Endpoint 1: POST /drawings (Upload)
```yaml
operationId: upload_drawing
summary: Upload drawing for validation
requestBody:
  content:
    multipart/form-data:
      schema:
        type: object
        properties:
          file:
            type: string
            format: binary
            description: Drawing file (PDF, PNG)
          project_id:
            type: string
            description: Optional project reference
parameters:
  - name: Authorization
    in: header
    required: true
    schema:
      type: string
      example: "Bearer {access_token}"
responses:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            drawing_id:
              type: string
            job_id:
              type: string
            status:
              type: string
              enum: [queued, processing]
            created_at:
              type: string
              format: date-time
```

#### Endpoint 2: GET /drawings/{drawing_id}/status (Poll)
```yaml
operationId: get_drawing_status
summary: Poll validation job status
parameters:
  - name: drawing_id
    in: path
    required: true
    schema:
      type: string
responses:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            drawing_id:
              type: string
            status:
              type: string
              enum: [queued, processing, complete, failed]
            progress:
              type: number
              example: 0.65
            eta_seconds:
              type: integer
              example: 45
            result:
              $ref: '#/components/schemas/ValidationResult'
              nullable: true
```

#### Endpoint 3: GET /drawings/{drawing_id}/report (Fetch Report)
```yaml
operationId: get_drawing_report
summary: Retrieve validation report
parameters:
  - name: drawing_id
    in: path
    required: true
  - name: format
    in: query
    schema:
      type: string
      enum: [json, html, csv]
      default: json
responses:
  200:
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ValidationResult'
  default:
    content:
      text/html:
        schema:
          type: string
          format: binary
```

#### Endpoint 4: POST /drawings/{drawing_id}/feedback (User Correction)
```yaml
operationId: submit_feedback
summary: User corrects system extraction or decision
requestBody:
  content:
    application/json:
      schema:
        type: object
        properties:
          zone_id:
            type: string
          field_name:
            type: string
          corrected_value:
            type: string
          reason:
            type: string
          rule_id:
            type: string
            nullable: true
responses:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            feedback_id:
              type: string
            status:
              type: string
              enum: [recorded, acknowledged]
```

#### Endpoint 5: POST /rag/ask (RAG Query)
```yaml
operationId: ask_iso_question
summary: Query ISO standards knowledge base
requestBody:
  content:
    application/json:
      schema:
        type: object
        properties:
          question:
            type: string
            example: "Is M6 socket-head cap screw per ISO 4762?"
responses:
  200:
    content:
      application/json:
        schema:
          type: object
          properties:
            answer:
              type: string
            sources:
              type: array
              items:
                type: object
                properties:
                  document:
                    type: string
                  relevance_score:
                    type: number
            confidence:
              type: number
```

---

## 5. FRONTEND ARCHITECTURE

### Tech Stack
- **Framework:** React 18 + TypeScript
- **State Management:** TanStack Query (async) + Zustand (local)
- **Routing:** React Router v6
- **UI Components:** Headless UI + Tailwind CSS (custom component library)
- **Visualization:** react-image-zoom (image interaction) + react-canvas-draw (markup)
- **Forms:** React Hook Form + Zod validation

### Page Structure

```
/pages
  ├── Dashboard.tsx         # Overview; recent validations
  ├── Upload.tsx            # File upload; drag-and-drop
  ├── Report.tsx            # Main report view; tabbed UI
  │  ├── Summary.tsx        # Pass/fail summary; metrics
  │  ├── Zones.tsx          # Detected zones; hover highlights
  │  ├── Violations.tsx     # Violations list; filterable
  │  └── Recommendations.tsx # Suggested fixes
  ├── ExpertQueue.tsx       # For reviewers; batch dashboard
  ├── RAGChat.tsx           # ISO standards Q&A
  └── History.tsx           # Historical validations

/components
  ├── UploadZone.tsx
  ├── ReportViewer.tsx
  ├── ViolationCard.tsx
  ├── ExpertDecisionForm.tsx
  └── RAGChatbot.tsx

/services
  ├── api.ts               # API client (axios + interceptors)
  ├── auth.ts              # OAuth2 flow
  └── rag.ts               # RAG queries
```

### Key UI Interactions

**Upload Flow:**
1. User drags file into drop zone
2. File validated client-side (type, size)
3. Upload button enabled
4. POST /api/v1/drawings
5. Redirect to Status page (job_id in URL)
6. Poll status every 1 second
7. When complete, auto-redirect to Report

**Report Viewing:**
1. Show tabbed interface: Summary | Zones | Violations | Recommendations
2. Violations displayed as list with severity color-coding
3. Click violation → highlight region on image thumbnail + zoom
4. Show OCR confidence; allow inline correction
5. Download button (JSON, HTML, CSV)

**Expert Queue:**
1. Filter by severity, rule category, date
2. Click drawing → detail page
3. Show system decision + context (OCR + related notes)
4. Buttons: Approve | Override | Request More Info
5. Text field for rationale
6. Submit → record decision + log to feedback system

---

## 6. DATABASE DESIGN

### PostgreSQL Schema (Simplified)

```sql
-- Core tables
CREATE TABLE drawings (
  drawing_id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  project_id VARCHAR(255),
  filename VARCHAR(255),
  file_path VARCHAR(512),  -- S3 path
  status ENUM('queued', 'processing', 'complete', 'failed'),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  model_version VARCHAR(50),
  processing_time_ms INTEGER
);

CREATE TABLE validation_results (
  result_id UUID PRIMARY KEY,
  drawing_id UUID FOREIGN KEY,
  zones_detected JSONB,  -- Array of {type, bbox, confidence}
  extractions JSONB,     -- Cartouche, dimensions, specs
  violations JSONB,      -- Array of {rule_id, severity, message}
  overall_status ENUM('PASS', 'FAIL', 'REVIEW'),
  pass_rate FLOAT,
  created_at TIMESTAMP DEFAULT NOW(),
  
  FOREIGN KEY (drawing_id) REFERENCES drawings(drawing_id)
);

CREATE TABLE zone_detections (
  detection_id UUID PRIMARY KEY,
  result_id UUID FOREIGN KEY,
  zone_type VARCHAR(50),  -- cartouche, dimensions, gdt, etc.
  bbox_xyxy FLOAT[4],     -- [x1, y1, x2, y2]
  bbox_obb FLOAT[8],      -- OBB: [x1, y1, x2, y2, ..., rotation]
  confidence FLOAT,
  ocr_text TEXT,
  ocr_confidence FLOAT,
  
  FOREIGN KEY (result_id) REFERENCES validation_results(result_id)
);

CREATE TABLE validation_rules (
  rule_id UUID PRIMARY KEY,
  rule_category VARCHAR(50),  -- cartouche, dimensions, gdt, etc.
  name VARCHAR(255),
  condition TEXT,
  severity ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE expert_decisions (
  decision_id UUID PRIMARY KEY,
  result_id UUID FOREIGN KEY,
  rule_id UUID FOREIGN KEY,
  system_decision ENUM('PASS', 'FAIL', 'REVIEW'),
  expert_decision ENUM('PASS', 'FAIL', 'REVIEW'),
  expert_id UUID,
  rationale TEXT,
  confidence_score FLOAT,
  created_at TIMESTAMP,
  
  FOREIGN KEY (result_id) REFERENCES validation_results(result_id),
  FOREIGN KEY (rule_id) REFERENCES validation_rules(rule_id)
);

CREATE TABLE feedback (
  feedback_id UUID PRIMARY KEY,
  drawing_id UUID FOREIGN KEY,
  zone_id VARCHAR(255),
  field_name VARCHAR(255),
  system_value TEXT,
  corrected_value TEXT,
  user_id UUID,
  reason TEXT,
  created_at TIMESTAMP,
  
  FOREIGN KEY (drawing_id) REFERENCES drawings(drawing_id)
);

CREATE TABLE audit_log (
  log_id UUID PRIMARY KEY,
  user_id UUID,
  action VARCHAR(50),  -- upload, view_report, submit_feedback
  drawing_id UUID,
  details JSONB,
  timestamp TIMESTAMP DEFAULT NOW(),
  ip_address INET
);

-- Indexing
CREATE INDEX idx_drawings_user ON drawings(user_id);
CREATE INDEX idx_drawings_created ON drawings(created_at);
CREATE INDEX idx_validation_drawing ON validation_results(drawing_id);
CREATE INDEX idx_expert_decisions_result ON expert_decisions(result_id);
CREATE INDEX idx_audit_user ON audit_log(user_id);
```

### Caching Strategy

**Redis Key Structure:**
```
drawing:{drawing_id}:metadata   → Drawing metadata (TTL: 24h)
drawing:{drawing_id}:report     → Validated report (TTL: 7d)
model:yolo:v1.0                 → YOLO model weights (TTL: 30d)
model:donut:v1.0                → Donut model weights (TTL: 30d)
session:{session_id}            → User session (TTL: 1h)
rag:embeddings:{doc_id}         → RAG embeddings (TTL: 30d)
```

---

## 7. AUTHENTICATION & AUTHORIZATION

### OAuth2 Flow (Corporate SSO)

**Setup:**
1. Register app in corporate OAuth2 provider (e.g., Okta, Azure AD)
2. Client ID + Secret stored in secrets manager
3. Redirect URI: `https://validator.internal.company.com/auth/callback`

**Login Flow:**
1. User clicks "Login"
2. Redirects to SSO provider
3. User authenticates
4. Callback to app with authorization code
5. Exchange code for access token (backend)
6. Token stored in secure httpOnly cookie
7. Set up refresh token rotation

**Token Claims:**
```json
{
  "sub": "user123",
  "email": "alice@company.com",
  "name": "Alice Engineer",
  "groups": ["designers", "validators"],
  "exp": 1234567890
}
```

### RBAC (Role-Based Access Control)

**Roles:**
- **Viewer:** Read-only; view reports
- **Reviewer:** Upload; view reports; submit feedback; approve validations
- **Admin:** Manage rules; manage users; view analytics

**Permission Matrix:**
| Action | Viewer | Reviewer | Admin |
|--------|--------|----------|-------|
| View own reports | ✓ | ✓ | ✓ |
| Upload drawing | ✗ | ✓ | ✓ |
| Approve validation | ✗ | ✓ | ✓ |
| Manage rules | ✗ | ✗ | ✓ |
| View analytics | ✗ | ✗ | ✓ |

**Implementation:** Middleware checks `Authorization` header; extracts claims; validates permissions

---

## 8. API STRATEGY

### Versioning
- Version in URL: `/api/v1/...`
- New major version only if breaking changes
- Deprecation policy: Support N-1 versions for 12 months

### Rate Limiting
- 100 requests/min per user (authenticated)
- 10 requests/min per IP (unauthenticated)
- Burst allowance: +50% for authenticated users

### Error Handling
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Drawing validation failed",
    "details": [
      {"field": "file", "message": "File size exceeds 50MB"}
    ],
    "trace_id": "uuid-for-support"
  }
}
```

---

## 9. CLOUD ARCHITECTURE

### AWS Deployment (Recommended)

**Services:**
- **ECS Fargate:** Stateless API containers (auto-scaling)
- **Lambda:** Asynchronous jobs (detection, OCR, reporting)
- **RDS:** PostgreSQL (multi-AZ; automated backups)
- **ElastiCache:** Redis (cluster mode; auto-failover)
- **S3:** File storage (versioning; lifecycle policies)
- **SageMaker:** Model training + hosting (optional)
- **ALB:** Load balancer (HTTPS termination; rate limiting)
- **CloudFront:** CDN (static assets)
- **EventBridge:** Job scheduling (weekly retraining, cleanups)
- **Secrets Manager:** Store credentials (API keys, DB password)
- **CloudWatch:** Logging + monitoring
- **VPC:** Network isolation (private subnets for DB/cache)

**Diagram:**
```
Internet → CloudFront (CDN) → ALB → ECS Fargate (API pods)
                                ↓ async jobs
                            Lambda (YOLO, Donut)
                                ↓
                    RDS (PostgreSQL) + ElastiCache (Redis)
                                ↓
                            S3 (file storage)
```

### Disaster Recovery
- **RTO:** 1 hour (backup restore)
- **RPO:** 5 minutes (incremental backups)
- **Backup:** Automated daily; 30-day retention
- **Failover:** Multi-AZ RDS; automatic failover

---

## 10. SCALABILITY STRATEGY

### Horizontal Scaling

**API Layer:**
- Stateless FastAPI servers
- Auto-scaling group: min 2, max 20 pods
- Scale metric: CPU >70% or memory >80%
- Target: <2.5s latency (p99)

**ML Inference:**
- Lambda for batch processing
- Concurrent executions: up to 100 jobs
- GPU instances: K80 or A100 (on-demand)
- Model cache: Redis for hot models (99 percentile)

**Database:**
- PostgreSQL read replicas for analytics queries
- Connection pooling: PgBouncer (max 500 connections)
- Sharding future-proof (if >10k draws/day)

### Performance Optimization

| Layer | Optimization |
|-------|-------------|
| **Frontend** | Lazy loading, code splitting, image compression |
| **API** | Async endpoints, caching headers (Cache-Control), query optimization |
| **Database** | Indexing, query planning, connection pooling |
| **ML** | Model quantization (FP16), batch inference, GPU optimization |

---

## 11. SECURITY ARCHITECTURE

### Defense-in-Depth

1. **Network Security:**
   - VPC with private subnets
   - Security groups (inbound: 443 only)
   - WAF rules (rate limiting, SQL injection protection)

2. **Application Security:**
   - Input validation (file type, size)
   - CSRF protection (SameSite cookies)
   - SQL injection prevention (parameterized queries)
   - XSS prevention (output encoding, CSP headers)

3. **Data Security:**
   - TLS 1.2+ in transit
   - AES-256 at rest (S3 + RDS encryption)
   - Encryption keys: AWS KMS managed
   - Secrets rotation: every 90 days

4. **Access Control:**
   - OAuth2 / OIDC (corporate SSO)
   - MFA required for admins
   - RBAC enforced at API level
   - Audit trail immutable (database triggers)

5. **Compliance:**
   - GDPR: Data retention policies (delete after 2 years)
   - ISO 27001 certification roadmap
   - Regular penetration testing (quarterly)
   - Vulnerability scanning (automated weekly)

---

## 12. LOGGING & MONITORING

### Metrics (Prometheus)
```
# Application Metrics
drawing_validation_duration_seconds (histogram)
drawing_validation_errors_total (counter)
zones_detected_per_drawing (gauge)
ocr_accuracy (gauge)
rule_violations_count_by_category (histogram)

# System Metrics
api_request_duration_seconds (histogram)
api_request_errors_total (counter)
database_connection_pool_utilization (gauge)
gpu_memory_utilization_percent (gauge)

# Business Metrics
time_saved_hours_total (counter)
drawings_validated_total (counter)
user_adoption_rate (gauge)
```

### Logging (ELK Stack)
```
Log Fields:
- timestamp
- level (DEBUG, INFO, WARN, ERROR)
- service (api, detector, ocr, rules, etc.)
- trace_id (correlation across services)
- user_id
- drawing_id
- message
- stack_trace (if error)

Log Levels:
- DEBUG: Model inference steps, detailed parsing
- INFO: API requests, job completion
- WARN: Low confidence detections, model performance degradation
- ERROR: Failures, exceptions
```

### Dashboards (Grafana)
1. **System Health:** Uptime, latency (p50/p95/p99), error rate
2. **Model Performance:** Precision, recall, hallucination rate
3. **User Activity:** Daily active users, validations per day, top users
4. **Quality Metrics:** False positive rate, expert decision agreement

---

## 13. DEPLOYMENT ARCHITECTURE

### CI/CD Pipeline (GitHub Actions + ArgoCD)

```
┌─────────────────────────────────────────┐
│   Git Commit (feature branch)            │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  GitHub Actions: Run Tests              │
│  - Linting (black, flake8)               │
│  - Unit tests (pytest)                   │
│  - Integration tests (docker-compose)    │
│  - SAST (Snyk, bandit)                   │
└────────────┬────────────────────────────┘
             │ (all pass)
             ▼
┌─────────────────────────────────────────┐
│  Build Docker Image                      │
│  - Tag with commit SHA                   │
│  - Push to ECR                           │
│  - Scan image (Trivy)                    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Create PR → Code Review                │
└────────────┬────────────────────────────┘
             │ (approved)
             ▼
┌─────────────────────────────────────────┐
│  Merge to Main                           │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Deploy to Staging (ArgoCD)              │
│  - Automated deployment from Git         │
│  - E2E tests (Selenium)                  │
│  - Performance tests (k6)                │
└────────────┬────────────────────────────┘
             │ (tests pass)
             ▼
┌─────────────────────────────────────────┐
│  Manual Approval → Deploy to Production │
│  - Canary deployment (10% traffic)       │
│  - Monitor error rate (5 min window)     │
│  - If error rate OK, roll out 100%       │
│  - If error, rollback automatically      │
└─────────────────────────────────────────┘
```

### Deployment Configuration (Helm)
- **Chart:** iso-validator (templates for API, Worker, etc.)
- **Values:** Environment-specific (dev, staging, prod)
- **GitOps:** ArgoCD syncs from Git; all changes auditable

---

## 14. CI/CD RECOMMENDATIONS

### Tools & Practices
- **Source Control:** Git (GitHub)
- **Code Review:** Pull requests; require 2 approvals
- **Build:** GitHub Actions (parallel jobs)
- **Artifact Registry:** AWS ECR (private)
- **Deployment:** ArgoCD (GitOps)
- **Testing:** pytest (unit), docker-compose (integration), Selenium (E2E)
- **Security:** Snyk (dependencies), Trivy (image), SAST (bandit)
- **Monitoring:** Datadog (real-time alerts during canary)

---

## 15. DATA FLOW DIAGRAMS

### Flow 1: Drawing Upload & Validation

```
┌──────────┐
│  User    │
└────┬─────┘
     │ 1. Upload PDF
     ▼
┌─────────────────────┐
│  Web UI             │
│  /upload            │
└────────┬────────────┘
         │ 2. POST /api/v1/drawings
         ▼
┌─────────────────────┐
│  API Gateway        │
│  - Auth check       │
│  - Rate limit       │
└────────┬────────────┘
         │ 3. Validate & Store
         ▼
┌─────────────────────┐
│  Drawing Intake     │
│  Service            │
│  - File validation  │
│  - Normalization    │
│  - S3 upload        │
└────────┬────────────┘
         │ 4. Queue job
         ▼
┌─────────────────────┐
│  Celery Queue       │
│  (Redis)            │
└────────┬────────────┘
         │ 5. Dequeue
         ▼
┌─────────────────────────────┐
│  Zone Detection Service     │
│  - Load YOLO model (cache)  │
│  - Run inference (GPU)      │
│  - Parse bboxes             │
└────────┬────────────────────┘
         │ 6. Crop zones
         ▼
┌─────────────────────────────┐
│  OCR Service                │
│  - Load Donut (cache)       │
│  - Extract text per zone    │
│  - Parse structures         │
└────────┬────────────────────┘
         │ 7. Validate
         ▼
┌─────────────────────────────┐
│  Rule Engine                │
│  - Apply 20+ rules          │
│  - Collect violations       │
│  - Assign severity          │
└────────┬────────────────────┘
         │ 8. Generate report
         ▼
┌─────────────────────────────┐
│  Report Service             │
│  - Render JSON              │
│  - Render HTML              │
│  - Store results (DB)       │
└────────┬────────────────────┘
         │ 9. Update status
         ▼
┌─────────────────────────────┐
│  PostgreSQL                 │
│  - Store result             │
│  - Log audit trail          │
└────────┬────────────────────┘
         │ 10. Notify user
         ▼
┌──────────────────────────────┐
│  Notification Service        │
│  - Email: "Validation ready" │
│  - WebSocket: Real-time UI   │
└──────────────────────────────┘
```

### Flow 2: Expert Review & Feedback

```
┌──────────────────┐
│  Expert (Claude) │
└────────┬─────────┘
         │ 1. View Queue
         ▼
┌─────────────────────────────────┐
│  Expert Dashboard               │
│  - List REVIEW_NEEDED drawings  │
│  - Filter by severity, date     │
└────────┬────────────────────────┘
         │ 2. Click drawing
         ▼
┌─────────────────────────────────┐
│  Detail Page                    │
│  - Flagged rule + context       │
│  - OCR confidence               │
│  - Related calc notes (DSM)     │
│  - Historical similar cases     │
└────────┬────────────────────────┘
         │ 3. Submit decision
         ▼
┌─────────────────────────────────┐
│  POST /api/expert_decision      │
│  - system_decision              │
│  - expert_decision              │
│  - rationale                    │
└────────┬────────────────────────┘
         │ 4. Record decision
         ▼
┌─────────────────────────────────┐
│  PostgreSQL                     │
│  - expert_decisions table       │
│  - audit_log entry              │
└────────┬────────────────────────┘
         │ 5. Aggregate feedback
         ▼
┌─────────────────────────────────┐
│  Feedback Analytics             │
│  - Weekly: Rule accuracy %      │
│  - Flag low performers          │
│  - Trigger retraining if <90%   │
└─────────────────────────────────┘
```

---

## 16. INTEGRATION ARCHITECTURE

### External Integrations (Phase 2+)

**CATIA Integration:**
- Export workflow trigger: When drawing saved → auto-export to validator
- Notification callback: When validation complete → notify user in CATIA

**DSM Integration:**
- Link drawing to calculation notes
- Fetch related metadata during validation
- Store validation result as new DSM artifact

**CAM/MES Integration:**
- API: Ingest validated drawing report
- Gate fabrication on validation pass
- Compliance tracking for audits

---

## 17. AI/ML COMPONENTS

### Model Architecture Details

**YOLO v11-obb:**
- Backbone: ResNet-based (efficient)
- Neck: PAN (Path Aggregation Network)
- Head: OBB (Oriented Bounding Box) detection
- Training: ImageNet pre-training → fine-tune on drawings dataset

**Donut (Document Understanding Transformer):**
- Architecture: Vision Encoder + Text Decoder
- Pre-trained on document understanding tasks
- Fine-tuned on 100-200 mechanical drawing crops
- Output: Structured text (e.g., {dimension: "Ø 10mm", tolerance: "±0.5mm"})

**Model Versioning & Retraining:**
- Current: v1.0 (50 drawings)
- Weekly retraining: v1.1, v1.2, etc.
- A/B test new model on 10% prod traffic before full rollout
- Rollback mechanism: Keep 2 prior versions; can revert if errors spike

---

## 18. RISKS & TRADEOFFS

### Technical Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Dataset too small (<50 drawings) | 🔴 CRITICAL | Negotiate with client for 100+ initial drawings; iterative improvement |
| OCR fails on poor-quality scans | 🟡 MEDIUM | Preprocessing pipeline (super-resolution); manual fallback UI |
| Rules too ambiguous → false positives | 🟠 HIGH | Expert refinement loop; prioritize CRITICAL violations only |
| Model drift (new drawing styles) | 🟠 HIGH | Continuous retraining; monitor performance on production data |
| GPU availability / cost | 🟡 MEDIUM | On-demand GPU (AWS Lambda); model quantization (FP16) |

### Architectural Tradeoffs

| Tradeoff | Decision | Rationale |
|----------|----------|-----------|
| **Monolith vs. Microservices** | Microservices (async) | Scalability for inference; separation of concerns |
| **Synchronous vs. Async** | Async (Celery) | ML inference is slow; don't block UI; user polls status |
| **Cloud vs. On-Prem** | Cloud (AWS) | Managed services; GPU availability; easier scaling |
| **Database: SQL vs. NoSQL** | PostgreSQL (SQL) | Structured data; ACID guarantees; audit trail compliance |
| **Model: Single vs. Ensemble** | Single (YOLO+Donut) | Latency <2.5s; single model sufficient with high recall |

---

## 19. ARCHITECTURE DECISION RECORDS (ADR)

### ADR-001: Choose YOLOv11-obb + Donut over Florence-2

**Decision:** Use YOLOv11-obb for detection + Donut for OCR

**Rationale:**
- Benchmark data (From Drawings to Decisions paper) shows:
  - Donut: 89.2% precision, 99.2% recall, 10.8% hallucination
  - Florence-2: 78.4% precision, 92.7% recall, 21.6% hallucination
- OBB (Oriented Bounding Box) perfectly matches rectangular drawing elements
- Total latency: 1.5-2.0s (acceptable for MVP)
- VRAM: 8GB (standard GPU)

**Consequence:** Lower latency than SAM2 (>3s) + PaddleOCR; acceptable hallucination rate

---

### ADR-002: Use Async Job Queue (Celery) for Inference

**Decision:** Async processing via Celery + Redis; client polls status

**Rationale:**
- Inference time: 1.5-2.5s; unacceptable as blocking HTTP request
- Allows 100+ concurrent jobs without blocking API pods
- User experience: Upload → redirect to status page → auto-refresh
- Horizontal scaling of worker nodes independent of API

**Consequence:** UI slightly more complex (polling); better scalability

---

### ADR-003: PostgreSQL for Primary Data Store

**Decision:** PostgreSQL with JSONB columns for flexible schema

**Rationale:**
- ACID compliance critical for audit trail immutability
- JSONB efficient for nested data (zones, extractions, rules)
- Rich query capabilities (full-text search, complex joins)
- Read replicas for analytics queries
- Mature ecosystem (security, backups, monitoring)

**Consequence:** Schema migrations required for new fields; no dynamic schema like NoSQL

---

## 20. NEXT STEPS

1. ✅ **This Architecture:** Approved by Solution Architect
2. ⏳ **Security Review:** Penetration test design; compliance checklist
3. ⏳ **DevOps Implementation:** Terraform IaC; CI/CD pipeline setup
4. ⏳ **Prototype:** Build minimal API + frontend scaffold
5. ⏳ **Team Alignment:** Architecture review meeting with full team

---

**END OF ARCHITECTURE DOCUMENT**

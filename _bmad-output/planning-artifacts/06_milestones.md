# PROJECT MILESTONES & TIMELINE
## ISO Technical Drawing Validator System

**Document Version:** 1.0  
**Prepared by:** Scrum Master (Project Lead)  
**Based on:** 04_epics.md + 05_tasks.md  
**Status:** ⏳ Draft (Pending Resource Confirmation)

---

## MILESTONE OVERVIEW

| Milestone | Timeline | Week | Key Deliverables | Go/No-Go Gate |
|-----------|----------|------|------------------|---------------|
| **M0** | Weeks 1-3 | Sprint 0-0.5 | Requirements locked, team assigned, infrastructure ready, NOTA processed, standards registry started | Scope approval, resource commitment, NOTA extraction working |
| **M1** | Weeks 4-9 | Sprint 1-2 | Dataset complete with drawing type labels, YOLO + Donut trained, classification module ready, extraction pipeline ready | mAP ≥0.85, CER <5%, classification accuracy >95% |
| **M2** | Weeks 10-15 | Sprint 3-4 | Rules codified (170 items), validation engine working, material + BOM validators, approval workflow DB ready, expert agreement >90% | Expert sign-off on 50 test cases, drawing type classification >98% |
| **M3** | Weeks 16-22 | Sprint 5-6 | Reports + UI functional, approval UI built, RAG system operational, all features integrated, UAT completed | UAT readiness, all systems tested end-to-end |
| **M4** | Weeks 23-28 | Sprint 6-7 | Production deployment, monitoring live, customer support trained, documentation complete | Production launch approval |
| **M5** | Week 29+ | Post-Launch | Phase 2 planning, continuous optimization, customer feedback loop | - |

**Total MVP Duration:** 28 weeks (7 months)  
**Team Ramp-up:** Week 1 (Sprint 0)  
**Production Launch:** End of Week 28

---

## MILESTONE 0: DISCOVERY & PLANNING (Weeks 1-2)

**Goal:** Lock scope, assign team, prepare infrastructure for rapid development

### Deliverables

**1. Requirements Specification Document**
- Finalized requirements from client (CTRL_PLAN_1-3 feedback incorporated)
- 8 zone types confirmed
- 20+ validation rules validated with client
- Acceptance criteria defined
- Sign-off from client + product owner
- **Owner:** Product Manager
- **Done When:** Client signature on requirements document

**2. Team Assigned & Onboarded**
- 6-8 people with clear RACI matrix
- Roles: 2 backend, 2 ML, 1-2 frontend, 1 DevOps, 1-2 QA, 1 rules architect
- Sprint 0 kickoff meeting completed
- Development environment working for all team members
- **Owner:** PM + HR
- **Done When:** All team members can run `docker-compose up` successfully

**3. Infrastructure Foundation**
- GitHub repo initialized + branching strategy documented
- AWS account provisioned + IAM roles assigned
- PostgreSQL local instance running
- Docker, Python 3.11, CUDA (GPU) available
- Pre-commit hooks configured
- **Owner:** DevOps Engineer
- **Done When:** `terraform plan` shows no errors; dev environment ready

**4. Scope Lock Document**
- Drawing zone types confirmed (8 types)
- Validation rules list finalized (20+ rules)
- Dataset hand-off date confirmed (client commits 100 drawings by Week 3)
- Model acceptance criteria (mAP50 ≥0.95, mAP50-95 ≥0.85)
- Out-of-scope items clearly listed (e.g., Phase 2 features, mobile app)
- **Owner:** Rules Architect + Product Manager
- **Done When:** Signed by stakeholders (client, tech lead, PM)

### Success Criteria

- ✅ All team members present (no key absences)
- ✅ Infrastructure tests passing (all tools functional)
- ✅ Client requirements verified (document signed)
- ✅ No blockers identified for Sprint 1
- ✅ Budget approved, timeline realistic

### Contingencies

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Client unable to provide 100 drawings by Week 3 | 30% | HIGH | Pre-arrange 50 synthetic drawings; annotate real ones later |
| Team member(s) unavailable at start | 10% | MEDIUM | Hire contractor ML engineer (budget contingency) |
| GPU allocation delayed on AWS | 15% | MEDIUM | Use Lambda with on-demand GPU; adjust timeline ±3 days |
| **NOTA document format changes** | 15% | HIGH | **Version external docs; create parser that tolerates format variations; maintain fallback manual mode** |
| **Drawing type classification accuracy <95%** | 20% | HIGH | **Implement manual override UI; requires expert review for ambiguous cases** |
| **External NOTA linking fails** | 10% | CRITICAL | **Keep weld validation working without NOTA temporarily; escalate to expert review** |

---

## MILESTONE 1: DATA & MODELS (Weeks 3-8)

**Goal:** Prepare training data, train detection + OCR models, validate accuracy

### Phase 1.1: Dataset Preparation (Weeks 3-4)

**Deliverables:**

1. **100 Annotated Drawings (YOLO Format)**
   - Bounding boxes for 8 zone types
   - Quality: Cohen's kappa ≥0.95 (2 annotators)
   - Format: COCO JSON + YOLO txt labels
   - Split: 70 train, 15 val, 15 test
   - Stored in DVC (version control)
   - **Owner:** Data Annotators + QA
   - **Done When:** Dataset uploaded to S3; validation passed

2. **OCR Training Dataset (500 Cropped Images)**
   - Zones cropped from above with ground truth text
   - Includes: cartouche, dimensions, notes, GD&T, weld symbols
   - Augmentation: rotations, noise, blur (simulate poor scans)
   - **Owner:** Data Lead + ML Engineer
   - **Done When:** Dataset ready in HuggingFace format

### Phase 1.2: YOLO Model Training (Weeks 5-6)

**Deliverables:**

1. **Trained YOLOv11-obb Model**
   - Architecture: YOLOv11n-obb (Oriented Bounding Box)
   - Metrics:
     - mAP50: ≥0.95 (primary metric)
     - mAP50-95: ≥0.85 (production threshold)
     - Per-class precision ≥0.90 (minimum)
   - Training time: <8 hours on single A100 GPU
   - Inference latency: <1000ms per image
   - **Owner:** ML Engineer
   - **Done When:** Model tested on holdout set; metrics validated

2. **Training Artifacts**
   - Training loss curves (logged to W&B)
   - Confusion matrix + per-class metrics
   - Inference time benchmarks (GPU + CPU)
   - Hyperparameter documentation
   - **Owner:** ML Engineer
   - **Done When:** Artifacts uploaded to S3 + documented

3. **Model Saved & Versioned**
   - Format: PyTorch .pt file
   - Location: `s3://iso-validator/models/yolo11n_v1.0.pt`
   - Version tag: v1.0 (date + metrics)
   - Rollback mechanism: Prior version archived
   - **Owner:** ML Engineer
   - **Done When:** Model downloadable; version hash recorded

### Phase 1.3: Donut OCR Fine-tuning (Weeks 5-6, Parallel)

**Deliverables:**

1. **Fine-tuned Donut Model**
   - Metrics:
     - CER (Character Error Rate): <5%
     - WER (Word Error Rate): <8%
   - Test set: 100 unseen cropped images
   - Tested on: Technical text (dimensions, specs, notes)
   - **Owner:** ML Engineer
   - **Done When:** Model accuracy validated

2. **Model Published to HuggingFace**
   - Repository: `hf://company-org/donut-iso-technical-drawings`
   - Version: 1.0 (timestamp)
   - License: MIT / Apache 2.0
   - **Owner:** ML Engineer
   - **Done When:** Model accessible via HuggingFace API

### Phase 1.4: Validation & Integration (Weeks 7-8)

**Deliverables:**

1. **Inference Pipeline Tested**
   - End-to-end: Image → YOLO detection → Donut OCR
   - Latency: <2.5s total (1.5s YOLO + 1.0s Donut)
   - Batch inference: 100 images in <5 min
   - **Owner:** Backend + ML Engineer
   - **Done When:** Performance targets met

2. **Corner Cases Documented**
   - Poor quality scans (low contrast)
   - Handwritten annotations (not supported v1)
   - Multiple languages (French, German - notes only)
   - Missing zones (graceful degradation)
   - **Owner:** QA + ML Engineer
   - **Done When:** Documented in known limitations list

3. **Go/No-Go Validation Report**
   - Signed by: ML Lead + Product Manager
   - Decision: "Proceed to Epic 3" or "Retrain with new data"
   - **Owner:** ML Lead
   - **Done When:** Report signed

### Success Criteria (M1)

- ✅ mAP50 ≥ 0.95, mAP50-95 ≥ 0.85 (YOLO)
- ✅ CER < 5%, WER < 8% (Donut)
- ✅ Inference latency <2.5s end-to-end
- ✅ 100 annotated drawings in YOLO format
- ✅ No critical bugs in inference pipeline
- ✅ Models versioned + backed up to S3

### Risk Mitigation

| Risk | Probability | Mitigation |
|------|------------|-----------|
| mAP50-95 < 0.85 | 15% | Augment dataset; retrain (add 1 week) |
| CER > 5% | 20% | Fine-tune longer; adjust hyperparameters |
| Annotation quality issues (kappa < 0.95) | 10% | Re-annotate failing images; expand training set |
| GPU insufficient (out of memory) | 5% | Use smaller batch; split across 2 GPUs |

---

## MILESTONE 2: VALIDATION RULES ENGINE (Weeks 9-12)

**Goal:** Codify ISO rules, build rule engine, validate on expert-reviewed drawings

### Phase 2.1: Rule Codification (Weeks 9-10)

**Deliverables:**

1. **Rules YAML Configuration File**
   - Location: `config/validation_rules.yaml`
   - Format: Version 1.0 (schema documented)
   - Total rules: 20+ across 7 categories
     - Cartouche rules: 5
     - Dimensional rules: 4
     - Tolerance rules: 3
     - GD&T rules: 3
     - Weld rules: 3
     - Surface finish rules: 2
     - Structural rules: 2
   - Each rule includes:
     - Unique ID (e.g., "cart_001")
     - Human-readable name
     - Severity (CRITICAL, HIGH, MEDIUM, LOW)
     - Condition (boolean expression)
     - Error message (with field interpolation)
     - Dependencies (other rules)
   - **Owner:** Rules Architect
   - **Done When:** All 20+ rules in YAML; syntax validated

2. **Rule Documentation**
   - For each rule: rationale + examples + edge cases
   - References to ISO standards (2768, 1101, 5817, 13920, etc.)
   - Decision trees for ambiguous cases (e.g., "mass only on final")
   - **Owner:** Rules Architect + Tech Writer
   - **Done When:** Documentation published to wiki/Notion

### Phase 2.2: Rule Engine Development (Weeks 10-11)

**Deliverables:**

1. **Rule Engine Implementation**
   - Component: `src/rules/rule_engine.py`
   - Features:
     - YAML loader + parser
     - Rule evaluator (for each rule → pass/fail/review)
     - Severity classification
     - Violation aggregator
   - Performance: <100ms to evaluate all rules per drawing
   - **Owner:** Backend Engineer
   - **Done When:** Unit tests passing (>95% coverage)

2. **Rule Versioning & A/B Testing**
   - Version tracking: rule set v1.0, v1.1, etc.
   - A/B test capability: Route % of traffic to new rules
   - Metrics: Violation rate, expert override %, false positives
   - **Owner:** Backend Engineer
   - **Done When:** A/B testing framework deployed

### Phase 2.3: Expert Validation (Weeks 11-12)

**Deliverables:**

1. **Expert Review on 50 Test Drawings**
   - Expert reviews system decisions (pass/fail/review)
   - Records: approval or correction
   - Measures: Agreement rate (target >90%)
   - **Owner:** Rules Architect + Expert Subject Matter Experts
   - **Done When:** 50 drawings reviewed; agreement >90%

2. **Rule Refinement Based on Feedback**
   - Adjust rules with low accuracy (<80%)
   - Add new rules for uncovered cases
   - Retrain if needed
   - **Owner:** Rules Architect
   - **Done When:** All rules accuracy ≥80%

3. **Go/No-Go Report**
   - Decision: "Proceed to data extraction" or "Refine rules"
   - Signed by: Rules Architect + Expert Panel
   - **Owner:** Rules Architect
   - **Done When:** Report signed

### Success Criteria (M2)

- ✅ 20+ rules coded in YAML
- ✅ Rule engine evaluates in <100ms
- ✅ Expert agreement >90% on 50 test drawings
- ✅ All rules documented (rationale + examples)
- ✅ Version control + audit trail working

### Critical Gate

**Go/No-Go Decision:** "Can we proceed to data extraction?"

- **GO:** If expert agreement ≥90% + rule accuracy ≥80%
- **NO-GO:** If expert agreement <80%; requires 1-2 weeks refinement

---

## MILESTONE 3: REPORTING & USER INTERFACE (Weeks 13-15)

**Goal:** Build data extraction pipeline, generate reports, deploy web UI

### Phase 3.1: Data Extraction (Weeks 13-14)

**Deliverables:**

1. **Extraction Pipeline Completed**
   - Components: Cartouche, Dimensions, GD&T, Weld, Surface Finish extractors
   - Accuracy: >90% on test set for each extractor
   - Confidence scoring: Each extracted field has confidence [0-100]
   - Linked to image regions: Each extraction can be highlighted on drawing
   - **Owner:** Backend + ML Engineer
   - **Done When:** All extractors tested; accuracy validated

2. **Data Models & JSON Schema**
   - Dataclasses: Cartouche, Dimension, GDT, etc.
   - JSON schema: Validated with jsonschema library
   - API documentation: OpenAPI spec for all endpoints
   - **Owner:** Backend
   - **Done When:** JSON schema deployed; tests passing

### Phase 3.2: Reporting System (Weeks 14-15)

**Deliverables:**

1. **JSON Report Generator**
   - Output: Structured JSON with all validation results
   - Size: <5MB per report (compression enabled)
   - **Owner:** Backend
   - **Done When:** Tested on 100 sample drawings

2. **HTML Report with Visualization**
   - Template: Jinja2 + Bootstrap CSS
   - Features: Tabbed interface (Summary, Zones, Violations, Details)
   - Interactivity: Hover highlights, zoom, clickable links
   - Export: PDF via weasyprint
   - **Owner:** Frontend
   - **Done When:** All pages styled + tested

3. **CSV Export for Bulk Analysis**
   - Format: RFC 4180 compliant UTF-8
   - Columns: drawing_id, status, violation_count, pass_rate
   - **Owner:** Backend
   - **Done When:** Tested on 100+ drawings

### Phase 3.3: Web UI (Weeks 13-15, Parallel)

**Deliverables:**

1. **Upload Page**
   - Drag-and-drop file upload
   - File type + size validation (client-side)
   - Progress bar for large files
   - **Owner:** Frontend
   - **Done When:** Tested in Chrome, Firefox, Safari

2. **Report View Page**
   - Tabbed interface: Summary | Zones | Violations | Details
   - Filtering: By severity, rule, status
   - Sorting: By date, severity, violation count
   - Download buttons: JSON, HTML, CSV, PDF
   - **Owner:** Frontend
   - **Done When:** Full feature parity with Figma mockup

3. **Dashboard Page**
   - Recent validations: Last 30 days
   - Statistics: Pass rate, violation trends
   - Filters: Status, date range, project
   - **Owner:** Frontend
   - **Done When:** Tested with sample data (100+ drawings)

### Phase 3.4: RAG System (Weeks 13-15, Parallel with E5)

**Deliverables:**

1. **Knowledge Base Compiled**
   - 30+ documents (ISO standards, client checklists, glossary)
   - Markdown format, well-structured
   - Indexed in FAISS (local) or Pinecone (cloud)
   - **Owner:** Knowledge Curator
   - **Done When:** All documents indexed; search tested

2. **RAG Query API**
   - Endpoint: `POST /api/v1/rag/ask`
   - Input: Natural language question
   - Output: Answer + sources + confidence
   - Latency: <2s per query
   - **Owner:** Backend + ML Engineer
   - **Done When:** Tested on 20 sample questions

3. **Chat UI**
   - Chat bubble interface
   - Source links (clickable)
   - History of questions
   - **Owner:** Frontend
   - **Done When:** Integrated with main web app

### Success Criteria (M3)

- ✅ All extractors >90% accurate
- ✅ Reports generated (JSON, HTML, CSV)
- ✅ Web UI all pages functional
- ✅ RAG system operational
- ✅ Ready for UAT

---

## MILESTONE 4: INTEGRATION & DEPLOYMENT (Weeks 16-21)

**Goal:** Deploy to production, conduct UAT, launch to customers

### Phase 4.1: Expert Workflow (Weeks 16-17)

**Deliverables:**

1. **Expert Dashboard**
   - List of REVIEW_NEEDED drawings
   - Filtering + sorting
   - Detail view with context
   - **Owner:** Frontend
   - **Done When:** Tested with 50 sample cases

2. **Decision Recording**
   - Expert submits: Approve/Override/Request Info + rationale
   - Feedback recorded to database
   - Weekly metrics generated
   - **Owner:** Backend + Frontend
   - **Done When:** Tested end-to-end

3. **Feedback Loop Active**
   - Weekly aggregation: Rule accuracy by type
   - Alert if accuracy drops >5%
   - Trigger retraining if needed
   - **Owner:** ML Engineer + Backend
   - **Done When:** Metrics pipeline running

### Phase 4.2: Production Deployment (Weeks 17-19)

**Deliverables:**

1. **Docker Containerization**
   - Docker images for API + Worker services
   - docker-compose.yml for local dev
   - Image size <2GB; security checks passed
   - **Owner:** DevOps
   - **Done When:** Images pushed to ECR

2. **Infrastructure as Code (Terraform)**
   - VPC + security groups + IAM roles
   - RDS (PostgreSQL multi-AZ) + ElastiCache (Redis)
   - ECS (Fargate) + ALB + CloudFront
   - Secrets Manager + KMS encryption
   - **Owner:** DevOps
   - **Done When:** `terraform apply` succeeds; resources live

3. **CI/CD Pipeline (GitHub Actions)**
   - Lint + test + security scan on every commit
   - Build + push Docker images on merge to main
   - Deploy to staging automatically
   - Canary deployment to production (10% → 100%)
   - **Owner:** DevOps + Backend
   - **Done When:** Full pipeline tested; no failures

4. **Monitoring & Alerting**
   - Prometheus: API latency, error rate, GPU utilization
   - ELK stack: Centralized logging
   - Grafana: Dashboards for operations team
   - PagerDuty: Alerts for critical issues
   - **Owner:** DevOps
   - **Done When:** Dashboards live; alert rules validated

### Phase 4.3: UAT & Fixes (Weeks 19-21)

**Deliverables:**

1. **End-to-End Testing**
   - 5 test scenarios covering main workflows
   - Performance: API <2.5s (p99), model inference <2.0s
   - Security: Penetration test results
   - **Owner:** QA
   - **Done When:** All tests passed; no critical bugs

2. **Customer UAT (2 weeks)**
   - Customer validates system with real drawings
   - Records feedback + issues
   - Issues triaged (critical, high, low)
   - **Owner:** PM + Customer
   - **Done When:** Customer sign-off on UAT report

3. **Critical Bug Fixes**
   - Bugs discovered during UAT prioritized + fixed
   - Regression testing ensures no new issues
   - **Owner:** Backend + Frontend
   - **Done When:** All critical bugs fixed

4. **Production Deployment**
   - Blue-green or canary deployment strategy
   - Monitor error rate / latency for 24 hours
   - If OK, full rollout; if issues, automatic rollback
   - **Owner:** DevOps
   - **Done When:** Deployment verified live; monitoring stable

### Phase 4.4: Launch Preparation (Week 21)

**Deliverables:**

1. **Customer Documentation**
   - User guide: How to upload + interpret reports
   - FAQ: Common questions + troubleshooting
   - Admin guide: System configuration + maintenance
   - **Owner:** Tech Writer
   - **Done When:** Published to customer portal

2. **Support Team Training**
   - 4-hour training session on system + troubleshooting
   - Runbooks for common issues
   - Escalation procedures
   - **Owner:** PM + Support
   - **Done When:** All support staff certified

3. **Go-Live Checklist**
   - All systems operational
   - Monitoring + alerting verified
   - Support team ready
   - Customer trained
   - **Owner:** PM
   - **Done When:** Checklist signed off by all stakeholders

### Success Criteria (M4)

- ✅ Production deployment successful (zero data loss)
- ✅ Customer UAT passed + sign-off obtained
- ✅ All critical bugs fixed
- ✅ Monitoring + alerting live + validated
- ✅ Support team trained + ready
- ✅ System performance meets SLAs (<2.5s latency p99, 99.5% uptime)

---

## MILESTONE 5: POST-LAUNCH & PHASE 2 PLANNING (Week 22+)

**Goal:** Stabilize system, collect feedback, plan Phase 2 features

### Phase 5.1: Stabilization & Optimization (Weeks 22-26)

**Deliverables:**

1. **Customer Support & Feedback Collection**
   - Monitor support tickets + error rates
   - Weekly customer check-in calls
   - Collect feature requests + pain points
   - **Owner:** PM + Support
   - **Done When:** Weekly summary reports published

2. **Performance Optimization**
   - Analyze slow queries; add database indexing
   - Profile model inference; optimize if needed
   - Cache frequently accessed data
   - **Owner:** Backend + ML Engineer
   - **Done When:** Response times improved >10%

3. **Continuous Retraining**
   - Weekly batch: Collect expert feedback → retrain models
   - Monitor model performance vs. baseline
   - Deploy improved versions automatically
   - **Owner:** ML Engineer
   - **Done When:** Retraining pipeline automated

### Phase 5.2: Phase 2 Planning (Week 26+)

**Deliverables:**

1. **CATIA Add-in Development** (Optional)
   - Design: Right-click drawing → validate in CATIA
   - Implementation: VB.NET macro
   - **Effort:** 3-4 weeks
   - **Owner:** Backend Engineer
   - **Decision Gate:** Customer prioritization + budget

2. **DSM Integration** (Optional)
   - Link validation results to design calculations
   - API: Accept validation result + reference
   - **Effort:** 2-3 weeks
   - **Owner:** Backend Engineer
   - **Decision Gate:** Customer prioritization + budget

3. **Phase 2 Requirements**
   - Collect + prioritize feature requests
   - Update roadmap (3-6 months ahead)
   - **Owner:** PM
   - **Done When:** Phase 2 epic list published

---

## CRITICAL PATH & DEPENDENCY MAP

```
┌─────────────────────────────────────────────────────┐
│         M0: Planning (Weeks 1-2)                    │
│   ├─ Scope lock ✓                                   │
│   ├─ Team assigned ✓                                │
│   └─ Infrastructure ready ✓                         │
│         │                                           │
│         ▼                                           │
│   ┌──────────────────────────────────────────────┐ │
│   │ M1: Data & Models (Weeks 3-8)                │ │
│   │   ├─ 100 drawings annotated ✓                │ │
│   │   ├─ YOLO trained (mAP50 ≥0.95) ✓            │ │
│   │   ├─ Donut trained (CER <5%) ✓               │ │
│   │   └─ Go/No-Go: Metrics validated ✓           │ │
│   │       │                                      │ │
│   │       ▼                                      │ │
│   │ ┌─────────────────────────────────────────┐ │ │
│   │ │ M2: Rules Engine (Weeks 9-12)           │ │ │
│   │ │   ├─ 20+ rules coded ✓                  │ │ │
│   │ │   ├─ Rule engine built ✓                │ │ │
│   │ │   ├─ Expert validation (50 cases) ✓     │ │ │
│   │ │   └─ Go/No-Go: Expert agreement >90% ✓  │ │ │
│   │ │       │                                 │ │ │
│   │ │       ▼                                 │ │ │
│   │ │ ┌────────────────────────────────────┐ │ │ │
│   │ │ │ M3: Reporting & UI (Weeks 13-15)  │ │ │ │
│   │ │ │   ├─ Extractors >90% accurate ✓   │ │ │ │
│   │ │ │   ├─ Reports (JSON, HTML, CSV) ✓  │ │ │ │
│   │ │ │   ├─ Web UI deployed ✓            │ │ │ │
│   │ │ │   ├─ RAG system live ✓            │ │ │ │
│   │ │ │   └─ Go/No-Go: UAT ready ✓        │ │ │ │
│   │ │ │       │                           │ │ │ │
│   │ │ │       ▼                           │ │ │ │
│   │ │ │ ┌──────────────────────────────┐ │ │ │ │
│   │ │ │ │ M4: Deploy (Weeks 16-21)    │ │ │ │ │
│   │ │ │ │   ├─ Expert dashboard ✓     │ │ │ │ │
│   │ │ │ │   ├─ Production deployed ✓  │ │ │ │ │
│   │ │ │ │   ├─ Customer UAT ✓         │ │ │ │ │
│   │ │ │ │   ├─ Critical bugs fixed ✓  │ │ │ │ │
│   │ │ │ │   └─ Go-Live ✓              │ │ │ │ │
│   │ │ │ │       │                     │ │ │ │ │
│   │ │ │ │       ▼                     │ │ │ │ │
│   │ │ │ │ MVP RELEASE (Week 21)       │ │ │ │ │
│   │ │ │ │                             │ │ │ │ │
│   │ │ │ └──────────────────────────────┘ │ │ │ │
│   │ │ │                                   │ │ │ │
│   │ │ └─────────────────────────────────┘ │ │ │
│   │ │                                     │ │ │
│   │ └──────────────────────────────────────┘ │ │
│   │                                          │ │
│   └──────────────────────────────────────────┘ │
│                                                │
│ ┌────────────────────────────────────────────┐ │
│ │ M5: Post-Launch (Week 22+)                 │ │
│ │   ├─ Stabilization & optimization         │ │
│ │   ├─ Continuous feedback loop              │ │
│ │   └─ Phase 2 planning                      │ │
│ └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘

PARALLEL WORKSTREAMS (Can overlap but not shown above):
├─ Infrastructure setup (T0.1-0.6) → M0
├─ Dataset annotation (T2.1-2.4) → M1
├─ Model training YOLO (T2.7-2.10) → M1
├─ Model training Donut (T2.14-2.18) → M1  (parallel with YOLO)
├─ Rules codification (T4.1-4.2) → M2
├─ Rule engine development (T4.8-4.9) → M2
├─ Expert validation (T4.20) → M2 (feedback loop)
├─ Data extraction (T3.1-3.9) → M3 (depends on M1)
├─ Reporting system (T5.1-5.2) → M3 (depends on M2)
├─ Web UI (T5.3-5.11) → M3 (parallel with reporting)
├─ RAG system (T6.1-6.7) → M3 (parallel, no dependencies)
├─ Expert dashboard (T7.1-7.6) → M4 (depends on M3)
├─ Docker + CI/CD (T8.1-8.9) → M4 (parallel from Sprint 5)
├─ Terraform + deployment (T8.10-8.26) → M4 (parallel from Sprint 5)
└─ UAT & launch (T9.1-9.10) → M4 (last 3 weeks)
```

---

## SPRINT SCHEDULE

| Sprint | Weeks | Duration | Focus | Story Points | Go/No-Go Gate |
|--------|-------|----------|-------|--------------|---------------|
| **0** | 1-2 | 2 wks | Planning + Setup | 22 | Scope approval |
| **1** | 3-5 | 3 wks | Data + YOLO/Donut | 83 | Model metrics |
| **2** | 6-8 | 3 wks | Data Extraction | 50 | Accuracy >90% |
| **3** | 9-12 | 4 wks | Rules Engine | 70 | Expert agreement |
| **4** | 13-15 | 3 wks | Reporting + UI | 65 | Feature complete |
| **5** | 16-18 | 3 wks | Expert WF + Deploy | 90 | Production ready |
| **6** | 19-21 | 3 wks | Testing + Launch | 38 | Go-live approval |
| **5+** | 22+ | TBD | Phase 2 Planning | TBD | - |

**Total Points (MVP):** 418  
**Avg per Week:** 418 / 21 ≈ 20 points/week

---

## BUFFER & CONTINGENCIES

### Buffer Allocation (15% of timeline)

```
Planned Timeline: 21 weeks
Recommended Buffer: 3 weeks (15%)
Realistic MVP Launch: 22-24 weeks (5-6 months)

Critical Path (0 float):
- Weeks 9-12: Rules engine must complete on time
  (delays here push entire timeline)

High Risk Points:
- Week 3-4: Annotation quality (if kappa <0.95, add 1 week)
- Week 8: Model accuracy (if mAP <0.85, add 2 weeks)
- Week 12: Expert validation (if agreement <90%, add 1-2 weeks)
```

### Risk Contingencies

| Milestone | Risk | Probability | Impact | Mitigation |
|-----------|------|------------|--------|-----------|
| **M0** | Scope creep | 40% | HIGH | Lock scope doc; enforce change control process |
| **M1** | Dataset annotation delayed | 30% | HIGH | Use 50 synthetic + 50 real initially |
| **M1** | Model accuracy below target | 25% | HIGH | Augment dataset; extend training |
| **M2** | Rule ambiguity → many refinements | 35% | MEDIUM | Allocate 1-week buffer; expert review early |
| **M3** | Extraction accuracy low | 20% | MEDIUM | Fallback to manual review UI for <70% confidence |
| **M4** | UAT uncovers major issues | 15% | MEDIUM | Add 1-2 weeks; prioritize critical fixes |
| **Overall** | GPU availability / costs | 20% | MEDIUM | Use on-demand; negotiate volume pricing |

---

## SUCCESS METRICS

### MVP Launch Criteria

| Metric | Target | Measurement | Owner |
|--------|--------|-------------|-------|
| **Detection Accuracy** | mAP50-95 ≥0.85 | Test set metrics | ML Lead |
| **OCR Accuracy** | CER <5%, WER <8% | OCR test set | ML Lead |
| **Rule Accuracy** | Expert agreement >90% | 50 test drawings | Rules Architect |
| **System Latency** | <2.5s (p99) | Production logs | DevOps |
| **Uptime** | 99.5% | CloudWatch SLA | DevOps |
| **Documentation** | Complete | User + admin guides | Tech Writer |
| **Customer Sign-Off** | UAT passed | Customer approval | PM |

### Post-Launch KPIs

| KPI | Target | Timeline |
|-----|--------|----------|
| **User Adoption** | 80% of design team | 3 months post-launch |
| **Time Savings** | 5 hours/week per engineer | 6 months post-launch |
| **System Availability** | 99.5% uptime SLA | Ongoing |
| **Customer Satisfaction** | NPS >50 | 3 months post-launch |
| **Rule Accuracy** | Maintain >90% expert agreement | Ongoing |

---

## CONTINGENCY RESERVES

### Schedule Reserve (by Milestone)

```
M0: +0 days (low risk, well-scoped)
M1: +5 days (dataset annotation)
M2: +3 days (rule refinement)
M3: +2 days (extraction testing)
M4: +3 days (UAT fixes)
────────────────────────
TOTAL BUFFER: +13 days (~2 weeks)
```

### Cost Reserve (estimated)

```
Labor: +15% (unforeseen complexity)
Infrastructure: +10% (GPU overages, storage)
Contractor: +20% (backup resources if key person absent)
────────────────────────────────────────
TOTAL COST BUFFER: ~15% of project budget
```

---

## DECISION GATES & SIGN-OFF REQUIREMENTS

### Pre-Sprint 1 Gate (End of M0)
- ✓ Scope document signed by client + PM + CTO
- ✓ Team fully onboarded + productive
- ✓ Infrastructure tested + accessible
- ✓ Dataset delivery timeline confirmed

**Go/No-Go:** Can proceed if all checkboxes ✓; else delay Sprint 1

### Post-M1 Gate (End of Week 8)
- ✓ Model metrics meet targets (mAP ≥0.85)
- ✓ 100 annotated drawings validated (kappa ≥0.95)
- ✓ Inference pipeline <2.5s latency
- ✓ No critical bugs in integration tests

**Go/No-Go:** Can proceed to M2 if all checkboxes ✓; else retrain

### Post-M2 Gate (End of Week 12)
- ✓ 20+ rules defined + validated
- ✓ Expert agreement >90% on 50 test drawings
- ✓ Rule engine <100ms evaluation time
- ✓ All rules documented

**Go/No-Go:** Can proceed to M3 if all checkboxes ✓; else refine rules

### Post-M3 Gate (End of Week 15)
- ✓ All extractors >90% accurate
- ✓ Reports generating (JSON, HTML, CSV)
- ✓ Web UI feature-complete
- ✓ RAG system operational + tested

**Go/No-Go:** Can proceed to M4 if ready for UAT

### Post-M4 Gate (End of Week 21)
- ✓ Customer UAT passed + sign-off obtained
- ✓ All critical bugs fixed
- ✓ Production deployment successful (0 data loss)
- ✓ Monitoring + alerting verified

**Go/No-Go:** Launch approved by PM + Customer; proceed to M5

---

**END OF MILESTONES DOCUMENT**

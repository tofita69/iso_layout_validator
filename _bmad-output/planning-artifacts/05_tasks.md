# IMPLEMENTATION TASKS & WORK BREAKDOWN
## ISO Technical Drawing Validator System

**Document Version:** 1.0  
**Prepared by:** Scrum Master (Project Lead)  
**Based on:** 04_epics.md  
**Status:** ⏳ Draft (Pending Team Refinement)

---

## TASK OVERVIEW

**Total Tasks:** 85  
**Total Story Points:** 280  
**Recommended Sprint Length:** 2 weeks (20 working days)  
**Sprints Required:** 7 sprints (MVP by week 18-21)

**Legend:**
- 🔴 **P0 (Critical Path):** Blocks downstream work
- 🟠 **P1 (High Value):** Enables feature; no external dependency
- 🟡 **P2 (Nice-to-Have):** Enhancement; can defer to Phase 2

---

## SPRINT 0: PLANNING & SETUP (Week 1-2)

### Infrastructure & Tooling Setup

| ID | Task | Epic | Points | Owner | Priority | Status |
|----|----|------|--------|-------|----------|--------|
| **T0.1** | Set up GitHub repo + branching strategy | E8 | 2 | DevOps | 🔴 P0 | Not Started |
| **T0.2** | Configure AWS account + IAM roles | E8 | 3 | DevOps | 🔴 P0 | Not Started |
| **T0.3** | Set up development environment (Docker, Python 3.11) | E8 | 3 | DevOps | 🔴 P0 | Not Started |
| **T0.4** | Initialize Terraform code structure | E8 | 3 | DevOps | 🟠 P1 | Not Started |
| **T0.5** | Set up PostgreSQL local dev instance | E1 | 2 | Backend | 🔴 P0 | Not Started |
| **T0.6** | Configure pre-commit hooks (linting, type checking) | E8 | 2 | DevOps | 🟠 P1 | Not Started |
| **T0.7** | Create project documentation template (README, ADRs) | E8 | 2 | Tech Writer | 🟡 P2 | Not Started |

**Sprint 0 Total:** 17 points

### Client Engagement & Requirements Finalization

| ID | Task | Epic | Points | Owner | Priority | Status |
|----|----|------|--------|-------|----------|--------|
| **T0.8** | Conduct requirements kickoff meeting with client | E1 | 1 | PM | 🔴 P0 | Not Started |
| **T0.9** | Lock scope: 8 zone types, 20+ rules | E4 | 2 | Rules Architect | 🔴 P0 | Not Started |
| **T0.10** | Negotiate dataset hand-off (100 drawings by Week 3) | E2 | 1 | PM | 🔴 P0 | Not Started |
| **T0.11** | Define acceptance criteria for model metrics | E2 | 1 | PM + ML Lead | 🔴 P0 | Not Started |

**Client Engagement Total:** 5 points

**Sprint 0 Grand Total:** 22 points

---

## SPRINT 1: DATA INGESTION & MODELS (Week 3-5)

### Epic 1: Data Ingestion & Preparation

| ID | Task | Story | Points | Owner | Priority | Dependencies |
|----|----|--------|--------|-------|----------|--------------|
| **T1.1** | Design drawing upload API endpoint (`POST /api/v1/drawings`) | US1.1 | 3 | Backend | 🔴 P0 | T0.5 |
| **T1.2** | Implement multipart file upload handler (FastAPI) | US1.1 | 3 | Backend | 🔴 P0 | T1.1 |
| **T1.3** | Implement file type + size validation (python-magic) | US1.1 | 2 | Backend | 🔴 P0 | T1.2 |
| **T1.4** | Build drawing status API endpoint (`GET /drawings/{id}/status`) | US1.1 | 2 | Backend | 🔴 P0 | T1.2 |
| **T1.5** | Implement S3 storage layer (uploads, images, results) | US1.1 | 3 | Backend | 🔴 P0 | T0.3 |
| **T1.6** | Build CATIA → PNG converter (LibreOffice headless) | US1.2 | 5 | ML Eng | 🔴 P0 | T0.3 |
| **T1.7** | Implement image preprocessing (rotation, contrast, denoise) | US1.3 | 4 | ML Eng | 🔴 P0 | T1.6 |
| **T1.8** | Build Celery task queue for async processing | US1.1 | 3 | Backend | 🔴 P0 | T0.5 |
| **T1.9** | Implement audit logging (immutable PostgreSQL table) | US1.5 | 3 | Backend | 🟠 P1 | T0.5 |
| **T1.10** | Build web UI for file upload (React + drag-drop) | US1.4 | 4 | Frontend | 🔴 P0 | T0.3 |
| **T1.11** | Create API documentation (OpenAPI/Swagger) | US1.1 | 2 | Tech Writer | 🟠 P1 | T1.2 |

**Epic 1 Total:** 34 points

### Epic 2a: Dataset Preparation & YOLO Training

| ID | Task | Story | Points | Owner | Priority | Dependencies |
|----|----|--------|--------|-------|----------|--------------|
| **T2.1** | Coordinate with client: receive 100 drawing files | US2.1 | 2 | PM | 🔴 P0 | T0.10 |
| **T2.2** | Set up CVAT annotation tool + train annotators | US2.1 | 3 | Data Lead | 🔴 P0 | T0.3 |
| **T2.3** | Annotate drawings (bounding boxes for 8 zones) | US2.1 | 8 | Data Annotators | 🔴 P0 | T2.2 |
| **T2.4** | Quality assurance: 2 annotators, Cohen's kappa >0.95 | US2.1 | 3 | QA | 🔴 P0 | T2.3 |
| **T2.5** | Convert COCO JSON to YOLO format + train/val/test split | US2.1 | 2 | ML Eng | 🔴 P0 | T2.4 |
| **T2.6** | Set up DVC for dataset versioning | US2.1 | 2 | ML Eng | 🟠 P1 | T0.3 |
| **T2.7** | Configure YOLO v11-obb training environment (GPU) | US2.2 | 2 | ML Eng | 🔴 P0 | T0.3 |
| **T2.8** | Train YOLO v11 model (30 epochs, batch=16) | US2.2 | 3 | ML Eng | 🔴 P0 | T2.5, T2.7 |
| **T2.9** | Monitor training: log metrics to W&B | US2.2 | 2 | ML Eng | 🟠 P1 | T2.8 |
| **T2.10** | Evaluate model on holdout test set (50 images) | US2.3 | 3 | QA | 🔴 P0 | T2.8 |
| **T2.11** | Generate confusion matrix + per-class metrics | US2.3 | 2 | ML Eng | 🔴 P0 | T2.10 |
| **T2.12** | Document corner cases (poor scans, handwritten notes) | US2.3 | 2 | QA | 🟠 P1 | T2.10 |
| **T2.13** | Save model to S3 + tag version (v1.0) | US2.2 | 1 | ML Eng | 🔴 P0 | T2.8 |

**Epic 2a Total:** 35 points

### Epic 2b: Donut OCR Fine-tuning

| ID | Task | Story | Points | Owner | Priority | Dependencies |
|----|----|--------|--------|-------|----------|--------------|
| **T2.14** | Download Donut base model (naver-clova-ix/donut-base) | US2.4 | 1 | ML Eng | 🔴 P0 | T0.3 |
| **T2.15** | Prepare OCR training dataset (500 cropped zone images) | US2.4 | 3 | ML Eng | 🔴 P0 | T2.3 |
| **T2.16** | Implement Donut fine-tuning script (3 epochs, lr=1e-4) | US2.4 | 4 | ML Eng | 🔴 P0 | T2.15 |
| **T2.17** | Fine-tune Donut model on GPU (8GB VRAM) | US2.4 | 3 | ML Eng | 🔴 P0 | T2.16 |
| **T2.18** | Evaluate OCR: CER <5%, WER <8% on test set | US2.4 | 2 | QA | 🔴 P0 | T2.17 |
| **T2.19** | Push Donut model to HuggingFace Model Hub + version | US2.4 | 1 | ML Eng | 🔴 P0 | T2.18 |

**Epic 2b Total:** 14 points

**Sprint 1 Grand Total:** 83 points

---

## SPRINT 2: DATA EXTRACTION (Week 6-8)

### Epic 3: Data Extraction & Structuring

| ID | Task | Story | Points | Owner | Priority | Dependencies |
|----|----|--------|--------|-------|----------|--------------|
| **T3.1** | Design data models (Cartouche, Dimension, GDT, etc.) | US3.1-3.6 | 3 | Backend | 🔴 P0 | T0.5 |
| **T3.2** | Implement YOLO inference service (load model from S3) | US2.5 | 4 | Backend | 🔴 P0 | T1.8, T2.13 |
| **T3.3** | Implement Donut inference service (OCR per zone) | US2.5 | 3 | Backend | 🔴 P0 | T2.19 |
| **T3.4** | Build cartouche extractor (designation, ref, scale, index) | US3.1 | 5 | Backend | 🔴 P0 | T3.1, T3.3 |
| **T3.5** | Build dimension extractor (value, unit, tolerance, type) | US3.2 | 5 | Backend | 🔴 P0 | T3.1, T3.3 |
| **T3.6** | Build GD&T extractor (symbols, datums, modifiers) | US3.3 | 6 | Backend | 🔴 P0 | T3.1, T3.3 |
| **T3.7** | Build weld specification extractor (symbols, CND, NOTA) | US3.4 | 4 | Backend | 🔴 P0 | T3.1, T3.3 |
| **T3.8** | Build surface finish extractor (Ra, Rz, environment) | US3.5 | 3 | Backend | 🔴 P0 | T3.1, T3.3 |
| **T3.9** | Implement extraction orchestration (run all extractors) | US3.1-3.6 | 3 | Backend | 🔴 P0 | T3.4-3.8 |
| **T3.10** | Add confidence scoring to all extractions | US3.1-3.6 | 2 | Backend | 🔴 P0 | T3.9 |
| **T3.11** | Implement extraction → image region linking | US3.6 | 3 | Backend | 🔴 P0 | T3.9 |
| **T3.12** | Build extraction result JSON schema | US3.1-3.6 | 2 | Backend | 🔴 P0 | T3.9 |
| **T3.13** | Unit tests for all extractors (>80% coverage) | US3.1-3.6 | 4 | QA | 🔴 P0 | T3.9 |
| **T3.14** | Integration tests: end-to-end extraction pipeline | US3.1-3.6 | 3 | QA | 🔴 P0 | T3.13 |

**Sprint 2 Grand Total:** 50 points

---

## SPRINT 3: VALIDATION RULES ENGINE (Week 9-12)

### Epic 4: Validation Rules Engine

| ID | Task | Story | Points | Owner | Priority | Dependencies |
|----|----|--------|--------|-------|----------|--------------|
| **T4.1** | Design rules YAML schema + template | US4.1 | 2 | Rules Architect | 🔴 P0 | T3.12 |
| **T4.2** | Codify cartouche rules (5 rules: required fields, format, mass) | US4.1 | 5 | Rules Architect | 🔴 P0 | T4.1 |
| **T4.3** | Codify dimension rules (4 rules: consistency, tolerance format) | US4.1 | 5 | Rules Architect | 🔴 P0 | T4.1 |
| **T4.4** | Codify GD&T rules (3 rules: symbol validity, datum, placement) | US4.1 | 4 | Rules Architect | 🔴 P0 | T4.1 |
| **T4.5** | Codify weld rules (3 rules: NOTA ↔ CNE alignment) | US4.1 | 4 | Rules Architect | 🔴 P0 | T4.1 |
| **T4.6** | Codify surface finish rules (2 rules: environment criteria) | US4.1 | 3 | Rules Architect | 🔴 P0 | T4.1 |
| **T4.7** | Codify structural rules (2 rules: no overlaps, mass on final) | US4.1 | 3 | Rules Architect | 🔴 P0 | T4.1 |
| **T4.8** | Build rule engine: YAML loader + evaluator | US4.2 | 5 | Backend | 🔴 P0 | T4.1 |
| **T4.9** | Implement expression evaluation (sandboxed Python eval) | US4.2 | 3 | Backend | 🔴 P0 | T4.8 |
| **T4.10** | Add rule versioning + A/B testing framework | US4.5 | 4 | Backend | 🟠 P1 | T4.8 |
| **T4.11** | Implement severity classification (CRITICAL, HIGH, MEDIUM, LOW) | US4.3 | 2 | Backend | 🔴 P0 | T4.8 |
| **T4.12** | Implement anomaly detection (missing zones, outliers) | US4.3 | 3 | Backend | 🟠 P1 | T4.8 |
| **T4.13** | Build expert dashboard backend (list violations by severity) | US4.4 | 4 | Backend | 🟠 P1 | T4.8 |
| **T4.14** | Build expert decision API (`POST /expert_decision`) | US4.4 | 3 | Backend | 🟠 P1 | T4.13 |
| **T4.15** | Implement feedback recording + auditing | US4.4 | 2 | Backend | 🟠 P1 | T4.14 |
| **T4.16** | Implement weekly accuracy metrics (rule performance) | US4.3 | 3 | Backend | 🟠 P1 | T4.15 |
| **T4.17** | Build performance dashboard (Grafana) | US4.3 | 3 | Backend + DevOps | 🟠 P1 | T4.16 |
| **T4.18** | Unit tests: all rules evaluated correctly | US4.1-4.2 | 4 | QA | 🔴 P0 | T4.8 |
| **T4.19** | Integration tests: end-to-end validation pipeline | US4.1-4.2 | 3 | QA | 🔴 P0 | T4.18 |
| **T4.20** | Expert validation (50 test drawings): >90% agreement | US4.2 | 5 | Rules Architect + Expert | 🔴 P0 | T4.19 |

**Sprint 3 Grand Total:** 70 points

---

## SPRINT 4: REPORTING & UI (Week 13-15)

### Epic 5: Reporting & User Interface

| ID | Task | Story | Points | Owner | Priority | Dependencies |
|----|----|--------|--------|-------|----------|--------------|
| **T5.1** | Design JSON report schema (OpenAPI spec) | US5.1 | 2 | Backend | 🔴 P0 | T4.19 |
| **T5.2** | Implement JSON report generator | US5.1 | 3 | Backend | 🔴 P0 | T5.1 |
| **T5.3** | Design HTML report template (Jinja2) | US5.2 | 3 | Frontend | 🔴 P0 | T5.1 |
| **T5.4** | Implement HTML report rendering + CSS styling | US5.2 | 5 | Frontend | 🔴 P0 | T5.3 |
| **T5.5** | Add image visualization + hover highlights | US5.2 | 4 | Frontend | 🔴 P0 | T5.4 |
| **T5.6** | Add PDF export (weasyprint) | US5.2 | 3 | Frontend | 🟠 P1 | T5.4 |
| **T5.7** | Implement CSV export | US5.3 | 2 | Backend | 🟠 P1 | T5.1 |
| **T5.8** | Build upload page UI (drag-drop, file validation) | US5.4 | 4 | Frontend | 🔴 P0 | T1.10 |
| **T5.9** | Build report view page (tabbed: Summary, Zones, Violations) | US5.5 | 5 | Frontend | 🔴 P0 | T5.4 |
| **T5.10** | Add filtering + sorting to violations table | US5.5 | 2 | Frontend | 🔴 P0 | T5.9 |
| **T5.11** | Build dashboard page (history, statistics) | US5.6 | 4 | Frontend | 🟠 P1 | T5.9 |
| **T5.12** | Implement status polling (WebSocket or HTTP) | US5.4 | 3 | Frontend + Backend | 🔴 P0 | T1.4 |
| **T5.13** | Authentication integration (OAuth2) | US5.4-5.6 | 3 | Backend | 🔴 P0 | T0.3 |
| **T5.14** | Build React component library (card, badge, modal) | US5.4-5.6 | 3 | Frontend | 🟠 P1 | T0.3 |

**Epic 5 Total:** 46 points

### Epic 6: RAG System (Parallel with E5)

| ID | Task | Story | Points | Owner | Priority | Dependencies |
|----|----|--------|--------|-------|----------|--------------|
| **T6.1** | Collect ISO standards documents (30+ markdown files) | US6.1 | 3 | Knowledge Curator | 🟠 P1 | None |
| **T6.2** | Create knowledge base indexing script | US6.2 | 2 | Backend | 🟠 P1 | T6.1 |
| **T6.3** | Implement document embedding (sentence-transformers) | US6.2 | 2 | Backend | 🟠 P1 | T6.2 |
| **T6.4** | Set up FAISS vector DB (local dev) or Pinecone (cloud) | US6.2 | 2 | Backend | 🟠 P1 | T6.3 |
| **T6.5** | Implement RAG query API (`POST /rag/ask`) | US6.3 | 3 | Backend | 🟠 P1 | T6.4 |
| **T6.6** | Build chat UI (React component) | US6.4 | 3 | Frontend | 🟠 P1 | T6.5 |
| **T6.7** | Add source attribution + confidence scoring | US6.3 | 2 | Backend | 🟠 P1 | T6.5 |
| **T6.8** | Unit + integration tests (RAG pipeline) | US6.1-6.4 | 2 | QA | 🟠 P1 | T6.5 |

**Epic 6 Total:** 19 points

**Sprint 4 Grand Total:** 65 points

---

## SPRINT 5: EXPERT WORKFLOW & INTEGRATION (Week 16-18)

### Epic 7: Expert Workflow & Feedback Loop

| ID | Task | Story | Points | Owner | Priority | Dependencies |
|----|----|--------|--------|-------|----------|--------------|
| **T7.1** | Build expert review dashboard UI | US7.1 | 4 | Frontend | 🟠 P1 | T5.4 |
| **T7.2** | Implement filtering + sorting on expert queue | US7.1 | 2 | Frontend | 🟠 P1 | T7.1 |
| **T7.3** | Build expert decision form (approve/override/request) | US7.2 | 3 | Frontend | 🟠 P1 | T7.1 |
| **T7.4** | Implement feedback recording backend | US7.2 | 2 | Backend | 🟠 P1 | T4.15 |
| **T7.5** | Build weekly accuracy metrics report | US7.3 | 3 | Backend | 🟠 P1 | T4.16 |
| **T7.6** | Implement feedback aggregation + alerting (accuracy drop) | US7.3 | 2 | Backend | 🟠 P1 | T7.5 |
| **T7.7** | Build retraining pipeline (weekly batch + validation) | US7.4 | 8 | ML Eng + Backend | 🟠 P1 | T4.20 |
| **T7.8** | Implement model versioning + rollback mechanism | US7.4 | 3 | Backend + DevOps | 🟠 P1 | T7.7 |

**Epic 7 Total:** 27 points

### Epic 8a: Containerization & CI/CD

| ID | Task | Story | Points | Owner | Priority | Dependencies |
|----|----|--------|--------|-------|----------|--------------|
| **T8.1** | Create Dockerfile for API service | US8.1 | 2 | DevOps | 🔴 P0 | T0.3 |
| **T8.2** | Create Dockerfile for worker service (Celery) | US8.1 | 2 | DevOps | 🔴 P0 | T0.3 |
| **T8.3** | Create docker-compose.yml (full stack: API, worker, DB, cache) | US8.1 | 2 | DevOps | 🔴 P0 | T8.1, T8.2 |
| **T8.4** | Test local development (docker-compose up) | US8.1 | 1 | DevOps | 🔴 P0 | T8.3 |
| **T8.5** | Set up GitHub Actions workflow (lint, test, build) | US8.2 | 4 | DevOps | 🔴 P0 | T0.1 |
| **T8.6** | Implement unit test runner in CI | US8.2 | 2 | Backend + DevOps | 🔴 P0 | T8.5 |
| **T8.7** | Implement integration test runner in CI | US8.2 | 2 | Backend + DevOps | 🔴 P0 | T8.5 |
| **T8.8** | Add security scanning (Snyk, bandit) to CI | US8.2 | 2 | DevOps | 🟠 P1 | T8.5 |
| **T8.9** | Set up ECR (Elastic Container Registry) + push Docker images | US8.2 | 2 | DevOps | 🔴 P0 | T8.5 |

**Epic 8a Total:** 19 points

### Epic 8b: Infrastructure as Code

| ID | Task | Story | Points | Owner | Priority | Dependencies |
|----|----|--------|--------|-------|----------|--------------|
| **T8.10** | Create Terraform modules (VPC, security groups, IAM) | US8.3 | 4 | DevOps | 🔴 P0 | T0.2 |
| **T8.11** | Create Terraform module for RDS (PostgreSQL multi-AZ) | US8.3 | 3 | DevOps | 🔴 P0 | T8.10 |
| **T8.12** | Create Terraform module for ElastiCache (Redis) | US8.3 | 2 | DevOps | 🔴 P0 | T8.10 |
| **T8.13** | Create Terraform module for S3 (versioning, encryption) | US8.3 | 2 | DevOps | 🔴 P0 | T8.10 |
| **T8.14** | Create Terraform module for ECS (Fargate cluster, task definition) | US8.3 | 4 | DevOps | 🔴 P0 | T8.10 |
| **T8.15** | Create Terraform environments (dev, staging, prod configs) | US8.3 | 2 | DevOps | 🔴 P0 | T8.14 |
| **T8.16** | Implement Secrets Manager integration (passwords, API keys) | US8.3 | 2 | DevOps | 🔴 P0 | T8.14 |
| **T8.17** | Document Terraform modules (README, examples) | US8.3 | 1 | DevOps | 🟠 P1 | T8.16 |

**Epic 8b Total:** 20 points

### Epic 8c: Production Deployment

| ID | Task | Story | Points | Owner | Priority | Dependencies |
|----|----|--------|--------|-------|----------|--------------|
| **T8.18** | Set up ArgoCD for GitOps deployment | US8.4 | 3 | DevOps | 🔴 P0 | T8.5, T8.15 |
| **T8.19** | Implement canary deployment strategy (10% → 100%) | US8.4 | 3 | DevOps | 🔴 P0 | T8.18 |
| **T8.20** | Set up Prometheus monitoring + Grafana dashboards | US8.4 | 4 | DevOps | 🔴 P0 | T8.15 |
| **T8.21** | Implement ELK stack (Elasticsearch, Logstash, Kibana) | US8.4 | 4 | DevOps | 🔴 P0 | T8.15 |
| **T8.22** | Configure alerting (error rate, latency, GPU utilization) | US8.4 | 2 | DevOps | 🔴 P0 | T8.20 |
| **T8.23** | Set up PagerDuty + Slack integration | US8.4 | 1 | DevOps | 🟠 P1 | T8.22 |
| **T8.24** | Perform load testing (k6) on staging environment | US8.4 | 3 | QA + DevOps | 🔴 P0 | T8.18 |
| **T8.25** | Create runbooks for operational incidents | US8.4 | 2 | DevOps | 🟠 P1 | T8.20 |
| **T8.26** | Deploy to production (blue-green or canary) | US8.4 | 2 | DevOps | 🔴 P0 | T8.24 |

**Epic 8c Total:** 24 points

**Sprint 5 Grand Total:** 90 points

---

## SPRINT 6: TESTING & LAUNCH (Week 19-21)

### Quality Assurance & Release Preparation

| ID | Task | Epic | Points | Owner | Priority | Dependencies |
|----|----|------|--------|-------|----------|--------------|
| **T9.1** | End-to-end system testing (5 test scenarios) | All | 5 | QA | 🔴 P0 | T8.26 |
| **T9.2** | Performance testing: API latency <2.5s (p99) | E5 | 3 | QA + DevOps | 🔴 P0 | T8.26 |
| **T9.3** | Security testing: Penetration test + vulnerability scan | E8 | 4 | Security | 🔴 P0 | T8.26 |
| **T9.4** | User acceptance testing (UAT) with client (2 weeks) | All | 5 | PM + Client | 🔴 P0 | T8.26 |
| **T9.5** | Fix critical bugs from UAT | All | 8 | Backend + Frontend | 🔴 P0 | T9.4 |
| **T9.6** | Performance optimization: Database query tuning | E5 | 3 | Backend | 🟠 P1 | T9.2 |
| **T9.7** | Performance optimization: Model inference batching | E2 | 3 | ML Eng | 🟠 P1 | T9.2 |
| **T9.8** | Write deployment runbook + operational docs | E8 | 2 | DevOps + Tech Writer | 🟠 P1 | T8.26 |
| **T9.9** | Prepare customer documentation (user guide, FAQs) | All | 3 | Tech Writer | 🟠 P1 | T9.4 |
| **T9.10** | Train customer support team | All | 2 | PM + Support | 🟠 P1 | T9.9 |

**Sprint 6 Grand Total:** 38 points

---

## SPRINT 7: PHASE 2 PREVIEW & POST-LAUNCH (Week 22+)

### Phase 2 Integration (CATIA, DSM) - Out of Scope for MVP

| ID | Task | Story | Points | Owner | Priority | Timeline |
|----|----|--------|--------|-------|----------|----------|
| **T10.1** | Design CATIA add-in architecture (VB.NET) | US8.5 | 5 | Backend | 🟡 P2 | Phase 2 Week 1-2 |
| **T10.2** | Implement CATIA macro wrapper | US8.5 | 5 | Backend | 🟡 P2 | Phase 2 Week 1-2 |
| **T10.3** | Design DSM integration API | US8.6 | 3 | Backend | 🟡 P2 | Phase 2 Week 3-4 |
| **T10.4** | Implement DSM API client | US8.6 | 4 | Backend | 🟡 P2 | Phase 2 Week 3-4 |

**Phase 2 Total:** 17 points (deferred)

---

## PRIORITY SEQUENCING & CRITICAL PATH

```
CRITICAL PATH (must complete in sequence):
┌─────────────────────────────────────┐
│ Sprint 0: Setup + Requirements      │ (22 pts)
│           ↓                         │
│ Sprint 1: Data + YOLO/Donut Models  │ (83 pts)
│           ↓                         │
│ Sprint 2: Data Extraction           │ (50 pts)
│           ↓                         │
│ Sprint 3: Rules Engine              │ (70 pts) ← Go/No-Go Gate
│           ↓                         │
│ Sprint 4: Reporting + UI            │ (65 pts)
│           ├─ Epic 5 (46 pts)        │
│           └─ Epic 6 (19 pts, parallel)
│           ↓                         │
│ Sprint 5: Expert Workflow + Deploy  │ (90 pts)
│           ├─ Epic 7 (27 pts)        │
│           └─ Epic 8 (63 pts)        │
│           ↓                         │
│ Sprint 6: Testing + Launch          │ (38 pts)
│           ↓                         │
│ MVP RELEASE (Week 21)               │
└─────────────────────────────────────┘
```

---

## DEPENDENCY MAP

```
T0.1 (GitHub)
├─ T0.2 (AWS Setup)
├─ T0.3 (Dev Env)
│  ├─ T1.1 → T1.2 → T1.3 → T1.5
│  ├─ T2.7 → T2.8 → T2.10
│  ├─ T2.14 → T2.15 → T2.16 → T2.17
│  └─ T8.1 → T8.3 → T8.4
└─ T0.5 (PostgreSQL)
   └─ T1.8 → T1.9 → (ALL Epic 1 tasks)

T1.6 (CATIA Converter) + T1.7 (Preprocess)
└─ T2.1 (Get 100 drawings) → T2.2 → T2.3 → T2.4 → T2.5

T2.5 (Dataset) + T2.7 → T2.8 (YOLO train)
└─ T2.10 (Validate) → T2.13 (Save to S3)

T2.13 (YOLO) + T2.19 (Donut)
└─ T3.2 + T3.3 (Inference) → T3.4-3.8 (Extractors)

T3.9 (Extraction Orch) → T3.12 (JSON Schema)
└─ T4.1 (Rules Schema) → T4.2-4.7 (Codify rules) → T4.8 (Engine)

T4.8 (Rule Engine) + T4.20 (Validation)
└─ T5.1 (Report Schema) → T5.2 (JSON Gen) → T5.4-5.5 (HTML)

T8.1-8.3 (Docker) → T8.5 (CI/CD) → T8.9 (ECR)
T0.2 → T8.10-8.15 (Terraform) → T8.18 (ArgoCD)
T8.18 + T8.19 → T8.24 (Load Test) → T8.26 (Production Deploy)
```

---

## RISK & BUFFER

| Risk | Mitigation | Buffer (Days) |
|------|-----------|---------------|
| Dataset annotation delay (client) | Negotiate early; provide template | +5 days Sprint 1 |
| Model training convergence issues | Monitor loss curves; adjust hyperparameters | +3 days Sprint 1 |
| Rule ambiguity → expert refinement needed | Allocate retraining loop (T7.7) | +5 days Sprint 5 |
| Infrastructure provisioning delays | Use pre-built Terraform modules | +2 days Sprint 5 |
| GPU availability on cloud | Use on-demand + spot instances | Contingency plan |

**Total Recommended Buffer:** ~15% of schedule (2-3 weeks)
**Realistic MVP Launch:** Week 21-23 (vs. planned Week 21)

---

## ACCEPTANCE CRITERIA BY EPIC

### Epic 1: ✅ All Story Points Complete When:
- [x] File upload API tested
- [x] CATIA conversion working
- [x] Preprocessing produces optimal images
- [x] S3 storage accessible
- [x] Audit trail immutable

### Epic 2: ✅ All Story Points Complete When:
- [x] 100 drawings annotated + validated (kappa >0.95)
- [x] YOLO trained (mAP50 ≥0.95, mAP50-95 ≥0.85)
- [x] Donut fine-tuned (CER <5%)
- [x] Inference latency <2.5s end-to-end

### Epic 3: ✅ All Story Points Complete When:
- [x] All extractors (cartouche, dim, GD&T, weld, finish) functional
- [x] >90% accuracy on test set
- [x] Extraction confidence scoring working

### Epic 4: ✅ All Story Points Complete When:
- [x] 20+ rules coded in YAML
- [x] Rule engine evaluating correctly
- [x] Expert agreement >90% on 50 test drawings
- [x] Anomalies detected accurately

### Epic 5: ✅ All Story Points Complete When:
- [x] JSON + HTML + CSV reports generating
- [x] Web UI all pages functional
- [x] Violations highlighted on images

### Epic 6: ✅ All Story Points Complete When:
- [x] Knowledge base indexed (30+ documents)
- [x] RAG queries returning relevant answers
- [x] Chat UI functional

### Epic 7: ✅ All Story Points Complete When:
- [x] Expert dashboard filtering/sorting working
- [x] Decisions recorded + feedback loop active
- [x] Weekly accuracy metrics generated

### Epic 8: ✅ All Story Points Complete When:
- [x] Docker images built + pushed to ECR
- [x] CI/CD pipeline passing all tests
- [x] Terraform infrastructure provisioned
- [x] Production deployment successful
- [x] Monitoring + alerting active

---

## RESOURCE ALLOCATION RECOMMENDATIONS

### Team Composition for 7 Sprints

| Role | Count | Full-Time | Sprints | Notes |
|------|-------|-----------|---------|-------|
| Backend Engineer | 2 | 100% | 0-6 | API, extraction, rules engine |
| ML Engineer | 2 | 100% | 0-6 | Data, training, inference, retraining |
| Frontend Engineer | 1-2 | 100% | 1-6 | Web UI, reporting visualization |
| DevOps Engineer | 1 | 100% | 0-6 | Infrastructure, CI/CD, monitoring |
| QA / Test Engineer | 1-2 | 100% | 0-6 | Testing, validation, metrics |
| Rules Architect | 1 | 50% | 3-5 | Rule definition, expert validation |
| Data Annotator(s) | 2-3 | 100% | 1-2 | Dataset annotation only |
| Product Manager | 1 | 50% | 0-6 | Requirements, stakeholder mgmt |
| Tech Writer | 1 | 50% | 1-6 | Documentation |

**Total FTE:** ~11.5 (range: 10-14 depending on sprint)

---

**END OF TASKS DOCUMENT**

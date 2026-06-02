# REQUIREMENTS ANALYSIS
## ISO Technical Drawing Validator System

**Document Version:** 1.0  
**Last Updated:** 2026-05-07  
**Prepared by:** Business Analyst (Mary)  
**Approval Status:** ⏳ Pending Stakeholder Validation

---

## EXECUTIVE SUMMARY

**Problem:** Engineering organizations lack automated validation of technical ISO drawings. Current workflows rely on manual expert review, which is time-consuming, error-prone, and dependent on individual expertise. Plans serve as the "final contract" before fabrication, making validation accuracy critical.

**Opportunity:** Implement an AI-powered validation system that detects layout elements (title blocks, GD&T frames, dimensions, weld specs) and verifies ISO conformance through automated rule checking, coupled with human-expert workflows for complex decisions.

**Scope:** Mechanical engineering domain (CATIA V5 digital drawings); future extensibility to automotive, systems engineering.

**Business Impact:** 
- Reduce plan review time by 40-60% (expert estimate: 4-6 hours → 2 hours per complex plan)
- Improve error detection rate to >90% on systematic violations (dimensional inconsistencies, missing specs)
- Standardize validation across teams; reduce domain expertise dependency

---

## BUSINESS CONTEXT

### Organization Profile
- **Type:** Manufacturing engineering / Design & Engineering services
- **Domain:** Mechanical design; ISO-compliant technical drawings
- **Current Tools:** CATIA V5 (digital drawing platform); manual checklist-based review
- **Team:** Design engineers, calculation engineers, verification experts, manufacturing support
- **Scale:** 20+ plans reviewed monthly; complex drawings take 4-6 hours each

### Current State
- **Process:** Design → 3D CATIA → 2D Drawing (export) → Manual Verification (checklist) → Fabrication
- **Verification Method:** Expert eye-ball review + printed checklists; no automated assistance
- **Data Storage:** CATIA files (V5) + DSM (Design Structure Matrix) files organized by project
- **Quality Gates:** 
  - Cartouche accuracy (designation, ref, indices, authors, scale, projection)
  - Dimensional consistency (2D/3D concordance)
  - GD&T frame validity (ISO 1101 compliance)
  - **Weld Specifications & NOTA:** Mécanosoudé drawings reference external quality document; system must cross-validate
- **Material Nomenclature:** EN/ISO material codes must be recognized and validated
- **BOM Validation:** Sub-assembly drawings must reconcile parts against BOM
- **Approval Workflow:** Immutable signature capture + audit trail for certification audits
  - Surface finish conformance (environmental criteria)
  - Structural consistency (no contradictions between tolerances, standards)

### Pain Points Identified
1. **Time-consuming manual review** — Complex plans take 4-6 hours for expert validation
2. **Error proneness** — Frequent mismatches between 2D/3D indices, outdated CATIA views, dimension inconsistencies
3. **Expertise dependency** — Validation quality varies by reviewer; junior engineers struggle
4. **No systematic coverage** — Checklists exist but application is inconsistent
5. **Calculation-to-3D verification gap** — Current method (visual overlay of FEA mesh + CATIA) is subjective
6. **Documentation standardization** — Calculation notes (NCE) lack uniform structure; hard to cross-reference
7. **Costly stabilization decisions** — Unclear when reinforcement/fine-tuning is needed; decided ad-hoc
8. **Expensive compliance data** — ISO standards are paid (~€1M for 700 standards); cannot acquire all

---

## PROBLEM STATEMENT

**Current Situation:**
- Plans are verified manually using printed checklists and expert judgment
- No automated detection of layout elements or rule violations
- Verification depends on individual expertise and is subject to human error
- Complex plans (with 50+ dimensions, 20+ GD&T frames, weld specs) require 4-6 expert-hours
- No feedback loop; errors caught late (during fabrication or assembly)
- Calculation-to-3D concordance verified visually (error-prone)

**Desired Future State:**
- Automated detection of drawing zones (title block, notes, GD&T, dimensions, weld symbols)
- Structured extraction of all metadata (text, symbols, specs)
- Rule-based validation against ISO standards (ISO 2768, 1101, 5817, 13920, 12944, etc.)
- Real-time anomaly flagging (contradictions, missing specs, wrong placement)
- Pre-filled validation report (pass/fail/review) with highlighted violations
- Human expert workflow for ambiguous cases (e.g., "stabilization necessary?")
- Continuous learning loop; dataset grows with user feedback

**Root Cause:** No systematic way to extract and validate drawing semantics at scale.

---

## GOALS & OBJECTIVES

### Business Goals
1. **Reduce validation cycle time** — 40-60% reduction in expert-hours per plan (4-6 hours → 2 hours)
2. **Improve error detection** — Catch 90%+ of systematic violations (dimensional, GD&T, surface finish inconsistencies) before fabrication
3. **Standardize validation** — Enforce consistent ISO compliance across all engineers and projects using **three distinct drawing type rules** (Pièce, Mécanosoudé, Sub-ensemble)
4. **Reduce expertise dependency** — Junior engineers can now validate using system-assisted workflow
5. **Enable feedback loop** — Collect failure data; use to improve 3D design processes
6. **Support formal approval workflow** — Track drawer & reviewer sign-offs; maintain immutable audit trail for compliance audits

### Technical Objectives
1. **Classify drawing type** — Automatically detect whether drawing is Part (076-A), Welded Assembly (077-A), or Sub-assembly (078-A) with >95% accuracy
2. **Automate zone detection** — Identify 8+ zone types (cartouche, notes, GD&T frames, dimensions, weld specs, material debris, BOM, surface finish) with >90% recall
3. **Extract structured data** — OCR + semantic parsing to populate standardized JSON schema; support 170+ validation checkpoints across drawing types
4. **Codify drawing-specific rules** — Translate client checklists (076-A: 59 rules, 077-A: 55 rules, 078-A: 56 rules) + ISO standards into rule engine
5. **Handle ambiguous cases** — Route to expert workflow with context (e.g., "is stabilization needed?"; "does weld spec match NOTA?")
6. **Support approval workflow** — Capture drawer & reviewer signatures; maintain immutable audit trail
7. **Integrate external documents** — Cross-validate weld specs against external NOTA document (ECM_Note Qualité en soudage)
8. **Integrate with tools** — API connectivity to CATIA export (PDF/PNG), report management system

### Success Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| **Precision** (detection) | >90% | Bounding box IoU > 0.85 on test set |
| **Recall** (detection) | >95% | No missed zones in 95% of drawings |
| **OCR Accuracy** | >92% | Character Error Rate <5% on dimensions/specs |
| **Rule Coverage** | 170+ checkpoints | 059-A: 59, 077-A: 55, 078-A: 56 across all drawing types |
| **Standards Registry** | ISO versions tracked | NF EN ISO 5459, 13920, 1101, 21920-1, etc., with effective dates |
| **Time Saved** | 40-60% | Expert validation <2.5 hours for complex plan |
| **BOM Extraction** | 100% | Extract part numbers, quantities, references for Sub-assembly drawings (078-A) |
| **Weld NOTA Validation** | >85% | Validate Mécanosoudé weld specs against external ECM NOTA document |
| **Approval Workflow** | 100% | Capture & track drawer + reviewer approval signatures + audit trail |
| **User Adoption** | 80%+ | 80% of team uses system within 6 months |

---

## STAKEHOLDERS

| Role | Title | Interest | Influence | Availability |
|------|-------|----------|-----------|--------------|
| **Valentin** | Design Director / Sponsor | Standardize validation; reduce costs | 🔴 Very High | Quarterly reviews |
| **Expert Reviewer (Manual)** | Senior Design Engineer | Reduce manual effort; maintain quality | 🟠 High | Sprint reviews |
| **Nathan** | Junior ML Engineer (Intern) | Learn AI/ML in production; contribute | 🟡 Medium | Daily |
| **Calculator/FEA** | Structural Engineer | Verify calculation-to-3D concordance | 🟡 Medium | As needed |
| **Manufacturing** | Production Lead | Early error detection; reduce rework | 🟠 High | Weekly |
| **IT/DevOps** | Infrastructure | System deployment; data storage | 🟡 Medium | On demand |

---

## USER PERSONAS

### Persona 1: Expert Verification Engineer
**Name:** Claude (Verification Lead)  
**Needs:**
- Automated pre-screening to flag obvious errors
- Human workflow for ambiguous cases ("is this tolerance contradiction critical?")
- Audit trail; documented decisions
- Quick access to ISO standards for reference

**Pain:** Currently spends 4 hours per complex plan; wants to focus on design improvement, not paperwork

**Usage Pattern:** Batch reviews; 2-3 plans per day

### Persona 2: Junior Design Engineer
**Name:** Alice (New to team)  
**Needs:**
- Guidance on what's wrong with a drawing
- Learning aid; understand ISO rules applied
- Suggestions for fixes

**Pain:** Doesn't know all ISO rules yet; fears missing critical errors

**Usage Pattern:** Frequent; whenever design is ready for review

### Persona 3: Manufacturing/Quality
**Name:** Bob (Production Planner)  
**Needs:**
- Early warning of specification inconsistencies
- Clear report of what was verified vs. what needs manual check
- Traceability for compliance audits

**Pain:** Receives drawings with errors; causes delays and rework

**New Persona 4: Project Manager / Compliance Officer**
**Name:** Carol (Compliance Lead)  
**Needs:**
- Formal approval audit trail for ISO certification audits
- Project-level custom rules configuration
- Batch validation reports (100+ drawings at once)

**Pain:** Currently no proof of compliance; auditors question validation methodology

**Usage Pattern:** Monthly compliance reporting; ad-hoc audits

---

## FUNCTIONAL REQUIREMENTS

### F1: Drawing Input & Preprocessing
- **F1.1** Accept CATDrawing exports (PDF, PNG, STEP format)
- **F1.2** Auto-normalize image (rotate, denoise, enhance contrast for OCR)
- **F1.3** Store original + processed image with metadata (filename, upload time, user)
- **F1.4** Handle multi-page drawings (split, process separately)

### F1.5: Drawing Type Classification
- **F1.5.1** Automatically classify drawing as one of three types:
  - Type A: Plan Pièce (Part Drawing, 076-A) → 59 validation rules
  - Type B: Plan Mécanosoudé (Welded Assembly, 077-A) → 55 validation rules + welding specs
  - Type C: Plan Sous-ensemble (Sub-assembly, 078-A) → 56 validation rules + BOM validation
- **F1.5.2** Confidence score for classification; route to manual review if <85%
- **F1.5.3** Trigger drawing-type-specific extraction & validation pipelines

### F2: Zone Detection & Localization
- **F2.1** Detect bounding boxes for zones (drawing-type-dependent):
  - **All types:** Title block / Cartouche, Notes section, GD&T frames, Dimension fields, Surface finish specs, Revision table, General drawing area
  - **Mécanosoudé (077-A):** Weld symbols/specs, Material & debris section
  - **Sub-ensemble (078-A):** BOM table, Assembly specifications
- **F2.2** Output bounding box coordinates + confidence scores
- **F2.3** Handle rotated/skewed zones (OBB support)
### F5 Approval Workflow
- **F5.1** Capture drawer signature + date (form field)
- **F5.2** Capture reviewer approval:
  - Approval status: OK / NOK / PENDING
  - Reviewer name, date, signature
  - Comments field
- **F5.3** Generate approval audit trail:
  - Timestamp of each state change
  - User who made change
  - Immutable database entries (no updates; only inserts + soft deletes)
- **F5.4** Support workflow: DRAFT → SUBMITTED → APPROVED/REJECTED
- **F2.5** For Mécanosoudé: Cross-reference detected weld symbols to external NOTA document

### F3: Text Extraction & Semantic Parsing
- **F3.1** OCR all detected zones (Donut model)
- **F3.2** Parse cartouche fields:
  - Designation, Reference, Index
  - Author names, Date
  - Scale, Projection system
  - Mass (if present)
  - Additional metadata (drawing status, etc.)
- **F3.3** Parse dimensions:
  - Value + unit
  - Tolerance (upper/lower)
  - GD&T modifiers (Ø, M, L)
  - Function/reference info
- **F3.4** Parse GD&T symbols + datums (ISO 1101)
### F6: Support External Document Links (NOTA, Standards)
- **F6.1** Fetch external documents (NOTA, ISO standards) from document registry
- **F6.2** For Mécanosoudé drawings: Validate weld specs against NOTA
- **F6.3** For all drawings: Link extracted data to applicable ISO standards
- **F6.4** Display document references in extraction output + validation report

### F7: Project-Level Custom Rules
- **F7.1** Load project-specific rule overrides from configuration
- **F7.2** Support 7-15 custom rules per project ("exigences spécifiques au projet")
- **F7.3** UI to manage custom rules (create, edit, delete, enable/disable)
- **F7.4** Version control custom rules; maintain audit trail of changes

### F4 Validation Rules Engine
- **F4.1** Load drawing-type-specific rule sets:
  - **Pièce (076-A):** 59 rules across 7 categories
  - **Mécanosoudé (077-A):** 55 rules + weld/NOTA validation
  - **Sub-ensemble (078-A):** 56 rules + BOM reconciliation
- **F4.2** Validate against ISO standards:
  - General: NF EN ISO 5459 (referencing), ISO 2768 (general tolerancing)
  - GD&T: NF EN ISO 1101, NF EN 14405
  - Welds: NF EN ISO 13920, ISO 5817 (referenced via NOTA)
  - Surface finish: NF EN ISO 21920-1, NF EN ISO 12944 (paint)
- **F4.3** Support project-level custom rules (7-15 per project)
- **F4.4** Return: violations array with {rule_id, severity, message, affected_field, standard_ref, recommendation}
- **F4.5** Severity levels: CRITICAL, HIGH, MEDIUM, LOW
- **F4.6** Overall status: PASS (all critical pass) | FAIL (≥1 critical fail) | REVIEW (high/ambiguous)
- **F4.1** Apply rules in categories:
  - **Cartouche:** Required fields present, format correct, indices match 3D
  - **Dimensions:** Functional vs. manufacturing distinction, hors-tout format (parentheses), consistency
  - **Tolerances:** ISO 2768 (machining) vs. 13920 (welding) coherence; no contradictions
  - **GD&T:** Symbol valid, datums referenced, placement correct
  - **Welds:** NOTA ↔ CNE alignment, CND levels specified, ISO conformance
  - **Surface Finish:** Env criteria specified (maritime, outdoor, climate-controlled)
  - **Structural:** No overlapping zones, mass only on final plan, stabilization logic
- **F4.2** Return rule results: PASS | FAIL | REVIEW_NEEDED (with context)
- **F4.3** Prioritize violations by severity (CRITICAL | HIGH | MEDIUM | LOW)

### F5: Anomaly Detection
- **F5.1** Flag unexpected patterns:
  - Missing expected zones (no cartouche)
  - Conflicting standards (ISO 2768 but no machining intent)
  - Geometric inconsistencies (dimensions off CATIA by >5%)
  - Rare conditions (e.g., mass specified on non-final plan)
- **F5.2** Human review flag with confidence score

### F6: Report Generation
- **F6.1** Generate structured JSON output:
  ```json
  {
    "drawing_id": "...",
    "zones_detected": [...],
    "extractions": {...},
    "validation_results": {...},
    "anomalies": [...],
    "overall_status": "PASS|FAIL|REVIEW",
    "pass_rate": 0.95,
    "violations": [...],
    "recommendations": [...]
  }
  ```
- **F6.2** Generate human-readable HTML report:
  - Thumbnail of original drawing
  - Highlighted violations (color-coded by severity)
  - Extracted fields (cartouche, dimensions, specs)
  - Pass/fail summary by category
  - Next steps / recommendations
- **F6.3** Export to CSV for bulk analysis
- **F6.4** Audit trail (what was checked, when, by whom)

### F7: Expert Workflow & Disambiguation
- **F7.1** Route ambiguous rules to expert queue:
  - "Stabilization necessary given design loads?"
  - "Is this tolerance conflict acceptable?"
  - "3D geometry matches drawing?" (requires manual check)
- **F7.2** Provide context:
  - OCR confidence scores
  - Related calculation notes (if available via DSM)
  - Historical similar cases
- **F7.3** Record expert decision + rationale
- **F7.4** Feedback loop: decisions used to refine rules/thresholds

### F8: ISO Standards Reference (RAG System)
- **F8.1** Searchable knowledge base:
  - Veritas synthesis (weld standards)
  - Open ISO references (ISO 286-1 free subset, etc.)
  - Client checklists (codified rules)
  - Technical glossary (bolt, nut, fastener, datum, etc.)
- **F8.2** Query system: "Is M6 socket-head cap screw per ISO 4762?"
- **F8.3** Answer with source + confidence
- **F8.4** Integrate with validation engine (e.g., rule engine queries RAG when uncertain)

### F9: User Interface & Interaction
- **F9.1** Web UI (React/Vue + FastAPI backend):
  - Upload drawing (drag & drop)
  - Auto-process (detect → extract → validate)
  - View report (tabbed: summary | zones | violations | recommendations)
  - Manual override for ambiguous detections
  - Download report (JSON, HTML, CSV)
- **F9.2** Role-based access:
  - Viewer: Read-only reports
  - Reviewer: Approve/reject, provide feedback
  - Admin: Manage rules, configure system
- **F9.3** Audit trail visible to all roles

### F10: Integration & Data Persistence
- **F10.1** API endpoints (OpenAPI spec):
  - POST /api/validate (async job)
  - GET /api/status/{job_id}
  - GET /api/report/{job_id}
  - POST /api/rag/ask (query ISO standards)
  - POST /api/feedback (user correction feedback)
- **F10.2** Store validated drawings + reports in database
- **F10.3** Versioning: track model versions used for each validation
- **F10.4** Export to external systems (CAM, MES, compliance tracking)

---

## NON-FUNCTIONAL REQUIREMENTS

### Performance
- **NFR1.1** Single drawing validation <2.5 seconds (YOLO + Donut inference)
- **NFR1.2** Report generation <1 second
- **NFR1.3** Web UI responsive; load report page <500ms
- **NFR1.4** Batch processing 50 drawings in <150 seconds (parallelizable)

### Scalability
- **NFR2.1** Support 100+ concurrent users
- **NFR2.2** Handle 1000+ validated drawings per day
- **NFR2.3** Horizontal scaling (stateless API, distributed inference)

### Reliability
- **NFR3.1** 99.5% uptime (SLA)
- **NFR3.2** Graceful degradation if models fail (fallback to manual mode)
- **NFR3.3** Automatic retraining pipeline (weekly model updates)

### Security
- **NFR4.1** Authentication (OAuth2 or OIDC via corporate SSO)
- **NFR4.2** Authorization: role-based access control (RBAC)
- **NFR4.3** Data encryption in transit (TLS 1.2+) and at rest
- **NFR4.4** Audit logging: all user actions traceable
- **NFR4.5** Data retention policy (drawings archived after 2 years)

### Maintainability
- **NFR5.1** Code modular; rules engine decoupled from inference
- **NFR5.2** Comprehensive logging (DEBUG, INFO, WARN, ERROR levels)
- **NFR5.3** Documentation: API docs, deployment guide, troubleshooting
- **NFR5.4** CI/CD pipeline (automated testing, automated deployment)

### Usability
- **NFR6.1** Intuitive UI; <5 min learning curve for new users
- **NFR6.2** Offline fallback: view reports without internet
- **NFR6.3** Internationalization: support French + English (initial); extensible to others
- **NFR6.4** Mobile-friendly (responsive design)

### Compliance
- **NFR7.1** GDPR compliance (personal data handling)
- **NFR7.2** Traceability for quality audits (ISO 9001, etc.)
- **NFR7.3** Data residency: comply with local storage laws

---

## BUSINESS RULES

### BR1: Drawing Status & Completeness
- A drawing must have a cartouche to be validated
- Mass field is only expected on FINAL plans; flag WARNING if present on intermediate
- Revision index must match 3D model index (CRITICAL if mismatch)

### BR2: Dimensional Rules
- Functional dimensions: must be clearly distinguished from manufacturing dimensions
- Hors-tout (overall) dimensions: enclosed in parentheses = informational only
- Manufacturing dimensions: no parentheses = binding specification
- No dimension should be "neither tail nor head" (meaningless)

### BR3: Tolerance Standards Coherence
- ISO 2768 (machining): applicable only if machining intent is present
- ISO 13920 (welding): very broad tolerances; contradiction if both 2768 + 13920 cited but no welding
- If both cited: explicit justification required (flag for REVIEW)

### BR4: GD&T & Datum Rules
- All datums referenced in GD&T must be defined as primary (A), secondary (B), or tertiary (C)
- Datum symbols must follow ISO 1101 conventions
- Position/profile frames must reference at least one datum (if required by function)

### BR5: Weld Specification Rules
- NOTA (marking drawing) must correspond to CNE (weld expertise note)
- CND levels (visual, dye penetrant, magnetic) must be specified for critical welds
- Weld symbols must follow ISO 1101/5817 conventions

### BR6: Surface Finish Rules
- Finish specification must include environmental context (storage location, climate)
- ISO 12944 equivalent required if marine/exterior environment
- Paint/coating criteria must be compatible with base material

### BR7: Structural Consistency
- No overlapping zones of importance (title block, GD&T frames, dimensions)
- All required zones must be detectable (else flag WARNING → REVIEW)
- Plan totality: all functional elements must be present for sign-off

### BR8: Stabilization Logic
- Stabilization (reinforcement/fine-tuning) needed ONLY if:
  - High loads pass through part (calculated), AND
  - Design geometry changed after calculation, OR
  - High-precision finish required AND geometry sensitive
- Flag: "Stabilization required: CONFIRM with engineer" (expert decision)

### BR9: Calculation-to-3D Concordance
- FEA mesh should overlay with 3D CATIA geometry (visual check)
- Tolerance envelope must accommodate calculated stress distribution
- If significant deviation: flag "Recalculation recommended"

### BR10: Data Standardization
- All extractions normalized to ISO terminology
- Dates in ISO 8601 format (YYYY-MM-DD)
- Dimensions in SI units (mm, m/s², etc.)
- Tolerance formatting: ±0.05 or +0.10/-0.05 conventions

---

## CONSTRAINTS

### Technical Constraints
- **TC1** Dataset limited (<50 annotated drawings at launch); model performance depends on quality
- **TC2** OCR fails on small text (<10pt); needs preprocessing or manual fallback
- **TC3** Handwritten annotations not supported (v1); future enhancement
- **TC4** Plans must be digital CATIA exports (PDF/PNG); scanned paper limited precision
- **TC5** Inference latency tied to image resolution; 1024px balance quality vs. speed

### Business Constraints
- **BC1** ISO standards are paid (€1M for 700 standards); cannot acquire all → use open + synthesized
- **BC2** No "perfect reference plan" available; dataset grows iteratively with user feedback
- **BC3** Validation depends on standardized drawing practices; legacy plans may fail
- **BC4** Expert review still required for ambiguous cases (cannot eliminate humans)
- **BC5** Scope limited to mechanical domain (v1); other domains (automotive, systems) later

### Resource Constraints
- **RC1** Team: 1 ML Eng + 1 Backend Dev + 1 QA + 1 DevOps + domain expert (part-time)
- **RC2** Infrastructure: GPU availability (training); cloud deployment
- **RC3** Timeline: 16 weeks MVP + 8 weeks hardening/deployment

### Organizational Constraints
- **OC1** Must integrate with CATIA workflow (non-intrusive; uses exports)
- **OC2** Must respect data governance (DSM structure; project-based organization)
- **OC3** Change management needed (process shift from fully manual → assisted validation)

---

## RISKS

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Dataset too small (<30 plans) | 🟡 MEDIUM | 🔴 CRITICAL | Early negotiation; promise incremental model improvements |
| OCR fails on poor-quality scans | 🟡 MEDIUM | 🟡 MEDIUM | Preprocessing pipeline; manual fallback UI |
| Rules too ambiguous; system flags everything | 🟡 MEDIUM | 🟠 HIGH | Expert refinement loop; prioritize CRITICAL violations |
| Calculation-to-3D verification too complex | 🟢 LOW | 🔴 CRITICAL | Scope for Phase 2; document as manual process + AI assist |
| Expert availability bottleneck (ambiguous cases) | 🟠 HIGH | 🟠 HIGH | Batch review workflow; clear SLA for expert decisions |
| Model drift (new drawing types) | 🟠 HIGH | 🟡 MEDIUM | Continuous retraining; monitor performance on production data |
| Adoption resistance ("system doesn't understand my design") | 🟠 HIGH | 🟡 MEDIUM | Pilot + training; show ROI (time saved) |

---

## ASSUMPTIONS

1. **A1** CATIA drawings follow standard ISO conventions (not all custom practices)
2. **A2** Expert will refine rules based on initial feedback
3. **A3** Internet connectivity available (cloud deployment)
4. **A4** Users have basic technical proficiency (engineering background)
5. **A5** Drawings provided as high-quality digital exports (PDF/PNG >300 DPI)
6. **A6** Historical checklists are sufficiently comprehensive to codify as rules
7. **A7** Calculation notes (NCE) will eventually be standardized/structured
8. **A8** Fabrication downstream accepts structured validation report format
9. **A9** Corporate SSO available for authentication
10. **A10** GPU/compute resources available (training + inference)

---

## SUCCESS METRICS (DETAILED)

### Phase 1: Model Validation (Week 8)
- Precision >90% (bounding box detection)
- Recall >95% (no missed zones)
- OCR CER <5% (character error rate)
- User feedback: "Detects what I expect" (confidence >80%)

### Phase 2: Rule Coverage (Week 10)
- 90% checklist items implemented as rules
- <10% false positive rate on "clean" drawings
- Expert time to configure rules <10 hours

### Phase 3: MVP Deployment (Week 14)
- E2E validation time <2.5 seconds
- Report generation time <1 second
- 80% user satisfaction (Likert 4+/5)
- <5% system errors (500 errors)

### Phase 4: Production (Week 20)
- 99.5% uptime (measured)
- 100+ validated drawings per day
- Adoption rate 60%+ across team
- Cost per validation <€5 (operational cost)

---

## WORKFLOW ANALYSIS

### Current Workflow (As-Is)
```
1. Engineer completes 3D CATIA model
2. Engineer exports 2D drawing (PDF)
3. Prints drawing + grabs checklist
4. Expert manually reviews:
   - Cartouche completeness
   - Dimensional consistency (2D/3D)
   - GD&T symbol correctness
   - Tolerance ranges
   - Weld specs alignment with CNE
   - Surface finish per environment
5. Mark pass/fail/review on checklist
6. Return to engineer with annotations
7. Engineer updates drawing if FAIL
8. Loop until PASS
9. Sign off; send to fabrication
```
**Current time:** 4-6 hours for complex plan; 1-2 hours for simple

### Desired Workflow (To-Be)
```
1. Engineer completes 3D CATIA model
2. Engineer exports drawing (PDF)
3. Upload to validator UI
4. System auto-processes:
   a. Detect zones (cartouche, dimensions, GD&T, etc.)
   b. Extract text (OCR)
   c. Parse structures (dimensions, tolerances, specs)
   d. Validate against rules
   e. Generate report (JSON + HTML)
5. Engineer views report:
   - If PASS: proceed to fabrication
   - If FAIL/REVIEW: review highlighted violations
   - Click on violation → zoom to region + rule explanation
   - If ambiguous: route to expert (async queue)
6. Expert reviews flagged items (batch):
   - Confirm/override system decision
   - Provide rationale
   - Feedback improves model
7. Final sign-off; data logged for audit
```
**New time:** <10 minutes system processing + 30-60 min expert review (batch) + 15 min engineer updates

**Improvement:** 60% time savings on systematic violations; expert focus on design improvements, not paperwork

---

## INTEGRATION POINTS

### Systems to Integrate
1. **CATIA** → Export mechanism (PDF/PNG); notification of validation completion
2. **DSM (Design Structure Matrix)** → Link drawing to calculation notes; fetch related metadata
3. **CAM/MES** → Ingest validated report; flag for fabrication
4. **Compliance/QMS** → Audit trail integration (ISO 9001)
5. **Email** → Notifications (validation complete, expert review ready)
6. **Corporate SSO** → User authentication (OAuth2 / OIDC)

### Data Exchange Formats
- **Input:** CATIA PDF export (A3 standard), PNG, STEP (optional future)
- **Output:** JSON (structured), HTML (report), CSV (bulk analysis)

---

## OPEN QUESTIONS

1. **Q1** How to handle legacy drawings that don't follow standardized practices?
2. **Q2** Should system integrate with 3D CATIA file directly, or stick with 2D exports?
3. **Q3** Calculation-to-3D verification: Is visual overlay sufficient, or needed FEA file access?
4. **Q4** How to handle multi-sheet drawings (e.g., main plan + detail inserts)?
5. **Q5** Are there domain-specific drawing practices not covered by ISO standards?
6. **Q6** What's the SLA for expert review of flagged items (ambiguous rules)?
7. **Q7** Should system suggest corrections (e.g., "Change tolerance to X"), or only flag violations?
8. **Q8** Long-term: Integrate feedback loop to auto-retrain models on user corrections?

---

## NEXT STEPS FOR REQUIREMENTS VALIDATION

1. ✅ **This Document:** Approved by Analyst
2. ⏳ **Stakeholder Review:** Valentin + Expert review (1 week)
3. ⏳ **Refinement:** Address Q1-Q8 with client input
4. ⏳ **Sign-Off:** Final requirements locked for architecture phase

---

**END OF REQUIREMENTS ANALYSIS**

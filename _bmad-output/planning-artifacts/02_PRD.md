# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## ISO Technical Drawing Validator System

**Document Version:** 1.0  
**Prepared by:** Product Manager (John)  
**Based on:** requirements.md  
**Status:** ⏳ Draft (Pending Architecture Review)

---

## PRODUCT VISION

> **Enable engineering teams to validate ISO technical drawings automatically, reducing expert review time by 60% while improving systematic error detection to >90%, thereby accelerating design-to-fabrication cycles and standardizing compliance across all projects. Supports three distinct drawing types (Part/Welded/Assembly) with type-specific validation rules, formal approval workflow, and integration with external quality standards (NOTA documents).**

---

## PRODUCT SCOPE

### In Scope (MVP - 26-28 weeks)
- ✅ Mechanical engineering drawings (CATIA V5 digital exports)
- ✅ **Drawing type classification** (3 types: Pièce 076-A, Mécanosoudé 077-A, Sub-ensemble 078-A)
- ✅ Zone detection (cartouche, dimensions, GD&T, weld specs, surface finish, material debris, BOM)
- ✅ OCR + structured text extraction
- ✅ **170+ ISO conformance validation rules** (59 + 55 + 56 per drawing type)
- ✅ Material nomenclature validation (EN/ISO codes)
- ✅ **External NOTA document integration** (ECM_Note Qualité en soudage for weld validation)
- ✅ BOM reconciliation (Sub-assembly drawings)
- ✅ **Formal approval workflow** with immutable audit trail (drawer + reviewer sign-offs)
- ✅ Project-level custom rules (7-15 per project)
- ✅ Automated report generation (JSON, HTML, CSV)
- ✅ Expert workflow for ambiguous cases (queue management)
- ✅ ISO standards RAG system (searchable knowledge base)
- ✅ Web UI (single-page app; role-based access)
- ✅ REST API for integration
- ✅ Database storage + immutable audit trail

### Out of Scope (Future - Phase 2+)
- ❌ Calculation-to-3D concordance verification (visual overlay; too complex for v1)
- ❌ 3D CATIA file direct parsing (would require CATIA SDK; integration risk)
- ❌ Automotive / systems engineering domains (mechanics-only v1)
- ❌ Scanned paper drawings (digital CATIA exports only)
- ❌ Handwritten annotation detection
- ❌ Real-time collaborative editing (batch process first)
- ❌ Mobile native app (web-responsive, not native)

---

## PRODUCT STRATEGY

### Market Positioning
**Category:** AI-powered engineering compliance automation  
**Target:** Mid-to-large manufacturing/engineering firms (50-500+ engineers)  
**Value Prop:** Automate 60% of validation work; focus experts on design improvements, not paperwork

### Go-to-Market
- **Phase 1:** Internal pilot (your organization; 6-week pilot)
- **Phase 2:** Beta external (1-2 partner firms; feedback loop)
- **Phase 3:** Commercial release (SaaS model; per-drawing pricing or annual seat license)

### Success Criteria (OKRs)
- **O1** Reduce validation time by 40-60% (measured on 20+ plans)
- **O2** Achieve >90% systematic error detection (false negatives <10%)
- **O3** Reach 60%+ user adoption within 6 months of launch
- **O4** Maintain 99.5% system uptime (production)
- **O5** Support three distinct drawing types (Pièce/Mécanosoudé/Sub-ensemble) with >98% classification accuracy
- **O6** Validate >85% of weld specifications against external NOTA document
- **O7** Capture 100% of approval workflows with immutable audit trail
- **O8** Reconcile >90% of BOM entries for sub-assembly drawings

---

## USER STORIES & ACCEPTANCE CRITERIA

### Epic 1: Core Validation Engine

#### US1.1 – Upload & Auto-Process Drawing
**As a** verification engineer  
**I want to** upload a drawing and automatically detect layout zones  
**So that** I don't manually measure bounding boxes

**Acceptance Criteria:**
- [ ] User can drag-and-drop or select file (PDF, PNG)
- [ ] System detects 8+ zone types (cartouche, dimensions, GD&T, weld, surface finish, notes, revision, drawing area)
- [ ] Detection precision >90%; recall >95%
- [ ] User sees detected zones highlighted on image within 2.5 seconds
- [ ] Confidence scores displayed for each zone
- [ ] Zone can be manually adjusted if system misses/overcounts
- [ ] Adjustment saved to audit trail

---

#### US1.2 – Extract & Parse Text from Zones
**As a** reviewer  
**I want to** see extracted text (cartouche fields, dimensions, specs) in structured form  
**So that** I can quickly spot errors

**Acceptance Criteria:**
- [ ] OCR output visible with confidence scores
- [ ] Cartouche fields parsed: Designation, Reference, Index, Authors, Date, Scale, Projection, Mass
- [ ] Dimensions parsed: Value, Unit, Tolerance (upper/lower), GD&T modifiers (Ø, M, L)
- [ ] GD&T frames parsed: Symbol, Tolerance Value, Datums
- [ ] Weld specs parsed: Symbol, ISO code, CND level
- [ ] Surface finish parsed: Code, Environment context
- [ ] OCR CER <5%; user can correct errors inline
- [ ] Corrections logged to feedback system

---

#### US1.3 – Validate Drawing Against ISO Rules
**As a** system  
**I want to** check extracted data against codified rules  
**So that** users get pass/fail/review decision

**Acceptance Criteria:**
- [ ] 20+ rules implemented (see Business Rules section)
- [ ] Each rule returns: PASS | FAIL | REVIEW_NEEDED + context
- [ ] Violations categorized by severity: CRITICAL | HIGH | MEDIUM | LOW
- [ ] Overall status calculated: PASS (all critical pass) | FAIL (≥1 critical fail) | REVIEW (≥1 ambiguous)
- [ ] Validation completes in <1 second
- [ ] Violations linked to drawing regions (clickable highlights)

---

#### US1.4 – Generate Validation Report
**As a** engineer  
**I want to** export a structured report with findings  
**So that** I can share with team and act on feedback

**Acceptance Criteria:**
- [ ] JSON output includes: zones_detected, extractions, validation_results, anomalies, pass_rate, recommendations
- [ ] HTML report displays: thumbnail + violations highlighted (color-coded by severity)
- [ ] HTML report includes: extracted fields, rule summary, next steps
- [ ] CSV export available for bulk analysis (100+ drawings)
- [ ] Report downloadable; also viewable in browser
- [ ] Audit trail: report generation time, user, model version

---

### Epic 2: Expert Workflow & Ambiguous Cases

#### US2.1 – Route Ambiguous Cases to Expert Queue
**As a** verification engineer  
**I want to** see a list of drawings flagged for expert review  
**So that** I can batch-check ambiguous findings

**Acceptance Criteria:**
- [ ] Dashboard shows: drawings with REVIEW_NEEDED status
- [ ] Sortable by: severity, date uploaded, zone type
- [ ] Filter by rule category (cartouche, tolerances, GD&T, weld, etc.)
- [ ] Queue refreshes in real-time
- [ ] Each item shows: drawing name, violated rule, system confidence, context

---

#### US2.2 – Provide Context for Expert Decision
**As an** expert reviewer  
**I want to** see system reasoning + OCR confidence + historical similar cases  
**So that** I can quickly make informed decisions

**Acceptance Criteria:**
- [ ] Violation detail page shows: flagged zone highlighted on image, OCR text + confidence, rule explanation
- [ ] Related calculation notes fetched from DSM (if linked)
- [ ] Historical similar cases displayed (e.g., "Last 5 times this rule triggered: 3 passed, 2 needed correction")
- [ ] Expert can approve/override/request more info
- [ ] Decision + rationale recorded

---

#### US2.3 – Feedback Loop Improves Model
**As the** system  
**I want to** collect expert corrections and analyze patterns  
**So that** future models improve automatically

**Acceptance Criteria:**
- [ ] Each expert decision logged: rule_id, system_decision, expert_decision, rationale
- [ ] Feedback aggregated weekly: "Rule X: system accuracy 92% (vs. expert)"
- [ ] Low-performing rules flagged for refinement
- [ ] Metrics dashboard shows: false positive rate, false negative rate by category
- [ ] Retraining trigger: if performance drops >5%, auto-flag for model update

---

### Epic 3: ISO Standards Reference System (RAG)

#### US3.1 – Query ISO Standards Knowledge Base
**As an** engineer  
**I want to** ask "Is M6 socket-head cap screw per ISO 4762?" and get an answer  
**So that** I don't need to manually look up standards

**Acceptance Criteria:**
- [ ] Search/chat interface available in UI
- [ ] Query answered within 2 seconds
- [ ] Answer includes: direct answer, relevant excerpt, ISO standard reference, source credibility
- [ ] Fallback for unknown queries: "Sorry, not in knowledge base; ask expert"
- [ ] Top 10 FAQ pre-populated with common questions

---

#### US3.2 – Integrate RAG into Validation Engine
**As the** system  
**I want to** query the knowledge base when a rule is ambiguous  
**So that** I can provide better context to users

**Acceptance Criteria:**
- [ ] Rule engine triggers RAG query if confidence <70%
- [ ] Query: "Is tolerance +0.10/-0.05 compatible with ISO 2768-mH?" → answer retrieved
- [ ] Answer logged; if contradictory, route to REVIEW queue
- [ ] User sees system reasoning: "System uncertain because [reason]; ISO guidance: [answer]"

---

### Epic 4: User Interface & User Management

#### US4.1 – Upload & View Reports
**As an** engineer  
**I want a** simple web UI to upload drawings and view reports  
**So that** I don't need special software

**Acceptance Criteria:**
- [ ] Upload page: drag-and-drop or file selector
- [ ] Processing indicator: progress bar + status updates
- [ ] Report page: tabbed interface (Summary | Zones | Violations | Recommendations)
- [ ] Violations clickable → zooms to region on image
- [ ] Download button (JSON, HTML, CSV)
- [ ] Mobile-responsive design
- [ ] Load report in <500ms

---

#### US4.2 – Role-Based Access Control
**As an** admin  
**I want to** control who can view/upload/approve validations  
**So that** data stays secure

**Acceptance Criteria:**
- [ ] Three roles defined: Viewer (read-only), Reviewer (approve/reject), Admin (configure)
- [ ] Authentication via corporate SSO (OAuth2 / OIDC)
- [ ] Per-drawing permissions: owner + assigned reviewers
- [ ] Audit log: all user actions timestamped + traceable
- [ ] Role assignment UI available to admin

---

#### US4.3 – Historical View & Comparison
**As an** engineer  
**I want to** see validation history for a drawing across versions  
**So that** I can track how issues were resolved

**Acceptance Criteria:**
- [ ] Drawing page shows: all validation runs for this file
- [ ] Comparison view: side-by-side violations (v1 vs. v2)
- [ ] Change log: what improved, what regressed
- [ ] Filter by: date range, rule category, status (pass/fail/review)

---

### Epic 5: System Integration

#### US5.1 – API for External Systems
**As a** CAM/MES integrator  
**I want to** send drawings to the validator via REST API  
**So that** fabrication workflow is fully automated

**Acceptance Criteria:**
- [ ] API endpoint: POST /api/validate (async job)
- [ ] Returns: job_id for polling
- [ ] Endpoint: GET /api/status/{job_id} → returns status + ETA
- [ ] Endpoint: GET /api/report/{job_id} → returns JSON report
- [ ] Webhook support: system calls callback URL when validation complete
- [ ] API authentication: API key + rate limiting
- [ ] OpenAPI/Swagger spec published

---

#### US5.2 – Export to Compliance System
**As a** quality manager  
**I want to** log validated drawings in our compliance database  
**So that** audits are automated

**Acceptance Criteria:**
- [ ] Report includes: unique drawing ID, validation date, model version, rules run, pass/fail status
- [ ] CSV bulk export: 100+ validated drawings for import
- [ ] Timestamps in ISO 8601 format
- [ ] Audit trail: traceable to user, approval chain

---

## END-TO-END WORKFLOWS

### Workflow A: Happy Path (Drawing Passes)
```
1. Alice (junior engineer) completes design in CATIA
2. Exports drawing as PDF
3. Opens validator UI; drags PDF into browser
4. System processes:
   - Detects zones (0.8s)
   - Extracts text (1.2s)
   - Validates rules (0.5s)
5. Report generated: "PASS" (all rules satisfied)
   - Cartouche: ✓ Complete
   - Dimensions: ✓ Consistent with 3D
   - Tolerances: ✓ No contradictions
   - GD&T: ✓ Valid symbols + datums
   - Weld specs: ✓ Aligned with CNE
   - Surface finish: ✓ Environment specified
6. Alice downloads JSON + HTML
7. Sends to Claude (verification lead) for sign-off
8. Claude reviews <5 min; approves
9. Drawing ready for fabrication ✓
**Time saved:** 4-6 hours → ~30 minutes ✓
```

---

### Workflow B: Violations Detected (Rule Failures)
```
1. Alice uploads drawing (similar scenario)
2. System processes; report: "FAIL"
   - CRITICAL: Cartouche missing mass field
   - HIGH: Dimension tolerance ±0.05 contradicts ISO 2768-mH (general tolerance)
   - MEDIUM: GD&T datum B referenced but not defined
3. Violations highlighted on report; regions zoomed on image
4. Alice clicks each violation → sees explanation + suggested fix
   - Violation #1: "Mass required for final plan signature; add to cartouche"
   - Violation #2: "If ISO 2768 applies, general tolerance >specific tolerance; either remove specific or explain"
   - Violation #3: "Datum B must be defined with ⌖ symbol on drawing"
5. Alice corrects drawing in CATIA; re-exports
6. Re-uploads to validator
7. System processes; report: "PASS"
8. Sends to Claude; approved ✓
**Time saved:** 4-6 hours manual review → ~1.5 hours (including 1 re-iteration) ✓
```

---

### Workflow C: Ambiguous Case (Expert Review Required)
```
1. Engineer uploads drawing
2. System processes; report: "REVIEW_NEEDED"
   - Issue: "Is stabilization required?" (no automatic answer)
   - Context: Design involves high loads + tight tolerances on critical surface
3. System routes to expert queue (Claude's dashboard)
4. Claude sees flagged item; clicks to review:
   - System shows: design loads (fetched from calculation notes), tolerance envelope, 3D geometry snapshot
   - Claude's expert judgment: "Yes, stabilization required; call machinist for fine-tuning spec"
5. Claude approves violation override; records rationale: "Stabilization justified per load analysis"
6. System learns: Next similar case will be flagged with same rule + confidence boost
7. Drawing marked PASS (with expert override noted in audit trail)
**Value:** Expert focus on design decisions, not paperwork ✓
```

---

## FEATURE BREAKDOWN (MVP)

| Feature | Priority | Status | Effort | Risk |
|---------|----------|--------|--------|------|
| **F1: Zone Detection (YOLO)** | P0 | Blueprint | HIGH | 🟡 Dataset size |
| **F2: Text Extraction (Donut OCR)** | P0 | Blueprint | HIGH | 🟡 Small text |
| **F3: Rule Engine** | P0 | Blueprint | MEDIUM | 🟢 Low |
| **F4: Report Generation** | P0 | Blueprint | LOW | 🟢 Low |
| **F5: Expert Queue** | P0 | Blueprint | MEDIUM | 🟡 UX complexity |
| **F6: ISO RAG System** | P1 | Blueprint | MEDIUM | 🟡 Knowledge base quality |
| **F7: Web UI** | P0 | Blueprint | MEDIUM | 🟡 User adoption |
| **F8: REST API** | P1 | Blueprint | LOW | 🟢 Low |
| **F9: Auth + RBAC** | P0 | Blueprint | LOW | 🟢 Low |
| **F10: Audit Trail** | P1 | Blueprint | LOW | 🟢 Low |

---

## MVP DEFINITION

### Minimal Viable Product Scope
- ✅ Zone detection (6 zone types minimum: cartouche, dimensions, GD&T, weld, surface finish, notes)
- ✅ OCR extraction (cartouche fields + dimensions + specs)
- ✅ 15+ core validation rules (cartouche, dimension consistency, tolerance coherence, GD&T, weld, surface finish)
- ✅ HTML + JSON report generation
- ✅ Expert queue (dashboard + decision recording)
- ✅ Basic web UI (upload + view report)
- ✅ REST API (POST /validate, GET /report)
- ✅ Database storage + audit trail
- ✅ Single-user authentication (corporate SSO)

### MVP Success Metrics
- Precision >88% (detection)
- Recall >93% (detection)
- OCR CER <6%
- Validation time <2.5 seconds
- E2E system availability >95% (pilot phase)
- User satisfaction >3.5/5 (Likert scale)

---

## FUTURE ENHANCEMENTS (Post-MVP)

### Phase 2 (Q3-Q4 2026)
- **Calculation-to-3D Integration:** Fetch STEP file; overlay with calculation mesh; flag geometry mismatches
- **Advanced GD&T Analysis:** Simulate tolerance stack-up; suggest redundant constraints
- **Batch Processing:** Validate 1000s of drawings via automated pipeline
- **Predictive Failure Analysis:** "Based on historical data, this design has X% chance of rework"
- **Mobile Native App:** iOS/Android for on-site validation

### Phase 3 (2027+)
- **Automotive Domain:** Extend rules for automotive engineering standards (AIAG, etc.)
- **Systems Engineering:** Electrical schematics, software architecture validation
- **Integration Marketplace:** Pre-built connectors to CAM, MES, ERP systems
- **AI Design Assistant:** "Suggested improvements to drawing" based on historical patterns
- **Multi-language Support:** Arabic, Chinese, Japanese, Spanish

---

## TECHNICAL CONSTRAINTS (From Architecture Perspective)

- **Model Architecture:** YOLOv11-obb (detection) + Donut (OCR) recommended (89% precision, 99% recall vs. competitors)
- **Infrastructure:** Needs GPU for inference; cloud-hosted (AWS/Azure) or on-prem with GPU
- **Dataset:** Requires ~100-200 annotated drawings for acceptable performance; grows over time
- **Performance Targets:** <2.5s inference time; <1s report generation
- **Scalability:** Horizontal scaling (stateless API); 100+ concurrent users required

---

## INTEGRATION REQUIREMENTS

### Pre-Launch
- [ ] CATIA integration testing (PDF export quality)
- [ ] Corporate SSO (OAuth2) connectivity verified
- [ ] Database schema finalized (PostgreSQL or similar)

### Post-Launch (Phase 2)
- [ ] DSM integration (fetch calculation notes context)
- [ ] CAM/MES API endpoint integration (drawing → fabrication)
- [ ] Compliance database connector (audit trail export)

---

## SECURITY REQUIREMENTS

### Authentication & Authorization
- OAuth2 / OIDC via corporate SSO
- Role-based access: Viewer, Reviewer, Admin
- API key + rate limiting for external integrations
- Session timeout: 1 hour

### Data Protection
- Encryption in transit: TLS 1.2+
- Encryption at rest: AES-256 (database + file storage)
- GDPR compliance: User data retention policy (2 years → delete)
- Audit logging: All user actions timestamped + immutable

### Infrastructure Security
- Network isolation: Firewall rules; no public API
- Container security: Image scanning; non-root execution
- Secrets management: Environment variables; no hardcoded keys
- Vulnerability scanning: Weekly automated scans

---

## REPORTING & ANALYTICS

### Built-in Dashboards
1. **Validation Summary:**
   - Total drawings validated (daily/weekly/monthly)
   - Pass rate by rule category
   - Top violations (sorted by frequency)
   - Time saved vs. manual review

2. **Model Performance:**
   - Detection precision/recall
   - OCR accuracy (CER/WER)
   - Model version history
   - Retraining schedule

3. **User Activity:**
   - Active users per day
   - Drawings validated per user
   - Expert decisions per rule
   - Feedback submission rate

4. **Quality Metrics:**
   - False positive rate (violations that weren't real)
   - False negative rate (missed violations)
   - Expert override frequency
   - Time to expert decision

---

## UX CONSIDERATIONS

### Design Principles
- **Clarity:** Violations clearly explained; next steps obvious
- **Speed:** < 2.5 seconds from upload to report
- **Accessibility:** Color-blind safe (violations not color-only); keyboard navigation
- **Responsiveness:** Mobile-friendly (iPad for on-site validation)
- **Feedback:** Real-time progress updates; visual confirmation of actions

### Key UI Components
- **Upload Zone:** Drag-and-drop with file type validation
- **Processing Indicator:** Progress bar + status messages
- **Report Tab:** Violations highlighted on image; clickable zones
- **Expert Queue:** Batch review interface; sort/filter
- **History View:** Version comparison; change tracking

---

## EDGE CASES & FAILURE SCENARIOS

### Edge Cases
1. **Multi-sheet drawing:** System should split pages; validate each separately; aggregate report
2. **Drawing in non-standard orientation:** Auto-rotate detected via cartouche position
3. **Overlapping zones:** Prioritize by importance (cartouche > dimensions > notes)
4. **Missing expected zone:** Flag WARNING; allow override (e.g., "No weld symbols on this drawing")
5. **Handwritten annotations:** Skip or flag for manual review
6. **Very small text (<8pt):** OCR will fail; flag region for manual check

### Failure Scenarios
1. **Model inference fails:** Fallback to manual mode; user notified; graceful degradation
2. **Database unavailable:** Cache report locally; sync when connection restored
3. **Expert not available (24h SLA):** Auto-escalate; notify admin
4. **Hallucinated zones:** OCR confidence low; flag for review; don't create false zones
5. **Rate limit exceeded:** Queue subsequent requests; notify user of delay

---

## DEPENDENCIES

### External Dependencies
- [ ] Corporate SSO system (OAuth2 compatible)
- [ ] GPU infrastructure (training + inference)
- [ ] Cloud deployment platform (AWS, Azure, GCP)
- [ ] Database service (managed PostgreSQL or similar)
- [ ] Email service (notifications)

### Internal Dependencies
- [ ] CATIA export quality (PDF/PNG >300 DPI)
- [ ] Historical checklists (codify as rules)
- [ ] Expert availability (SLA for ambiguous cases)
- [ ] Dataset annotations (initial 50+ drawings)

---

## RELEASE STRATEGY

### Phase 1: Internal Pilot (Weeks 1-8)
- Limited to 5-10 users (your organization)
- Weekly feedback loops
- Model retraining every 2 weeks
- No public announcement

### Phase 2: Beta (Weeks 9-14)
- Expand to 2-3 partner organizations
- Collect feedback; refine rules
- Harden infrastructure (99%+ uptime target)
- Security audit

### Phase 3: General Availability (Week 16+)
- Public launch (SaaS model or enterprise license)
- Full support structure
- Continuous monitoring + model updates
- Community feedback channel

---

## SUCCESS METRICS (KPIs)

| KPI | Target | Measurement | Owner |
|-----|--------|-------------|-------|
| **Time Reduction** | 40-60% | (Manual hours - AI hours) / Manual hours | Expert |
| **Error Detection** | >90% | (True violations caught) / (Total violations) | QA |
| **False Positive Rate** | <10% | (False violations) / (Total violations flagged) | Expert |
| **System Uptime** | 99.5% | Availability monitoring | DevOps |
| **User Adoption** | 60%+ | Active users / Total users (6 months) | PM |
| **Model Accuracy** | >88% precision | Detection evaluation on test set | ML Eng |
| **Response Time** | <2.5s | Inference + report generation | Backend |

---

## NEXT STEPS

1. ✅ **This PRD:** Approved by Product Manager
2. ⏳ **Architecture Review:** Solution Architect validates technical feasibility
3. ⏳ **Stakeholder Sign-Off:** Valentin + Expert final approval
4. ⏳ **Sprint Planning:** Breakdown into epics & sprints (Scrum Master)
5. ⏳ **Kick-Off:** Team alignment; design docs + prototypes

---

**END OF PRD**

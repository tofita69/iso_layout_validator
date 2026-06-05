# CRITICAL UPDATE: CLIENT CHECKLIST IMPACT ANALYSIS
## ISO Technical Drawing Validator - May 2026

**Document Purpose:** Summarize checklist analysis findings and required planning document updates

---

## KEY FINDINGS FROM CLIENT CHECKLISTS

### Three Distinct Drawing Types (NEW REQUIREMENT)
- **076-A: Plan Pièce** (Part Drawing) - 59 validation checkpoints
- **077-A: Plan Mécanosoudé** (Welded Assembly) - 55 validation checkpoints + welding specs
- **078-A: Plan Sous-ensemble** (Sub-assembly) - 56 validation checkpoints + BOM validation
- **TOTAL: 170 validation checkpoints** across all drawing types

### External Document Dependency (CRITICAL)
- **Document:** `ECM_Note Qualité en soudage_26337519-1-0_07-2025.pdf`
- **Used by:** 077-A (Mécanosoudé) checklist for weld validation
- **Requirement:** System must fetch & cross-validate weld specs against this NOTA document
- **Impact:** Creates external document linking requirement; adds complexity to weld validation

### Approval Workflow Requirement (NEW)
- Each checklist includes formal approval tracking:
  - Drawer name, date, signature
  - Reviewer (3rd party) name, date, signature, comments
  - Status field: DRAFT, SUBMITTED, APPROVED, REJECTED
  - Comments field for exceptions
- **Requirement:** Immutable audit trail for compliance audits

### Drawing-Type-Specific Validation Categories

| Category | Pièce (076-A) | Mécanosoudé (077-A) | Sub-ensemble (078-A) |
|----------|-------|----------|------------|
| GENERAL | ✅ (4 items) | ✅ (4 items) | ✅ (4 items) |
| CARTOUCHE | ✅ (8 items) | ✅ (8 items) | ✅ (8 items) |
| MATERIAL | ✅ (4 items) | ✅ (4 items) | ❌ |
| MATERIAL & DEBRIS | ❌ | ✅ (3 items) | ❌ |
| WELDS | ❌ | ✅ (4 items + NOTA link) | ❌ |
| NOMENCLATURE | ❌ | ❌ | ✅ (3 items + BOM) |
| ASSEMBLY | ❌ | ❌ | ✅ (2 items) |
| GEOMETRY | ✅ (7 items) | ✅ (7 items) | ✅ (6 items) |
| FINISH/PROTECTION | ✅ (5 items) | ✅ (5 items) | ❌ |
| PROJECT SPECIFIC | ✅ (7-15 slots) | ✅ (5-7 slots) | ✅ (7-10 slots) |
| **TOTAL** | **59** | **55** | **56** |

---

## PLANNING DOCUMENT UPDATES REQUIRED

### 01_requirements.md
**Changes:**
- Add drawing type classification as F1.5
- Expand F2 to include drawing-type-specific zones (weld, BOM, material debris)
- Add F3.5-F3.8 for weld, material, BOM, approval extraction
- Add F6 for external document links
- Add F7 for project-level custom rules
- Update success metrics (170+ checkpoints, >98% classification accuracy, weld NOTA validation)
- Add new personas: Project Manager / Compliance Officer
- Update timeline: 26-28 weeks (was 18-21 weeks)
- Update team size: 8-10 people (was 6-8)

### 02_PRD.md
**Changes:**
- Add "Drawing Type Classification" as new capability
- Expand scope: Weld NOTA cross-validation, BOM validation, approval workflow
- Add success criteria: "Support three distinct drawing types with >98% accuracy"
- Update timeline: 21 weeks → 26-28 weeks
- Add "External Document Integration" as system capability
- Add "Formal Approval Workflow" to product capabilities
- Revise scope boundaries: explicitly list 076-A, 077-A, 078-A support

### 03_architecture.md
**Changes:**
- Add "Drawing Classification Service" to Service Breakdown (after intake service)
- Update Service B (Zone Detection) to be drawing-type-aware
- Add "Service C.1: External Document Fetcher" (for NOTA linking)
- Add data models for:
  - `DrawingClassification` entity
  - `ApprovalWorkflow` entity
  - `ExternalDocumentLink` entity
  - `StandardsRegistry` entity
  - `ProjectCustomRule` entity
- Update database schema section with new tables
- Add "Standards Registry Module" to architecture
- Update data model for extraction to include approval fields

### 04_epics.md
**Major Changes:**
- ADD **NEW EPIC E9: Drawing Type Classification & Standards Registry**
  - US9.1: Build drawing classification module (3 types)
  - US9.2: Create standards registry (ISO versions, material codes, treatment codes)
  - US9.3: Build project custom rules engine
  - Story Points: 21 total
  
- **EXPAND Epic 2:** Zone Detection & OCR
  - Add US2.6: Detect drawing-type-specific zones (weld, BOM, debris)
  - Add US2.7: Train model with drawing-type labels
  - Additional Story Points: +5 (37 → 42 points)

- **EXPAND Epic 3:** Data Extraction & Structuring
  - Add US3.6: Extract material & treatment specifications
  - Add US3.7: Extract weld specs with NOTA cross-reference
  - Add US3.8: Extract BOM & reconciliation (078-A only)
  - Add US3.9: Extract approval workflow fields
  - Remove/merge old US3.6 (image linking; too simple)
  - Additional Story Points: +13 (34 → 47 points)

- **EXPAND Epic 4:** Validation Rules Engine
  - Add US4.1.1: Drawing type classification validation
  - Add US4.1.2: Standards registry integration
  - Add US4.2.1: Material nomenclature resolver
  - Add US4.3.1: BOM reconciliation validator
  - Add US4.3.2: External document cross-validator (NOTA)
  - Add US4.4.1: Project custom rules support
  - Add US4.5: Approval workflow & sign-off tracking
  - Additional Story Points: +26 (34 → 60 points)

- **EXPAND Epic 5:** Reporting & UI
  - Add US5.4: Approval form UI (drawer & reviewer sign-off capture)
  - Add US5.5: Display classification, standard refs, approval status in report
  - Additional Story Points: +5 (20 → 25 points)

- Update Epic Summary table: Duration 18-21 weeks → 26-28 weeks
- Update Total Story Points: 145 → 180-190
- Add dependencies: E9 → E2 (classification before extraction), E3 → E4 (approval workflow)
- Add NEW Go/No-Go Gates:
  - E9 Gate: >98% drawing type classification on 50-sample test set
  - E3 Gate: Material & BOM extraction >95% accuracy
  - E4 Gate: Weld NOTA validation >85% accurate

### 05_tasks.md
**Changes:**
- ADD **SPRINT 0.5 (Week 2-3): External Document Processing**
  - T0.12: Extract & parse NOTA PDF (ECM_Note Qualité en soudage)
  - T0.13: Create weld specification validation lookup table
  - Story Points: +5
  
- ADD **Sprint 1.5: Drawing Classification (Week 5-6)**
  - T1.12-T1.18: Drawing type classifier module (heuristics + model)
  - T1.19-T1.23: Standards registry creation (YAML files)
  - Story Points: +21

- **EXPAND Sprint 2 (Data Extraction): Add +8 points**
  - T3.15-T3.18: Material extractor
  - T3.19-T3.22: Weld spec extractor + NOTA linker
  - T3.23-T3.26: BOM extractor (078-A)
  - T3.27-T3.30: Approval field extractor

- **EXPAND Sprint 3 (Rules Engine): Add +26 points**
  - T4.21-T4.30: Drawing type classification rules
  - T4.31-T4.40: Material nomenclature validation
  - T4.41-T4.50: BOM reconciliation rules
  - T4.51-T4.60: External document cross-validation
  - T4.61-T4.70: Project custom rule support
  - T4.71-T4.76: Approval workflow state machine

- **EXPAND Sprint 4 (UI): Add +5 points**
  - T5.15-T5.19: Approval form & sign-off UI

- Update Sprint summary table: Total 280 points → 330-340 points
- Add Sprint 6-7 for integration/hardening

### 06_milestones.md
**Changes:**
- Update **Milestone 0:** Add "External Document Processing" deliverable
- Add **Milestone 0.5:** Standards Registry & Classification (Week 2-3)
  - Deliverable: Drawing type classifier working, standards YAML files completed, NOTA PDF processed
  - Go/No-Go: >95% classification accuracy on sample set
  
- Update **Milestone 1:** Expand to include classification model training
  - Add: "Drawing type classifier trained on 50-sample dataset"
  - Add: "Material & weld extractors passing unit tests"

- Update **Milestone 2:** Expand rules engine scope
  - Add: "Material nomenclature validation rules working"
  - Add: "BOM reconciliation engine tested"
  - Add: "External document (NOTA) validation >85% accurate"
  - Add: "Approval workflow state machine implemented"

- Update **Milestone 3:** Add UI for approval
  - Add: "Approval form UI tested"
  - Add: "Sign-off workflow integrated end-to-end"

- Update timeline: 21 weeks → 26-28 weeks
- Update Go/No-Go gates for each milestone to include new requirements

### 07_project_summary.md
**Changes:**
- Update "What we're building" section:
  - Add: "Drawing classification module (3 types: Pièce/Mécanosoudé/Sub-ensemble)"
  - Add: "External NOTA document integration for weld validation"
  - Add: "Formal approval workflow with immutable audit trail"
  - Add: "BOM reconciliation for sub-assemblies"

- Update "Why it matters" section:
  - Add: "Supports three distinct drawing type validations per client checklists"
  - Add: "Integrates with external quality standards (NOTA) for weld specs"
  - Add: "Enables compliance audit trail for ISO certification"

- Update capability table:
  - Add row: "Drawing Type Classification: 3 types with >98% accuracy"
  - Add row: "External Document Integration: NOTA weld validation"
  - Add row: "Approval Workflow: Immutable audit trail"
  - Add row: "BOM Validation: Part reconciliation for assemblies"
  - Update "Validation Rules" row: "170+ checkpoints across 3 types (76 rules each type)"

- Update Timeline: "21 weeks → 26-28 weeks"
- Update Team Size: "6-8 people → 8-10 people"
- Update Budget: "€300-400K → €380-500K" (10-20% increase for classification + standards)
- Update "System Overview" data flow diagram to include:
  - Classification step after detection
  - External document fetcher
  - Approval workflow capture

- Update "High-Level System Architecture" to add:
  - Classification Service box
  - External Document Registry
  - Standards Repository
  - Approval Workflow Service

- Add new risk to "Contingencies":
  - Risk: External NOTA document format changes
  - Probability: Low (15%)
  - Impact: HIGH (weld validation breaks)
  - Mitigation: Version external docs; create parser that tolerates format variations

---

## IMPLEMENTATION PRIORITIES

### Phase 1 (Weeks 1-3): Foundation
1. Process & extract NOTA PDF (T0.12-T0.13)
2. Build drawing classifier heuristics (T1.12-T1.14)
3. Create standards registry YAML files (T1.19-T1.23)
4. Update training data with drawing type labels (T2.1-T2.5)

### Phase 2 (Weeks 4-8): Models & Extraction
5. Train YOLO with drawing-type-aware zones (T2.8-T2.13)
6. Build extractors for material, weld, BOM (T3.15-T3.30)
7. Implement approval field capture (T3.27-T3.30)

### Phase 3 (Weeks 9-14): Validation Rules
8. Implement classification validation (T4.21-T4.30)
9. Build material + BOM + NOTA validators (T4.31-T4.60)
10. Implement approval workflow (T4.71-T4.76)

### Phase 4 (Weeks 15-21): UI & Integration
11. Build approval UI (T5.15-T5.19)
12. Integrate all components
13. UAT with client

---

## CRITICAL SUCCESS FACTORS

1. **NOTA PDF Processing:** Must extract weld specs correctly; any parsing errors block weld validation
2. **Drawing Type Classification:** >98% accuracy required; misclassification → wrong rules applied
3. **Standards Registry:** Must be comprehensive (all ISO versions, material codes, treatment codes)
4. **External Document Versioning:** NOTA doc may change; system must handle versions gracefully
5. **Approval Workflow Immutability:** Cannot allow retroactive changes; audit trail must be tamper-proof

---

## TIMELINE DELTA

| Item | Before | After | Delta |
|------|--------|-------|-------|
| Total Duration | 21 weeks | 26-28 weeks | +5-7 weeks |
| Story Points | 145 | 180-190 | +35-45 |
| Team Size | 6-8 | 8-10 | +2 |
| New Epics | 8 | 9 | +1 (E9) |
| New Modules | 4 | 10+ | +6 |
| Database Tables | 8 | 14 | +6 |
| External Dependencies | 0 | 2 | +2 (NOTA, standards docs) |

---

## NEXT STEPS

1. ✅ **Complete** - Checklist analysis & impact assessment (THIS DOCUMENT)
2. ⏳ **NOW** - Update all 7 planning documents with new requirements
3. **Then** - Client review & sign-off on updated scope/timeline
4. **Then** - Adjust budget & resource allocation
5. **Then** - Begin Sprint 0.5 with NOTA processing

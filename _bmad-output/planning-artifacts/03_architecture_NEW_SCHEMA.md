# NEW DATABASE SCHEMA & DATA MODELS
## ISO Technical Drawing Validator - Updated Architecture

---

## 5. EXPANDED DATA MODELS & DATABASE SCHEMA (NEW)

### Drawing Classification & Type Tracking

```sql
CREATE TABLE IF NOT EXISTS drawing_classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drawing_id UUID NOT NULL REFERENCES drawings(id),
    
    -- Drawing type: 'piece' (076-A), 'mecano' (077-A), 'assembly' (078-A)
    drawing_type VARCHAR(50) NOT NULL,
    classification_confidence FLOAT NOT NULL,
    
    -- Markers detected for classification
    markers_detected JSONB NOT NULL,  -- e.g., {"weld_symbols": true, "bom_table": false, "material_spec": true}
    classification_method VARCHAR(50),  -- 'heuristic', 'ensemble', 'manual'
    
    -- Whether expert reviewed/overrode
    expert_validated BOOLEAN DEFAULT FALSE,
    expert_notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_drawing_type (drawing_id, drawing_type),
    INDEX idx_confidence (classification_confidence)
);
```

### Approval Workflow Tracking

```sql
CREATE TABLE IF NOT EXISTS drawing_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drawing_id UUID NOT NULL REFERENCES drawings(id),
    
    -- Drawer (author) info
    drawer_name VARCHAR(200),
    drawer_date DATE,
    drawer_signature_path VARCHAR(500),  -- S3 path to signature image
    drawer_signature_timestamp TIMESTAMP,
    
    -- Reviewer (3rd party) info
    reviewer_name VARCHAR(200),
    reviewer_date DATE,
    reviewer_signature_path VARCHAR(500),
    reviewer_signature_timestamp TIMESTAMP,
    reviewer_comments TEXT,
    
    -- Workflow status
    approval_status VARCHAR(50),  -- 'DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED'
    rejection_reason TEXT,
    
    -- Audit trail (immutable)
    audit_log JSONB NOT NULL,  -- Full history of all state changes
    -- e.g., [{"timestamp": "2026-05-18T10:30:00", "status_from": "DRAFT", "status_to": "SUBMITTED", "changed_by": "user_id"}]
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_status (approval_status),
    INDEX idx_drawing (drawing_id)
);
```

### Standards & Compliance Registry

```sql
CREATE TABLE IF NOT EXISTS iso_standards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Standard identification
    standard_code VARCHAR(100) NOT NULL UNIQUE,  -- e.g., "ISO 5459", "NF EN ISO 13920"
    standard_name VARCHAR(300) NOT NULL,
    standard_version VARCHAR(20),  -- e.g., "2015", "2020"
    
    -- Metadata
    effective_date DATE,
    document_url VARCHAR(500),
    description TEXT,
    
    -- Classification
    category VARCHAR(50),  -- 'reference', 'tolerancing', 'gdt', 'weld', 'surface_finish', 'material'
    drawing_type VARCHAR(50),  -- 'piece', 'mecano', 'assembly', or 'all'
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_code (standard_code),
    INDEX idx_category (category),
    INDEX idx_drawing_type (drawing_type)
);
```

### Material & Treatment Nomenclature

```sql
CREATE TABLE IF NOT EXISTS material_nomenclature (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Material code (EN/ISO format)
    material_code VARCHAR(100) NOT NULL UNIQUE,  -- e.g., "16MnCr5", "1.7131"
    description VARCHAR(300),
    
    -- Classification
    material_type VARCHAR(50),  -- 'steel', 'aluminum', 'cast_iron', 'titanium', etc.
    standard_ref UUID REFERENCES iso_standards(id),  -- Reference to EN/ISO material standard
    
    -- Properties
    typical_uses TEXT,
    mechanical_properties JSONB,  -- e.g., {"tensile_strength": "1000-1200", "hardness": "30-40 HRC"}
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_material_code (material_code),
    INDEX idx_material_type (material_type)
);

CREATE TABLE IF NOT EXISTS surface_treatments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Treatment code
    treatment_code VARCHAR(100) NOT NULL UNIQUE,  -- e.g., "galvanizing", "anodizing_III", "paint_ISO12944_C5"
    treatment_name VARCHAR(200) NOT NULL,
    
    -- Standard reference
    standard_ref UUID REFERENCES iso_standards(id),
    
    -- Details
    environment_category VARCHAR(50),  -- 'C1', 'C2', 'C3', 'C4', 'C5', etc. (ISO 12944)
    duration_years INTEGER,  -- Expected durability
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_code (treatment_code),
    INDEX idx_environment (environment_category)
);
```

### External Document Links

```sql
CREATE TABLE IF NOT EXISTS external_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Document metadata
    document_name VARCHAR(300) NOT NULL,
    document_type VARCHAR(50),  -- 'weld_nota', 'quality_standard', 'material_guide', 'iso_standard'
    version VARCHAR(20),  -- Document version, e.g., "1.0", "26337519-1-0_07-2025"
    
    -- File storage
    file_path VARCHAR(500) NOT NULL,  -- S3 path
    file_size_bytes BIGINT,
    file_hash VARCHAR(64),  -- SHA-256 for integrity checking
    
    -- Metadata
    document_description TEXT,
    effective_date DATE,
    superseded_by UUID REFERENCES external_documents(id),  -- If new version exists
    
    -- Relationships
    applies_to_drawing_types VARCHAR(200),  -- JSON: ['mecano'] or ['all']
    drawing_type VARCHAR(50),  -- Shortcut: 'piece', 'mecano', 'assembly', 'all'
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_document_type (document_type),
    INDEX idx_drawing_type (drawing_type),
    INDEX idx_effective_date (effective_date)
);
```

### Project-Level Custom Rules

```sql
CREATE TABLE IF NOT EXISTS project_custom_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL,  -- Reference to project management system
    
    -- Rule definition
    rule_id VARCHAR(100) NOT NULL,  -- e.g., "proj_custom_001"
    rule_name VARCHAR(200) NOT NULL,
    rule_description TEXT,
    
    -- Implementation
    yaml_rule TEXT NOT NULL,  -- YAML condition (same format as standard rules)
    severity VARCHAR(20),  -- 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    category VARCHAR(50),  -- 'cartouche', 'geometry', 'material', 'assembly', 'project_specific'
    
    -- Management
    enabled BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(100),
    approved_by VARCHAR(100),
    approval_date DATE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_project (project_id),
    INDEX idx_rule_id (rule_id),
    INDEX idx_enabled (enabled),
    
    UNIQUE (project_id, rule_id)
);
```

### Validation Rules (Expanded from Original)

```sql
CREATE TABLE IF NOT EXISTS validation_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Rule identification
    rule_id VARCHAR(100) NOT NULL UNIQUE,  -- e.g., "cart_001", "weld_005"
    rule_name VARCHAR(200) NOT NULL,
    rule_description TEXT,
    
    -- Scope
    drawing_type VARCHAR(50),  -- 'piece', 'mecano', 'assembly', 'all'
    category VARCHAR(50),  -- 'cartouche', 'geometry', 'material', 'weld', 'bom', 'assembly', etc.
    
    -- Severity
    severity VARCHAR(20),  -- 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    rule_version VARCHAR(20),  -- For A/B testing: "1.0", "1.1", etc.
    
    -- Implementation
    yaml_rule TEXT NOT NULL,  -- Rule logic in YAML format
    
    -- Compliance
    related_standards JSONB,  -- Array of standard_ids this rule references
    auto_fix_possible BOOLEAN DEFAULT FALSE,
    
    -- Versioning
    effective_date DATE DEFAULT CURRENT_DATE,
    superseded_by UUID REFERENCES validation_rules(id),
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_rule_id (rule_id),
    INDEX idx_drawing_type (drawing_type),
    INDEX idx_category (category),
    INDEX idx_severity (severity),
    INDEX idx_version (rule_version)
);
```

### Detailed Validation Results (Audit Trail)

```sql
CREATE TABLE IF NOT EXISTS validation_results_detailed (
    id BIGSERIAL PRIMARY KEY,
    drawing_id UUID NOT NULL REFERENCES drawings(id),
    
    -- Rule that was evaluated
    rule_id VARCHAR(100) NOT NULL,
    
    -- Evaluation result
    evaluation_status VARCHAR(20),  -- 'PASS', 'FAIL', 'REVIEW', 'ERROR'
    severity VARCHAR(20),
    violation_message TEXT,
    
    -- Context
    affected_field VARCHAR(200),  -- Which extracted field caused the violation
    affected_zone_id VARCHAR(100),  -- Which zone on the drawing
    
    -- Recommendation
    recommendation TEXT,
    suggested_fix TEXT,
    
    -- Expert review (if applicable)
    expert_reviewed BOOLEAN DEFAULT FALSE,
    expert_override BOOLEAN DEFAULT FALSE,
    expert_override_rationale TEXT,
    expert_user_id VARCHAR(100),
    
    -- Metadata
    rule_version VARCHAR(20),
    model_version VARCHAR(50),  -- Which model version flagged this
    confidence_score FLOAT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_drawing (drawing_id),
    INDEX idx_rule (rule_id),
    INDEX idx_status (evaluation_status),
    INDEX idx_severity (severity),
    INDEX idx_created (created_at)
);
```

### BOM (Bill of Materials) Reconciliation

```sql
CREATE TABLE IF NOT EXISTS bom_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drawing_id UUID NOT NULL REFERENCES drawings(id),
    
    -- BOM line item
    part_number VARCHAR(100) NOT NULL,
    part_designation VARCHAR(300),
    quantity INTEGER,
    
    -- References
    reference_to_manufacture VARCHAR(100),  -- Internal part number
    reference_commerce VARCHAR(100),  -- Supplier part number
    supplier_name VARCHAR(200),
    
    -- Bullage mark (marking on drawing)
    bullage_mark VARCHAR(50),  -- e.g., "A", "1.1", "2.3.1"
    bullage_detected BOOLEAN,  -- Did system find it on drawing?
    
    -- Validation
    reconciliation_status VARCHAR(20),  -- 'MATCH', 'MISMATCH', 'MISSING_ON_DRAWING', 'EXTRA_ON_DRAWING'
    validation_message TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_drawing (drawing_id),
    INDEX idx_part_number (part_number),
    INDEX idx_status (reconciliation_status)
);
```

### Weld Specification Cross-Validation (NOTA Linking)

```sql
CREATE TABLE IF NOT EXISTS weld_specifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drawing_id UUID NOT NULL REFERENCES drawings(id),
    
    -- Weld specification extracted from drawing
    weld_symbol VARCHAR(100),  -- ISO 1101 weld symbol
    weld_type VARCHAR(100),  -- e.g., "fillet", "butt", "plug"
    
    -- Standards references
    iso_standard_ref UUID REFERENCES iso_standards(id),  -- Reference standard (ISO 5817, 13920, etc.)
    nota_document_ref UUID REFERENCES external_documents(id),  -- Link to NOTA document
    
    -- Specifications
    weld_length_mm FLOAT,
    throat_thickness_mm FLOAT,
    pit_depth_allowance_mm FLOAT,
    
    -- Quality requirements
    cnd_level VARCHAR(50),  -- CND control level (visual, radiography, ultrasonic, etc.)
    stabilization_required BOOLEAN,  -- If fatigue, rework, or machining recovery
    
    -- Validation against NOTA
    nota_validation_passed BOOLEAN,
    nota_validation_message TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_drawing (drawing_id),
    INDEX idx_nota_doc (nota_document_ref),
    INDEX idx_validation (nota_validation_passed)
);
```

### Material & Treatment Extraction Results

```sql
CREATE TABLE IF NOT EXISTS material_treatment_extractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    drawing_id UUID NOT NULL REFERENCES drawings(id),
    
    -- Extracted material
    material_code_extracted VARCHAR(100),
    material_code_validated UUID REFERENCES material_nomenclature(id),
    material_confidence FLOAT,
    
    -- Heat treatment (core)
    heat_treatment_core VARCHAR(200),
    heat_treatment_core_standard UUID REFERENCES iso_standards(id),
    heat_treatment_temperature_c INTEGER,
    heat_treatment_confidence FLOAT,
    
    -- Surface treatment (localized)
    surface_treatment_extracted VARCHAR(200),
    surface_treatment_validated UUID REFERENCES surface_treatments(id),
    surface_treatment_confidence FLOAT,
    
    -- Validation
    material_valid BOOLEAN,
    treatment_combination_valid BOOLEAN,  -- Is the combination of treatments compatible?
    validation_notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_drawing (drawing_id),
    INDEX idx_material_code (material_code_extracted),
    INDEX idx_valid (material_valid)
);
```

### Model & Rule Version Tracking

```sql
CREATE TABLE IF NOT EXISTS model_deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Model identification
    model_type VARCHAR(50),  -- 'yolo', 'donut', 'classifier'
    model_version VARCHAR(50),  -- e.g., "1.0", "v11n_20260515"
    
    -- File location
    model_path VARCHAR(500),  -- S3 path
    model_hash VARCHAR(64),  -- SHA-256
    
    -- Metadata
    training_date DATE,
    training_dataset_version VARCHAR(50),
    accuracy_metrics JSONB,  -- {"mAP50": 0.95, "mAP50_95": 0.85, "precision": 0.93}
    
    -- Deployment status
    status VARCHAR(50),  -- 'training', 'validated', 'deployed', 'archived'
    deployed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_model_type (model_type),
    INDEX idx_status (status),
    INDEX idx_deployed (deployed_at)
);

CREATE TABLE IF NOT EXISTS rule_deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Rule set identification
    rule_set_version VARCHAR(50),  -- e.g., "1.0", "1.1", "2.0_pilote"
    drawing_type VARCHAR(50),  -- 'piece', 'mecano', 'assembly'
    
    -- Composition
    rules_included JSONB,  -- Array of rule_ids: ["cart_001", "dim_001", ...]
    total_rules INTEGER,
    
    -- Status
    status VARCHAR(50),  -- 'testing', 'piloting', 'production', 'archived'
    deployment_date DATE,
    
    -- A/B Testing
    ab_test_percentage FLOAT,  -- 10% piloting, 100% for full deployment
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_version (rule_set_version),
    INDEX idx_drawing_type (drawing_type),
    INDEX idx_status (status)
);
```

---

## 6. DATA FLOW WITH NEW SCHEMA

### Drawing Upload & Classification Flow

```
1. Drawing Uploaded
   ↓
2. Create drawing_classifications entry
   - Detect type (Pièce/Mécanosoudé/Assembly)
   - Store markers detected
   - Confidence score
   ↓
3. Load appropriate rule set based on classification
   - Type A: Load 076-A rules (59 items)
   - Type B: Load 077-A rules (55 items) + weld_specifications table
   - Type C: Load 078-A rules (56 items) + bom_entries table
   ↓
4. Extract data → Store in extraction tables
   ↓
5. Run validation_rules from validation_rules table
   ↓
6. Store results in validation_results_detailed
   ↓
7. If drawing_type = 'mecano': Cross-validate weld_specifications against weld_documents
   ↓
8. If drawing_type = 'assembly': Reconcile bom_entries
   ↓
9. Capture approval workflow in drawing_approvals (immutable audit trail)
   ↓
10. Generate report
```

---

## 7. STANDARDS REGISTRY POPULATION

The `iso_standards` table must be populated with entries like:

```sql
-- Referencing Standards
INSERT INTO iso_standards VALUES (uuid_generate_v4(), 'ISO 5459', 'Geometrical tolerancing - Datums and datum systems', '2015', '2015-05-15', 'https://www.iso.org/standard/63082.html', 'Defines how to establish datums for geometric tolerancing', 'reference', 'all');
INSERT INTO iso_standards VALUES (uuid_generate_v4(), 'NF EN ISO 13920', 'Tolerances for welded construction - Execution tolerances for components in mild steel, aluminum, magnesium and their alloys', '1996', '1996-12-15', '', 'Welding tolerances for fabrication', 'tolerancing', 'mecano');
INSERT INTO iso_standards VALUES (uuid_generate_v4(), 'ISO 2768', 'General tolerances', '2015', '2015-03-18', 'https://www.iso.org/standard/50265.html', 'General tolerancing for parts', 'tolerancing', 'piece');

-- Material Standards
INSERT INTO material_nomenclature VALUES (uuid_generate_v4(), '16MnCr5', 'Case hardening steel', 'steel', standard_ref, 'Bearing component applications', '{"tensile_strength_mpa": 1000, "yield_strength_mpa": 700}');
INSERT INTO material_nomenclature VALUES (uuid_generate_v4(), 'EN-AC 42100', 'Aluminum alloy (AlSi7Mg0.6)', 'aluminum', standard_ref, 'Casting applications', '{"tensile_strength_mpa": 240, "yield_strength_mpa": 140}');

-- Surface Treatments
INSERT INTO surface_treatments VALUES (uuid_generate_v4(), 'galvanizing_ISO1461', 'Hot-dip galvanizing per ISO 1461', standard_ref, 'C4', 25);
INSERT INTO surface_treatments VALUES (uuid_generate_v4(), 'paint_ISO12944_C5', 'Paint system category C5 (industrial)', standard_ref, 'C5', 15);
```

---

## 8. MIGRATION PATH (From Original to New Schema)

For existing implementations, a data migration is required:

```sql
-- Step 1: Create new tables (non-breaking)
-- Step 2: Populate iso_standards from hardcoded registry
-- Step 3: Add drawing_type column to drawings table (if not already present)
-- Step 4: Backfill drawing_classifications for existing drawings
-- Step 5: Create indexes
-- Step 6: Validate data integrity
-- Step 7: Decommission old schema (if applicable)
```

---

## 9. CRITICAL DATA INTEGRITY RULES

1. **Approval Audit Trail:** INSERT-only to drawing_approvals (no UPDATEs to state transitions; only audit_log changes)
2. **Standards Versioning:** Each iso_standards row is immutable; new versions create new rows with superseded_by links
3. **External Documents:** File hash (file_hash) must match before validation; version tracking prevents obsolete document use
4. **Drawing Classification:** Once classified, must be expert-validated before re-classification is allowed
5. **Rule Deployment:** Rules cannot be deleted; only marked as superseded; maintains full audit trail

---

## 10. EXAMPLE QUERIES

### Find all validation failures for a specific drawing type

```sql
SELECT vrd.rule_id, vrd.violation_message, COUNT(*) as frequency
FROM validation_results_detailed vrd
JOIN drawing_classifications dc ON vrd.drawing_id = dc.drawing_id
WHERE dc.drawing_type = 'mecano'
  AND vrd.evaluation_status = 'FAIL'
  AND vrd.created_at > NOW() - INTERVAL '7 days'
GROUP BY vrd.rule_id, vrd.violation_message
ORDER BY frequency DESC;
```

### Check weld specification compliance for a drawing

```sql
SELECT ws.weld_type, ws.cnd_level, ws.nota_validation_passed, ws.nota_validation_message
FROM weld_specifications ws
WHERE ws.drawing_id = $1
  AND ws.nota_validation_passed = FALSE;
```

### Audit trail for specific drawing's approval

```sql
SELECT da.drawer_name, da.drawer_date, da.reviewer_name, da.reviewer_date, 
       jsonb_array_elements(da.audit_log) -> 'timestamp' as event_time,
       jsonb_array_elements(da.audit_log) -> 'status_to' as status_change
FROM drawing_approvals da
WHERE da.drawing_id = $1
ORDER BY event_time;
```

---

**This schema expansion supports all new requirements from client checklists while maintaining data integrity and audit trail requirements.**

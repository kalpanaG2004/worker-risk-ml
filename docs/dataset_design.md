# Dataset Design and Synthetic Data Generation

## Overview
This document describes the dataset schema, synthetic generation strategy, and feature engineering logic for the Adaptive Skill and Safety Recommendation System.

## 1. Dataset Schema

### 1.1 Worker Dataset (`workers.csv`)
Captures worker profiles, skills, certifications, and safety history.

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| worker_id | String | W00001-W00500 | Unique worker identifier |
| experience_years | Integer | 0-30 | Total years of work experience |
| certification_level | Integer | 0, 1, 2 | 0=None, 1=Basic, 2=Advanced |
| training_completed | Binary | 0, 1 | Whether worker completed safety training |
| past_incident_count | Integer | 0-5+ | Number of past safety incidents |
| avg_incident_severity | Float | 1-5 | Average severity rating of incidents (1=Minor, 5=Critical) |
| skill_score | Float | 0-100 | Composite skill assessment score |

**Generated Statistics:**
- 500 worker records
- Realistic correlations:
  - Experience → Higher skill score
  - Certifications → Higher skill score
  - Past incidents → Lower skill score

### 1.2 Task Dataset (`tasks.csv`)
Captures task characteristics and risk attribution.

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| task_id | String | T0001-T0200 | Unique task identifier |
| task_type | Categorical | Mechanical, Electrical, Chemical, Assembly | Category of work task |
| required_skill_level | Integer | 1, 2, 3 | Skill level required (1=Basic, 3=Expert) |
| environment_risk | Integer | 1, 2, 3 | Environmental hazard level |
| supervision_required | Binary | 0, 1 | Whether task requires supervision |
| risk_label | Categorical | Low, Medium, High | Target variable for classification |

**Generated Statistics:**
- 200 task records
- Risk distribution: Balanced across Low/Medium/High
- Chemical tasks have higher inherent risk

### 1.3 Assignments Dataset (`assignments.csv`)
Captures worker-task pairings and derived risk assessments.

| Field | Type | Description |
|-------|------|-------------|
| assignment_id | String | Unique assignment identifier (A000001-A001500) |
| worker_id | String | Reference to worker |
| task_id | String | Reference to task |
| skill_mismatch | Float | Absolute difference between required and actual skill (0-100) |
| actual_risk | Categorical | Assigned risk level (Low, Medium, High) |

**Generated Statistics:**
- 1500 assignment records (realistic repetition of workers/tasks)
- Actual risk computed from:
  - Task's inherent risk (environment_risk)
  - Skill mismatch penalty
  - Worker's incident history penalty

---

## 2. Synthetic Data Generation Strategy

### 2.1 Rationale
Since real plant data is unavailable, synthetic generation approach:
1. **Realistic constraints**: Features follow industrial safety patterns
2. **Controlled relationships**: Correlations reflect domain knowledge
3. **Reproducibility**: Fixed random seed for consistency
4. **Scalability**: Easy to generate different dataset sizes for testing

### 2.2 Generation Assumptions

#### Worker Distribution
- **Experience**: Uniform distribution (0-30 years)
  - Reflects diverse workforce (fresh hires to long-term employees)
- **Certification**: Stratified
  - 30% no certification (entry-level)
  - 45% basic certification
  - 25% advanced certification
- **Incidents**: Poisson distribution with λ=0.8
  - Models rare but realistic incident occurrence
- **Skill Score**: Composite calculation
  - Base: Experience influence (0-40 points)
  - Add: Certification influence (0-30 points)
  - Add: Training influence (0-10 points)
  - Subtract: Incident penalty (3 points per incident)
  - Add: Random noise ~N(0, 5)

#### Task Distribution
- **Task Type**: Balanced across 4 categories
  - Mechanical, Electrical, Chemical, Assembly
  - Chemical tasks receive inherent risk boost
- **Required Skill**: Uniform (1-3)
- **Environment Risk**: Uniform (1-3)
- **Supervision Required**: ~50% tasks require supervision
- **Risk Label**: Derived from risk score
  - Low Risk: score < 1.8
  - Medium Risk: 1.8 ≤ score < 2.8
  - High Risk: score ≥ 2.8

#### Assignment Risk Computation
For each worker-task pair:
```
risk_score = environment_risk × 0.4 + 
             skill_mismatch_penalty × 0.3 +
             past_incidents × 0.3
             
where:
  skill_mismatch_penalty = |required_skill_level - worker_skill_level| / 100
  past_incidents = past_incident_count × 0.3
```

Actual risk label assigned based on risk_score thresholds.

---

## 3. Feature Engineering Logic

### 3.1 Feature Preprocessing
All features are standardized using StandardScaler from sklearn:
```
X_scaled = (X - X.mean()) / X.std()
```

### 3.2 Features Used for Risk Classification
1. **required_skill_level** (from tasks)
2. **environment_risk** (from tasks)
3. **supervision_required** (from tasks)
4. **experience_years** (from workers)
5. **certification_level** (from workers)
6. **training_completed** (from workers)
7. **past_incident_count** (from workers)
8. **skill_mismatch** (derived from assignments)

**Total: 8 features**

---

## 4. Train/Test Split Strategy

- **Test Size**: 20%
- **Train Size**: 80%
- **Stratification**: Stratified by risk label to maintain class distribution
- **Random State**: 42 (for reproducibility)

**Data Split Statistics:**
- Training samples: 1200
- Testing samples: 300
- Class distribution maintained in both sets

---

## 5. Evaluation Metrics Definition

### 5.1 Risk Classification Metrics
- **Accuracy**: Overall correctness
- **Precision**: False positive rate control
- **Recall**: False negative rate control (especially for High Risk)
- **F1-Score**: Harmonic mean of precision and recall
- **Confusion Matrix**: Detailed error breakdown
- **ROC-AUC** (optional): Probability ranking quality

### 5.2 Priority: High-Risk Recall
**Why it matters**: Missing a high-risk task assignment is worse than a false alarm.
- Target: Minimize false negatives for High-Risk tasks
- Metric: Recall specifically for "High Risk" class
- Acceptable threshold: ≥ 0.85 (85% of high-risk tasks detected)

### 5.3 Baseline Model Comparison
Models are ranked by:
1. **Primary**: High-Risk Recall (safety first)
2. **Secondary**: F1-Score (balance)
3. **Tertiary**: Accuracy (efficiency)

---

## 6. Data Quality and Validation

### 6.1 Sanity Checks
- No missing values in generated datasets
- All categorical fields use expected values
- Numeric ranges respect domain constraints
- Risk label distribution reasonable (Low: ~35%, Medium: ~35%, High: ~30%)

### 6.2 Correlation Validation
- Experience vs. Skill Score: Positive correlation ✓
- Incidents vs. Skill Score: Negative correlation ✓
- Environment Risk vs. Task Risk: Positive correlation ✓

---

## 7. File Locations

```
tata-project/
├── data/
│   ├── workers.csv                    (500 records)
│   ├── tasks.csv                      (200 records)
│   ├── assignments.csv                (1500 records)
│   ├── X_train.csv, X_test.csv        (features)
│   ├── y_train.csv, y_test.csv        (labels)
│   └── best_model.pkl                 (serialized model)
├── visualizations/
│   ├── risk_distribution.png
│   ├── skill_distribution.png
│   ├── environment_risk_distribution.png
│   ├── certification_distribution.png
│   ├── actual_risk_distribution.png
│   ├── experience_vs_skill.png
│   ├── model_comparison.png
│   ├── confusion_matrix_best_model.png
│   └── high_risk_recall_comparison.png
└── docs/
    └── dataset_design.md              (this file)
```

---

## 8. Reproducibility

All data generation and model training use fixed random seeds:
- Workers: `random_state=42`
- Tasks: `random_state=42`
- Assignments: `random_state=42`
- Model Training: `random_state=42`

This ensures bit-level reproducibility across runs.

---

## 9. Future Extensions

- Incident type dataset (optional): Categorize incidents by type
- Temporal data: Include timespan for incident trends
- Real data integration: Replace synthetic data with actual plant data
- Multi-site data: Extend to include location/plant differences

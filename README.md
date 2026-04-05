# Adaptive Skill and Safety Recommendation System

An AI/ML-driven decision support system that evaluates worker skill profiles and task characteristics to recommend required training, safety precautions, supervision requirements, and task suitability in industrial environments.

## Project Overview

**Goal**: Reduce operational risk and improve workforce safety preparedness through data-driven insights.

**Approach**: ML-heavy (80% ML, 20% AI-based recommendation logic)

## System Architecture

```
User Input
   ↓
Feature Processing
   ↓
ML Models
   ├── Risk Classification Model
   └── Worker Clustering Model
   ↓
Decision Engine
   ↓
Recommendation Generator
   ↓
Safety & Skill Recommendations
```

## Key Components

### 1. Risk Classification
Predicts task risk level (Low/Medium/High) using supervised learning.

**Candidate Models**:
- Logistic Regression
- Random Forest
- Gradient Boosting

**Priority Metric**: High recall for High-Risk tasks (safety first)

### 2. Worker Clustering
Groups workers by experience, skills, and incident history using unsupervised learning.

**Candidate Models**:
- K-Means
- Hierarchical Clustering

### 3. Recommendation Engine
Rule-based decision logic converting ML outputs to actionable recommendations.

**Outputs**:
- Required training suggestions
- Safety precautions
- Supervision requirements
- Risk explanations
- Confidence levels

## Technology Stack

- **Language**: Python 3.8+
- **Data Processing**: Pandas, NumPy
- **ML Framework**: Scikit-learn
- **Visualization**: Matplotlib, Seaborn
- **Optional**: SHAP (explainability), Streamlit (UI)

## Project Structure

```
tata-project/
├── main.py                          # Entry point
├── src/                             # Python modules
│   ├── __init__.py
│   ├── generate_workers.py          # Worker dataset generation
│   ├── generate_tasks.py            # Task dataset generation
│   ├── generate_assignments.py      # Assignment & risk labeling
│   ├── eda_analysis.py              # Exploratory data analysis
│   ├── baseline_model.py            # Baseline classification model
│   └── clustering.py                # (Week 3) Clustering models
├── data/                            # Generated datasets
│   ├── workers.csv                  # 500 worker records
│   ├── tasks.csv                    # 200 task records
│   ├── assignments.csv              # 1500 assignment records
│   ├── X_train.csv, X_test.csv      # Feature sets
│   ├── y_train.csv, y_test.csv      # Labels
│   └── best_model.pkl               # Trained model
├── visualizations/                  # Generated plots
│   ├── risk_distribution.png
│   ├── skill_distribution.png
│   ├── model_comparison.png
│   └── ...
└── docs/                            # Documentation
    ├── dataset_design.md            # Schema & generation logic
    └── evaluation_metrics.md         # Metrics definitions
```

## Quick Start

### 1. Setup Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
```

### 2. Install Dependencies
```bash
pip install pandas numpy scikit-learn matplotlib seaborn
```

### 3. Run Week 1 Pipeline
```bash
python main.py
```

This will:
- Generate synthetic worker, task, and assignment datasets
- Perform exploratory data analysis
- Create visualizations
- Train baseline classification models
- Evaluate and select the best model

### 4. View Results
Check the following directories:
- `data/` - Generated datasets and train/test splits
- `visualizations/` - Charts and model performance plots
- `docs/` - Dataset schema and methodology documentation

## Dataset Specifications

### Workers (500 records)
- Experience: 0-30 years
- Certifications: None/Basic/Advanced
- Skill Score: 0-100
- Incident History: Tracked with severity

### Tasks (200 records)
- Types: Mechanical, Electrical, Chemical, Assembly
- Risk Levels: Low/Medium/High
- Required Skill: 1-3 scale
- Supervision: Required/Not Required

### Assignments (1500 records)
- Worker-Task pairings
- Skill mismatch scores
- Risk assessments
- Target variable: Risk Level

## Key Evaluation Metrics

| Metric | Purpose | Target |
|--------|---------|--------|
| Accuracy | Overall correctness | >0.80 |
| Precision | False positive control | >0.75 |
| Recall | False negative control | >0.80 |
| F1-Score | Balance precision/recall | >0.77 |
| **High-Risk Recall** | **Safety critical** | **≥0.85** |

## Next Steps (Week 2)

1. Fine-tune risk classification models
2. Implement feature importance analysis
3. Optimize model hyperparameters
4. Prepare for worker clustering phase

## Documentation

- [Dataset Design](docs/dataset_design.md) - Detailed schema and generation logic
- [Evaluation Metrics](docs/evaluation_metrics.md) - Metric definitions and methodology
- [Week 1 Summary](docs/week1_summary.md) - Results and key findings

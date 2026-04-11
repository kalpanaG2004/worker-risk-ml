# Adaptive Skill and Safety Recommendation System

AI/ML-driven worker risk assessment and skill development recommendation system for industrial environments.

**Status**: **COMPLETE & PRODUCTION READY** | **Workers**: 500 | **ML Accuracy**: 88% | **Confidence**: 87.2%

## Quick Start

### Launch Dashboard
```bash
cd c:\Users\Admin\Desktop\coding\worker-risk-ml
.venv\Scripts\Activate.ps1
streamlit run app.py
```
Opens interactive dashboard at `http://localhost:8501`

### Key Metrics
| Metric | Value | Status |
|--------|-------|--------|
| ML Accuracy | 88% | ✅ |
| High-Risk Recall | 85% | ✅ |
| Confidence Score | 87.2% | ✅ |
| Data Coverage | 100% (500 workers) | ✅ |
| Critical Workers | 15 identified | 🚨 |

## System Architecture

```
User Interfaces
├── Streamlit Dashboard (Web UI)
├── CLI Interface
└── Python API

Integration Layer
├── Risk Model (Gradient Boosting, 88% accuracy)
├── Clustering (K-Means, k=2)
└── Recommendations (6 categories)

Data Layer
├── 500 workers, 200 tasks, 1500 assignments
└── Trained models & predictions
```

## Components

✅ **ML Risk Model** - Gradient Boosting with 88% accuracy, identifies 15 high-risk workers\
✅ **Worker Clustering** - K-Means with k=2 (experienced vs. developing workforce)\
✅ **Recommendation Engine** - 6-category decision system with personalized training suggestions\
✅ **Dashboard** - Interactive Streamlit UI for data exploration and worker analysis\
✅ **Integration Layer** - Unified Python API combining all components\
✅ **CLI Interface** - Command-line access to all features

## Technology Stack

Python 3.11+ | Scikit-learn | Pandas | Streamlit | Matplotlib | SciPy

## Project Structure

```
├── app.py                    # Streamlit dashboard
├── main.py                   # Full pipeline
├── requirements.txt          # Dependencies
├── src/                      # Core modules
│   ├── integration_layer.py  # Unified API
│   ├── cli_interface.py      # CLI commands
│   ├── baseline_model.py     # ML model
│   ├── worker_clustering.py  # Clustering
│   └── recommendation_engine.py
├── data/                     # Datasets & models
└── docs/                     # Documentation
```

## Installation

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows
source .venv/bin/activate            # Linux/macOS
pip install -r requirements.txt
```

## Usage

**Option 1: Streamlit Dashboard**
```bash
streamlit run app.py
```

**Option 2: CLI**
```bash
python src/cli_interface.py
```

**Option 3: Python API**
```python
from src.integration_layer import IntegrationLayer
integration = IntegrationLayer()
profile = integration.get_worker_profile('W00001')
```

## Documentation

- **[STREAMLIT_QUICKSTART.md](STREAMLIT_QUICKSTART.md)** - Dashboard setup
- **[docs/WEEK7_FINALIZATION.md](docs/WEEK7_FINALIZATION.md)** - Full documentation
- **[docs/WEEK7_DEMO_SCENARIOS.md](docs/WEEK7_DEMO_SCENARIOS.md)** - Demo workflows


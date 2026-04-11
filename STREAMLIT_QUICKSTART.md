# Quick Start: Running the Worker Risk ML Dashboard

## Prerequisites

✅ Streamlit installed
✅ Virtual environment activated
✅ All data files in `data/` directory
✅ All model files (best_model.pkl, kmeans_model.pkl) present

## Starting the Dashboard

### Option 1: PowerShell (Windows)

```powershell
cd c:\Users\Admin\Desktop\coding\worker-risk-ml
.venv\Scripts\Activate.ps1
streamlit run app.py
```

### Option 2: Command Prompt (Windows)

```cmd
cd c:\Users\Admin\Desktop\coding\worker-risk-ml
.venv\Scripts\activate.bat
streamlit run app.py
```

### What to Expect

1. **Server starts** - "You can now view your Streamlit app in your browser"
2. **Browser opens** - Automatically navigates to http://localhost:8501
3. **Dashboard loads** - System overview appears with key metrics
4. **Ready to use** - All tabs and features functional

**Startup time**: ~5-10 seconds (first time may take longer)

## Dashboard Navigation

### Main Tabs (Left Sidebar)

1. **Dashboard** - System overview and statistics
2. **Worker Profile** - Search and view individual workers
3. **Cluster Analysis** - Compare workforce segments
4. **Search Workers** - Advanced filtering interface
5. **Recommendations** - View system recommendations
6. **About** - System information and help

### System Status (Left Sidebar)

Always visible:
- Workers Analyzed: 500/500
- ML Coverage: 100%
- Avg Confidence: 87.2%

## Quick Demo (2 minutes)

1. **Dashboard tab** appears by default - note key metrics
2. **Click**: Worker Profile tab
3. **Enter**: W00042 in search box
4. **View**: Detailed worker analysis
5. **Click**: Export Report (optional)

## Stopping the App

Press `Ctrl+C` in the terminal where streamlit is running.

## Troubleshooting

### "Connection refused" / "Failed to connect"

```
1. Ensure streamlit is running in terminal
2. Check browser URL: http://localhost:8501
3. Try clearing browser cache: Ctrl+Shift+Delete
4. Restart: Ctrl+C then streamlit run app.py again
```

### "Worker not found" error

- Check worker ID format: **W00001** (capital W, 5 digits)
- Valid range: W00001 to W00500

### "AttributeError: 'IntegrationLayer' has no attribute..."

- Ensure data/ directory has all required files
- Files needed:
  - workers.csv
  - worker_clusters.csv
  - worker_recommendations.csv
  - best_model.pkl
  - kmeans_model.pkl

### Performance is slow

- Clear Streamlit cache: `streamlit cache clear`
- Reduce workers displayed in tables
- Restart the app

## Using Alternative Interfaces

### CLI Interface
```bash
python src/cli_interface.py
# Type: help
```

### Python API
```python
from src.integration_layer import IntegrationLayer
integration = IntegrationLayer()
profile = integration.get_worker_profile('W00001')
print(profile)
```

## Accessing on Network

**For local network (not recommended for production):**

```bash
streamlit run app.py --server.address 0.0.0.0
```

Then access from another machine: `http://<YOUR_IP>:8501`

## Production Deployment

For production use, see: `docs/WEEK7_FINALIZATION.md` → Deployment Instructions

## Next Steps

1. **Demo to stakeholders** - See: `docs/WEEK7_DEMO_SCENARIOS.md`
2. **Monitor system** - Check Dashboard weekly
3. **Track training** - Use Worker Profile to monitor progress
4. **Plan improvements** - See: `docs/WEEK7_FINALIZATION.md` → Future Roadmap

---

For comprehensive documentation, see: [docs/WEEK7_FINALIZATION.md](docs/WEEK7_FINALIZATION.md)

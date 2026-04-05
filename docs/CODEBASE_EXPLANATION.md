# Complete Codebase Explanation: File-by-File Breakdown

## 🏗️ System Architecture Overview

```
main.py (Orchestrator)
    ↓
    ├─→ generate_workers.py (Creates worker profiles)
    ├─→ generate_tasks.py (Creates task definitions)
    ├─→ generate_assignments.py (Creates worker-task pairings)
    ├─→ eda_analysis.py (Analyzes data, creates visualizations)
    └─→ baseline_model.py (Trains and evaluates models)
    
Output: 3 datasets + visualizations + trained model
```

---

## 📄 FILE 1: `main.py` (The Orchestrator)

### **Purpose**
Acts as the **entry point** for the entire Week 1 pipeline. Coordinates all other modules in the correct sequence.

### **Importance**
- **Why it exists**: Without an orchestrator, users would need to manually run each script in order. This automates the complete pipeline.
- **Critical for reproducibility**: Ensures consistent execution order and parameters across runs
- **Professional structure**: Standard practice in ML projects

### **How It Works**

**Step 1: Import all modules**
```python
from generate_workers import generate_workers, save_workers
from generate_tasks import generate_tasks, save_tasks
from generate_assignments import generate_assignments, save_assignments
from eda_analysis import perform_eda, load_datasets
from baseline_model import train_baseline_model
```
Loads the functions from all other modules.

**Step 2: Execute pipeline in sequence**
```python
# STEP 1: Generate worker data
workers = generate_workers(n_workers=500, random_state=42)
save_workers(workers, 'data/workers.csv')

# STEP 2: Generate task data
tasks = generate_tasks(n_tasks=200, random_state=42)
save_tasks(tasks, 'data/tasks.csv')

# STEP 3: Generate assignments
assignments = generate_assignments(workers, tasks, n_assignments=1500)
save_assignments(assignments, 'data/assignments.csv')

# STEP 4: Analyze and visualize
perform_eda(workers, tasks, assignments)

# STEP 5: Train models
train_baseline_model(data_dir='data', vis_dir='visualizations')
```

**Step 3: Print final summary**
- Displays all created files
- Shows key metrics (accuracy, recall, etc.)
- Provides next steps

### **Key Features**
✅ Formatted console output with progress tracking  
✅ All parameters centralized (easy to modify)  
✅ Modular design (can run individual steps independently)  
✅ Clear success message upon completion  

### **When to Use**
```bash
python main.py  # Runs entire Week 1 pipeline
```

---

## 📊 FILE 2: `generate_workers.py` (Worker Data Generation)

### **Purpose**
Creates a **realistic synthetic dataset of 500 workers** with skills, certifications, and incident history.

### **Importance**
- **Foundation of ML training**: Models need quality input data
- **Avoids privacy concerns**: No real employee data needed
- **Reproducible**: Fixed random seed ensures same results every time
- **Realistic constraints**: Features have realistic correlations

### **How It Works**

**Function 1: `generate_workers(n_workers=500, random_state=42)`**

```python
# Step 1: Create basic structure
workers_data = {
    'worker_id': [f'W{i:05d}' for i in range(1, n_workers + 1)],  # W00001, W00002, ...
    'experience_years': np.random.randint(0, 31, size=n_workers),  # 0-30 years
    'certification_level': np.random.choice([0, 1, 2], ..., p=[0.3, 0.45, 0.25]),  # 30% None, 45% Basic, 25% Advanced
    'training_completed': np.random.randint(0, 2, size=n_workers),  # Binary: 0 or 1
    'past_incident_count': np.random.poisson(lam=0.8, size=n_workers),  # Rare but realistic incidents
    'avg_incident_severity': np.random.uniform(1, 5, size=n_workers),  # 1-5 scale
    'skill_score': np.random.uniform(0, 100, size=n_workers),  # Initial random score
}
```

**Step 2: Apply realistic relationships**

The key insight: we adjust skill_score based on other factors to create realistic patterns

```python
# More experience → Higher skills
experience_influence = (experience_years / 30) * 40  # Up to 40 points
# Certification → Higher skills  
cert_influence = certification_level * 15  # Up to 30 points
# Training → Higher skills
training_influence = training_completed * 10  # Up to 10 points
# Add random variation
noise = np.random.normal(0, 5)

skill_score = (experience_influence + cert_influence + training_influence + noise).clip(0, 100)
```

**Step 3: Apply penalties for incidents**
```python
# More incidents → Lower skills
skill_score = (skill_score - (past_incident_count * 3)).clip(0, 100)
```

### **Output Dataset Structure**

| Column | Type | Range | Example |
|--------|------|-------|---------|
| worker_id | String | W00001-W00500 | "W00042" |
| experience_years | Integer | 0-30 | 15 |
| certification_level | Integer | 0, 1, 2 | 2 (Advanced) |
| training_completed | Binary | 0, 1 | 1 (Yes) |
| past_incident_count | Integer | 0-5+ | 2 |
| avg_incident_severity | Float | 1-5 | 3.45 |
| skill_score | Float | 0-100 | 62.5 |

### **Why Each Field Matters**
- **worker_id**: Unique identifier for merging with other datasets
- **experience_years**: Strong predictor of skill level
- **certification_level**: Indicates formal training/qualification
- **training_completed**: Safety training completion status
- **past_incident_count**: Safety history indicator
- **avg_incident_severity**: Quality of incidents (minor vs. critical)
- **skill_score**: Composite measure used in model training

### **Key Features**
✅ Realistic correlations (experience → skill, incidents → lower skill)  
✅ Stratified certification distribution  
✅ Poisson distribution for incidents (rare but possible)  
✅ Reproducible with fixed random seed  
✅ Saves to CSV automatically

---

## 🎯 FILE 3: `generate_tasks.py` (Task Definition Generation)

### **Purpose**
Creates a **synthetic dataset of 200 tasks** with characteristics and risk levels that will serve as the **target for our predictions**.

### **Importance**
- **Defines the prediction problem**: Models predict task risk from task features
- **Realistic risk distribution**: Tasks have varying risk levels, not all equally dangerous
- **Balanced dataset**: Helps models learn all risk classes fairly

### **How It Works**

**Function: `generate_tasks(n_tasks=200, random_state=42)`**

```python
# Step 1: Create basic task structure
tasks_data = {
    'task_id': [f'T{i:04d}' for i in range(1, n_tasks + 1)],  # T0001, T0002, ...
    'task_type': np.random.choice(task_types, size=n_tasks),  # Mechanical, Electrical, Chemical, Assembly
    'required_skill_level': np.random.randint(1, 4, size=n_tasks),  # 1=Basic, 2=Intermediate, 3=Expert
    'environment_risk': np.random.randint(1, 4, size=n_tasks),  # 1=Low, 2=Medium, 3=High
    'supervision_required': np.random.randint(0, 2, size=n_tasks),  # Binary: 0=No, 1=Yes
}
```

**Step 2: Compute risk score from task characteristics**

```python
risk_score = (
    environment_risk * 0.4 +        # Environment is 40% important
    required_skill_level * 0.3 +    # Skill requirement is 30% important
    supervision_required * 0.2 +    # Supervision is 20% important
    np.random.normal(0, 0.3)        # Add small randomness
)

# Chemical tasks are inherently more dangerous
if task_type == 'Chemical':
    risk_score += 0.5  # Extra risk boost
```

**Step 3: Assign risk labels based on score**

```python
# Use thresholds to categorize:
# Score < 1.8 → Low Risk
# 1.8 ≤ Score < 2.8 → Medium Risk
# Score ≥ 2.8 → High Risk

risk_label = pd.cut(
    risk_score,
    bins=[-np.inf, 1.8, 2.8, np.inf],
    labels=['Low', 'Medium', 'High']
)
```

### **Output Dataset Structure**

| Column | Type | Values | Example |
|--------|------|--------|---------|
| task_id | String | T0001-T0200 | "T0047" |
| task_type | Categorical | Mechanical, Electrical, Chemical, Assembly | "Chemical" |
| required_skill_level | Integer | 1, 2, 3 | 3 |
| environment_risk | Integer | 1, 2, 3 | 2 |
| supervision_required | Binary | 0, 1 | 1 |
| risk_label | Categorical | Low, Medium, High | "High" |

### **Why This Design?**
- **task_type**: Different task types have different inherent risks
- **required_skill_level**: Harder tasks need more skilled workers
- **environment_risk**: Physical/chemical hazards in the environment
- **supervision_required**: Management decision based on risk
- **risk_label**: What we want to predict! This is our target variable

### **Key Features**
✅ Realistic risk composition (multiple factors contribute)  
✅ Chemical tasks weighted higher (accurately reflects industry reality)  
✅ Balanced risk class distribution  
✅ Reproducible with fixed seed  

---

## 🔗 FILE 4: `generate_assignments.py` (Worker-Task Matching)

### **Purpose**
Creates **1,500 worker-task assignments** and computes the **actual risk** for each pairing. This is the critical dataset for training the ML model.

### **Importance**
- **Training data**: Creates input-output pairs for supervised learning
- **Complexity modeling**: Combines worker profile + task profile to create realistic scenarios
- **Feature engineering**: Calculates derived features (skill_mismatch) used in models
- **Ground truth labels**: Generates the target variable we'll predict

### **How It Works**

**Step 1: Create random pairings**
```python
# Randomly select workers and tasks
worker_ids = np.random.choice(workers_df['worker_id'], size=1500)
task_ids = np.random.choice(tasks_df['task_id'], size=1500)

assignments_data = {
    'assignment_id': [f'A{i:06d}' for i in range(1, 1501)],  # A000001, A000002, ...
    'worker_id': worker_ids,
    'task_id': task_ids,
}
```

**Step 2: Merge with worker and task data**
```python
# Get worker properties
df = df.merge(workers_df[['worker_id', 'skill_score', 'past_incident_count']], 
              on='worker_id', how='left')

# Get task properties
df = df.merge(tasks_df[['task_id', 'required_skill_level', 'environment_risk', 'risk_label']], 
              on='task_id', how='left')
```

Now each row has: worker info + task info + both IDs

**Step 3: Calculate skill mismatch (derived feature)**

The key insight: A worker's actual risk depends on how well they match the task

```python
# Convert skill level (1-3) to expected skill score
# Level 1 → 35 points, Level 2 → 65 points, Level 3 → 95 points
required_skill_score = (required_skill_level - 1) * 30 + 35

# How far off is the worker?
skill_mismatch = abs(worker_skill_score - required_skill_score)
```

**Example:**
- Task requires skill level 3 (95 points)
- Worker has skill score 70
- Skill mismatch = |70 - 95| = 25 (significant gap!)

**Step 4: Compute actual risk combining three factors**

```python
risk_score = environment_risk  # Base: task's inherent risk

# Add penalty for skill mismatch
# More mismatch → higher risk
skill_penalty = (skill_mismatch / 100) * 1.0  # Up to 1.0 points
risk_score += skill_penalty

# Add penalty for past incidents
# Worker with incidents is riskier
incident_penalty = past_incident_count * 0.3
risk_score += incident_penalty

# Assign labels using same thresholds as tasks
# Low: < 1.8, Medium: 1.8-2.8, High: > 2.8
actual_risk = pd.cut(..., labels=['Low', 'Medium', 'High'])
```

**Step 5: Clean up and save**
```python
# Keep only necessary columns for training
df = df[['assignment_id', 'worker_id', 'task_id', 'skill_mismatch', 'actual_risk']]
```

### **Output Dataset Structure**

| Column | Type | Values | Meaning |
|--------|------|--------|---------|
| assignment_id | String | A000001-A001500 | Unique assignment ID |
| worker_id | String | W00001-W00500 | Which worker |
| task_id | String | T0001-T0200 | Which task |
| skill_mismatch | Float | 0-100 | Gap between worker & task skill |
| actual_risk | Categorical | Low, Medium, High | **Target variable** (what we predict) |

### **Why This Design?**
- **Mixed dataset**: 1,500 samples from 500 workers × 200 tasks gives variety
- **Skill mismatch**: Captures "wrong person for the job" scenarios
- **Realistic risk**: Combines inherent task risk with worker capability
- **Labeled data**: Has ground truth for supervised learning

### **Key Formula**
```
Actual Risk = f(environment_risk, skill_mismatch, past_incidents)
            = environment_risk + (skill_mismatch/100)*1.0 + past_incidents*0.3
```

This formula means:
- A harder task (high environment_risk) is inherently riskier
- A badly-matched worker (high skill_mismatch) makes it riskier
- A worker with incident history (past_incidents) adds risk

---

## 📈 FILE 5: `eda_analysis.py` (Exploratory Data Analysis)

### **Purpose**
**Explores and visualizes the datasets** to understand their characteristics and validate quality.

### **Importance**
- **Data validation**: Ensures data looks reasonable before training models
- **Insight generation**: Discovers patterns and relationships
- **Problem understanding**: Helps us understand what the data is telling us
- **Stakeholder communication**: Visualizations explain data to non-technical people

### **How It Works**

**Function 1: `load_datasets(data_dir='data')`**
```python
workers = pd.read_csv(f'{data_dir}/workers.csv')
tasks = pd.read_csv(f'{data_dir}/tasks.csv')
assignments = pd.read_csv(f'{data_dir}/assignments.csv')
return workers, tasks, assignments
```
Simple data loading function.

**Function 2: `summarize_datasets(workers, tasks, assignments)`**

Prints statistical summaries:
```python
workers.describe()  # Mean, std, min, max for each numeric column
workers.dtypes      # Data types
workers.isnull().sum()  # Missing values (should all be 0)
```

**Outputs like:**
```
       experience_years  skill_score  past_incident_count
count        500.000000   500.000000        500.000000
mean          15.218000    37.240661         0.812000
std            9.451409    17.113878         0.933159
min            0.000000     0.000000         0.000000
25%            7.000000    25.654323         0.000000
50%           16.000000    36.641305         1.000000
75%           24.000000    49.148695         1.000000
max           30.000000    80.572407         5.000000
```

This tells us:
- Workers average 15 years experience (reasonable)
- Skill scores average 37/100 (implies room for improvement)
- 0.8 incidents per worker on average (realistic)
- No missing data (data quality ✅)

**Function 3: `create_visualizations(workers, tasks, assignments, vis_dir)`**

Creates 9 different visualizations:

1. **Risk Distribution** (Bar chart)
   - How many tasks are Low/Medium/High risk?
   - Validates balanced distribution

2. **Skill Distribution** (Histogram)
   - Shows the spread of worker skills
   - Validates feature range and distribution

3. **Environment Risk Distribution** (Bar chart)
   - Environmental hazard levels distribution
   - Helps understand task difficulty

4. **Certification Distribution** (Bar chart)
   - How many workers at each certification level?
   - Validates the 30/45/25 split we programmed

5. **Actual Risk Distribution** (Bar chart)
   - Risk levels of assignments (worker + task combined)
   - Shows the distribution of our target variable

6. **Experience vs Skill** (Scatter plot with trend line)
   - Do experienced workers have higher skills?
   - Validates the realistic correlation we built in

7. **Model Comparison** (Multi-panel chart)
   - Compares model performance (created by baseline_model.py)

8. **Confusion Matrix** (Heatmap)
   - Shows which risk classes are confused with each other

9. **High-Risk Recall** (Bar chart)
   - Most important metric: do we catch high-risk tasks?

### **Key Features**
✅ Statistical summaries for data validation  
✅ 9 professional visualizations  
✅ All plots saved as high-resolution PNGs  
✅ Formatted console output for human readability  

---

## 🤖 FILE 6: `baseline_model.py` (Machine Learning Training)

### **Purpose**
**Trains, evaluates, and compares three classification models** to predict task risk level.

### **Importance**
- **Core ML component**: This is where learning happens
- **Model selection**: Tests different algorithms to find the best one
- **Safety focus**: Prioritizes catching high-risk tasks (high recall)
- **Production baseline**: Establishes performance to improve upon in Week 2

### **How It Works**

**Function 1: `load_and_prepare_data(data_dir='data', test_size=0.2)`**

```python
# Load the three datasets
tasks = pd.read_csv('data/tasks.csv')
assignments = pd.read_csv('data/assignments.csv')
workers = pd.read_csv('data/workers.csv')

# Merge them into one matrix for training
data = assignments.merge(tasks[...], on='task_id')  # Add task features
data = data.merge(workers[...], on='worker_id')     # Add worker features

# Create feature matrix X
feature_cols = [
    'required_skill_level',
    'environment_risk', 
    'supervision_required',
    'experience_years',
    'certification_level',
    'training_completed',
    'past_incident_count',
    'skill_mismatch'
]
X = data[feature_cols]  # 1500 rows × 8 features

# Create target vector y
y = data['actual_risk']  # 1500 risk labels (Low/Medium/High)

# Encode text labels to numbers (Low→0, Medium→1, High→2)
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split: 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)
# Result: 1200 training samples, 300 test samples

# Standardize features (mean=0, std=1)
# Why? Different scales would confuse the models
# (experience in 0-30 range vs certification in 0-2 range)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # Learn scaling from train set
X_test_scaled = scaler.transform(X_test)        # Apply same scaling to test
```

**Function 2: `train_models(X_train, X_test, y_train, y_test)`**

Trains three different algorithms:

**Model 1: Logistic Regression**
```python
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train_scaled, y_train)
y_pred = model.predict(X_test_scaled)
```
- Pros: Fast, interpretable, good baseline
- Cons: Assumes linear decision boundaries

**Model 2: Random Forest** ⭐
```python
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train_scaled, y_train)
y_pred = model.predict(X_test_scaled)
```
- Pros: Non-linear, handles feature interactions, resilient to outliers
- Cons: Less interpretable, slower

**Model 3: Gradient Boosting**
```python
model = GradientBoostingClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)
y_pred = model.predict(X_test_scaled)
```
- Pros: Best overall accuracy, sequential learning
- Cons: Slower training, prone to overfitting if not careful

**Function 3: Evaluate models**

For each model, calculate metrics:

```python
accuracy = accuracy_score(y_test, y_pred)      # Overall correctness
precision = precision_score(y_test, y_pred, average='weighted')  # FP control
recall = recall_score(y_test, y_pred, average='weighted')        # FN control
f1 = f1_score(y_test, y_pred, average='weighted')                # Balance

# MOST IMPORTANT: High-risk recall
high_risk_idx = label_encoder.transform(['High'])[0]  # Get the "High" encoding
high_risk_recall = recall_score(y_test, y_pred, labels=[high_risk_idx])
```

**Why High-Risk Recall?**
- In safety-critical systems, missing a danger (false negative) is worse than a false alarm
- If we miss even 1 high-risk assignment out of 100, an accident could happen
- Therefore: **Maximize recall for high-risk tasks**

**Function 4: `evaluate_and_compare(results, y_test, label_encoder)`**

```python
# Select best model by highest High-Risk Recall
best_model_name = max(results.keys(), 
                      key=lambda x: results[x]['high_risk_recall'])
```

**Week 1 Results:**
- Logistic Regression: 98.29% high-risk recall
- Random Forest: **100.00% high-risk recall** ← WINNER
- Gradient Boosting: 99.15% high-risk recall

Random Forest was selected because it perfectly detected all high-risk assignments!

**Function 5: `visualize_results(...)`**

Creates 3 visualizations:

1. Model Comparison (4 metrics side-by-side)
2. Confusion Matrix (heatmap of predictions)
3. High-Risk Recall Comparison (most important metric)

**Function 6: `train_baseline_model()`**

Orchestrates the entire training pipeline:

```
load_and_prepare_data() 
    ↓
train_models()
    ↓
evaluate_and_compare()
    ↓
visualize_results()
    ↓
save_best_model()
    ↓
print summary
```

### **Key Metrics Explained**

**Accuracy** = (Correct Predictions) / (Total Predictions)
- 99% accuracy = 297 out of 300 predictions correct
- Easy metric, but doesn't account for class importance

**Precision** = (True High-Risk) / (Predicted High-Risk)
- 99% precision = when we say "High Risk", 99% of the time it's truly high risk
- Controls false alarms

**Recall** = (Detected High-Risk) / (All Actual High-Risk)
- 99% recall = we catch 99% of all high-risk tasks
- Controls missed dangers (critical for safety!)

**F1-Score** = Harmonic mean of Precision and Recall
- Balances both metrics
- Good overall performance measure

**High-Risk Recall** (Special emphasis)
- The metric we care about most
- Answers: "Of the 117 truly high-risk assignments, how many did we identify?"
- Week 1 result: 100% = we caught all 117!

### **Output Files Generated**
- `data/X_train.csv` - Training features
- `data/X_test.csv` - Testing features
- `data/y_train.csv` - Training labels
- `data/y_test.csv` - Testing labels
- `data/best_model.pkl` - Serialized Random Forest model
- `visualizations/model_comparison.png` - Performance chart
- `visualizations/confusion_matrix_best_model.png` - Prediction breakdown
- `visualizations/high_risk_recall_comparison.png` - Safety metric

---

## 🔄 How All Files Work Together

```
┌─────────────────────────────────────────────────────────────┐
│                    main.py (Orchestrator)                    │
│  Coordinates the entire pipeline with progress tracking     │
└──────┬─────────────────────────────────────────────────────┘
       │
       ├─────────────────────────────────────────────┐
       │                                             │
       ▼                                             ▼
   ┌──────────────────────┐              ┌──────────────────────┐
   │ generate_workers.py  │              │  generate_tasks.py   │
   │                      │              │                      │
   │ Creates: 500 workers │              │ Creates: 200 tasks   │
   │ Output: workers.csv  │              │ Output: tasks.csv    │
   │                      │              │                      │
   │ Features: skill,     │              │ Features: risk_label │
   │ experience, certs,   │              │ required_skill_level │
   │ incidents            │              │ environment_risk     │
   └──────────┬───────────┘              └──────────┬───────────┘
              │                                     │
              │                                     │
              └───────────────┬────────────────────┘
                              │
                              ▼
                   ┌──────────────────────────┐
                   │ generate_assignments.py  │
                   │                          │
                   │ Merges workers + tasks   │
                   │ Creates 1500 pairs       │
                   │ Computes skill_mismatch  │
                   │ Derives actual_risk      │
                   │                          │
                   │ Output: assignments.csv  │
                   │ (TRAINING DATA)          │
                   └──────────┬───────────────┘
                              │
                              ├─────────────────────────┐
                              │                         │
                              ▼                         ▼
                   ┌──────────────────────┐  ┌──────────────────────┐
                   │  eda_analysis.py     │  │ baseline_model.py    │
                   │                      │  │                      │
                   │ Summarizes data      │  │ Trains 3 models:     │
                   │ Creates 9 plots      │  │ - Log. Regression    │
                   │ Validates quality    │  │ - Random Forest ⭐   │
                   │                      │  │ - Gradient Boosting  │
                   │ Output: PNG charts   │  │                      │
                   └──────────────────────┘  │ Evaluates & compares │
                                             │ Selects best model   │
                                             │                      │
                                             │ Output: best_model.pk│
                                             │ PNG visualizations   │
                                             └──────────────────────┘
                                             
                              │
                              ▼
                   ┌──────────────────────────┐
                   │   Week 1 Complete! ✅    │
                   │                          │
                   │ Ready for Week 2:        │
                   │ - Feature optimization  │
                   │ - Hyperparameter tuning │
                   │ - SHAP analysis         │
                   └──────────────────────────┘
```

---

## 🎯 Data Flow Example

Let's trace one worker-task assignment through the system:

```
Worker W00042:
├─ experience_years = 15
├─ certification_level = 2 (Advanced)
├─ training_completed = 1
├─ past_incident_count = 1
├─ avg_incident_severity = 3.2
└─ skill_score = 58.5  (calculated by generate_workers.py)

Task T0047:
├─ task_type = "Chemical"
├─ required_skill_level = 3
├─ environment_risk = 3
├─ supervision_required = 1
└─ risk_label = "High"  (computed by generate_tasks.py)

Assignment A000123 creates pairing:
├─ worker_id: "W00042"
├─ task_id: "T0047"
├─ skill_mismatch = |58.5 - 95| = 36.5
│  (task requires higher skill!)
├─ risk_component = 3 (environment_risk)
├─ + skill_penalty = 36.5/100 * 1.0 = 0.365
├─ + incident_penalty = 1 * 0.3 = 0.3
├─ = total_risk_score = 3.665
└─ → actual_risk = "High"  (>2.8 threshold)

Model Training:
├─ Input features: [required_skill_level=3, environment_risk=3, supervision=1,
│                   experience=15, cert=2, training=1, incidents=1, 
│                   skill_mismatch=36.5]
├─ Random Forest learns: "These features predict HIGH risk"
├─ Training on 1200 samples
└─ Tests on 300 samples → 99% accuracy!

Result: Model learns to identify high-risk assignments ✅
```

---

## 📊 File Dependencies Map

```
main.py
├── imports generate_workers → uses workers.csv
├── imports generate_tasks → uses tasks.csv
├── imports generate_assignments → uses workers.csv + tasks.csv → produces assignments.csv
├── imports eda_analysis → reads workers, tasks, assignments → creates 9 PNGs
└── imports baseline_model → reads assignments + workers + tasks 
                             → trains 3 models 
                             → saves best_model.pkl
                             → creates 3 PNGs
```

---

## ✅ Quality Checklist

**Each file implements:**

- ✅ **Modularity**: Functions are self-contained, reusable
- ✅ **Documentation**: Docstrings explain purpose, parameters, outputs
- ✅ **Reproducibility**: Fixed random seeds ensure consistent results
- ✅ **Error Handling**: Path creation, file I/O protection
- ✅ **Logging**: Print statements show progress
- ✅ **Clean Code**: Clear variable names, logical structure
- ✅ **Professional Structure**: Follows ML project best practices

---

## 🚀 Execution Flow

When you run `python main.py`:

```
1. main.py starts
   ├─ Imports all modules
   └─ Calls main() function

2. Generate workers (2 seconds)
   ├─ 500 workers created
   └─ Saved to workers.csv

3. Generate tasks (0.5 seconds)
   ├─ 200 tasks created
   └─ Saved to tasks.csv

4. Generate assignments (1 second)
   ├─ 1500 worker-task pairs created
   ├─ Skill mismatch calculated
   ├─ Risk labels derived
   └─ Saved to assignments.csv

5. EDA Analysis (3 seconds)
   ├─ Statistics printed
   └─ 9 PNG visualizations created

6. Model Training (5 seconds)
   ├─ Data loaded and merged
   ├─ Features scaled
   ├─ 3 models trained
   ├─ Metrics calculated
   ├─ Best model selected (Random Forest)
   └─ 3 visualizations created

7. Summary printed
   ├─ All files listed
   └─ Key metrics displayed

TOTAL TIME: ~12 seconds ⚡
```

---

## 📚 Summary Table

| File | Lines | Purpose | Key Function | Output |
|------|-------|---------|--------------|--------|
| main.py | ~70 | Pipeline orchestration | main() | Console summary |
| generate_workers.py | ~50 | Worker data creation | generate_workers() | workers.csv |
| generate_tasks.py | ~50 | Task data creation | generate_tasks() | tasks.csv |
| generate_assignments.py | ~70 | Assignment creation & risk derivation | generate_assignments() | assignments.csv |
| eda_analysis.py | ~150 | Exploratory analysis | perform_eda() | 9 PNG charts |
| baseline_model.py | ~250 | Model training & evaluation | train_baseline_model() | best_model.pkl + 3 PNGs |

**Total Code**: ~640 lines of clean, modular Python

**No dependencies on real data** - everything is reproducible with fixed random seeds

---

This structure enables:
✅ **Reproducibility**: Same code → same results every time  
✅ **Scalability**: Easy to generate bigger datasets  
✅ **Modularity**: Run individual files independently or together  
✅ **Maintainability**: Clean separation of concerns  
✅ **Extensibility**: Easy to add Week 2 refinements  

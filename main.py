import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from generate_workers import generate_workers, save_workers
from generate_tasks import generate_tasks, save_tasks
from generate_assignments import generate_assignments, save_assignments
from eda_analysis import perform_eda, load_datasets
from baseline_model import train_baseline_model


def main():
    print("\n" + "=" * 70)
    print("ADAPTIVE SKILL AND SAFETY RECOMMENDATION SYSTEM")
    print("Week 1: Foundation & Baseline Model")
    print("=" * 70)
    
    # === STEP 1: Generate Synthetic Datasets ===
    print("\n📦 STEP 1: Generating Synthetic Datasets...")
    print("-" * 70)
    
    workers = generate_workers(n_workers=500, random_state=42)
    save_workers(workers, 'data/workers.csv')
    
    tasks = generate_tasks(n_tasks=200, random_state=42)
    save_tasks(tasks, 'data/tasks.csv')
    
    assignments = generate_assignments(workers, tasks, n_assignments=1500, random_state=42)
    save_assignments(assignments, 'data/assignments.csv')
    
    # === STEP 2: Exploratory Data Analysis ===
    print("\n📊 STEP 2: Performing Exploratory Data Analysis...")
    print("-" * 70)
    
    workers, tasks, assignments = load_datasets('data')
    perform_eda(workers, tasks, assignments)
    
    # === STEP 3: Train Baseline Model ===
    print("\n🤖 STEP 3: Training Baseline Risk Classification Model...")
    print("-" * 70)
    
    model_results = train_baseline_model(data_dir='data', vis_dir='visualizations')
    
    # === STEP 4: Summary ===
    print("\n" + "=" * 70)
    print("WEEK 1 EXECUTION COMPLETE ✓")
    print("=" * 70)
    
    print("\n📁 Generated Files:")
    print("  Data:")
    print("    ✓ data/workers.csv (500 records)")
    print("    ✓ data/tasks.csv (200 records)")
    print("    ✓ data/assignments.csv (1500 records)")
    print("    ✓ data/X_train.csv, X_test.csv (features)")
    print("    ✓ data/y_train.csv, y_test.csv (labels)")
    print("    ✓ data/best_model.pkl (trained model)")
    
    print("\n  Visualizations:")
    print("    ✓ visualizations/risk_distribution.png")
    print("    ✓ visualizations/skill_distribution.png")
    print("    ✓ visualizations/environment_risk_distribution.png")
    print("    ✓ visualizations/certification_distribution.png")
    print("    ✓ visualizations/actual_risk_distribution.png")
    print("    ✓ visualizations/experience_vs_skill.png")
    print("    ✓ visualizations/model_comparison.png")
    print("    ✓ visualizations/confusion_matrix_best_model.png")
    print("    ✓ visualizations/high_risk_recall_comparison.png")
    
    print("\n  Code Modules:")
    print("    ✓ src/generate_workers.py")
    print("    ✓ src/generate_tasks.py")
    print("    ✓ src/generate_assignments.py")
    print("    ✓ src/eda_analysis.py")
    print("    ✓ src/baseline_model.py")
    
    print("\n📊 Key Metrics:")
    print(f"  Best Model: {model_results['best_model_name']}")
    print(f"  Test Accuracy: {model_results['best_result']['accuracy']:.4f}")
    print(f"  High-Risk Recall: {model_results['best_result']['high_risk_recall']:.4f}")
    print(f"  F1-Score: {model_results['best_result']['f1']:.4f}")
    
    print("\n✅ Week 1 Foundation Complete!")
    print("📋 Next: Week 2 - Risk Classification Model Refinement")


if __name__ == '__main__':
    main()


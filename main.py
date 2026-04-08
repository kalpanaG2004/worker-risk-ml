import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from generate_workers import generate_workers, save_workers
from generate_tasks import generate_tasks, save_tasks
from generate_assignments import generate_assignments, save_assignments
from eda_analysis import perform_eda, load_datasets
from baseline_model import train_baseline_model
from model_refinement import model_refinement_pipeline


def main():
    print("\n" + "=" * 70)
    print("ADAPTIVE SKILL AND SAFETY RECOMMENDATION SYSTEM")
    print("Week 1: Foundation & Baseline Model")
    print("=" * 70)
    
    print("\nSTEP 1: Generating Synthetic Datasets...")
    print("-" * 70)
    
    workers = generate_workers(n_workers=500, random_state=42)
    save_workers(workers, 'data/workers.csv')
    
    tasks = generate_tasks(n_tasks=200, random_state=42)
    save_tasks(tasks, 'data/tasks.csv')
    
    assignments = generate_assignments(workers, tasks, n_assignments=1500, random_state=42)
    save_assignments(assignments, 'data/assignments.csv')
    
    print("\nSTEP 2: Performing Exploratory Data Analysis...")
    print("-" * 70)
    
    workers, tasks, assignments = load_datasets('data')
    perform_eda(workers, tasks, assignments)
    
    print("\nSTEP 3: Training Baseline Risk Classification Model...")
    print("-" * 70)
    
    model_results = train_baseline_model(data_dir='data', vis_dir='visualizations')
    
    print("\n" + "=" * 70)
    print("WEEK 1 EXECUTION COMPLETE")
    print("=" * 70)
    
    print("\nGenerated Files:")
    print("  Data:")
    print("    - data/workers.csv (500 records)")
    print("    - data/tasks.csv (200 records)")
    print("    - data/assignments.csv (1500 records)")
    print("    - data/X_train.csv, X_test.csv (features)")
    print("    - data/y_train.csv, y_test.csv (labels)")
    print("    - data/best_model.pkl (trained model)")
    
    print("\n  Visualizations:")
    print("    - visualizations/risk_distribution.png")
    print("    - visualizations/skill_distribution.png")
    print("    - visualizations/environment_risk_distribution.png")
    print("    - visualizations/certification_distribution.png")
    print("    - visualizations/actual_risk_distribution.png")
    print("    - visualizations/experience_vs_skill.png")
    print("    - visualizations/model_comparison.png")
    print("    - visualizations/confusion_matrix_best_model.png")
    print("    - visualizations/high_risk_recall_comparison.png")
    
    print("\n  Code Modules:")
    print("    - src/generate_workers.py")
    print("    - src/generate_tasks.py")
    print("    - src/generate_assignments.py")
    print("    - src/eda_analysis.py")
    print("    - src/baseline_model.py")
    
    print("\nKey Metrics:")
    print(f"  Best Model: {model_results['best_model_name']}")
    print(f"  Test Accuracy: {model_results['best_result']['accuracy']:.4f}")
    print(f"  High-Risk Recall: {model_results['best_result']['high_risk_recall']:.4f}")
    print(f"  F1-Score: {model_results['best_result']['f1']:.4f}")
    
    print("\nWeek 1 Foundation Complete!")
    print("Next: Week 2 - Risk Classification Model Refinement")


def run_week2_refinement():
    print("\n" + "=" * 70)
    print("ADAPTIVE SKILL AND SAFETY RECOMMENDATION SYSTEM")
    print("Week 2: Model Refinement & Optimization")
    print("=" * 70)
    
    refinement_results = model_refinement_pipeline()
    
    print("\n" + "=" * 70)
    print("Week 2 Model Refinement Complete")
    print("=" * 70)
    
    print("\nRefinement Summary:")
    print("\nFeature Importance (Top 5):")
    top_features = refinement_results['feature_importance'].head(5)
    for idx, row in top_features.iterrows():
        print(f"  {row['Feature']}: {row['Importance']:.4f}")
    
    print("\nOptimized Hyperparameters:")
    for param, value in refinement_results['best_params'].items():
        print(f"  - {param}: {value}")
    
    print("\nCross-Validation Performance:")
    for metric, scores in refinement_results['cv_summary'].items():
        print(f"  - {metric}: {scores['mean']:.4f} (+/- {scores['std']:.4f})")
    
    print("\nROC-AUC Scores:")
    for class_idx, auc_score in refinement_results['roc_auc_scores'].items():
        print(f"  - Class {class_idx}: {auc_score:.4f}")
    
    print(f"\nOptimal Probability Threshold: {refinement_results['optimal_threshold']:.2f}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'week2':
        run_week2_refinement()
    else:
        main()


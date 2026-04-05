import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
import pickle


def load_and_prepare_data(data_dir='data', test_size=0.2, random_state=42):
    # Load datasets
    tasks = pd.read_csv(f'{data_dir}/tasks.csv')
    assignments = pd.read_csv(f'{data_dir}/assignments.csv')
    workers = pd.read_csv(f'{data_dir}/workers.csv')
    
    # Merge assignments with task and worker data for complete feature set
    data = assignments.merge(tasks[['task_id', 'task_type', 'required_skill_level', 
                                     'environment_risk', 'supervision_required', 'risk_label']],
                             on='task_id', how='left')
    data = data.merge(workers[['worker_id', 'experience_years', 'certification_level',
                               'training_completed', 'past_incident_count', 'skill_score']],
                      on='worker_id', how='left')
    
    # Select features for the model
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
    
    X = data[feature_cols].copy()
    y = data['actual_risk'].copy()  # Target variable
    
    # Encode target variable
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save processed data
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    pd.DataFrame(X_train_scaled, columns=feature_cols).to_csv(f'{data_dir}/X_train.csv', index=False)
    pd.DataFrame(X_test_scaled, columns=feature_cols).to_csv(f'{data_dir}/X_test.csv', index=False)
    pd.Series(y_train, name='risk_label').to_csv(f'{data_dir}/y_train.csv', index=False)
    pd.Series(y_test, name='risk_label').to_csv(f'{data_dir}/y_test.csv', index=False)
    
    print(f"✓ Data split: {len(X_train)} training, {len(X_test)} testing samples")
    print(f"✓ Features: {feature_cols}")
    print(f"✓ Risk classes: {list(label_encoder.classes_)}")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, feature_cols, label_encoder


def train_models(X_train, X_test, y_train, y_test, label_encoder):
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
    }
    
    results = {}
    
    print("\n" + "=" * 70)
    print("MODEL TRAINING")
    print("=" * 70)
    
    for model_name, model in models.items():
        print(f"\n🤖 Training {model_name}...")
        
        # Train
        model.fit(X_train, y_train)
        
        # Predict
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)
        
        # Evaluate
        accuracy = accuracy_score(y_test, y_pred)
        
        # Calculate metrics for each class
        avg_precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        avg_recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        avg_f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # High-risk recall (most important for safety)
        high_risk_idx = label_encoder.transform(['High'])[0]
        high_risk_recall = recall_score(
            y_test, y_pred, labels=[high_risk_idx], average='weighted', zero_division=0
        )
        
        results[model_name] = {
            'model': model,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba,
            'accuracy': accuracy,
            'precision': avg_precision,
            'recall': avg_recall,
            'f1': avg_f1,
            'high_risk_recall': high_risk_recall,
            'cm': confusion_matrix(y_test, y_pred)
        }
        
        print(f"  ✓ Accuracy: {accuracy:.4f}")
        print(f"  ✓ Precision: {avg_precision:.4f}")
        print(f"  ✓ Recall: {avg_recall:.4f}")
        print(f"  ✓ F1-Score: {avg_f1:.4f}")
        print(f"  ✓ High-Risk Recall: {high_risk_recall:.4f} ⚠️  (Priority metric)")
    
    return results


def evaluate_and_compare(results, y_test, label_encoder):
    print("\n" + "=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)
    
    # Create comparison dataframe
    comparison_data = []
    for model_name, metrics in results.items():
        comparison_data.append({
            'Model': model_name,
            'Accuracy': f"{metrics['accuracy']:.4f}",
            'Precision': f"{metrics['precision']:.4f}",
            'Recall': f"{metrics['recall']:.4f}",
            'F1-Score': f"{metrics['f1']:.4f}",
            'High-Risk Recall': f"{metrics['high_risk_recall']:.4f}" 
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    print("\n" + comparison_df.to_string(index=False))
    
    # Select best model based on High-Risk Recall
    best_model_name = max(results.keys(), key=lambda x: results[x]['high_risk_recall'])
    print(f"\n🏆 Best Model: {best_model_name} (prioritizes High-Risk detection)")
    
    return best_model_name, results[best_model_name]


def visualize_results(results, best_model_name, label_encoder, vis_dir='visualizations'):
    Path(vis_dir).mkdir(parents=True, exist_ok=True)
    
    # 1. Model Comparison - Bar Chart
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Model Performance Comparison', fontsize=16, fontweight='bold')
    
    metrics_to_plot = ['accuracy', 'precision', 'recall', 'f1']
    metrics_labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    
    for idx, (metric, label) in enumerate(zip(metrics_to_plot, metrics_labels)):
        ax = axes[idx // 2, idx % 2]
        model_names = list(results.keys())
        values = [results[m][metric] for m in model_names]
        
        colors = ['#2ecc71' if m == best_model_name else '#3498db' for m in model_names]
        ax.bar(model_names, values, color=colors, alpha=0.7, edgecolor='black')
        ax.set_ylabel(label, fontsize=11)
        ax.set_ylim([0, 1.1])
        ax.grid(axis='y', alpha=0.3)
        ax.set_title(f'{label} by Model', fontsize=12, fontweight='bold')
        
        for i, v in enumerate(values):
            ax.text(i, v + 0.02, f'{v:.3f}', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/model_comparison.png', dpi=300)
    print(f"✓ Saved: {vis_dir}/model_comparison.png")
    plt.close()
    
    # 2. Confusion Matrix of Best Model
    best_result = results[best_model_name]
    cm = best_result['cm']
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
    plt.title(f'Confusion Matrix - {best_model_name}', fontsize=14, fontweight='bold')
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/confusion_matrix_best_model.png', dpi=300)
    print(f"✓ Saved: {vis_dir}/confusion_matrix_best_model.png")
    plt.close()
    
    # 3. High-Risk Recall Comparison (Most Important Metric)
    fig, ax = plt.subplots(figsize=(10, 6))
    model_names = list(results.keys())
    high_risk_recalls = [results[m]['high_risk_recall'] for m in model_names]
    
    colors = ['#2ecc71' if m == best_model_name else '#e74c3c' for m in model_names]
    bars = ax.bar(model_names, high_risk_recalls, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel('Recall Score', fontsize=12)
    ax.set_ylim([0, 1.1])
    ax.set_title('High-Risk Detection Recall (Safety Critical Metric)', 
                 fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    for i, (bar, val) in enumerate(zip(bars, high_risk_recalls)):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.02, f'{val:.3f}',
                ha='center', fontweight='bold', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/high_risk_recall_comparison.png', dpi=300)
    print(f"✓ Saved: {vis_dir}/high_risk_recall_comparison.png")
    plt.close()


def save_best_model(best_model_name, best_result, output_path='data/best_model.pkl'):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        pickle.dump(best_result['model'], f)
    print(f"✓ Saved best model: {output_path}")


def train_baseline_model(data_dir='data', vis_dir='visualizations'):
    print("\n" + "=" * 70)
    print("BASELINE RISK CLASSIFICATION MODEL")
    print("=" * 70)
    
    # Load and prepare data
    X_train, X_test, y_train, y_test, feature_names, label_encoder = load_and_prepare_data(data_dir)
    
    # Train models
    results = train_models(X_train, X_test, y_train, y_test, label_encoder)
    
    # Evaluate and select best model
    best_model_name, best_result = evaluate_and_compare(results, y_test, label_encoder)
    
    # Visualize results
    visualize_results(results, best_model_name, label_encoder, vis_dir)
    
    # Save best model
    save_best_model(best_model_name, best_result)
    
    print("\n" + "=" * 70)
    print("BASELINE MODEL TRAINING COMPLETE ✓")
    print("=" * 70)
    print(f"\n📊 Key Results:")
    print(f"  - Best Model: {best_model_name}")
    print(f"  - Test Accuracy: {best_result['accuracy']:.4f}")
    print(f"  - High-Risk Recall: {best_result['high_risk_recall']:.4f} (Priority Metric)")
    print(f"  - F1-Score: {best_result['f1']:.4f}")
    
    # Print detailed classification report
    print(f"\n📋 Detailed Classification Report ({best_model_name}):")
    print(classification_report(y_test, best_result['y_pred'], 
                              target_names=label_encoder.classes_))
    
    return {
        'best_model_name': best_model_name,
        'best_result': best_result,
        'label_encoder': label_encoder,
        'feature_names': feature_names
    }


if __name__ == '__main__':
    train_baseline_model()

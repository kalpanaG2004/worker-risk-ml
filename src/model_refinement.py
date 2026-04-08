import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pickle
from sklearn.model_selection import GridSearchCV, cross_val_score, cross_validate
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, auc
)


def load_model_and_data(data_dir='data', model_path='data/best_model.pkl'):
    X_train = pd.read_csv(f'{data_dir}/X_train.csv')
    X_test = pd.read_csv(f'{data_dir}/X_test.csv')
    y_train = pd.read_csv(f'{data_dir}/y_train.csv')['risk_label'].values
    y_test = pd.read_csv(f'{data_dir}/y_test.csv')['risk_label'].values
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    return X_train, X_test, y_train, y_test, model


def feature_importance_shap(model, X_train, X_test, feature_cols, vis_dir='visualizations'):
    print("\n" + "="*70)
    print("FEATURE IMPORTANCE ANALYSIS")
    print("="*70)
    
    feature_importance = model.feature_importances_
    
    importance_df = pd.DataFrame({
        'Feature': feature_cols,
        'Importance': feature_importance
    }).sort_values('Importance', ascending=False)
    
    print("\nFeature Importance Ranking:")
    print(importance_df.to_string(index=False))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(importance_df['Feature'], importance_df['Importance'], color='#3498db', edgecolor='black')
    ax.set_xlabel('Importance Score', fontsize=12)
    ax.set_title('Feature Importance (Random Forest)', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/feature_importance.png', dpi=300)
    print(f"Saved: {vis_dir}/feature_importance.png")
    plt.close()
    
    return importance_df


def hyperparameter_tuning(X_train, y_train, feature_cols):
    print("\n" + "="*70)
    print("HYPERPARAMETER TUNING (GridSearchCV)")
    print("="*70)
    
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
    }
    
    rf = RandomForestClassifier(random_state=42, n_jobs=-1)
    grid_search = GridSearchCV(rf, param_grid, cv=5, scoring='f1_weighted', n_jobs=-1, verbose=1)
    
    print("\nPerforming grid search (5-fold CV)...")
    grid_search.fit(X_train, y_train)
    
    print(f"\nBest Parameters: {grid_search.best_params_}")
    print(f"Best CV Score (F1): {grid_search.best_score_:.4f}")
    
    best_model = grid_search.best_estimator_
    
    results_df = pd.DataFrame(grid_search.cv_results_)
    results_df = results_df[['param_n_estimators', 'param_max_depth', 'param_min_samples_split',
                               'param_min_samples_leaf', 'mean_test_score', 'std_test_score']]
    results_df = results_df.sort_values('mean_test_score', ascending=False).head(10)
    
    print("\nTop 10 Parameter Combinations:")
    print(results_df.to_string(index=False))
    
    return best_model, grid_search.best_params_


def cross_validation_analysis(model, X_train, y_train, feature_cols):
    print("\n" + "="*70)
    print("CROSS-VALIDATION ANALYSIS (5-Fold)")
    print("="*70)
    
    scoring_metrics = {
        'accuracy': 'accuracy',
        'precision': 'precision_weighted',
        'recall': 'recall_weighted',
        'f1': 'f1_weighted'
    }
    
    cv_results = cross_validate(model, X_train, y_train, cv=5, scoring=scoring_metrics, n_jobs=-1)
    
    cv_summary = {}
    print("\nCross-Validation Results (5-Fold):")
    for metric, scores in cv_results.items():
        if metric.startswith('test_'):
            metric_name = metric.replace('test_', '')
            cv_summary[metric_name] = {
                'mean': scores.mean(),
                'std': scores.std(),
                'scores': scores
            }
            print(f"\n{metric_name.upper()}:")
            print(f"  Mean: {scores.mean():.4f} (+/- {scores.std():.4f})")
            print(f"  Fold Scores: {[f'{s:.4f}' for s in scores]}")
    
    return cv_summary


def roc_auc_analysis(model, X_test, y_test, vis_dir='visualizations'):
    print("\n" + "="*70)
    print("ROC-AUC ANALYSIS")
    print("="*70)
    
    y_pred_proba = model.predict_proba(X_test)
    
    n_classes = y_pred_proba.shape[1]
    fpr_dict = {}
    tpr_dict = {}
    roc_auc_dict = {}
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for i in range(n_classes):
        y_test_binary = (y_test == i).astype(int)
        fpr, tpr, _ = roc_curve(y_test_binary, y_pred_proba[:, i])
        roc_auc = auc(fpr, tpr)
        
        fpr_dict[i] = fpr
        tpr_dict[i] = tpr
        roc_auc_dict[i] = roc_auc
        
        ax.plot(fpr, tpr, lw=2, label=f'Class {i} (AUC = {roc_auc:.3f})')
    
    ax.plot([0, 1], [0, 1], 'k--', lw=2, label='Random Classifier')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title('ROC Curves - One-vs-Rest', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/roc_auc_curves.png', dpi=300)
    print(f"Saved: {vis_dir}/roc_auc_curves.png")
    plt.close()
    
    print("\nROC-AUC Scores:")
    for i, auc_score in roc_auc_dict.items():
        print(f"  Class {i}: {auc_score:.4f}")
    
    macro_auc = np.mean(list(roc_auc_dict.values()))
    print(f"  Macro Average: {macro_auc:.4f}")
    
    return roc_auc_dict


def threshold_optimization(model, X_test, y_test, target_class=1):
    print("\n" + "="*70)
    print("THRESHOLD OPTIMIZATION")
    print("="*70)
    
    y_pred_proba = model.predict_proba(X_test)[:, target_class]
    
    thresholds = np.arange(0.1, 1.0, 0.05)
    results = []
    
    for threshold in thresholds:
        y_pred_threshold = (y_pred_proba >= threshold).astype(int)
        y_test_binary = (y_test == target_class).astype(int)
        
        tn = np.sum((y_pred_threshold == 0) & (y_test_binary == 0))
        fp = np.sum((y_pred_threshold == 1) & (y_test_binary == 0))
        fn = np.sum((y_pred_threshold == 0) & (y_test_binary == 1))
        tp = np.sum((y_pred_threshold == 1) & (y_test_binary == 1))
        
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        results.append({
            'threshold': threshold,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        })
    
    results_df = pd.DataFrame(results)
    
    print("\nThreshold Optimization Results:")
    print(results_df.to_string(index=False))
    
    best_f1_idx = results_df['f1'].idxmax()
    best_threshold = results_df.loc[best_f1_idx, 'threshold']
    
    print(f"\nOptimal Threshold (max F1): {best_threshold:.2f}")
    print(f"  - Accuracy: {results_df.loc[best_f1_idx, 'accuracy']:.4f}")
    print(f"  - Precision: {results_df.loc[best_f1_idx, 'precision']:.4f}")
    print(f"  - Recall: {results_df.loc[best_f1_idx, 'recall']:.4f}")
    print(f"  - F1-Score: {results_df.loc[best_f1_idx, 'f1']:.4f}")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(results_df['threshold'], results_df['accuracy'], marker='o', label='Accuracy')
    ax.plot(results_df['threshold'], results_df['precision'], marker='s', label='Precision')
    ax.plot(results_df['threshold'], results_df['recall'], marker='^', label='Recall')
    ax.plot(results_df['threshold'], results_df['f1'], marker='d', label='F1-Score')
    ax.axvline(best_threshold, color='r', linestyle='--', label=f'Optimal Threshold ({best_threshold:.2f})')
    ax.set_xlabel('Probability Threshold', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Threshold Optimization', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('visualizations/threshold_optimization.png', dpi=300)
    print(f"Saved: visualizations/threshold_optimization.png")
    plt.close()
    
    return best_threshold, results_df


def save_refined_model(model, output_path='data/refined_model.pkl'):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Saved refined model: {output_path}")


def model_refinement_pipeline():
    print("\n" + "="*70)
    print("WEEK 2: MODEL REFINEMENT & OPTIMIZATION")
    print("="*70)
    
    X_train, X_test, y_train, y_test, baseline_model = load_model_and_data()
    feature_cols = X_train.columns.tolist()
    
    print(f"\nDataset Summary:")
    print(f"  - Training samples: {len(X_train)}")
    print(f"  - Testing samples: {len(X_test)}")
    print(f"  - Features: {len(feature_cols)}")
    
    importance_df = feature_importance_shap(baseline_model, X_train, X_test, feature_cols)
    
    refined_model, best_params = hyperparameter_tuning(X_train, y_train, feature_cols)
    
    cv_summary = cross_validation_analysis(refined_model, X_train, y_train, feature_cols)
    
    roc_auc_scores = roc_auc_analysis(refined_model, X_test, y_test)
    
    best_threshold, threshold_results = threshold_optimization(refined_model, X_test, y_test, target_class=1)
    
    save_refined_model(refined_model)
    
    print("\n" + "="*70)
    print("WEEK 2 REFINEMENT COMPLETE")
    print("="*70)
    
    y_pred = refined_model.predict(X_test)
    print(f"\nRefined Model Performance:")
    print(f"  - Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(f"  - Precision: {precision_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")
    print(f"  - Recall: {recall_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")
    print(f"  - F1-Score: {f1_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")
    
    return {
        'refined_model': refined_model,
        'feature_importance': importance_df,
        'best_params': best_params,
        'cv_summary': cv_summary,
        'roc_auc_scores': roc_auc_scores,
        'optimal_threshold': best_threshold
    }


if __name__ == '__main__':
    model_refinement_pipeline()

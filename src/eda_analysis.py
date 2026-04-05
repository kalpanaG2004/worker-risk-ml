import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def load_datasets(data_dir='data'):
    workers = pd.read_csv(f'{data_dir}/workers.csv')
    tasks = pd.read_csv(f'{data_dir}/tasks.csv')
    assignments = pd.read_csv(f'{data_dir}/assignments.csv')
    return workers, tasks, assignments


def summarize_datasets(workers, tasks, assignments):
    print("=" * 70)
    print("DATASET SUMMARIES")
    print("=" * 70)
    
    print(f"\n📊 WORKERS DATASET ({len(workers)} records)")
    print("-" * 70)
    print(workers.describe())
    print("\nData Types:")
    print(workers.dtypes)
    print(f"\nMissing Values:\n{workers.isnull().sum()}")
    
    print(f"\n📊 TASKS DATASET ({len(tasks)} records)")
    print("-" * 70)
    print(tasks.describe())
    print("\nData Types:")
    print(tasks.dtypes)
    print(f"\nMissing Values:\n{tasks.isnull().sum()}")
    print(f"\nTask Type Distribution:\n{tasks['task_type'].value_counts()}")
    print(f"\nRisk Label Distribution:\n{tasks['risk_label'].value_counts()}")
    
    print(f"\n📊 ASSIGNMENTS DATASET ({len(assignments)} records)")
    print("-" * 70)
    print(assignments.describe())
    print("\nData Types:")
    print(assignments.dtypes)
    print(f"\nMissing Values:\n{assignments.isnull().sum()}")
    print(f"\nActual Risk Distribution:\n{assignments['actual_risk'].value_counts()}")


def create_visualizations(workers, tasks, assignments, vis_dir='visualizations'):
    Path(vis_dir).mkdir(parents=True, exist_ok=True)
    sns.set_style("whitegrid")
    
    # 1. Risk Distribution (from Tasks)
    plt.figure(figsize=(10, 6))
    risk_counts = tasks['risk_label'].value_counts()
    colors = {'Low': '#2ecc71', 'Medium': '#f39c12', 'High': '#e74c3c'}
    plt.bar(risk_counts.index, risk_counts.values, 
            color=[colors.get(x, '#95a5a6') for x in risk_counts.index])
    plt.title('Tasks Risk Distribution', fontsize=14, fontweight='bold')
    plt.xlabel('Risk Level', fontsize=12)
    plt.ylabel('Number of Tasks', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    for i, v in enumerate(risk_counts.values):
        plt.text(i, v + 2, str(v), ha='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/risk_distribution.png', dpi=300)
    print(f"✓ Saved: {vis_dir}/risk_distribution.png")
    plt.close()
    
    # 2. Skill Score Distribution
    plt.figure(figsize=(10, 6))
    plt.hist(workers['skill_score'], bins=30, color='#3498db', alpha=0.7, edgecolor='black')
    plt.title('Workers Skill Score Distribution', fontsize=14, fontweight='bold')
    plt.xlabel('Skill Score (0-100)', fontsize=12)
    plt.ylabel('Number of Workers', fontsize=12)
    plt.axvline(workers['skill_score'].mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Mean: {workers["skill_score"].mean():.2f}')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/skill_distribution.png', dpi=300)
    print(f"✓ Saved: {vis_dir}/skill_distribution.png")
    plt.close()
    
    # 3. Environment Risk Distribution
    plt.figure(figsize=(10, 6))
    env_dist = tasks['environment_risk'].value_counts().sort_index()
    plt.bar(env_dist.index, env_dist.values, color=['#2ecc71', '#f39c12', '#e74c3c'], 
            alpha=0.7, edgecolor='black')
    plt.title('Tasks Environment Risk Level Distribution', fontsize=14, fontweight='bold')
    plt.xlabel('Environment Risk Level', fontsize=12)
    plt.ylabel('Number of Tasks', fontsize=12)
    plt.xticks([1, 2, 3])
    for i, v in enumerate(env_dist.values):
        plt.text(env_dist.index[i], v + 2, str(v), ha='center', fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/environment_risk_distribution.png', dpi=300)
    print(f"✓ Saved: {vis_dir}/environment_risk_distribution.png")
    plt.close()
    
    # 4. Experience vs Skill Score
    plt.figure(figsize=(10, 6))
    plt.scatter(workers['experience_years'], workers['skill_score'], 
                alpha=0.5, s=50, color='#9b59b6')
    plt.title('Experience Years vs Skill Score', fontsize=14, fontweight='bold')
    plt.xlabel('Experience (Years)', fontsize=12)
    plt.ylabel('Skill Score', fontsize=12)
    # Add trend line
    z = np.polyfit(workers['experience_years'], workers['skill_score'], 1)
    p = np.poly1d(z)
    plt.plot(workers['experience_years'].sort_values(), 
             p(workers['experience_years'].sort_values()), 
             "r--", linewidth=2, label='Trend')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/experience_vs_skill.png', dpi=300)
    print(f"✓ Saved: {vis_dir}/experience_vs_skill.png")
    plt.close()
    
    # 5. Actual Risk Distribution in Assignments
    plt.figure(figsize=(10, 6))
    actual_risk_counts = assignments['actual_risk'].value_counts()
    plt.bar(actual_risk_counts.index, actual_risk_counts.values,
            color=[colors.get(x, '#95a5a6') for x in actual_risk_counts.index],
            alpha=0.7, edgecolor='black')
    plt.title('Actual Risk Distribution (Worker-Task Assignments)', fontsize=14, fontweight='bold')
    plt.xlabel('Risk Level', fontsize=12)
    plt.ylabel('Number of Assignments', fontsize=12)
    for i, v in enumerate(actual_risk_counts.values):
        plt.text(i, v + 20, str(v), ha='center', fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/actual_risk_distribution.png', dpi=300)
    print(f"✓ Saved: {vis_dir}/actual_risk_distribution.png")
    plt.close()
    
    # 6. Certification Level Distribution
    plt.figure(figsize=(10, 6))
    cert_labels = {0: 'None', 1: 'Basic', 2: 'Advanced'}
    cert_dist = workers['certification_level'].value_counts().sort_index()
    plt.bar([cert_labels[i] for i in cert_dist.index], cert_dist.values,
            color=['#e74c3c', '#f39c12', '#2ecc71'], alpha=0.7, edgecolor='black')
    plt.title('Workers Certification Level Distribution', fontsize=14, fontweight='bold')
    plt.xlabel('Certification Level', fontsize=12)
    plt.ylabel('Number of Workers', fontsize=12)
    for i, v in enumerate(cert_dist.values):
        plt.text(i, v + 10, str(v), ha='center', fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/certification_distribution.png', dpi=300)
    print(f"✓ Saved: {vis_dir}/certification_distribution.png")
    plt.close()


def perform_eda(workers, tasks, assignments):
    print("\n" + "=" * 70)
    print("EXPLORATORY DATA ANALYSIS")
    print("=" * 70)
    
    summarize_datasets(workers, tasks, assignments)
    
    print("\n" + "=" * 70)
    print("CREATING VISUALIZATIONS")
    print("=" * 70)
    create_visualizations(workers, tasks, assignments)
    
    # Additional insights
    print("\n" + "=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    
    avg_skill = workers['skill_score'].mean()
    print(f"\n✓ Average worker skill score: {avg_skill:.2f}/100")
    print(f"✓ Workers with incidents: {(workers['past_incident_count'] > 0).sum()} "
          f"({100 * (workers['past_incident_count'] > 0).sum() / len(workers):.1f}%)")
    print(f"✓ Tasks requiring supervision: {tasks['supervision_required'].sum()} "
          f"({100 * tasks['supervision_required'].sum() / len(tasks):.1f}%)")
    print(f"✓ High-risk tasks: {(tasks['risk_label'] == 'High').sum()} "
          f"({100 * (tasks['risk_label'] == 'High').sum() / len(tasks):.1f}%)")
    
    # Risk distribution in assignments
    risk_dist = assignments['actual_risk'].value_counts()
    print(f"\n✓ Assignments by risk:")
    for risk_level in ['Low', 'Medium', 'High']:
        count = risk_dist.get(risk_level, 0)
        pct = 100 * count / len(assignments)
        print(f"  - {risk_level}: {count} ({pct:.1f}%)")


if __name__ == '__main__':
    workers, tasks, assignments = load_datasets()
    perform_eda(workers, tasks, assignments)

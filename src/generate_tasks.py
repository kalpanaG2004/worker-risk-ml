import pandas as pd
import numpy as np
from pathlib import Path


def generate_tasks(n_tasks=200, random_state=42):
    np.random.seed(random_state)
    
    task_types = ['Mechanical', 'Electrical', 'Chemical', 'Assembly']
    risk_labels = ['Low', 'Medium', 'High']
    
    tasks_data = {
        'task_id': [f'T{i:04d}' for i in range(1, n_tasks + 1)],
        'task_type': np.random.choice(task_types, size=n_tasks),
        'required_skill_level': np.random.randint(1, 4, size=n_tasks),
        'environment_risk': np.random.randint(1, 4, size=n_tasks),
        'supervision_required': np.random.randint(0, 2, size=n_tasks),
    }
    
    df = pd.DataFrame(tasks_data)
    
    # Assign risk labels based on environment_risk, required_skill_level, and supervision
    # Higher environment risk, higher required skill level, or supervision needed → higher risk
    risk_score = (
        df['environment_risk'] * 0.4 + 
        df['required_skill_level'] * 0.3 +
        df['supervision_required'] * 0.2 + 
        np.random.normal(0, 0.3, size=n_tasks)
    )
    
    # Chemical tasks tend to be higher risk
    chemical_boost = (df['task_type'] == 'Chemical').astype(int) * 0.5
    risk_score += chemical_boost
    
    # Assign labels based on risk score
    df['risk_label'] = pd.cut(
        risk_score,
        bins=[-np.inf, 1.8, 2.8, np.inf],
        labels=['Low', 'Medium', 'High']
    )
    
    return df

def save_tasks(df, output_path='data/tasks.csv'):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✓ Saved tasks dataset: {output_path} ({len(df)} records)")

if __name__ == '__main__':
    tasks = generate_tasks(n_tasks=200)
    save_tasks(tasks)
    print(f"\nTasks Dataset Summary:\n{tasks.describe()}")
    print(f"\nRisk Label Distribution:\n{tasks['risk_label'].value_counts()}")

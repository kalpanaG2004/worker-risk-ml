import pandas as pd
import numpy as np
from pathlib import Path


def generate_assignments(workers_df, tasks_df, n_assignments=1500, random_state=42):
    np.random.seed(random_state)
    
    # Randomly assign workers to tasks
    worker_ids = np.random.choice(workers_df['worker_id'], size=n_assignments)
    task_ids = np.random.choice(tasks_df['task_id'], size=n_assignments)
    
    assignments_data = {
        'assignment_id': [f'A{i:06d}' for i in range(1, n_assignments + 1)],
        'worker_id': worker_ids,
        'task_id': task_ids,
    }
    
    df = pd.DataFrame(assignments_data)
    
    # Merge with worker and task data
    df = df.merge(workers_df[['worker_id', 'skill_score', 'past_incident_count']], 
                  on='worker_id', how='left')
    df = df.merge(tasks_df[['task_id', 'required_skill_level', 'environment_risk', 'risk_label']], 
                  on='task_id', how='left')
    
    # Calculate skill mismatch
    # Convert required_skill_level (1-3) to estimated required_skill_score (35, 65, 95)
    required_skill_score = (df['required_skill_level'] - 1) * 30 + 35
    df['skill_mismatch'] = abs(df['skill_score'] - required_skill_score)
    
    # Determine actual risk based on:
    # 1. Task's inherent risk
    # 2. Skill mismatch
    # 3. Worker's incident history
    
    risk_score = df['environment_risk'].copy()
    
    # Add penalty for skill mismatch
    skill_penalty = (df['skill_mismatch'] / 100) * 1.0  # Up to 1 point penalty
    risk_score += skill_penalty
    
    # Add penalty for past incidents
    incident_penalty = df['past_incident_count'] * 0.3
    risk_score += incident_penalty
    
    # Assign actual risk labels
    df['actual_risk'] = pd.cut(
        risk_score,
        bins=[-np.inf, 1.8, 2.8, np.inf],
        labels=['Low', 'Medium', 'High']
    )
    
    # Clean up temporary columns
    df = df[['assignment_id', 'worker_id', 'task_id', 'skill_mismatch', 'actual_risk']]
    
    return df

def save_assignments(df, output_path='data/assignments.csv'):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✓ Saved assignments dataset: {output_path} ({len(df)} records)")


if __name__ == '__main__':
    from generate_workers import generate_workers
    from generate_tasks import generate_tasks
    
    workers = generate_workers(n_workers=500)
    tasks = generate_tasks(n_tasks=200)
    assignments = generate_assignments(workers, tasks, n_assignments=1500)
    
    save_assignments(assignments)
    print(f"\nAssignments Dataset Summary:\n{assignments.describe()}")
    print(f"\nActual Risk Distribution:\n{assignments['actual_risk'].value_counts()}")

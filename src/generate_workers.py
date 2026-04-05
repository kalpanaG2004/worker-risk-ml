import pandas as pd
import numpy as np
from pathlib import Path


def generate_workers(n_workers=500, random_state=42):
    np.random.seed(random_state)
    
    workers_data = {
        'worker_id': [f'W{i:05d}' for i in range(1, n_workers + 1)],
        'experience_years': np.random.randint(0, 31, size=n_workers),
        'certification_level': np.random.choice([0, 1, 2], size=n_workers, p=[0.3, 0.45, 0.25]),
        'training_completed': np.random.randint(0, 2, size=n_workers),
        'past_incident_count': np.random.poisson(lam=0.8, size=n_workers),
        'avg_incident_severity': np.random.uniform(1, 5, size=n_workers),
        'skill_score': np.random.uniform(0, 100, size=n_workers),
    }
    
    df = pd.DataFrame(workers_data)
    
    # Enforce realistic relationship: more experience → higher skill score
    experience_influence = (df['experience_years'] / 30) * 40  # Up to 40 points
    cert_influence = df['certification_level'] * 15  # Up to 30 points
    training_influence = df['training_completed'] * 10  # Up to 10 points
    
    df['skill_score'] = (
        experience_influence + cert_influence + training_influence + 
        np.random.normal(0, 5, size=n_workers)
    ).clip(0, 100)
    
    # Enforce: more incidents → lower skill score
    df['skill_score'] = (df['skill_score'] - (df['past_incident_count'] * 3)).clip(0, 100)
    
    # Round severity to 2 decimals
    df['avg_incident_severity'] = df['avg_incident_severity'].round(2)
    
    return df


def save_workers(df, output_path='data/workers.csv'):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✓ Saved workers dataset: {output_path} ({len(df)} records)")


if __name__ == '__main__':
    workers = generate_workers(n_workers=500)
    save_workers(workers)
    print(f"\nWorkers Dataset Summary:\n{workers.describe()}")

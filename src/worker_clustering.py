import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, silhouette_samples, davies_bouldin_score, calinski_harabasz_score
from scipy.cluster.hierarchy import dendrogram, linkage
import pickle
import warnings
warnings.filterwarnings('ignore')


def load_worker_data_for_clustering(data_dir='data'):
    print("\nLoading worker data for clustering...")
    
    workers = pd.read_csv(f'{data_dir}/workers.csv')
    assignments = pd.read_csv(f'{data_dir}/assignments.csv')
    tasks = pd.read_csv(f'{data_dir}/tasks.csv')
    
    # Encode actual_risk to numeric values
    risk_encoding = {'Low': 0, 'Medium': 1, 'High': 2}
    assignments['actual_risk_numeric'] = assignments['actual_risk'].map(risk_encoding)
    
    # Aggregate assignment statistics per worker
    assignment_stats = assignments.groupby('worker_id').agg({
        'skill_mismatch': ['mean', 'std', 'min', 'max'],
        'actual_risk_numeric': ['mean', 'count']
    }).reset_index()
    
    assignment_stats.columns = ['worker_id', 'skill_mismatch_mean', 'skill_mismatch_std',
                                'skill_mismatch_min', 'skill_mismatch_max',
                                'avg_assignment_risk', 'n_assignments']
    
    # Fill NaN std with 0 (workers with single assignment)
    assignment_stats['skill_mismatch_std'] = assignment_stats['skill_mismatch_std'].fillna(0)
    
    # Merge worker features with assignment statistics
    worker_clustering_data = workers.merge(assignment_stats, on='worker_id', how='left')
    
    print(f"✓ Loaded {len(worker_clustering_data)} workers")
    print(f"✓ Features: {worker_clustering_data.columns.tolist()}")
    
    return worker_clustering_data


def prepare_clustering_features(worker_data):
    print("\nPreparing features for clustering...")
    
    clustering_features = [
        'experience_years',           # Experience level
        'certification_level',         # Professional qualification
        'skill_score',                 # Computed skill capability
        'training_completed',          # Training status (binary)
        'past_incident_count',         # Safety history
        'skill_mismatch_mean',        # Historical skill-task alignment
        'avg_assignment_risk',        # Average risk in assignments
        'n_assignments'               # Workload/engagement level
    ]
    
    # Extract clustering features
    X_clustering = worker_data[clustering_features].copy()
    
    # Handle any missing values
    X_clustering = X_clustering.fillna(X_clustering.mean())
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clustering)
    
    print(f"✓ Extracted {len(clustering_features)} features")
    print(f"✓ Scaled {X_scaled.shape[0]} records")
    
    return X_scaled, clustering_features, scaler


def find_optimal_clusters_kmeans(X_scaled, max_k=10, random_state=42, vis_dir='visualizations'):
    print("\n" + "="*70)
    print("DETERMINING OPTIMAL CLUSTERS - K-MEANS ANALYSIS")
    print("="*70)
    
    inertias = []
    silhouette_scores = []
    davies_bouldin_scores = []
    calinski_harabasz_scores = []
    K_range = range(2, max_k + 1)
    
    for k in K_range:
        print(f"  Evaluating k={k}...", end='\r')
        
        kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(X_scaled, cluster_labels))
        davies_bouldin_scores.append(davies_bouldin_score(X_scaled, cluster_labels))
        calinski_harabasz_scores.append(calinski_harabasz_score(X_scaled, cluster_labels))
    
    print("  " + " " * 50)  # Clear line
    
    # Find optimal k based on silhouette score (highest is best)
    optimal_k_silhouette = K_range[np.argmax(silhouette_scores)]
    
    # Find elbow point (steepest decline in inertia)
    inertia_diffs = np.diff(inertias)
    second_diff = np.diff(inertia_diffs)
    optimal_k_elbow = K_range[np.argmax(second_diff) + 1]
    
    print(f"\n✓ Optimal clusters (Silhouette): {optimal_k_silhouette} (score: {max(silhouette_scores):.4f})")
    print(f"✓ Optimal clusters (Elbow): {optimal_k_elbow}")
    
    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Elbow curve
    axes[0, 0].plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
    axes[0, 0].axvline(optimal_k_elbow, color='r', linestyle='--', label=f'Elbow: k={optimal_k_elbow}')
    axes[0, 0].set_xlabel('Number of Clusters (k)')
    axes[0, 0].set_ylabel('Inertia')
    axes[0, 0].set_title('Elbow Method')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)
    
    # Silhouette scores
    axes[0, 1].plot(K_range, silhouette_scores, 'go-', linewidth=2, markersize=8)
    axes[0, 1].axvline(optimal_k_silhouette, color='r', linestyle='--', label=f'Best: k={optimal_k_silhouette}')
    axes[0, 1].set_xlabel('Number of Clusters (k)')
    axes[0, 1].set_ylabel('Silhouette Score')
    axes[0, 1].set_title('Silhouette Analysis')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)
    
    # Davies-Bouldin Index (lower is better)
    axes[1, 0].plot(K_range, davies_bouldin_scores, 'mo-', linewidth=2, markersize=8)
    axes[1, 0].set_xlabel('Number of Clusters (k)')
    axes[1, 0].set_ylabel('Davies-Bouldin Index')
    axes[1, 0].set_title('Davies-Bouldin Index (Lower is Better)')
    axes[1, 0].grid(alpha=0.3)
    
    # Calinski-Harabasz Score (higher is better)
    axes[1, 1].plot(K_range, calinski_harabasz_scores, 'co-', linewidth=2, markersize=8)
    axes[1, 1].set_xlabel('Number of Clusters (k)')
    axes[1, 1].set_ylabel('Calinski-Harabasz Score')
    axes[1, 1].set_title('Calinski-Harabasz Score (Higher is Better)')
    axes[1, 1].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/kmeans_optimization_metrics.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved: {vis_dir}/kmeans_optimization_metrics.png")
    plt.close()
    
    # Use silhouette score as primary metric
    optimal_k = optimal_k_silhouette
    
    return optimal_k, silhouette_scores, inertias


def perform_kmeans_clustering(X_scaled, optimal_k, random_state=42):
    print(f"\nPerforming K-Means with k={optimal_k}...")
    
    kmeans = KMeans(n_clusters=optimal_k, random_state=random_state, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    silhouette_avg = silhouette_score(X_scaled, cluster_labels)
    print(f"✓ Silhouette Score: {silhouette_avg:.4f}")
    
    return kmeans, cluster_labels


def perform_hierarchical_clustering(X_scaled, optimal_k, vis_dir='visualizations'):
    print(f"\nPerforming Hierarchical Clustering with k={optimal_k}...")
    
    # Compute linkage matrix
    Z = linkage(X_scaled, method='ward')
    
    # Cut dendrogram to get cluster labels
    hierarchical = AgglomerativeClustering(n_clusters=optimal_k, linkage='ward')
    cluster_labels = hierarchical.fit_predict(X_scaled)
    
    silhouette_avg = silhouette_score(X_scaled, cluster_labels)
    print(f"✓ Silhouette Score: {silhouette_avg:.4f}")
    
    # Create dendrogram (on sample for visualization clarity)
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Use subset of data for dendrogram if dataset is large
    sample_size = min(50, X_scaled.shape[0])
    if X_scaled.shape[0] > sample_size:
        sample_indices = np.random.choice(X_scaled.shape[0], sample_size, replace=False)
        Z_sample = linkage(X_scaled[sample_indices], method='ward')
    else:
        Z_sample = Z
    
    dendrogram(Z_sample, ax=ax, truncate_mode=None)
    ax.set_title(f'Hierarchical Clustering Dendrogram (Ward Linkage, k={optimal_k})', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Worker Index')
    ax.set_ylabel('Distance')
    ax.axhline(y=ax.get_ylim()[1] * 0.7, color='r', linestyle='--', label='Cluster Cutoff')
    ax.legend()
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/hierarchical_dendrogram.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {vis_dir}/hierarchical_dendrogram.png")
    plt.close()
    
    return hierarchical, cluster_labels


def analyze_cluster_profiles(worker_data, X_scaled, kmeans_labels, hierarchical_labels, 
                            clustering_features, vis_dir='visualizations'):
    print("\n" + "="*70)
    print("CLUSTER PROFILING AND ANALYSIS")
    print("="*70)
    
    # Add cluster labels to worker data
    analysis_df = worker_data.copy()
    analysis_df['kmeans_cluster'] = kmeans_labels
    analysis_df['hierarchical_cluster'] = hierarchical_labels
    
    # Compare K-Means clusters (primary analysis)
    print("\n" + "-"*70)
    print("K-MEANS CLUSTER PROFILES")
    print("-"*70)
    
    num_clusters = len(np.unique(kmeans_labels))
    cluster_profiles = []
    
    for cluster_id in range(num_clusters):
        cluster_mask = kmeans_labels == cluster_id
        cluster_data = analysis_df[cluster_mask]
        
        profile = {
            'Cluster': cluster_id,
            'Size': len(cluster_data),
            'Avg_Experience': cluster_data['experience_years'].mean(),
            'Avg_Skill_Score': cluster_data['skill_score'].mean(),
            'Certified_%': (cluster_data['certification_level'] > 0).sum() / len(cluster_data) * 100,
            'Training_Completed_%': cluster_data['training_completed'].mean() * 100,
            'Avg_Incidents': cluster_data['past_incident_count'].mean(),
            'Avg_Skill_Mismatch': cluster_data['skill_mismatch_mean'].mean(),
            'Avg_Assignment_Risk': cluster_data['avg_assignment_risk'].mean()
        }
        
        cluster_profiles.append(profile)
        
        print(f"\nCluster {cluster_id}:")
        print(f"  Size: {profile['Size']} workers ({profile['Size']/len(analysis_df)*100:.1f}%)")
        print(f"  Avg Experience: {profile['Avg_Experience']:.2f} years")
        print(f"  Avg Skill Score: {profile['Avg_Skill_Score']:.2f}/100")
        print(f"  Certified: {profile['Certified_%']:.1f}%")
        print(f"  Training Completed: {profile['Training_Completed_%']:.1f}%")
        print(f"  Avg Past Incidents: {profile['Avg_Incidents']:.2f}")
        print(f"  Avg Skill Mismatch: {profile['Avg_Skill_Mismatch']:.3f}")
        print(f"  Avg Assignment Risk: {profile['Avg_Assignment_Risk']:.3f}")
    
    profiles_df = pd.DataFrame(cluster_profiles)
    
    # Characterize clusters
    print("\n" + "-"*70)
    print("CLUSTER CHARACTERIZATION")
    print("-"*70)
    
    characterizations = []
    for idx, profile in enumerate(profiles_df.itertuples()):
        exp = profile.Avg_Experience
        skill = profile.Avg_Skill_Score
        incidents = profile.Avg_Incidents
        mismatch = profile.Avg_Skill_Mismatch
        
        if exp > 10 and skill > 75 and incidents < 1:
            label = "VETERAN EXPERTS - Highly experienced, low risk"
        elif exp > 5 and skill > 60 and incidents < 2:
            label = "COMPETENT PROFESSIONALS - Solid experience, managed risk"
        elif exp < 5 and mismatch > 0.5:
            label = "DEVELOPING WORKERS - Newer staff, higher mismatch"
        elif incidents > 2:
            label = "HIGH-RISK WORKERS - Safety concerns, incident history"
        elif exp < 2:
            label = "TRAINEES - Entry-level, requires supervision"
        else:
            label = "STANDARD WORKFORCE - Mid-level experience and skill"
        
        characterizations.append(label)
        print(f"Cluster {idx}: {label}")
    
    profiles_df['Characterization'] = characterizations
    
    # Create cluster visualization
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    
    # Experience by cluster
    axes[0, 0].bar(profiles_df['Cluster'], profiles_df['Avg_Experience'], color='#3498db', edgecolor='black')
    axes[0, 0].set_ylabel('Years')
    axes[0, 0].set_title('Average Experience by Cluster')
    axes[0, 0].grid(axis='y', alpha=0.3)
    
    # Skill score by cluster
    axes[0, 1].bar(profiles_df['Cluster'], profiles_df['Avg_Skill_Score'], color='#2ecc71', edgecolor='black')
    axes[0, 1].set_ylabel('Score (0-100)')
    axes[0, 1].set_title('Average Skill Score by Cluster')
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # Certification by cluster
    axes[0, 2].bar(profiles_df['Cluster'], profiles_df['Certified_%'], color='#e74c3c', edgecolor='black')
    axes[0, 2].set_ylabel('Percentage (%)')
    axes[0, 2].set_title('Certified Workers by Cluster')
    axes[0, 2].grid(axis='y', alpha=0.3)
    
    # Training by cluster
    axes[1, 0].bar(profiles_df['Cluster'], profiles_df['Training_Completed_%'], color='#f39c12', edgecolor='black')
    axes[1, 0].set_ylabel('Percentage (%)')
    axes[1, 0].set_title('Training Completion by Cluster')
    axes[1, 0].grid(axis='y', alpha=0.3)
    
    # Past incidents by cluster
    axes[1, 1].bar(profiles_df['Cluster'], profiles_df['Avg_Incidents'], color='#9b59b6', edgecolor='black')
    axes[1, 1].set_ylabel('Count')
    axes[1, 1].set_title('Average Past Incidents by Cluster')
    axes[1, 1].grid(axis='y', alpha=0.3)
    
    # Cluster size
    axes[1, 2].pie(profiles_df['Size'], labels=[f"C{c}" for c in profiles_df['Cluster']], 
                   autopct='%1.1f%%', startangle=90)
    axes[1, 2].set_title('Cluster Distribution')
    
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/cluster_profiles.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved: {vis_dir}/cluster_profiles.png")
    plt.close()
    
    # Save cluster assignments
    analysis_df[['worker_id', 'kmeans_cluster', 'hierarchical_cluster']].to_csv(
        'data/worker_clusters.csv', index=False
    )
    print(f"✓ Saved cluster assignments: data/worker_clusters.csv")
    
    return analysis_df, profiles_df


def visualize_cluster_silhouettes(X_scaled, kmeans_labels, optimal_k, vis_dir='visualizations'):
    print("\nGenerating silhouette analysis visualization...")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    y_lower = 10
    silhouette_vals = silhouette_samples(X_scaled, kmeans_labels)
    
    for i in range(optimal_k):
        cluster_silhouette_vals = silhouette_vals[kmeans_labels == i]
        cluster_silhouette_vals.sort()
        
        size_cluster_i = cluster_silhouette_vals.shape[0]
        y_upper = y_lower + size_cluster_i
        
        color = plt.cm.nipy_spectral(float(i) / optimal_k)
        ax.fill_betweenx(np.arange(y_lower, y_upper),
                         0, cluster_silhouette_vals,
                         facecolor=color, edgecolor=color, alpha=0.7)
        
        ax.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))
        y_lower = y_upper + 10
    
    ax.set_title(f'Silhouette Plot for {optimal_k} Clusters', fontsize=14, fontweight='bold')
    ax.set_xlabel('Silhouette Coefficient')
    ax.set_ylabel('Cluster Label')
    ax.axvline(x=silhouette_vals.mean(), color='red', linestyle='--', label='Average Score')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{vis_dir}/silhouette_analysis.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {vis_dir}/silhouette_analysis.png")
    plt.close()


def save_clustering_models(kmeans, hierarchical, scaler, clustering_features):
    print("\nSaving clustering models...")
    
    with open('data/kmeans_model.pkl', 'wb') as f:
        pickle.dump({'kmeans': kmeans, 'scaler': scaler, 'features': clustering_features}, f)
    print("✓ Saved: data/kmeans_model.pkl")
    
    with open('data/hierarchical_model.pkl', 'wb') as f:
        pickle.dump({'hierarchical': hierarchical, 'scaler': scaler, 'features': clustering_features}, f)
    print("✓ Saved: data/hierarchical_model.pkl")


def worker_clustering_pipeline(data_dir='data', vis_dir='visualizations'):
    print("\n" + "="*70)
    print("WEEK 3: WORKER CLUSTERING ANALYSIS")
    print("="*70)
    
    # Ensure visualization directory exists
    Path(vis_dir).mkdir(parents=True, exist_ok=True)
    
    # Load and prepare data
    worker_data = load_worker_data_for_clustering(data_dir)
    X_scaled, clustering_features, scaler = prepare_clustering_features(worker_data)
    
    # Find optimal clusters
    optimal_k, silhouette_scores, inertias = find_optimal_clusters_kmeans(X_scaled, vis_dir=vis_dir)
    
    # Perform clustering
    kmeans, kmeans_labels = perform_kmeans_clustering(X_scaled, optimal_k)
    hierarchical, hierarchical_labels = perform_hierarchical_clustering(X_scaled, optimal_k, vis_dir)
    
    # Visualize silhouettes
    visualize_cluster_silhouettes(X_scaled, kmeans_labels, optimal_k, vis_dir)
    
    # Analyze profiles
    analysis_df, profiles_df = analyze_cluster_profiles(
        worker_data, X_scaled, kmeans_labels, hierarchical_labels, clustering_features, vis_dir
    )
    
    # Save models
    save_clustering_models(kmeans, hierarchical, scaler, clustering_features)
    
    # Save profile summary
    profiles_df.to_csv('data/cluster_profiles.csv', index=False)
    print("✓ Saved: data/cluster_profiles.csv")
    
    print("\n" + "="*70)
    print("Week 3 Clustering Analysis Complete")
    print("="*70)
    
    return {
        'optimal_k': optimal_k,
        'kmeans': kmeans,
        'hierarchical': hierarchical,
        'kmeans_labels': kmeans_labels,
        'hierarchical_labels': hierarchical_labels,
        'profiles': profiles_df,
        'analysis_df': analysis_df
    }


if __name__ == "__main__":
    results = worker_clustering_pipeline()

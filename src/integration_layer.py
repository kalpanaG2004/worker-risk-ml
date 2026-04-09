"""
Integration Layer - Week 6
Combines ML model outputs, worker clustering, and recommendations into unified interface.
Provides confidence scoring and integration metrics.
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class IntegrationLayer:
    """
    Unified interface combining all system components:
    - ML risk prediction model
    - Worker clustering
    - Recommendation engine
    - Confidence scoring
    """
    
    def __init__(self, data_dir='data', model_dir='data'):
        """Initialize integration layer with all trained models"""
        
        print("Initializing Integration Layer...")
        
        self.data_dir = data_dir
        self.model_dir = model_dir
        
        # Load all components
        self._load_models()
        self._load_data()
        self._load_recommendations()
        
        print("✓ Integration Layer ready")
    
    def _load_models(self):
        """Load all trained models"""
        
        # Load ML risk prediction model
        with open(f'{self.model_dir}/best_model.pkl', 'rb') as f:
            self.risk_model = pickle.load(f)
        print("  ✓ Risk prediction model loaded")
        
        # Load clustering model
        with open(f'{self.model_dir}/kmeans_model.pkl', 'rb') as f:
            cluster_data = pickle.load(f)
            self.kmeans = cluster_data['kmeans']
            self.clustering_scaler = cluster_data['scaler']
            self.clustering_features = cluster_data['features']
        print("  ✓ Clustering model loaded")
        
        # Load recommendation engine
        from recommendation_engine import DecisionEngine
        self.decision_engine = DecisionEngine()
        print("  ✓ Decision engine loaded")
    
    def _load_data(self):
        """Load datasets"""
        
        self.workers = pd.read_csv(f'{self.data_dir}/workers.csv')
        self.tasks = pd.read_csv(f'{self.data_dir}/tasks.csv')
        self.assignments = pd.read_csv(f'{self.data_dir}/assignments.csv')
        self.worker_clusters = pd.read_csv(f'{self.data_dir}/worker_clusters.csv')
        self.cluster_profiles = pd.read_csv(f'{self.data_dir}/cluster_profiles.csv')
        
        print("  ✓ Data loaded")
    
    def _load_recommendations(self):
        """Load pre-generated recommendations"""
        
        self.recommendations = pd.read_csv(f'{self.data_dir}/worker_recommendations.csv')
        print("  ✓ Recommendations loaded")
    
    def get_worker_profile(self, worker_id: str) -> Dict:
        """
        Get complete worker profile including cluster, risk, and recommendations.
        
        Args:
            worker_id: Worker identifier
        
        Returns:
            Dictionary with complete worker information
        """
        
        worker = self.workers[self.workers['worker_id'] == worker_id]
        if worker.empty:
            return {'error': f'Worker {worker_id} not found'}
        
        worker_data = worker.iloc[0].to_dict()
        
        # Get cluster assignment
        cluster_info = self.worker_clusters[self.worker_clusters['worker_id'] == worker_id]
        if not cluster_info.empty:
            worker_data['kmeans_cluster'] = int(cluster_info.iloc[0]['kmeans_cluster'])
            worker_data['hierarchical_cluster'] = int(cluster_info.iloc[0]['hierarchical_cluster'])
        
        # Get recommendations
        rec_info = self.recommendations[self.recommendations['worker_id'] == worker_id]
        if not rec_info.empty:
            rec = rec_info.iloc[0]
            worker_data['predicted_risk'] = rec['predicted_risk']
            worker_data['priority'] = rec['priority']
            worker_data['confidence'] = rec['confidence']
            worker_data['training_priority'] = rec['training_priority']
        
        # Get assignment statistics
        worker_assignments = self.assignments[self.assignments['worker_id'] == worker_id]
        if not worker_assignments.empty:
            worker_data['n_assignments'] = len(worker_assignments)
            worker_data['avg_skill_mismatch'] = worker_assignments['skill_mismatch'].mean()
            high_risk_count = (worker_assignments['actual_risk'] == 'High').sum()
            worker_data['high_risk_assignments'] = high_risk_count
        
        return worker_data
    
    def get_cluster_summary(self, cluster_id: int) -> Dict:
        """
        Get summary statistics for a cluster.
        
        Args:
            cluster_id: Cluster number (0 or 1)
        
        Returns:
            Cluster statistics and worker information
        """
        
        cluster_data = self.worker_clusters[self.worker_clusters['kmeans_cluster'] == cluster_id]
        if cluster_data.empty:
            return {'error': f'Cluster {cluster_id} not found'}
        
        worker_ids = cluster_data['worker_id'].tolist()
        cluster_workers = self.workers[self.workers['worker_id'].isin(worker_ids)]
        
        # Get profile for this cluster
        profile = self.cluster_profiles[self.cluster_profiles['Cluster'] == cluster_id]
        
        # Risk distribution
        cluster_recs = self.recommendations[self.recommendations['worker_id'].isin(worker_ids)]
        risk_dist = cluster_recs['predicted_risk'].value_counts().to_dict()
        priority_dist = cluster_recs['priority'].value_counts().to_dict()
        
        return {
            'cluster_id': cluster_id,
            'total_workers': len(worker_ids),
            'percentage': f"{len(worker_ids)/len(self.workers)*100:.1f}%",
            'profile': profile.iloc[0].to_dict() if not profile.empty else {},
            'risk_distribution': risk_dist,
            'priority_distribution': priority_dist,
            'avg_experience': cluster_workers['experience_years'].mean(),
            'avg_skill_score': cluster_workers['skill_score'].mean(),
            'certification_rate': (cluster_workers['certification_level'] > 0).sum() / len(cluster_workers),
            'training_completion': cluster_workers['training_completed'].mean()
        }
    
    def search_by_criteria(self, criteria: Dict) -> pd.DataFrame:
        """
        Search workers by multiple criteria.
        
        Args:
            criteria: Dictionary with filters
                - cluster: int (0 or 1)
                - risk_level: str ('Low', 'Medium', 'High')
                - priority: str
                - min_experience: int
                - max_incidents: int
        
        Returns:
            DataFrame of matching workers
        """
        
        results = self.recommendations.copy()
        
        if 'cluster' in criteria:
            cluster_workers = self.worker_clusters[
                self.worker_clusters['kmeans_cluster'] == criteria['cluster']
            ]['worker_id'].tolist()
            results = results[results['worker_id'].isin(cluster_workers)]
        
        if 'risk_level' in criteria:
            results = results[results['predicted_risk'] == criteria['risk_level']]
        
        if 'priority' in criteria:
            results = results[results['priority'] == criteria['priority']]
        
        if 'min_confidence' in criteria:
            results = results[results['confidence'] >= criteria['min_confidence']]
        
        # Merge with worker details
        results = results.merge(self.workers[['worker_id', 'experience_years', 'skill_score']], 
                                on='worker_id', how='left')
        
        return results
    
    def get_confidence_metrics(self) -> Dict:
        """
        Get confidence score statistics and distribution.
        
        Returns:
            Confidence metrics
        """
        
        confidence_scores = self.recommendations['confidence'].values
        
        return {
            'mean_confidence': float(confidence_scores.mean()),
            'median_confidence': float(np.median(confidence_scores)),
            'std_confidence': float(confidence_scores.std()),
            'min_confidence': float(confidence_scores.min()),
            'max_confidence': float(confidence_scores.max()),
            'high_confidence_count': int((confidence_scores > 0.85).sum()),
            'high_confidence_pct': float((confidence_scores > 0.85).sum() / len(confidence_scores) * 100),
            'medium_confidence_count': int(((confidence_scores >= 0.70) & (confidence_scores <= 0.85)).sum()),
            'low_confidence_count': int((confidence_scores < 0.70).sum()),
            'distribution_percentiles': {
                'p25': float(np.percentile(confidence_scores, 25)),
                'p50': float(np.percentile(confidence_scores, 50)),
                'p75': float(np.percentile(confidence_scores, 75)),
                'p90': float(np.percentile(confidence_scores, 90))
            }
        }
    
    def get_system_summary(self) -> Dict:
        """
        Get overall system integration summary.
        
        Returns:
            Comprehensive system statistics
        """
        
        recs = self.recommendations
        
        return {
            'total_workers': len(self.workers),
            'total_analyzed': len(recs),
            'ml_coverage': f"{len(recs)/len(self.workers)*100:.1f}%",
            'risk_distribution': {
                'low': {
                    'count': int((recs['predicted_risk'] == 'Low').sum()),
                    'pct': float((recs['predicted_risk'] == 'Low').sum() / len(recs) * 100)
                },
                'medium': {
                    'count': int((recs['predicted_risk'] == 'Medium').sum()),
                    'pct': float((recs['predicted_risk'] == 'Medium').sum() / len(recs) * 100)
                },
                'high': {
                    'count': int((recs['predicted_risk'] == 'High').sum()),
                    'pct': float((recs['predicted_risk'] == 'High').sum() / len(recs) * 100)
                }
            },
            'priority_distribution': recs['priority'].value_counts().to_dict(),
            'cluster_distribution': {
                'cluster_0': int(len(self.worker_clusters[self.worker_clusters['kmeans_cluster'] == 0])),
                'cluster_1': int(len(self.worker_clusters[self.worker_clusters['kmeans_cluster'] == 1]))
            },
            'confidence_metrics': self.get_confidence_metrics(),
            'critical_interventions': int((recs['priority'] == 'CRITICAL - INTERVENTION REQUIRED').sum()),
            'high_priority': int((recs['priority'].str.contains('HIGH|URGENT|CRITICAL', na=False)).sum())
        }
    
    def export_worker_report(self, worker_id: str, output_path: Optional[str] = None) -> str:
        """
        Export detailed worker report.
        
        Args:
            worker_id: Worker identifier
            output_path: Optional output file path
        
        Returns:
            Report text
        """
        
        profile = self.get_worker_profile(worker_id)
        
        if 'error' in profile:
            return profile['error']
        
        report = []
        report.append("=" * 80)
        report.append("INTEGRATED WORKER REPORT")
        report.append("=" * 80)
        
        report.append(f"\nWorker ID: {worker_id}")
        report.append(f"Experience: {profile.get('experience_years', 'N/A')} years")
        report.append(f"Skill Score: {profile.get('skill_score', 'N/A')}/100")
        report.append(f"Certification Level: {profile.get('certification_level', 'N/A')}")
        
        report.append("\n" + "-" * 80)
        report.append("CLUSTERING & ML PREDICTIONS")
        report.append("-" * 80)
        
        report.append(f"Cluster Assignment: {profile.get('kmeans_cluster', 'N/A')}")
        report.append(f"Predicted Risk Level: {profile.get('predicted_risk', 'N/A')}")
        report.append(f"Confidence Score: {profile.get('confidence', 'N/A'):.1%}")
        report.append(f"Priority Level: {profile.get('priority', 'N/A')}")
        
        report.append("\n" + "-" * 80)
        report.append("ASSIGNMENT HISTORY")
        report.append("-" * 80)
        
        report.append(f"Total Assignments: {profile.get('n_assignments', 0)}")
        report.append(f"Avg Skill Mismatch: {profile.get('avg_skill_mismatch', 0):.2f}")
        report.append(f"High-Risk Assignments: {profile.get('high_risk_assignments', 0)}")
        
        report.append("\n" + "-" * 80)
        report.append("TRAINING PRIORITIES")
        report.append("-" * 80)
        
        training = profile.get('training_priority', 'N/A')
        if isinstance(training, str):
            for item in training.split(', '):
                report.append(f"  • {item}")
        
        report.append("\n" + "=" * 80)
        
        report_text = "\n".join(report)
        
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(report_text)
            print(f"✓ Report saved to {output_path}")
        
        return report_text
    
    def get_recommendation_samples(self, n_samples: int = 10, 
                                  criteria: Optional[Dict] = None) -> pd.DataFrame:
        """
        Get sample recommendations with optional filtering.
        
        Args:
            n_samples: Number of samples to return
            criteria: Optional filter criteria
        
        Returns:
            DataFrame of sample recommendations
        """
        
        if criteria:
            results = self.search_by_criteria(criteria)
        else:
            results = self.recommendations.copy()
        
        # Sample diverse priorities
        samples = []
        for priority in results['priority'].unique():
            priority_recs = results[results['priority'] == priority]
            n_to_take = min(2, len(priority_recs))
            samples.append(priority_recs.sample(min(n_to_take, len(priority_recs))))
        
        result = pd.concat(samples).drop_duplicates().head(n_samples)
        return result[['worker_id', 'cluster', 'predicted_risk', 'confidence', 'priority']]


def integration_summary():
    """Generate integration layer summary"""
    
    print("\n" + "=" * 80)
    print("WEEK 6: INTEGRATION LAYER")
    print("=" * 80)
    
    integration = IntegrationLayer()
    
    print("\n" + "-" * 80)
    print("SYSTEM SUMMARY")
    print("-" * 80)
    
    summary = integration.get_system_summary()
    
    print(f"\nTotal Workers: {summary['total_workers']}")
    print(f"Coverage: {summary['ml_coverage']}")
    
    print("\nRisk Distribution:")
    for risk, data in summary['risk_distribution'].items():
        print(f"  {risk.title()}: {data['count']} ({data['pct']:.1f}%)")
    
    print("\nCluster Distribution:")
    for cluster, count in summary['cluster_distribution'].items():
        print(f"  {cluster}: {count} workers")
    
    print("\nPriority Levels:")
    for priority, count in sorted(summary['priority_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {priority}: {count}")
    
    print("\nConfidence Metrics:")
    conf = summary['confidence_metrics']
    print(f"  Mean: {conf['mean_confidence']:.1%}")
    print(f"  High (>85%): {conf['high_confidence_count']} workers ({conf['high_confidence_pct']:.1f}%)")
    print(f"  Medium (70-85%): {conf['medium_confidence_count']} workers")
    print(f"  Low (<70%): {conf['low_confidence_count']} workers")
    
    print("\nCritical Interventions: " + str(summary['critical_interventions']))
    print("High Priority Workers: " + str(summary['high_priority']))
    
    print("\n" + "-" * 80)
    print("SAMPLE RECOMMENDATIONS")
    print("-" * 80)
    
    samples = integration.get_recommendation_samples(n_samples=5)
    print("\n" + samples.to_string())
    
    print("\n" + "=" * 80)
    print("Integration Layer Ready")
    print("=" * 80)
    
    return integration


if __name__ == "__main__":
    integration_summary()

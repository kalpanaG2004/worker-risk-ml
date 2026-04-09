import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


@dataclass
class Recommendation:
    worker_id: str
    cluster: int
    predicted_risk_level: str
    recommendations: Dict[str, any]
    explanations: Dict[str, str]
    confidence_score: float
    priority_level: str


class DecisionEngine:
    
    def __init__(self, risk_threshold_low=0.4, risk_threshold_high=0.7):
        self.risk_threshold_low = risk_threshold_low
        self.risk_threshold_high = risk_threshold_high
        
        # Cluster profiles (from Week 3 analysis)
        self.cluster_profiles = {
            0: {
                'name': 'Experienced Workforce',
                'experience': 19.32,
                'skill_score': 49.41,
                'certification_rate': 0.901,
                'training_completion': 0.57,
                'avg_incidents': 0.65,
                'skill_mismatch': 22.37,
                'size': 272,
                'percentage': 0.544
            },
            1: {
                'name': 'Developing Workforce',
                'experience': 10.32,
                'skill_score': 22.73,
                'certification_rate': 0.496,
                'training_completion': 0.368,
                'avg_incidents': 0.97,
                'skill_mismatch': 45.24,
                'size': 228,
                'percentage': 0.456
            }
        }
        
        # Define recommendation rules per cluster-risk combination
        self._initialize_rules()
    
    def _initialize_rules(self):
        
        # Cluster 0 (Experienced) - Low Risk
        self.rules = {
            (0, 'Low'): {
                'skill_development': ['Advanced certifications', 'Specialized technical skills'],
                'task_suitability': ['Complex technical tasks', 'High-skill-requirement projects', 'Leadership roles'],
                'supervision': 'Minimal - Worker is highly capable',
                'training_priority': ['Specialization courses', 'Emerging technologies', 'Leadership development'],
                'career_path': ['Senior roles', 'Technical leadership', 'Mentoring positions'],
                'safety_measures': ['Standard safety protocols', 'Self-directed responsibility'],
                'confidence': 0.95,
                'priority': 'MAINTAIN'
            },
            
            # Cluster 0 (Experienced) - Medium Risk
            (0, 'Medium'): {
                'skill_development': ['Task-specific skills', 'Skill gap analysis'],
                'task_suitability': ['Standard technical tasks', 'Moderate complexity projects'],
                'supervision': 'Light - Spot checks and periodic reviews',
                'training_priority': ['Skill gap training', 'Refresher courses', 'New technology adoption'],
                'career_path': ['Continued advancement', 'Specialized roles', 'Senior positions'],
                'safety_measures': ['Periodic safety reviews', 'Enhanced hazard awareness'],
                'confidence': 0.85,
                'priority': 'MONITOR'
            },
            
            # Cluster 0 (Experienced) - High Risk
            (0, 'High'): {
                'skill_development': ['Critical skill remediation', 'Certifications renewal'],
                'task_suitability': ['Lower-risk tasks initially', 'Building back to complex tasks'],
                'supervision': 'Regular - Weekly check-ins and reviews',
                'training_priority': ['Immediate skill development', 'Safety protocols review', 'Risk management training'],
                'career_path': ['Pause advancement', 'Focus on skill recovery', 'Mentoring support'],
                'safety_measures': ['Enhanced supervision', 'Buddy system', 'Regular safety briefings'],
                'confidence': 0.80,
                'priority': 'HIGH ATTENTION'
            },
            
            # Cluster 1 (Developing) - Low Risk
            (1, 'Low'): {
                'skill_development': ['Foundation skill strengthening', 'Core competency development'],
                'task_suitability': ['Simple, well-defined tasks', 'Structured projects', 'Training assignments'],
                'supervision': 'Moderate - Regular check-ins',
                'training_priority': ['Skill certification', 'Core competency training', 'Safety fundamentals'],
                'career_path': ['Structured progression path', 'Skill milestones', 'Potential advancement'],
                'safety_measures': ['Regular safety training', 'Buddy system recommended', 'Enhanced monitoring'],
                'confidence': 0.75,
                'priority': 'DEVELOP'
            },
            
            # Cluster 1 (Developing) - Medium Risk
            (1, 'Medium'): {
                'skill_development': ['Urgent skill development', 'Competency gap closure', 'Certification pursuit'],
                'task_suitability': ['Simplified tasks', 'Skill-matched assignments only', 'Training roles'],
                'supervision': 'Close - Multiple check-ins',
                'training_priority': ['Comprehensive skill training (HIGH)', 'Safety protocols', 'Risk awareness training'],
                'career_path': ['Skill development focus', 'Pause advancement', 'Mentoring support needed'],
                'safety_measures': ['Buddy system mandatory', 'Close supervision', 'Daily safety briefings'],
                'confidence': 0.70,
                'priority': 'URGENT DEVELOPMENT'
            },
            
            # Cluster 1 (Developing) - High Risk
            (1, 'High'): {
                'skill_development': ['Critical skill gap closure', 'Immediate remediation', 'Intensive training'],
                'task_suitability': ['Minimal work - Training focus', 'Very simple, supervised tasks'],
                'supervision': 'Constant - 1-on-1 with experienced worker',
                'training_priority': ['Immediate intensive training', 'Safety protocols (CRITICAL)', 'Risk management', 'Incident prevention'],
                'career_path': ['Pause all activities', 'Intensive development only', 'Transition planning if needed'],
                'safety_measures': ['Constant supervision', 'Mandatory buddy system', 'Risk mitigation protocols', 'Daily briefings'],
                'confidence': 0.65,
                'priority': 'CRITICAL - INTERVENTION REQUIRED'
            }
        }
    
    def predict_risk_level(self, risk_probability: float) -> str:
        if risk_probability < self.risk_threshold_low:
            return 'Low'
        elif risk_probability < self.risk_threshold_high:
            return 'Medium'
        else:
            return 'High'
    
    def generate_recommendations(self, worker_data: pd.Series, cluster: int, 
                                risk_probability: float) -> Recommendation:
        
        risk_level = self.predict_risk_level(risk_probability)
        rule_key = (cluster, risk_level)
        
        if rule_key not in self.rules:
            raise ValueError(f"No rules defined for cluster {cluster}, risk {risk_level}")
        
        rules = self.rules[rule_key]
        cluster_name = self.cluster_profiles[cluster]['name']
        
        # Build detailed explanations
        explanations = self._build_explanations(
            worker_data, cluster, risk_level, risk_probability, cluster_name
        )
        
        # Extract recommendations from rules
        recommendations = {
            'skill_development': rules['skill_development'],
            'task_suitability': rules['task_suitability'],
            'supervision_level': rules['supervision'],
            'training_priority': rules['training_priority'],
            'career_path': rules['career_path'],
            'safety_measures': rules['safety_measures']
        }
        
        # Calculate confidence based on cluster and ML prediction certainty
        confidence = rules['confidence'] * min(
            1.0, max(risk_probability, 1 - risk_probability) * 2
        )
        
        return Recommendation(
            worker_id=str(worker_data.get('worker_id', 'UNKNOWN')),
            cluster=cluster,
            predicted_risk_level=risk_level,
            recommendations=recommendations,
            explanations=explanations,
            confidence_score=confidence,
            priority_level=rules['priority']
        )
    
    def _build_explanations(self, worker_data: pd.Series, cluster: int, risk_level: str,
                           risk_probability: float, cluster_name: str) -> Dict[str, str]:
        
        profile = self.cluster_profiles[cluster]
        explanations = {}
        
        # Overall assessment explanation
        cluster_desc = (
            f"Worker is in the '{cluster_name}' group, which typically has "
            f"{profile['experience']:.1f} years experience and "
            f"{profile['skill_score']:.1f}/100 skill score on average."
        )
        
        risk_desc = (
            f"ML model predicts {risk_level} risk (probability: {risk_probability:.1%}). "
        )
        
        if risk_level == 'Low':
            risk_detail = (
                "This worker shows low risk indicators and is suitable for most assignments. "
                "Focus should be on skill enhancement and potential advancement."
            )
        elif risk_level == 'Medium':
            risk_detail = (
                "This worker shows moderate risk. Careful task matching and periodic "
                "supervision recommended. Focus on skill gap closure and safety awareness."
            )
        else:  # High
            risk_detail = (
                "This worker shows high risk indicators. Close supervision required. "
                "Immediate action needed for skill development and safety intervention."
            )
        
        explanations['overall_assessment'] = f"{cluster_desc} {risk_desc} {risk_detail}"
        
        # Skill analysis
        skill_gap = profile['skill_score']
        if cluster == 1:  # Developing workforce
            if skill_gap < 30:
                skill_msg = (
                    f"Significant skill gap identified ({skill_gap:.1f}/100). "
                    "Urgent: comprehensive training program recommended."
                )
            else:
                skill_msg = (
                    f"Moderate skill level ({skill_gap:.1f}/100). "
                    "Skill development training is a priority."
                )
        else:  # Experienced
            if skill_gap < 50:
                skill_msg = (
                    f"Worker has {skill_gap:.1f}/100 skill score. "
                    "Specialty training opportunities available."
                )
            else:
                skill_msg = (
                    f"Strong skill level ({skill_gap:.1f}/100). "
                    "Worker ready for advanced assignments."
                )
        
        explanations['skill_analysis'] = skill_msg
        
        # Task alignment analysis
        if 'skill_mismatch_mean' in worker_data:
            mismatch = worker_data['skill_mismatch_mean']
            if cluster == 1 and mismatch > 40:
                alignment_msg = (
                    f"Critical: High skill-task mismatch ({mismatch:.1f}). Current assignments "
                    "may be above worker capability level. Recommend task reassignment and intensive training."
                )
            elif mismatch > 30:
                alignment_msg = (
                    f"Moderate mismatch ({mismatch:.1f}) between worker skills and assigned tasks. "
                    "Recommend careful task matching and skill development."
                )
            else:
                alignment_msg = (
                    f"Good skill-task alignment ({mismatch:.1f}). Worker is well-matched to current assignments."
                )
            
            explanations['task_alignment'] = alignment_msg
        
        # Safety factors
        if 'past_incident_count' in worker_data:
            incidents = worker_data['past_incident_count']
            if incidents > 1:
                safety_msg = (
                    f"Safety concern: {incidents} incidents in history. "
                    "Enhanced supervision and safety training recommended immediately."
                )
            elif incidents > 0:
                safety_msg = (
                    f"One incident recorded. Monitor closely and reinforce safety protocols."
                )
            else:
                safety_msg = (
                    f"Good safety record. Standard safety practices sufficient."
                )
            
            explanations['safety_factors'] = safety_msg
        
        # Recommendation priority explanation
        if risk_level == 'High':
            priority_msg = (
                "This worker requires immediate attention. A comprehensive intervention plan "
                "(training, supervision, task reassignment) should be implemented immediately."
            )
        elif risk_level == 'Medium':
            priority_msg = (
                "Medium priority. Recommend addressing skill gaps and improving task alignment "
                "within the next 2-4 weeks."
            )
        else:
            priority_msg = (
                "Low priority for intervention. Maintain current approach with periodic reviews."
            )
        
        explanations['recommendation_priority'] = priority_msg
        
        return explanations


class RecommendationFormatter:
    
    @staticmethod
    def format_text_report(rec: Recommendation) -> str:
        
        report = []
        report.append("=" * 80)
        report.append("PERSONALIZED WORKER RECOMMENDATION REPORT")
        report.append("=" * 80)
        report.append(f"\nWorker ID: {rec.worker_id}")
        report.append(f"Cluster: {rec.cluster} (Cluster {rec.cluster} Worker)")
        report.append(f"Predicted Risk Level: {rec.predicted_risk_level}")
        report.append(f"Confidence Score: {rec.confidence_score:.1%}")
        report.append(f"Priority: {rec.priority_level}")
        
        report.append("\n" + "-" * 80)
        report.append("EXPLANATIONS")
        report.append("-" * 80)
        
        for key, explanation in rec.explanations.items():
            formatted_key = key.replace('_', ' ').title()
            report.append(f"\n{formatted_key}:")
            report.append(f"  {explanation}")
        
        report.append("\n" + "-" * 80)
        report.append("RECOMMENDATIONS")
        report.append("-" * 80)
        
        for category, items in rec.recommendations.items():
            formatted_category = category.replace('_', ' ').title()
            report.append(f"\n{formatted_category}:")
            
            if isinstance(items, list):
                for item in items:
                    report.append(f"  • {item}")
            else:
                report.append(f"  {items}")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    @staticmethod
    def to_dataframe(recommendations: List[Recommendation]) -> pd.DataFrame:
        
        data = []
        for rec in recommendations:
            data.append({
                'worker_id': rec.worker_id,
                'cluster': rec.cluster,
                'predicted_risk': rec.predicted_risk_level,
                'confidence': rec.confidence_score,
                'priority': rec.priority_level,
                'skill_focus': ', '.join(rec.recommendations['skill_development']),
                'suitable_tasks': ', '.join(rec.recommendations['task_suitability']),
                'supervision': rec.recommendations['supervision_level'],
                'training_priority': ', '.join(rec.recommendations['training_priority']),
                'career_path': ', '.join(rec.recommendations['career_path'])
            })
        
        return pd.DataFrame(data)


class RecommendationPipeline:
    
    def __init__(self, data_dir='data', model_path='data/best_model.pkl'):
        """Initialize recommendation pipeline"""
        
        self.data_dir = data_dir
        self.model_path = model_path
        
        # Load trained model
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        # Load clustering models
        with open(f'{data_dir}/kmeans_model.pkl', 'rb') as f:
            cluster_data = pickle.load(f)
            self.kmeans = cluster_data['kmeans']
            self.clustering_scaler = cluster_data['scaler']
            self.clustering_features = cluster_data['features']
        
        # Load cluster assignments
        self.worker_clusters = pd.read_csv(f'{data_dir}/worker_clusters.csv')
        
        # Initialize decision engine
        self.engine = DecisionEngine()
        self.formatter = RecommendationFormatter()
    
    def generate_all_recommendations(self, worker_data_path: str = None) -> List[Recommendation]:
        
        print("\n" + "=" * 80)
        print("GENERATING RECOMMENDATIONS FOR ALL WORKERS")
        print("=" * 80)
        
        # Load worker data
        if worker_data_path:
            workers = pd.read_csv(worker_data_path)
        else:
            workers = pd.read_csv(f'{self.data_dir}/workers.csv')
            assignments = pd.read_csv(f'{self.data_dir}/assignments.csv')
            
            # Aggregate features
            assignment_stats = assignments.groupby('worker_id').agg({
                'skill_mismatch': 'mean',
                'actual_risk': lambda x: (x == 'High').sum()
            }).reset_index()
            assignment_stats.columns = ['worker_id', 'skill_mismatch_mean', 'high_risk_count']
            
            workers = workers.merge(assignment_stats, on='worker_id', how='left')
        
        # Merge cluster assignments
        worker_data = workers.merge(self.worker_clusters, on='worker_id', how='left')
        
        # Generate feature vectors for risk prediction
        feature_cols = [
            'required_skill_level', 'environment_risk', 'supervision_required',
            'experience_years', 'certification_level', 'training_completed',
            'past_incident_count', 'skill_mismatch_mean'
        ]
        
        # Load X_train for reference (to understand scaling)
        X_test = pd.read_csv(f'{self.data_dir}/X_test.csv')
        
        recommendations = []
        
        for idx, (_, worker) in enumerate(worker_data.iterrows()):
            if idx % 100 == 0:
                print(f"Processing worker {idx+1}/{len(worker_data)}...", end='\r')
            
            # Build feature vector
            worker_features = {}
            for col in feature_cols:
                if col in worker.index:
                    val = worker[col]
                    # Handle missing values
                    if pd.isna(val):
                        if col in X_test.columns:
                            val = X_test[col].mean()
                        else:
                            val = 0
                    worker_features[col] = val
                else:
                    worker_features[col] = 0
            
            feature_vec = np.array([worker_features[col] for col in feature_cols]).reshape(1, -1)
            
            # Predict risk (using probability of high-risk class)
            try:
                risk_probs = self.model.predict_proba(feature_vec)[0]
                # Assume class 2 is 'High' risk (from baseline_model.py)
                risk_probability = risk_probs[2] if len(risk_probs) > 2 else risk_probs[1]
            except:
                # Fallback
                risk_probability = 0.5
            
            cluster = int(worker.get('kmeans_cluster', 0))
            
            # Generate recommendation
            rec = self.engine.generate_recommendations(
                worker, cluster, risk_probability
            )
            
            recommendations.append(rec)
        
        print(f"\nGenerated {len(recommendations)} recommendations")
        
        return recommendations
    
    def save_recommendations(self, recommendations: List[Recommendation], 
                            output_dir: str = 'data'):
        
        print(f"\nSaving recommendations to {output_dir}/...")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Save as CSV
        df = self.formatter.to_dataframe(recommendations)
        df.to_csv(f'{output_dir}/worker_recommendations.csv', index=False)
        print(f"✓ Saved: {output_dir}/worker_recommendations.csv")
        
        # Save individual reports
        report_dir = Path(f'{output_dir}/recommendations_detailed')
        report_dir.mkdir(exist_ok=True)
        
        for rec in recommendations[:50]:  # Save first 50 detailed reports
            report_text = self.formatter.format_text_report(rec)
            with open(f'{report_dir}/{rec.worker_id}_recommendation.txt', 'w') as f:
                f.write(report_text)
        
        print(f"✓ Saved detailed reports: {report_dir}/ (first 50 workers)")
        
        # Save summary statistics
        summary_stats = self._generate_summary_statistics(recommendations)
        summary_stats.to_csv(f'{output_dir}/recommendations_summary_stats.csv', index=False)
        print(f"✓ Saved: {output_dir}/recommendations_summary_stats.csv")
    
    def _generate_summary_statistics(self, recommendations: List[Recommendation]) -> pd.DataFrame:
        
        stats = {
            'Total Workers': len(recommendations),
            'High Priority Count': sum(1 for r in recommendations if r.priority_level.startswith('HIGH') or r.priority_level.startswith('CRITICAL')),
            'High Priority %': sum(1 for r in recommendations if r.priority_level.startswith('HIGH') or r.priority_level.startswith('CRITICAL')) / len(recommendations) * 100,
            'High Risk Count': sum(1 for r in recommendations if r.predicted_risk_level == 'High'),
            'High Risk %': sum(1 for r in recommendations if r.predicted_risk_level == 'High') / len(recommendations) * 100,
            'Medium Risk Count': sum(1 for r in recommendations if r.predicted_risk_level == 'Medium'),
            'Medium Risk %': sum(1 for r in recommendations if r.predicted_risk_level == 'Medium') / len(recommendations) * 100,
            'Low Risk Count': sum(1 for r in recommendations if r.predicted_risk_level == 'Low'),
            'Low Risk %': sum(1 for r in recommendations if r.predicted_risk_level == 'Low') / len(recommendations) * 100,
            'Avg Confidence': np.mean([r.confidence_score for r in recommendations]),
            'Cluster 0 Count': sum(1 for r in recommendations if r.cluster == 0),
            'Cluster 1 Count': sum(1 for r in recommendations if r.cluster == 1)
        }
        
        return pd.DataFrame([stats])


def recommendation_pipeline() -> Dict:
    
    print("\n" + "=" * 80)
    print("WEEK 4: RECOMMENDATION ENGINE")
    print("=" * 80)
    
    # Initialize pipeline
    pipeline = RecommendationPipeline()
    
    # Generate recommendations
    recommendations = pipeline.generate_all_recommendations()
    
    # Save recommendations
    pipeline.save_recommendations(recommendations)
    
    # Print sample recommendations
    print("\n" + "=" * 80)
    print("SAMPLE RECOMMENDATIONS")
    print("=" * 80)
    
    for i in [0, 50, 100, 150, 200]:
        if i < len(recommendations):
            rec = recommendations[i]
            print(f"\n--- Sample {i+1}: Worker {rec.worker_id} ---")
            print(f"Cluster: {rec.cluster}, Risk: {rec.predicted_risk_level}, Priority: {rec.priority_level}")
            print(f"Confidence: {rec.confidence_score:.1%}")
            print("Key Recommendations:")
            for item in rec.recommendations['task_suitability'][:2]:
                print(f"  • {item}")
    
    # Generate summary
    print("\n" + "=" * 80)
    print("RECOMMENDATION SUMMARY")
    print("=" * 80)
    
    stats_df = pipeline._generate_summary_statistics(recommendations)
    print("\nRecommendation Statistics:")
    for col in stats_df.columns:
        val = stats_df[col].iloc[0]
        if '%' in col:
            print(f"  {col}: {val:.1f}%")
        elif 'Count' in col or 'Total' in col:
            print(f"  {col}: {int(val)}")
        else:
            if isinstance(val, float):
                print(f"  {col}: {val:.2f}")
            else:
                print(f"  {col}: {val}")
    
    print("\n" + "=" * 80)
    print("Week 4 Recommendation Engine Complete")
    print("=" * 80)
    
    return {
        'recommendations': recommendations,
        'pipeline': pipeline,
        'summary_stats': stats_df
    }


if __name__ == "__main__":
    recommendation_pipeline()

import argparse
import sys
from pathlib import Path
from typing import Optional
import textwrap

from integration_layer import IntegrationLayer


class RecommendationCLI:
    
    def __init__(self):
        self.integration = None
        self.load_system()
    
    def load_system(self):
        try:
            self.integration = IntegrationLayer()
        except Exception as e:
            print(f"Error loading system: {e}")
            sys.exit(1)
    
    def worker_info(self, worker_id: str):
        print("\n" + "=" * 80)
        print("WORKER PROFILE")
        print("=" * 80)
        
        profile = self.integration.get_worker_profile(worker_id)
        
        if 'error' in profile:
            print(f"❌ {profile['error']}")
            return
        
        print(f"\n{worker_id}")
        print("-" * 80)
        
        # Basic info
        print("\nBasic Information:")
        print(f"  Experience: {profile.get('experience_years', 'N/A')} years")
        print(f"  Skill Score: {profile.get('skill_score', 'N/A'):.0f}/100")
        print(f"  Certification: Level {profile.get('certification_level', 'N/A')}")
        print(f"  Training Complete: {'Yes' if profile.get('training_completed') else 'No'}")
        
        # Cluster and Risk
        print("\nCluster & ML Predictions:")
        print(f"  Cluster: {profile.get('kmeans_cluster', 'N/A')}")
        print(f"  Predicted Risk: {profile.get('predicted_risk', 'N/A')}")
        print(f"  Confidence: {profile.get('confidence', 0):.1%}")
        print(f"  Priority: {profile.get('priority', 'N/A')}")
        
        # Assignment History
        print("\nAssignment History:")
        print(f"  Total Assignments: {profile.get('n_assignments', 0)}")
        print(f"  Avg Skill Mismatch: {profile.get('avg_skill_mismatch', 0):.2f}")
        print(f"  High-Risk Assignments: {profile.get('high_risk_assignments', 0)}")
        print(f"  Past Incidents: {profile.get('past_incident_count', 0)}")
        
        # Training Priority
        training = profile.get('training_priority', 'N/A')
        print("\nTraining Priorities:")
        if isinstance(training, str) and training != 'N/A':
            for item in training.split(', '):
                print(f"  • {item}")
        else:
            print("  No specific priorities")
        
        print("\n" + "=" * 80 + "\n")
    
    def search_workers(self, query: str):
        print("\n" + "=" * 80)
        print("WORKER SEARCH RESULTS")
        print("=" * 80)
        
        # Parse query
        try:
            if query.startswith("risk:"):
                risk_level = query.split(":")[1].strip()
                results = self.integration.search_by_criteria({'risk_level': risk_level})
            elif query.startswith("priority:"):
                priority = query.split(":")[1].strip()
                results = self.integration.search_by_criteria({'priority': priority})
            elif query.startswith("cluster:"):
                cluster = int(query.split(":")[1].strip())
                results = self.integration.search_by_criteria({'cluster': cluster})
            elif query.startswith("confidence>"):
                conf = float(query.split(">")[1].strip())
                results = self.integration.search_by_criteria({'min_confidence': conf})
            else:
                print("❌ Invalid query format")
                print("Supported formats:")
                print("  risk:<Low|Medium|High>")
                print("  priority:<MAINTAIN|MONITOR|DEVELOP|etc>")
                print("  cluster:<0|1>")
                print("  confidence><score>")
                return
        except Exception as e:
            print(f"❌ Error parsing query: {e}")
            return
        
        if results.empty:
            print("❌ No workers found matching criteria")
            return
        
        print(f"\nFound {len(results)} workers\n")
        
        # Display results
        display_cols = ['worker_id', 'cluster', 'predicted_risk', 'confidence', 'priority']
        available_cols = [col for col in display_cols if col in results.columns]
        
        print(results[available_cols].head(20).to_string(index=False))
        
        if len(results) > 20:
            print(f"\n... and {len(results) - 20} more")
        
        print("\n" + "=" * 80 + "\n")
    
    def cluster_summary(self, cluster_id: int):
        print("\n" + "=" * 80)
        print(f"CLUSTER {cluster_id} SUMMARY")
        print("=" * 80)
        
        summary = self.integration.get_cluster_summary(cluster_id)
        
        if 'error' in summary:
            print(f"❌ {summary['error']}")
            return
        
        print(f"\nTotal Workers: {summary['total_workers']} ({summary['percentage']})")
        print("-" * 80)
        
        print("\nCluster Profile:")
        profile = summary.get('profile', {})
        print(f"  Avg Experience: {profile.get('Avg_Experience', 'N/A'):.1f} years")
        print(f"  Avg Skill Score: {profile.get('Avg_Skill_Score', 'N/A'):.1f}")
        print(f"  Certification Rate: {profile.get('Certified_%', 0):.1f}%")
        print(f"  Training Complete: {profile.get('Training_Completed_%', 0):.1f}%")
        
        print("\nRisk Distribution:")
        for risk, count in summary['risk_distribution'].items():
            pct = count / summary['total_workers'] * 100 if summary['total_workers'] > 0 else 0
            print(f"  {risk}: {count} workers ({pct:.1f}%)")
        
        print("\nPriority Distribution:")
        for priority, count in sorted(summary['priority_distribution'].items(), 
                                     key=lambda x: x[1], reverse=True):
            pct = count / summary['total_workers'] * 100 if summary['total_workers'] > 0 else 0
            print(f"  {priority}: {count} workers ({pct:.1f}%)")
        
        print("\n" + "=" * 80 + "\n")
    
    def show_recommendations(self, n: int = 10):
        print("\n" + "=" * 80)
        print("SAMPLE RECOMMENDATIONS")
        print("=" * 80)
        
        samples = self.integration.get_recommendation_samples(n_samples=n)
        
        print(f"\nShowing {len(samples)} recommendations:\n")
        print(samples.to_string(index=False))
        
        print("\n" + "=" * 80 + "\n")
    
    def confidence_report(self):
        print("\n" + "=" * 80)
        print("CONFIDENCE METRICS")
        print("=" * 80)
        
        metrics = self.integration.get_confidence_metrics()
        
        print("\nOverall Statistics:")
        print(f"  Mean Confidence: {metrics['mean_confidence']:.1%}")
        print(f"  Median Confidence: {metrics['median_confidence']:.1%}")
        print(f"  Std Dev: {metrics['std_confidence']:.1%}")
        print(f"  Range: {metrics['min_confidence']:.1%} - {metrics['max_confidence']:.1%}")
        
        print("\nConfidence Distribution:")
        print(f"  High (>85%): {metrics['high_confidence_count']} workers ({metrics['high_confidence_pct']:.1f}%)")
        print(f"  Medium (70-85%): {metrics['medium_confidence_count']} workers")
        print(f"  Low (<70%): {metrics['low_confidence_count']} workers")
        
        print("\nPercentiles:")
        percentiles = metrics['distribution_percentiles']
        print(f"  25th: {percentiles['p25']:.1%}")
        print(f"  50th (median): {percentiles['p50']:.1%}")
        print(f"  75th: {percentiles['p75']:.1%}")
        print(f"  90th: {percentiles['p90']:.1%}")
        
        print("\n" + "=" * 80 + "\n")
    
    def system_status(self):
        print("\n" + "=" * 80)
        print("SYSTEM STATUS")
        print("=" * 80)
        
        summary = self.integration.get_system_summary()
        
        print(f"\nTotal Workers: {summary['total_workers']}")
        print(f"Workers Analyzed: {summary['total_analyzed']}")
        print(f"Coverage: {summary['ml_coverage']}")
        
        print("\n" + "-" * 80)
        print("Risk Distribution:")
        print("-" * 80)
        for risk, data in summary['risk_distribution'].items():
            pct = data['pct']
            bar = "█" * int(pct / 5)
            print(f"  {risk.title():8s}: {data['count']:3d} workers ({pct:5.1f}%) {bar}")
        
        print("\n" + "-" * 80)
        print("Cluster Distribution:")
        print("-" * 80)
        for cluster, count in summary['cluster_distribution'].items():
            pct = count / summary['total_workers'] * 100
            bar = "█" * int(pct / 5)
            cluster_name = "Experienced" if cluster == "cluster_0" else "Developing"
            print(f"  {cluster_name:15s}: {count:3d} workers ({pct:5.1f}%) {bar}")
        
        print("\n" + "-" * 80)
        print("Key Metrics:")
        print("-" * 80)
        conf = summary['confidence_metrics']
        print(f"  Average Confidence: {conf['mean_confidence']:.1%}")
        print(f"  Critical Interventions: {summary['critical_interventions']}")
        print(f"  High Priority Workers: {summary['high_priority']}")
        
        print("\n" + "=" * 80 + "\n")
    
    def export_report(self, worker_id: str, output_file: Optional[str] = None):
        
        if output_file is None:
            output_file = f"reports/{worker_id}_integrated_report.txt"
        
        print(f"\nExporting report for {worker_id}...")
        
        report = self.integration.export_worker_report(worker_id, output_file)
        
        if "Error" not in report:
            print(f"✓ Report saved to {output_file}")
        else:
            print(f"❌ {report}")


def main():
    
    parser = argparse.ArgumentParser(
        description='Worker Recommendation System CLI Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''
            EXAMPLES:
              python -m cli worker W00001              # Show worker profile
              python -m cli search "risk:High"         # Search high-risk workers
              python -m cli cluster 0                  # Show cluster 0 summary
              python -m cli status                     # Show system status
              python -m cli confidence                 # Show confidence metrics
              python -m cli samples 20                 # Show 20 sample recommendations
              python -m cli export W00001              # Export worker report
            
            SEARCH QUERIES:
              risk:<Low|Medium|High>                   # Filter by risk level
              priority:<MAINTAIN|MONITOR|DEVELOP|...>  # Filter by priority
              cluster:<0|1>                            # Filter by cluster
              confidence><score>                       # Filter by confidence
        ''')
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Worker info command
    worker_parser = subparsers.add_parser('worker', help='Get worker profile')
    worker_parser.add_argument('worker_id', help='Worker ID (e.g., W00001)')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search workers by criteria')
    search_parser.add_argument('query', help='Search query')
    
    # Cluster command
    cluster_parser = subparsers.add_parser('cluster', help='Show cluster summary')
    cluster_parser.add_argument('cluster_id', type=int, choices=[0, 1], help='Cluster ID')
    
    # Samples command
    samples_parser = subparsers.add_parser('samples', help='Show sample recommendations')
    samples_parser.add_argument('--n', type=int, default=10, help='Number of samples (default: 10)')
    
    # Confidence command
    subparsers.add_parser('confidence', help='Show confidence metrics')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export worker report')
    export_parser.add_argument('worker_id', help='Worker ID')
    export_parser.add_argument('--output', help='Output file path')
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = RecommendationCLI()
    
    # Execute commands
    if args.command == 'worker':
        cli.worker_info(args.worker_id)
    elif args.command == 'search':
        cli.search_workers(args.query)
    elif args.command == 'cluster':
        cli.cluster_summary(args.cluster_id)
    elif args.command == 'samples':
        cli.show_recommendations(n=args.n)
    elif args.command == 'confidence':
        cli.confidence_report()
    elif args.command == 'status':
        cli.system_status()
    elif args.command == 'export':
        cli.export_report(args.worker_id, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

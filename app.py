import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from integration_layer import IntegrationLayer


# Page configuration
st.set_page_config(
    page_title="Worker Risk ML Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3em;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .risk-high {
        color: #ff6b6b;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffa94d;
        font-weight: bold;
    }
    .risk-low {
        color: #51cf66;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)


# Initialize session state and data
@st.cache_resource
def load_integration_layer():
    try:
        return IntegrationLayer(data_dir='data', model_dir='data')
    except Exception as e:
        st.error(f"Error loading system: {e}")
        st.stop()


def get_risk_color(risk_level):
    if risk_level == 'High':
        return '#ff6b6b'
    elif risk_level == 'Medium':
        return '#ffa94d'
    else:
        return '#51cf66'


def format_confidence(conf):
    return f"{conf:.1%}" if isinstance(conf, (int, float)) else "N/A"


def dashboard_page(integration):
    st.markdown("<div class='main-header'>🏭 Dashboard</div>", unsafe_allow_html=True)
    
    # Get system summary
    summary = integration.get_system_summary()
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Workers",
            summary['total_workers'],
            delta=f"{summary['ml_coverage']} analyzed"
        )
    
    with col2:
        st.metric(
            "High Risk",
            summary['risk_distribution']['high']['count'],
            delta=f"{summary['risk_distribution']['high']['pct']:.1f}%"
        )
    
    with col3:
        st.metric(
            "Critical Priority",
            summary['critical_interventions'],
            delta=f"{summary['high_priority']} urgent"
        )
    
    with col4:
        conf_metrics = summary['confidence_metrics']
        st.metric(
            "Avg Confidence",
            f"{conf_metrics['mean_confidence']:.1%}",
            delta=f"σ={conf_metrics['std_confidence']:.3f}"
        )
    
    # Risk distribution chart
    st.subheader("📊 Risk Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        risk_data = pd.DataFrame({
            'Risk Level': ['Low', 'Medium', 'High'],
            'Count': [
                summary['risk_distribution']['low']['count'],
                summary['risk_distribution']['medium']['count'],
                summary['risk_distribution']['high']['count']
            ]
        })
        
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = ['#51cf66', '#ffa94d', '#ff6b6b']
        ax.pie(risk_data['Count'], labels=risk_data['Risk Level'], autopct='%1.1f%%',
               colors=colors, startangle=90)
        ax.set_title('Risk Level Distribution')
        st.pyplot(fig)
    
    with col2:
        # Priority distribution
        priority_data = pd.DataFrame({
            'Priority': list(summary['priority_distribution'].keys()),
            'Count': list(summary['priority_distribution'].values())
        }).sort_values('Count', ascending=False).head(8)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(priority_data['Priority'], priority_data['Count'], color='#1f77b4')
        ax.set_xlabel('Number of Workers')
        ax.set_title('Priority Distribution')
        st.pyplot(fig)
    
    # Confidence distribution
    st.subheader("📈 Confidence Metrics")
    conf_metrics = summary['confidence_metrics']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Mean Confidence", f"{conf_metrics['mean_confidence']:.1%}")
    with col2:
        st.metric("Median Confidence", f"{conf_metrics['median_confidence']:.1%}")
    with col3:
        st.metric("High Confidence (>85%)", f"{conf_metrics['high_confidence_count']} ({conf_metrics['high_confidence_pct']:.1f}%)")
    with col4:
        st.metric("Low Confidence (<70%)", f"{conf_metrics['low_confidence_count']}")
    
    # Cluster distribution
    st.subheader("🎯 Cluster Distribution")
    col1, col2 = st.columns(2)
    
    cluster_dist = summary['cluster_distribution']
    total_workers = cluster_dist['cluster_0'] + cluster_dist['cluster_1']
    
    with col1:
        st.write(f"**Cluster 0 (Experienced Workforce)**")
        st.write(f"Workers: {cluster_dist['cluster_0']} ({cluster_dist['cluster_0']/total_workers*100:.1f}%)")
    
    with col2:
        st.write(f"**Cluster 1 (Developing Workforce)**")
        st.write(f"Workers: {cluster_dist['cluster_1']} ({cluster_dist['cluster_1']/total_workers*100:.1f}%)")


def worker_profile_page(integration):
    st.markdown("<div class='main-header'>👤 Worker Profile</div>", unsafe_allow_html=True)
    
    # Search section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        worker_id = st.text_input(
            "Enter Worker ID (e.g., W00001):",
            value="W00001",
            placeholder="W00001"
        )
    
    with col2:
        search_button = st.button("🔍 Search", use_container_width=True)
    
    if search_button or worker_id:
        profile = integration.get_worker_profile(worker_id)
        
        if 'error' in profile:
            st.error(f"❌ {profile['error']}")
        else:
            # Header with risk badge
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.title(f"{worker_id}")
            
            with col2:
                risk = profile.get('predicted_risk', 'Unknown')
                color = get_risk_color(risk)
                st.markdown(
                    f'<div style="background-color: {color}; color: white; padding: 10px; border-radius: 5px; text-align: center;"><b>{risk}</b></div>',
                    unsafe_allow_html=True
                )
            
            with col3:
                priority = profile.get('priority', 'N/A')
                st.markdown(
                    f'<div style="background-color: #345ef4; color: white; padding: 10px; border-radius: 5px; text-align: center;"><b>{priority}</b></div>',
                    unsafe_allow_html=True
                )
            
            # Basic Information
            st.subheader("📋 Basic Information")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Experience", f"{profile.get('experience_years', 'N/A')} years")
            with col2:
                st.metric("Skill Score", f"{profile.get('skill_score', 'N/A'):.0f}/100")
            with col3:
                cert_level = profile.get('certification_level', 'N/A')
                st.metric("Certification", f"Level {cert_level}")
            with col4:
                training = "✓ Yes" if profile.get('training_completed') else "✗ No"
                st.metric("Training Complete", training)
            
            # ML Predictions
            st.subheader("🤖 ML Predictions & Clustering")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                cluster = profile.get('kmeans_cluster', 'N/A')
                cluster_name = "Experienced" if cluster == 0 else "Developing" if cluster == 1 else "Unknown"
                st.metric("Cluster", f"{cluster} ({cluster_name})")
            
            with col2:
                st.metric("Predicted Risk", profile.get('predicted_risk', 'N/A'))
            
            with col3:
                conf = profile.get('confidence', 0)
                st.metric("Confidence", format_confidence(conf))
            
            with col4:
                st.metric("Priority", profile.get('priority', 'N/A'))
            
            # Assignment History
            st.subheader("📊 Assignment History")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Assignments", profile.get('n_assignments', 0))
            with col2:
                st.metric("Avg Skill Mismatch", f"{profile.get('avg_skill_mismatch', 0):.2f}")
            with col3:
                st.metric("High-Risk Assignments", profile.get('high_risk_assignments', 0))
            with col4:
                st.metric("Past Incidents", profile.get('past_incident_count', 0))
            
            # Training Priorities
            st.subheader("🎓 Training Priorities")
            training = profile.get('training_priority', 'N/A')
            
            if isinstance(training, str) and training != 'N/A':
                priorities = [p.strip() for p in training.split(',')]
                for i, priority in enumerate(priorities, 1):
                    st.write(f"{i}. {priority}")
            else:
                st.write("No specific training priorities identified")
            
            # Export report
            if st.button("📥 Export Report"):
                report = integration.export_worker_report(worker_id)
                st.download_button(
                    label="Download Report",
                    data=report,
                    file_name=f"{worker_id}_report.txt",
                    mime="text/plain"
                )


def cluster_analysis_page(integration):
    st.markdown("<div class='main-header'>🎯 Cluster Analysis</div>", unsafe_allow_html=True)
    
    # Select cluster
    cluster_id = st.radio("Select Cluster:", [0, 1], horizontal=True,
                         captions=["Cluster 0: Experienced Workforce", "Cluster 1: Developing Workforce"])
    
    cluster_summary = integration.get_cluster_summary(cluster_id)
    
    if 'error' in cluster_summary:
        st.error(f"❌ {cluster_summary['error']}")
    else:
        # Cluster header
        cluster_name = "Experienced Workforce" if cluster_id == 0 else "Developing Workforce"
        st.title(f"Cluster {cluster_id}: {cluster_name}")
        
        # Key metrics
        st.subheader("📊 Cluster Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Workers", cluster_summary['total_workers'], 
                     delta=cluster_summary['percentage'])
        with col2:
            st.metric("Avg Experience", f"{cluster_summary['avg_experience']:.1f} years")
        with col3:
            st.metric("Avg Skill Score", f"{cluster_summary['avg_skill_score']:.1f}/100")
        with col4:
            st.metric("Certification Rate", f"{cluster_summary['certification_rate']:.1%}")
        
        # Risk and Priority Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Risk Distribution")
            risk_dist = cluster_summary['risk_distribution']
            risk_df = pd.DataFrame({
                'Risk': risk_dist.keys(),
                'Count': risk_dist.values()
            })
            
            fig, ax = plt.subplots(figsize=(8, 5))
            colors = [get_risk_color(risk) for risk in risk_df['Risk']]
            ax.bar(risk_df['Risk'], risk_df['Count'], color=colors)
            ax.set_ylabel('Number of Workers')
            ax.set_title(f'Cluster {cluster_id} Risk Distribution')
            st.pyplot(fig)
        
        with col2:
            st.subheader("Priority Distribution")
            priority_dist = cluster_summary['priority_distribution']
            priority_df = pd.DataFrame({
                'Priority': list(priority_dist.keys()),
                'Count': list(priority_dist.values())
            }).sort_values('Count', ascending=False)
            
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.barh(priority_df['Priority'], priority_df['Count'], color='#1f77b4')
            ax.set_xlabel('Number of Workers')
            ax.set_title(f'Cluster {cluster_id} Priority Distribution')
            st.pyplot(fig)
        
        # Profile Information
        st.subheader("📋 Cluster Profile")
        profile = cluster_summary.get('profile', {})
        
        profile_cols = st.columns(3)
        for idx, (key, value) in enumerate(list(profile.items())[:9]):
            with profile_cols[idx % 3]:
                st.write(f"**{key}**: {value}")


def search_workers_page(integration):
    st.markdown("<div class='main-header'>🔍 Search Workers</div>", unsafe_allow_html=True)
    
    st.subheader("Filter Workers")
    
    col1, col2, col3 = st.columns(3)
    
    # Filter options
    with col1:
        risk_levels = st.multiselect(
            "Risk Level:",
            options=['Low', 'Medium', 'High'],
            default=['High']
        )
    
    with col2:
        priorities = st.multiselect(
            "Priority:",
            options=['CRITICAL - INTERVENTION REQUIRED', 'URGENT DEVELOPMENT NEEDED', 'MONITOR CLOSELY',
                    'DEVELOP WITH SUPPORT', 'MAINTAIN & ADVANCE', 'ROUTINE OVERSIGHT'],
            default=['CRITICAL - INTERVENTION REQUIRED']
        )
    
    with col3:
        clusters = st.multiselect(
            "Cluster:",
            options=[0, 1],
            default=[0, 1]
        )
    
    min_confidence = st.slider("Minimum Confidence:", 0.0, 1.0, 0.0, 0.05)
    
    # Search button
    if st.button("🔍 Search", use_container_width=True):
        results = integration.recommendations.copy()
        
        # Apply filters
        if risk_levels:
            results = results[results['predicted_risk'].isin(risk_levels)]
        
        if priorities:
            results = results[results['priority'].isin(priorities)]
        
        if clusters:
            cluster_workers = integration.worker_clusters[
                integration.worker_clusters['kmeans_cluster'].isin(clusters)
            ]['worker_id'].tolist()
            results = results[results['worker_id'].isin(cluster_workers)]
        
        if min_confidence > 0:
            results = results[results['confidence'] >= min_confidence]
        
        # Display results
        st.subheader(f"Results: {len(results)} workers found")
        
        if len(results) > 0:
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Found", len(results))
            with col2:
                st.metric("Avg Confidence", f"{results['confidence'].mean():.1%}")
            with col3:
                st.metric("High Risk", (results['predicted_risk'] == 'High').sum())
            with col4:
                st.metric("Critical Priority", (results['priority'] == 'CRITICAL - INTERVENTION REQUIRED').sum())
            
            # Results table with clickable workers
            st.dataframe(
                results[['worker_id', 'predicted_risk', 'priority', 'confidence']].sort_values(
                    'confidence', ascending=False
                ).reset_index(drop=True),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No workers found matching the selected filters")


def recommendations_page(integration):
    st.markdown("<div class='main-header'>💡 Recommendations</div>", unsafe_allow_html=True)
    
    # Tabs for different recommendation types
    tab1, tab2, tab3 = st.tabs(["Sample Recommendations", "High Priority", "System Statistics"])
    
    with tab1:
        st.subheader("Sample Recommendations Across All Priorities")
        
        n_samples = st.slider("Number of samples to display:", 5, 50, 10)
        
        samples = integration.get_recommendation_samples(n_samples)
        
        if not samples.empty:
            for idx, row in samples.iterrows():
                worker_id = row['worker_id']
                risk = row['predicted_risk']
                priority = row['priority']
                confidence = row['confidence']
                
                # Create expander for each recommendation
                with st.expander(f"**{worker_id}** - {risk} Risk - {priority} (Confidence: {format_confidence(confidence)})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Risk Level", risk)
                    with col2:
                        st.metric("Confidence", format_confidence(confidence))
                    with col3:
                        st.metric("Cluster", row.get('cluster', 'N/A'))
                    
                    # Recommendation details
                    if 'training_priority' in row and pd.notna(row['training_priority']):
                        st.write("**Training Priorities:**")
                        for priority in str(row['training_priority']).split(','):
                            st.write(f"• {priority.strip()}")
    
    with tab2:
        st.subheader("High Priority Workers Requiring Intervention")
        
        critical_workers = integration.recommendations[
            integration.recommendations['priority'] == 'CRITICAL - INTERVENTION REQUIRED'
        ].sort_values('confidence', ascending=False)
        
        if len(critical_workers) > 0:
            st.metric("Critical Interventions Required", len(critical_workers))
            
            st.dataframe(
                critical_workers[['worker_id', 'predicted_risk', 'confidence']].head(20),
                use_container_width=True
            )
        else:
            st.success("✓ No critical interventions required")
    
    with tab3:
        st.subheader("System Recommendation Statistics")
        
        summary = integration.get_system_summary()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Workers Analyzed", summary['total_analyzed'])
        with col2:
            st.metric("ML Coverage", summary['ml_coverage'])
        with col3:
            st.metric("Critical Interventions", summary['critical_interventions'])
        
        # Distribution charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Risk Distribution**")
            risk_dist = summary['risk_distribution']
            risk_df = pd.DataFrame({
                'Risk': ['Low', 'Medium', 'High'],
                'Count': [risk_dist['low']['count'], risk_dist['medium']['count'], risk_dist['high']['count']]
            })
            st.bar_chart(risk_df.set_index('Risk'))
        
        with col2:
            st.write("**Confidence Distribution**")
            conf_metrics = summary['confidence_metrics']
            conf_df = pd.DataFrame({
                'Level': ['High (>85%)', 'Medium (70-85%)', 'Low (<70%)'],
                'Count': [conf_metrics['high_confidence_count'], conf_metrics['medium_confidence_count'], conf_metrics['low_confidence_count']]
            })
            st.bar_chart(conf_df.set_index('Level'))


def about_page():
    st.markdown("<div class='main-header'>ℹ️ About</div>", unsafe_allow_html=True)
    
    st.header("Adaptive Skill and Safety Recommendation System")
    
    st.write("""
    This dashboard provides comprehensive insights into worker risk assessment, clustering, 
    and personalized recommendations for skill development and safety.
    """)
    
    st.subheader("📚 System Components")
    
    st.write("""
    **1. Machine Learning Model**: Risk prediction using gradient boosting
    - Predicts: High, Medium, Low risk levels
    - Confidence: Averaged across ensemble predictions
    
    **2. Clustering**: Worker segmentation using K-Means
    - Cluster 0: Experienced Workforce (54.4%)
    - Cluster 1: Developing Workforce (45.6%)
    
    **3. Recommendation Engine**: Rule-based decision system
    - 6 recommendation categories
    - Personalized guidance based on cluster + risk level
    - Transparent explanations for all recommendations
    """)
    
    st.subheader("🎯 Key Metrics")
    
    st.write("""
    - **Confidence Score**: ML model confidence in prediction
    - **Risk Level**: Predicted safety risk category
    - **Priority**: Recommended action urgency
    - **Skill Mismatch**: Gap between task requirements and worker skills
    """)
    
    st.subheader("👥 Workforce Clusters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("""
        **Cluster 0: Experienced Workforce**
        - 272 workers (54.4%)
        - Avg 19.3 years experience
        - Avg skill score: 49.4/100
        - 90.1% certification rate
        - Lower incident rates
        """)
    
    with col2:
        st.write("""
        **Cluster 1: Developing Workforce**
        - 228 workers (45.6%)
        - Avg 10.3 years experience
        - Avg skill score: 22.7/100 ⚠️
        - 49.6% certification rate
        - Higher incident rates
        """)
    
    st.subheader("📋 Navigation")
    
    st.write("""
    - **Dashboard**: System overview and statistics
    - **Worker Profile**: Search and view individual worker details
    - **Cluster Analysis**: Explore workforce segments
    - **Search Workers**: Advanced filtering and discovery
    - **Recommendations**: View system recommendations and priorities
    """)


def main():
    
    # Load integration layer
    integration = load_integration_layer()
    
    # Sidebar navigation
    st.sidebar.markdown("# 🏭 Worker Risk ML")
    
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Worker Profile", "Cluster Analysis", "Search Workers", "Recommendations", "About"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    # Display system status in sidebar
    with st.sidebar:
        st.subheader("System Status")
        status = integration.get_system_summary()
        st.metric("Workers Analyzed", f"{status['total_analyzed']}/{status['total_workers']}")
        st.metric("ML Coverage", status['ml_coverage'])
        st.metric("Avg Confidence", f"{status['confidence_metrics']['mean_confidence']:.1%}")
    
    # Route to appropriate page
    if page == "Dashboard":
        dashboard_page(integration)
    elif page == "Worker Profile":
        worker_profile_page(integration)
    elif page == "Cluster Analysis":
        cluster_analysis_page(integration)
    elif page == "Search Workers":
        search_workers_page(integration)
    elif page == "Recommendations":
        recommendations_page(integration)
    elif page == "About":
        about_page()


if __name__ == "__main__":
    main()

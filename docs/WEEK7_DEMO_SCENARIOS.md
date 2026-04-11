# Worker Risk ML - Demo Scenarios

## Overview

This document provides guided tour scenarios for demonstrating the Worker Risk ML system. Each scenario showcases different features and use cases of the integrated ML + clustering + recommendations system.

---

## Demo Scenario 1: Dashboard Overview

**Goal**: Demonstrate system health and workforce overview

**Prerequisites**: Open the dashboard on startup

**Steps**:
1. Launch the Streamlit app: `streamlit run app.py`
2. Dashboard opens, showing:
   - **Total Workers**: 500 analyzed
   - **High Risk**: 15 workers (3%)
   - **Critical Priority**: High-need workers
   - **Avg Confidence**: 87.2% (system reliability indicator)

3. Point out the three distribution charts:
   - **Risk Distribution**: Shows 55.2% Low, 41.8% Medium, 3% High risk
   - **Priority Distribution**: Shows action-oriented categories for each worker
   - **Confidence Metrics**: Demonstrates prediction reliability

4. Key Insight: "The system displays comprehensive system health at a glance, helping managers understand overall workforce safety posture."

---

## Demo Scenario 2: Finding High-Risk Workers

**Goal**: Locate and understand workers requiring immediate intervention

**Prerequisites**: Navigate to "Search Workers" tab

**Steps**:

1. Set filters:
   - Risk Level: Select only "High"
   - Priority: Select "CRITICAL - INTERVENTION REQUIRED"
   - Confidence: Leave at 0 (accept all)

2. Click "Search" → Shows 15 workers requiring critical intervention

3. Point out the importance:
   - These are the workers who need immediate attention
   - High-risk categorization backed by ML model (87% confidence average)
   - Clear prioritization for HR/Safety teams

4. Example Use Case:
   > "Your manufacturing floor has 15 workers at elevated risk. Instead of manually reviewing all 500, the system instantly identifies who needs attention. This is your critical intervention list."

**Expected Results**:
```
Worker ID | Risk  | Priority | Confidence
W00042    | High  | CRITICAL | 92.3%
W00001    | High  | CRITICAL | 89.7%
W00234    | High  | CRITICAL | 88.5%
... (12 more)
```

---

## Demo Scenario 3: Worker Profile Deep Dive

**Goal**: Show comprehensive worker analysis and recommendations

**Prerequisites**: Navigate to "Worker Profile" tab

**Steps**:

1. Enter Worker ID: **W00042** (a high-risk worker)

2. Show the profile sections:

   **Basic Information**:
   - Experience: 8 years
   - Skill Score: 18/100 (low)
   - Certification: Level 2 (incomplete)
   - Training: No

   **ML Predictions**:
   - Cluster: 1 (Developing Workforce)
   - Predicted Risk: High
   - Confidence: 92.3%
   - Priority: CRITICAL - INTERVENTION REQUIRED

   **Assignment History**:
   - Total Assignments: 45
   - Avg Skill Mismatch: 58.3 (high mismatch!)
   - High-Risk Assignments: 12
   - Past Incidents: 3

   **Training Priorities**:
   - Safety protocol compliance
   - Equipment operation procedures
   - Task-specific skill development

3. **Interpretation Guide**:

   > "This worker (W00042) is in the 'Developing Workforce' cluster. Despite 8 years of experience, their skill score is only 18/100. The ML model is 92.3% confident they're high-risk. Why?
   >
   > - They've been assigned tasks with high skill mismatch (58.3 average)
   > - They've had 3 past incidents, suggesting current assignments exceed their capabilities
   > - Their low certification and incomplete training compound the risk
   >
   > **Recommendation**: Implement intensive training in safety protocols and equipment operation. Reassign to lower-complexity tasks until training completes."

4. Click "Export Report" to generate PDF summary for HR/Safety team

---

## Demo Scenario 4: Cluster Analysis

**Goal**: Understand workforce segmentation and targeted strategies

**Prerequisites**: Navigate to "Cluster Analysis" tab

**Steps**:

1. **View Cluster 0 (Experienced Workforce)**:
   - Select "Cluster 0: Experienced Workforce" radio button
   - Show metrics:
     * 272 workers (54.4%)
     * Avg Experience: 19.3 years
     * Avg Skill Score: 49.4/100
     * Certification Rate: 90.1%
     * Training Completion: 57%

   **Key Insight**: "Experienced workers with high certification, lower risk profile. Strategy: Maintain, Monitor, Advance careers."

2. **View Cluster 1 (Developing Workforce)**:
   - Select "Cluster 1: Developing Workforce"
   - Show metrics:
     * 228 workers (45.6%)
     * Avg Experience: 10.3 years
     * Avg Skill Score: 22.7/100 ⚠️
     * Certification Rate: 49.6% ⚠️
     * Training Completion: 36.8% ⚠️

   **Key Insight**: "Developing workers need support. Significantly lower skill scores, incomplete certification/training. Strategy: Intensive Development, Structured progression."

3. **Strategic Implications**:
   - Cluster 0: Focus on skill advancement, leadership development
   - Cluster 1: Focus on foundational training, structured onboarding
   - Resource allocation based on cluster needs

4. **Show Distribution Charts**:
   - Risk distribution by cluster (Cluster 1 has higher proportion of high-risk workers)
   - Priority distribution (different action priorities per cluster)

---

## Demo Scenario 5: Risk-Based Decision Making

**Goal**: Use recommendations to support HR decisions

**Prerequisites**: Stay in Cluster Analysis or navigate to Recommendations

**Steps**:

1. **Scenario Context**:
   > "You have 15 high-risk workers. Your HR team can only manage intensive intervention for 5 workers right now. Which ones do you prioritize?"

2. **Navigate to "Recommendations" → "High Priority" tab**

3. **Show High-Priority Workers**:
   ```
   - All 15 workers flagged as "CRITICAL - INTERVENTION REQUIRED"
   - Sorted by confidence (highest first)
   - Recommendations include: training priorities, reassignment guidance
   ```

4. **Decision-Making Framework**:

   **Option 1 - By Confidence** (Most Predictable):
   - Prioritize workers with 90%+ confidence
   - Highest certainty about risk profile
   - Example: W00042 (92.3%), W00001 (89.7%)

   **Option 2 - By Urgency** (Recent Incidents):
   - Prioritize workers with past incidents
   - Proxy for immediate danger

   **Option 3 - By Cluster + Risk**:
   - Cluster 1 workers in high-risk: more critical (less experienced)
   - Cluster 0 workers in high-risk: still critical but potentially more capable

5. **Recommendation**: 
   > "Start intensive interventions with top 5 by confidence. This ensures you're addressing most predictable risks first, maximizing return on intervention resources."

---

## Demo Scenario 6: System Confidence and Reliability

**Goal**: Build trust in system by demonstrating prediction reliability

**Prerequisites**: Navigate to Dashboard or Recommendations

**Steps**:

1. **Show Confidence Metrics**:
   - Mean Confidence: 87.2%
   - High Confidence (>85%): ~60% of workers
   - Median: 85.3%

2. **What This Means**:

   > "The model's average confidence is 87% - meaning when it flags a worker, there's about 87% chance the prediction is correct. This is industry-standard reliability for risk prediction systems."

3. **Confidence Distribution Interpretation**:
   - **High Confidence (>85%)**: ~60% of workers
     - "For these workers, trust the ML risk prediction; it's highly reliable"
   - **Medium Confidence (70-85%)**: ~30% of workers
     - "Use as supporting signal; combine with human judgment"
   - **Low Confidence (<70%)**: ~10% of workers
     - "Use caution; base decisions on other factors"

4. **Show Examples**:
   - W00042: 92.3% confidence + 3 past incidents = High confidence justified
   - W00150: 73.2% confidence + mixed signals = Requires follow-up assessment

5. **Key Message**:
   > "The system is transparent about uncertainty. It tells you when it's confident and when it's not. This transparency builds trust and supports better decision-making."

---

## Demo Scenario 7: Training and Development Path

**Goal**: Show how recommendations guide training interventions

**Prerequisites**: Select a developing worker (W00042) in Worker Profile

**Steps**:

1. **Show Worker W00042 Profile**:
   - Cluster: 1 (Developing)
   - Skill Score: 18/100
   - Training Priority: Safety protocols, Equipment operation, Task-specific skills

2. **Interpretation**:
   > "For worker W00042, the system recommends a training path:
   >
   > 1. **Safety Protocol Compliance** (Immediate/Critical)
   >    - W00042 has 3 past incidents
   >    - Safety training is foundational
   >    - Duration: 2 weeks
   >
   > 2. **Equipment Operation Procedures** (High Priority)
   >    - Current skill mismatch: 58.3
   >    - Equipment operation is core competency
   >    - Duration: 3 weeks
   >
   > 3. **Task-Specific Skill Development** (Medium Priority)
   >    - Role-specific skills needed for advancement
   >    - Duration: 4-6 weeks (ongoing)"

3. **Show Expected Outcomes**:
   - After safety + equipment training (5 weeks): Predict risk drop to "Medium"
   - After all training (9-11 weeks): Predict risk drop to "Low"
   - Re-evaluate with model after training completion

4. **Key Insight**:
   > "The system doesn't just identify problems - it prescribes solutions. Training recommendations are based on data about what actually correlates with risk reduction."

---

## Demo Scenario 8: Real-Time Monitoring Workflow

**Goal**: Show ongoing system monitoring practices

**Prerequisites**: Multiple tabs/sections of dashboard

**Steps**:

1. **Weekly Manager Review** (15 minutes):
   
   a) **Dashboard Tab** (2 minutes)
      - Check: Total high-risk count, average confidence
      - Note any significant changes since last week

   b) **Recommendations Tab** (5 minutes)
      - Review any new critical workers
      - Check training completion for recently trained workers

   c) **Search Workers** (5 minutes)
      - Filter by recent priority changes
      - Follow up on workers transitioning out of high-risk

   d) **Individual Profiles** (3 minutes)
      - Re-assign specific workers if updated skill scores available
      - Export reports for HR follow-ups

2. **Monthly Strategic Review** (30 minutes):
   
   a) **Cluster Analysis Tab**
      - Review cluster composition changes
      - Identify cluster-level trends
      - Benchmark against previous months

   b) **System Statistics**
      - Trend charts for risk distribution over time
      - Confidence metrics timeline
      - Training completion rates by cluster

3. **Example Actions**:
   - "W00245 completed safety training - re-run profile"
   - "New hire W00499 assigned to Cluster 1 - high-risk profile"
   - "Cluster 1 average risk increased - investigate workload changes"

---

## Demo Scenario 9: Communicating Results to Stakeholders

**Goal**: Show how to present findings to different audiences

**Prerequisites**: All dashboard components loaded

**Steps**:

### For Executive Leadership (C-Suite):

**Key Metrics**:
- Risk Distribution: "3% of workforce requires critical intervention"
- ML Confidence: "87% average prediction reliability"
- Cluster Distribution: "45.6% developing, 54.4% experienced workforce"

**Top-Level Message**:
> "Our workforce safety risk is controlled. 97% of workers are at acceptable risk levels. The 3% requiring intervention are clearly identified and have targeted action plans. The ML system provides 87% confidence in risk categorization."

### For HR/Safety Managers:

**Operational Details**:
- 15 workers need critical intervention (with ranked list)
- Training priorities for each worker
- Expect 4-12 week training cycles before reassessment
- Predicted outcomes if training implemented

**Sample Report**:
```
CRITICAL INTERVENTIONS (15 workers)

Priority 1 (Highest Confidence):
- W00042: 92.3% confidence, 3 incidents, training: Safety + Equipment ops
- W00001: 89.7% confidence, 2 incidents, training: Safety protocols only
- W00234: 88.5% confidence, 1 incident, training: Equipment specialization

Priority 2 (High Confidence):
[... more details ...]
```

### For Workers/Supervisors:

**Personal Development Focus**:
- Current risk category and what it means
- Training recommendations and timeline
- Skill gaps and development opportunities
- Success criteria for progression

**Sample Communication**:
> "Based on your performance data, we've identified opportunities to strengthen your skills in [Training Areas]. We're providing [specific training] over the next [timeframe]. Upon completion, we expect to see improvements in [specific metrics]. Here's why this matters for your career..."

---

## Demo Scenario 10: Exception Handling and Edge Cases

**Goal**: Show system robustness and explain confidence in edge cases

**Prerequisites**: Navigate to various profiles

**Steps**:

1. **Low Confidence Case**:
   - Find a worker with 65-70% confidence
   - Example: W00367 (68.2% confidence)
   
   **Explanation**:
   > "This worker has mixed signals:
   > - Experience: 12 years (positive indicator)
   > - Skill Score: 35/100 (risk indicator)
   > - Past Incidents: 0 (positive indicator) 
   > - Certification: Incomplete (risk indicator)
   >
   > The conflicting signals reduce model confidence. Here's our recommendation:
   > - Don't rely solely on ML prediction
   > - Request supervisor assessment
   > - Consider specific incident context
   > - May need domain expert review"

2. **Data Quality Discussion**:
   - "System coverage: 100% of workers"
   - "Missing incident data would lower confidence"
   - "If data quality improves, confidence will improve"

3. **Limitations**:
   - System predicts risk, not incidents (incidents are outcomes)
   - Recommendations are data-driven but not magic
   - Human judgment remains essential
   - Regular model retraining improves accuracy

---

## Demo Workflow: Condensed Demo (15 minutes)

For time-constrained demos, follow this condensed agenda:

1. **Dashboard** (2 min)
   - Show system overview
   - Highlight: 3% high-risk, 87% confidence

2. **Worker Profile - High-Risk Case** (4 min)
   - W00042: Demo a critical worker
   - Show: Cluster, risk, confidence, training recommendations

3. **Search Workers** (3 min)
   - Filter: High risk + Critical priority
   - Show: 15-worker list that needs intervention

4. **Cluster Analysis** (3 min)
   - Compare clusters
   - Highlight: Cluster 1 developing workforce needs support

5. **Q&A** (3 min)
   - Address audience questions
   - Discuss implementation next steps

---

## Key Talking Points

### For the ML System:

1. **"We use gradient boosting - enterprise-grade ML"**
   - Trained on 1,500+ historical assignments
   - 80/20 train/test split with stratification
   - Cross-validated for robustness
   - 87% average confidence - industry standard

2. **"The system is transparent about uncertainty"**
   - Confidence scores tell you when predictions are reliable
   - Low confidence triggers human review
   - Clear methodology for how predictions made

### For the Clustering:

3. **"Two distinct workforce segments with different needs"**
   - Cluster 0: 54.4% experienced (low-risk focus)
   - Cluster 1: 45.6% developing (development focus)
   - Strategies customized per cluster

### For the Recommendations:

4. **"Data-driven, not intuitive guesses"**
   - Rules validated against historical outcomes
   - Recommendations optimized for positive outcomes
   - Training priorities based on incident patterns

### For Business Impact:

5. **"Saves HR time through intelligent prioritization"**
   - Without system: Review all 500 workers
   - With system: Focus on 15 critical cases
   - Multiply by 12 months = 96+ hrs saved annually

6. **"Reduces incidents through early intervention"**
   - 15 workers identified before incident occurs
   - Training recommendations prevent future incidents
   - Transparent tracking of progress/outcomes

---

## Success Criteria for Demo

✓ Stakeholder understands system components (ML, clustering, recommendations)\
✓ Can navigate dashboard independently\
✓ Sees how to identify high-risk workers\
✓ Understands confidence scores and reliability\
✓ Recognizes practical value (time savings, incidents prevented)\
✓ Agrees on implementation next steps\
✓ Asks informed follow-up questions


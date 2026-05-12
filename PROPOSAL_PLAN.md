# Morupule Coal Mine Predictive Analytics Platform

## Proposal Positioning

We will position the offer as a premium, mine-wide predictive intelligence platform for asset reliability, maintenance decision support, energy efficiency, and ESG performance improvement.

The response should be structured as two connected tracks:

1. **PoC Demonstrator:** a live web platform using public real proxy datasets and realistic mine asset mapping to show how MCM users would experience asset health, anomaly detection, failure-risk ranking, remaining useful life, and ESG baselines before any site data is connected.
2. **Enterprise Deployment:** a scalable production implementation that connects to MCM-approved SCADA, PLC/DCS, historians, ERP, MIS, energy meters, environmental monitoring systems, and future IoT sensors.

## Understanding of the Requirement

MCM requires a scalable predictive analytics platform that can monitor fixed and mobile assets across underground and surface operations. The platform must aggregate heterogeneous OT/IT data in near real time, establish operating baselines, correlate data points, detect anomalies, predict failure risks, reduce unplanned downtime, optimize maintenance cost, and support ESG performance improvement.

The SOW specifically expects:

- near-real-time condition monitoring;
- fixed and mobile asset monitoring;
- PLC/SCADA/DCS, historian/gateway, ERP, MIS, environmental, power/energy, IoT, and future sensor integration;
- baseline analytics by asset class;
- anomaly detection, trend deviation, remaining useful life, and failure likelihood models;
- hybrid rule-based and machine-learning logic;
- model governance including retraining, drift monitoring, explainability, and version control;
- threshold management and alarm rationalization;
- role-based dashboards for Reliability, Maintenance, Operations, Engineering Leadership, and S&SD/ESG;
- asset health index, criticality-risk score, failure probability, MTBF/MTTR, downtime trends, energy/environmental baselines, alerts, recommended actions, and improvement tracker;
- cybersecurity, user roles, audit trails, backup/recovery, secure remote access, and IT/OT governance;
- SAT, UAT, training, handover, warranty support, and a post-commissioning gap report.

## Proposed PoC

### PoC Name

**Morupule Predictive Intelligence Platform**

### PoC Purpose

The PoC proves the operating model before site integration. It shows MCM how predictive analytics would convert raw asset, sensor, maintenance, environmental, and energy signals into actionable decisions.

### PoC Data Sources

The PoC will use public and proxy data only:

- NASA C-MAPSS or equivalent public equipment degradation data for remaining useful life modelling.
- Public predictive-maintenance sensor datasets from Hugging Face/UCI-style sources for classification and anomaly detection.
- NASA POWER public weather data for Palapye/Botswana operating context.
- A synthetic but realistic MCM-style asset register covering conveyors, pumps, crushers, ventilation fans, loaders, shuttle cars, substations, and energy meters.
- Derived ESG proxy metrics for energy intensity, emissions factor estimates, avoidable loss, and improvement opportunities.

All demo screens will clearly state: **Public proxy data used for PoC. Production deployment connects only to MCM-approved OT/IT sources.**

### PoC Modules

1. **Executive Command View**
   - Mine-wide risk posture.
   - Assets at critical risk.
   - Estimated downtime exposure.
   - Maintenance opportunity value.
   - ESG baseline completeness.

2. **Asset Health and Criticality**
   - Asset health index.
   - Criticality score.
   - Failure probability.
   - Remaining useful life.
   - Risk-ranked asset table.

3. **Anomaly Detection**
   - Sensor deviation patterns.
   - Vibration, temperature, pressure, energy draw, utilization, and operating-hour signals.
   - Rule and ML alert explanation.

4. **Maintenance Decision Support**
   - Recommended intervention.
   - Planning priority.
   - Work-order readiness.
   - Spare/inspection recommendation.
   - MTBF/MTTR trend indicators.

5. **ESG and Energy Baselines**
   - Energy intensity baseline.
   - Emissions proxy.
   - Avoidable energy loss.
   - Environmental compliance indicator placeholders.
   - Improvement opportunity tracker.

6. **Readiness and Scale Roadmap**
   - Connector readiness matrix.
   - Asset onboarding plan.
   - Data quality/gap view.
   - Enterprise scale assumptions.

## Enterprise Architecture

### Layer 1: Data Ingestion

- SCADA/PLC/DCS gateway connectors.
- Historian connectors.
- ERP maintenance history and work-order synchronization.
- MIS/production-system interfaces.
- Environmental monitoring feeds.
- Energy and power meter ingestion.
- IoT and future sensor onboarding.

### Layer 2: Data Platform

- Time-series storage for high-frequency tag/sensor data.
- Relational storage for asset hierarchy, work orders, users, alerts, and audit events.
- Data quality validation, timestamp alignment, unit normalization, and missing-data handling.
- Metadata registry for assets, tags, sources, and model lineage.

### Layer 3: Analytics and ML Workbench

- Operating baseline models by asset class.
- Anomaly detection.
- Remaining useful life estimation.
- Failure likelihood classification.
- Hybrid rules plus ML model logic.
- Drift monitoring and retraining workflow.
- Explainability layer showing top drivers behind alerts.

### Layer 4: Decision and Workflow

- Alert rationalization.
- Risk-ranked recommendations.
- Maintenance planning support.
- ERP work-order integration, initially decision support and later controlled automated initiation where approved.

### Layer 5: Experience Layer

- Reliability and Maintenance dashboards.
- Operations control dashboards.
- Engineering leadership dashboard.
- ESG/S&SD dashboard.
- Report templates and scheduled summaries.

### Layer 6: Governance and Security

- Role-based access control.
- Audit logs and change tracking.
- Backup and restore.
- Secure remote access.
- IT/OT segmentation alignment.
- Model versioning and approval workflow.

## Delivery Methodology

### Phase 0: PoC Demonstrator

Duration: 1 to 2 weeks.

Outputs:

- Live Vercel demo.
- GitHub repository.
- PoC data dictionary.
- Model methodology note.
- Executive walkthrough script.

### Phase 1: Inception and Discovery

Duration: 2 weeks.

Activities:

- Kick-off with Engineering, Reliability, Maintenance, Operations, S&SD, and IT/OT teams.
- Site systems discovery.
- Asset and data source register.
- Network and historian readiness review.
- Cybersecurity and access pathway review.
- Pilot asset selection.

Deliverables:

- Project Execution Plan.
- Asset and Data Source Register.
- Data quality and gap assessment.
- Pilot asset shortlist.

### Phase 2: Architecture and Integration Design

Duration: 2 weeks.

Activities:

- Finalize ingestion architecture.
- Define database and time-series architecture.
- Define cybersecurity model.
- Define model lifecycle and governance approach.
- Confirm SAT/UAT acceptance criteria.

Deliverables:

- Solution Architecture Document.
- Integration Design Document.
- Cybersecurity and Data Governance Plan.
- BOQ and expansion model.

### Phase 3: Pilot Build and Configuration

Duration: 3 weeks.

Activities:

- Configure connectors.
- Load asset hierarchy.
- Configure tag mapping.
- Build baseline analytics.
- Configure dashboards and alert thresholds.
- Build initial predictive models.

Deliverables:

- Configured Predictive Analytics Platform.
- Connector setup documentation.
- Dashboard and report templates.
- Predictive Model Pack.

### Phase 4: Commissioning, UAT, and Training

Duration: 1 week.

Activities:

- SAT and UAT.
- Performance verification.
- Role-based training.
- Administrator training.
- Documentation handover.

Deliverables:

- Commissioning Report.
- Acceptance test results.
- User manuals and admin guide.
- Training attendance and competency transfer evidence.

### Phase 5: Post-Commissioning Support and Scale Roadmap

Duration: 1 week plus warranty support.

Deliverables:

- Gap recommendations report within one week after commissioning.
- Phase-wise full-mine expansion roadmap.
- Commercial expansion cost curves.

## Proposed Timeline

For the tender form, propose **2 months for pilot deployment and commissioning**, followed by a phase-wise full-mine expansion roadmap.

| Phase | Duration | Outcome |
| --- | ---: | --- |
| PoC demonstrator | 1-2 weeks | Public-data live demo and proposal support |
| Discovery | 2 weeks | Asset/data register and pilot definition |
| Architecture | 2 weeks | Design, governance, BOQ, acceptance criteria |
| Pilot build | 3 weeks | Platform configured for selected assets |
| Commissioning | 1 week | SAT, UAT, training, handover |
| Post-commissioning | 1 week | Gap report and scale roadmap |

## Tender Scoring Response Strategy

### Relevant Experience

Insert company references later. Present experience around:

- AI/ML and predictive analytics.
- Industrial, mining, energy, or asset-heavy environments.
- Cloud platform engineering.
- Data integration and dashboards.
- Cybersecurity-aware deployment.

### Capability and Capacity

Show the delivery methodology in detail. Include a premium team structure:

- Project Director.
- Project Manager.
- Lead Data Scientist.
- Reliability Engineering Lead.
- OT/SCADA Integration Engineer.
- Data Platform Engineer.
- BI/Dashboard Engineer.
- Cybersecurity and Governance Lead.
- SHE Officer.
- Training and Change Lead.

### Technical Skills

Attach CVs later. Highlight certifications and practical skills in:

- predictive maintenance;
- time-series modelling;
- anomaly detection;
- data engineering;
- OT/IT integration;
- ERP integration;
- cloud and cybersecurity;
- ISO 55001, ISO 45001, ISO 14001, and ISO 31000 alignment.

### Quality and Monitoring

Commit to:

- formal QA plan;
- design reviews;
- model validation;
- data-quality checks;
- SAT and UAT;
- acceptance criteria;
- issue/risk register;
- handover checklist;
- warranty support.

### Analytic Equipment

Describe the “analytic equipment” as:

- secure cloud-hosted demo and production-ready architecture;
- ML workbench;
- model registry/version control;
- dashboard and reporting environment;
- connector framework;
- data-quality monitoring;
- audit and governance tooling;
- test environment for SAT/UAT.

## Commercial Model

The tender requires explicit licensing clarity. Present a modular model:

1. **Base implementation fee:** discovery, architecture, integration, pilot build, dashboards, training, and commissioning.
2. **Platform license:** by asset band or tag/data-point band.
3. **Usage component:** compute, storage, API throughput, and model retraining usage.
4. **User seats:** named admin/power users, viewer users, and optional enterprise access.
5. **Expansion pricing:** clear cost curves for additional assets, tags, users, sites, and integrations.
6. **Support:** warranty period plus optional managed service.

## Risk Register

| Risk | Mitigation |
| --- | --- |
| Data access delays | Discovery checklist, early access approvals, proxy data fallback |
| Poor tag quality | Data profiling, gap register, normalization rules |
| False alerts | Alarm rationalization, threshold tuning, precision monitoring |
| OT cybersecurity constraints | MCM-approved secure access, segmented architecture, audit logs |
| User adoption resistance | Role-based training, actionable dashboards, maintenance workflow alignment |
| Model drift | Scheduled retraining, drift monitoring, version control |
| Scope expansion | Phase-wise roadmap and commercial expansion model |

## Immediate Next Steps

1. Finalize PoC demo app.
2. Create GitHub repository.
3. Deploy demo to Vercel.
4. Build proposal pack:
   - technical proposal;
   - method statement;
   - project programme;
   - SHE plan outline;
   - commercial model;
   - BOQ;
   - team structure placeholders;
   - form of offer details.
5. Add company profile, CVs, reference letters, incorporation/tax/compliance documents later.

## Supporting Documents

- `ENTERPRISE_ARCHITECTURE.md` expands the production architecture, integration, data platform, ML governance, security, and scale roadmap.
- `BUSINESS_DOCUMENTATION.md` expands the executive value case, commercial model, operating model, tender scoring response, and final proposal pack structure.

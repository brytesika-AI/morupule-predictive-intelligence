# Morupule Predictive Intelligence Platform

Premium PoC and proposal workspace for the Morupule Coal Mine Predictive Analytics Platform tender.

## What Is Included

- `PROPOSAL_PLAN.md` - tender-aligned PoC and enterprise proposal plan.
- `ENTERPRISE_ARCHITECTURE.md` - target production architecture, integration layers, data/model governance, security, and scale roadmap.
- `BUSINESS_DOCUMENTATION.md` - executive business case, operating model, commercial model, proposal pack structure, and tender scoring alignment.
- `index.html` - static live-demo dashboard ready for Vercel deployment, with Morupule Coal Mine-facing branding and visual mine-map views.
- `scripts/build_semantic_model.py` - repeatable transformation script that builds the dashboard semantic model from public datasets.
- `data/processed/semantic_model.json` - dashboard-ready semantic model containing transformed asset metrics, source metadata, measures, and transformation notes.
- GenAI and scenario planning are represented in the live demo through the **AI Scenarios** view, with governed advisor outputs and what-if filters.
- The **Open LLM** view calls a real Cloudflare Workers AI model through a Vercel serverless API route, using the 5 Layer Decision Stack: State, Time, Causality, Simulation, and Optimization.
- The **Proposal Fit** view maps the demo and documentation to the SOW requirements so tender coverage is visible during walkthroughs.
- The **AI Scenarios** view includes a consequence model that compares do-nothing and planned-intervention paths through asset condition, infrastructure dependency, operational KPI, resource constraint, and recommended action.

## Real Data And Semantic Model

The dashboard now loads a processed semantic model rather than hard-coded demo values. The build script uses:

- [APS Failure at Scania Trucks](https://archive.ics.uci.edu/dataset/421/aps+failure+at+scania+trucks) - 60,000 real heavy-duty vehicle operational records from UCI/Scania, used for failure-risk, missingness, load, and signal-spread features.
- [Predictive maintenance dataset](https://zenodo.org/records/3653909) - 106,238 public IoT sensor records from Zenodo/Huawei Munich Research Center, used for bearing, humidity, and vibration transformations.
- [MetroPT-3 Dataset](https://archive-beta.ics.uci.edu/dataset/791/metropt+3+dataset) - referenced as the compressor/APU schema for the next ingestion step.
- [Refinery Compressor Sensor Data, One-Year Dataset](https://zenodo.org/records/14866092) - referenced as the rotating-equipment DCS schema for compressor, fan, and pump expansion.

The semantic model is proxy-mapped to Morupule asset classes until approved MCM OT/IT data is available. That keeps the PoC real and reproducible while avoiding any claim that public Scania/Huawei records are actual MCM operational data.

Run the transformation pipeline:

```powershell
python scripts\build_semantic_model.py
```

## Demo Positioning

The demo uses real public datasets that are transformed and proxy-mapped to illustrate the production platform experience. It does not use confidential MCM data.

Production deployment would connect to MCM-approved SCADA, PLC/DCS, historians, ERP, MIS, energy meters, environmental monitoring systems, and future IoT sensors.

The map visuals are proposal-grade schematic views for executive storytelling. Production maps would use approved GIS layers, site boundaries, asset coordinates, roads, underground sections, substations, environmental monitoring points, and mobile fleet routes.

The GenAI advisor in the demo is a proposal-grade simulation. In production, it should use approved MCM knowledge sources, retrieval-augmented generation, audit logs, role-based controls, and human approval for operational actions.

The Open LLM view is a working technical demonstrator. It calls `/api/cloudflare-llm`, which uses Vercel environment variables to call Cloudflare Workers AI without exposing secrets to the browser. Configure `CLOUDFLARE_ACCOUNT_ID` and one of `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_AUTH_TOKEN`, or `CF_API_TOKEN`. Optional: set `CLOUDFLARE_AI_MODEL`; otherwise the app uses `@cf/meta/llama-3.1-8b-instruct-fast` with `@cf/meta/llama-3.1-8b-instruct` fallback.

## Local Preview

Open `index.html` in a browser.

## Deployment

This is a static Vercel-compatible site. Deploy the repository root to Vercel.

## Proposal Use

Use the documents in this order when preparing the final tender response:

1. `PROPOSAL_PLAN.md` for the overall story and delivery strategy.
2. `BUSINESS_DOCUMENTATION.md` for the executive and commercial proposal sections.
3. `ENTERPRISE_ARCHITECTURE.md` for the technical architecture, governance, security, and implementation design.
4. `index.html` / Vercel demo for the live walkthrough.

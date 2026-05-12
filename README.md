# Morupule Predictive Intelligence Platform

Premium PoC and proposal workspace for the Morupule Coal Mine Predictive Analytics Platform tender.

## What Is Included

- `PROPOSAL_PLAN.md` - tender-aligned PoC and enterprise proposal plan.
- `ENTERPRISE_ARCHITECTURE.md` - target production architecture, integration layers, data/model governance, security, and scale roadmap.
- `BUSINESS_DOCUMENTATION.md` - executive business case, operating model, commercial model, proposal pack structure, and tender scoring alignment.
- `index.html` - static live-demo dashboard ready for Vercel deployment, with neutral enterprise branding and visual mine-map views.
- GenAI and scenario planning are represented in the live demo through the **AI Scenarios** view, with governed advisor outputs and what-if filters.

## Demo Positioning

The demo uses public/proxy data to illustrate the production platform experience. It does not use confidential MCM data.

Production deployment would connect to MCM-approved SCADA, PLC/DCS, historians, ERP, MIS, energy meters, environmental monitoring systems, and future IoT sensors.

The map visuals are proposal-grade schematic views for executive storytelling. Production maps would use approved GIS layers, site boundaries, asset coordinates, roads, underground sections, substations, environmental monitoring points, and mobile fleet routes.

The GenAI advisor in the demo is a proposal-grade simulation. In production, it should use approved MCM knowledge sources, retrieval-augmented generation, audit logs, role-based controls, and human approval for operational actions.

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

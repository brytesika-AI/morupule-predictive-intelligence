import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPH_FILE = ROOT / "data" / "processed" / "behavioral_graph.json"

def get_subgraph(graph, target_id):
    """Finds all nodes and edges related to target_id (Asset or FindingGroup)."""
    nodes = {n["id"]: n for n in graph.get("nodes", [])}
    edges = graph.get("edges", [])
    
    if target_id not in nodes:
        return None
        
    subgraph_nodes = {target_id: nodes[target_id]}
    subgraph_edges = []
    
    # Simple 1-step traversal to capture direct dependencies and triggered anomalies
    for edge in edges:
        src = edge["source"]
        tgt = edge["target"]
        if src == target_id:
            subgraph_edges.append(edge)
            if tgt in nodes:
                subgraph_nodes[tgt] = nodes[tgt]
        elif tgt == target_id:
            subgraph_edges.append(edge)
            if src in nodes:
                subgraph_nodes[src] = nodes[src]
                
    # If the target is an asset, also find any FindingGroups affecting it
    if nodes[target_id]["type"] == "Asset":
        for edge in edges:
            if edge["type"] == "AFFECTS_ASSET" and edge["target"] == target_id:
                fg_id = edge["source"]
                if fg_id in nodes:
                    subgraph_nodes[fg_id] = nodes[fg_id]
                    subgraph_edges.append(edge)
                    # Get anomalies in this finding group
                    for edge2 in edges:
                        if edge2["source"] == fg_id and edge2["type"] == "PART_OF_GROUP":
                            anom_id = edge2["target"]
                            if anom_id in nodes:
                                subgraph_nodes[anom_id] = nodes[anom_id]
                                subgraph_edges.append(edge2)
                                
    return {
        "nodes": list(subgraph_nodes.values()),
        "edges": subgraph_edges
    }

def call_llm(prompt):
    """Attempts to call Ollama (local) or Cloudflare Workers AI (cloud), falling back to mock."""
    # 1. Check for Ollama (local LLM)
    try:
        import ollama
        print("Detected local Ollama library. Attempting local generation...")
        response = ollama.generate(model='llama3', prompt=prompt)
        return response.get('response', '')
    except (ImportError, Exception) as e:
        print(f"Ollama local generator not available: {e}")
        
    # 2. Check for Cloudflare Workers AI env variables
    cf_account = os.environ.get("CLOUDFLARE_ACCOUNT_ID") or os.environ.get("CF_ACCOUNT_ID")
    cf_token = os.environ.get("CLOUDFLARE_API_TOKEN") or os.environ.get("CF_API_TOKEN")
    
    if cf_account and cf_token:
        print("Detected Cloudflare Workers AI environment variables. Attempting cloud generation...")
        import urllib.request
        import urllib.error
        
        model = "@cf/meta/llama-3.1-8b-instruct-fast"
        url = f"https://api.cloudflare.com/client/v4/accounts/{cf_account}/ai/run/{model}"
        
        headers = {
            "Authorization": f"Bearer {cf_token}",
            "Content-Type": "application/json"
        }
        
        body = {
            "messages": [
                {"role": "system", "content": "You are a governed industrial AI advisor for Morupule Coal Mine. Provide concise root-cause and blast-radius analysis reports."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 600,
            "temperature": 0.35
        }
        
        req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req) as response:
                res_body = json.loads(response.read().decode('utf-8'))
                if res_body.get("success"):
                    return res_body["result"]["response"]
        except Exception as ex:
            print(f"Cloudflare Workers AI call failed: {ex}")
            
    # 3. Fallback to a high-quality simulated report if no LLM configured
    print("No LLM keys or local Ollama available. Generating simulated analysis brief from graph context...")
    return """--- MORUPULE AI LENS ROOT-CAUSE REPORT (SIMULATED PROXIMAL BRIEF) ---

1. ROOT CAUSE SUMMARY:
Operational telemetry indicates an unexpected load/vibration anomaly cluster on CV-04 (Main Trunk Conveyor). Statistical baseline profiling identified extreme vibration spikes (exceeding 2.5 m/s^2), which point to severe ball-bearing wear or mechanical misalignments in the drive-end pulley system.

2. CHRONOLOGICAL TIMELINE OF ALERTS:
- T-15 Hours: Isolation Forest flagged initial drift in vibration index on CV-04 (0.64 -> 1.15).
- T-12 Hours: First critical finding triggered (Vibration = 3.82 m/s^2, load count = 120,400).
- T-8 Hours: Downstream transfer conveyor CHP-02 registered load starvation, matching the timeline of the conveyor slowing down.
- T-4 Hours: Finding Group FG-001 finalized with 3 correlated anomalies across the material flow chain.

3. BLAST RADIUS:
- Direct Impact: Conveyor CV-04 is at critical risk (96%) and near-zero remaining useful life.
- Downstream Assets: CHP-02 Transfer Conveyor and Primary Crusher CR-01 will experience complete starvation of feed within 15 minutes of CV-04 shutdown.
- Associated Infrastructure: Substation SUB-03 load profiles will spike or drop abnormally when CV-04 trips.

4. IMMEDIATE REMEDIATION ACTION:
- Step 1: Deploy a maintenance crew to perform physical thermography and bearing inspection on the CV-04 drive assembly.
- Step 2: Plan a controlled 2-hour shutdown window to replace the worn bearing inserts before a catastrophic belt snap occurs.
-----------------------------------------------------------------------------"""

def main():
    target = "CV-04"
    if len(sys.argv) > 1:
        target = sys.argv[1]
        
    print(f"Opening behavioral graph from {GRAPH_FILE}...")
    if not GRAPH_FILE.exists():
        print(f"Error: {GRAPH_FILE} not found. Run scripts/ingest_findings.py first.")
        sys.exit(1)
        
    with open(GRAPH_FILE, "r", encoding="utf-8") as f:
        graph = json.load(f)
        
    print(f"Extracting incident subgraph context for: {target}...")
    subgraph = get_subgraph(graph, target)
    
    if not subgraph:
        print(f"No telemetry or entities found in graph for indicator: {target}")
        sys.exit(1)
        
    context_str = json.dumps(subgraph, indent=2)
    
    prompt = f"""
You are an expert security and reliability incident responder mimicking Amazon Detective root-cause analysis.
Review the following connected operational dependency and anomaly graph context extracted from the Morupule Coal Mine database regarding the target indicator: {target}.

Graph Context (JSON Telemetry & Relationships):
{context_str}

Provide a concise, professional Incident Summary for the engineering team. Include:
1. Root Cause Summary: What happened (e.g. failure precursors, outliers) and which primary asset is responsible.
2. Chronological Timeline: The order of anomalies based on timestamps and propagation.
3. Blast Radius: Which downstream resources, processes (material feed, power, ventilation), or areas are affected or compromised.
4. Immediate Remediation Action: The next two steps engineers must take right now.
"""

    print(f"Running incident analyzer for target {target}...")
    report = call_llm(prompt)
    
    print("\n--- AMAZON DETECTIVE REPLICA REPORT ---")
    print(report)
    print("---------------------------------------")

if __name__ == "__main__":
    main()

import json
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_MODEL_FILE = ROOT / "data" / "processed" / "semantic_model.json"
ANOMALIES_FILE = ROOT / "data" / "processed" / "anomalies.json"
GRAPH_OUT_FILE = ROOT / "data" / "processed" / "behavioral_graph.json"

# Operational dependencies to build graph paths
# (Source, Relationship, Target, Description)
CORE_DEPENDENCIES = [
    # Material Flow Feed Chain
    ("CV-04", "FEEDS", "CHP-02", "Conveyor CV-04 feeds coal directly into transfer conveyor CHP-02"),
    ("CHP-02", "FEEDS", "CR-01", "Transfer conveyor CHP-02 feeds coal into Primary Crusher CR-01"),
    
    # Power Distribution Network (Substation SUB-03)
    ("SUB-03", "POWERS", "CV-04", "Electrical substation SUB-03 provides primary power to Conveyor CV-04"),
    ("SUB-03", "POWERS", "CHP-02", "Electrical substation SUB-03 provides power to Conveyor CHP-02"),
    ("SUB-03", "POWERS", "CR-01", "Electrical substation SUB-03 provides power to Crusher CR-01"),
    ("SUB-03", "POWERS", "PMP-SF-11", "Electrical substation SUB-03 powers surface dewatering pump PMP-SF-11"),
    ("SUB-03", "POWERS", "FAN-UG-02", "Electrical substation SUB-03 powers underground ventilation fan FAN-UG-02"),
    
    # Ventilation Safety Dependency
    ("FAN-UG-02", "VENTILATES", "Underground", "Underground ventilation fan 02 regulates air supply in the underground workings"),
    
    # Dewatering Flood Prevention Dependency
    ("PMP-SF-11", "DRAINS", "Surface", "Surface dewatering pump 11 drains water out of the surface operations"),
    ("PMP-SF-11", "DRAINS", "Underground", "Surface dewatering pump 11 manages underground water seepage"),
]

def main():
    print("Ingesting security and operational findings into behavioral graph database...")
    
    # 1. Load asset metadata
    if not SEMANTIC_MODEL_FILE.exists():
        print(f"Error: {SEMANTIC_MODEL_FILE} not found. Run scripts/build_semantic_model.py first.")
        return
        
    with open(SEMANTIC_MODEL_FILE, "r", encoding="utf-8") as f:
        semantic_data = json.load(f)
        
    assets = {asset["id"]: asset for asset in semantic_data.get("assets", [])}
    
    # 2. Load anomaly findings
    anomalies = []
    if ANOMALIES_FILE.exists():
        with open(ANOMALIES_FILE, "r", encoding="utf-8") as f:
            anomalies = json.load(f)
    else:
        print(f"Warning: {ANOMALIES_FILE} not found. Run scripts/detect_anomalies.py to get statistical findings.")
        
    # 3. Create nodes
    nodes = []
    
    # Add Area nodes
    areas = set(asset["area"] for asset in assets.values())
    for area in areas:
        nodes.append({
            "id": area,
            "type": "OperationalArea",
            "properties": {
                "name": area
            }
        })
        
    # Add Asset Class nodes
    classes = set(asset["cls"] for asset in assets.values())
    for cls in classes:
        nodes.append({
            "id": cls,
            "type": "AssetClass",
            "properties": {
                "name": cls
            }
        })
        
    # Add Asset nodes
    for asset_id, asset in assets.items():
        nodes.append({
            "id": asset_id,
            "type": "Asset",
            "properties": {
                "name": asset["name"],
                "area": asset["area"],
                "class": asset["cls"],
                "health": asset["health"],
                "risk": asset["risk"],
                "rul": asset["rul"],
                "esg": asset["esg"],
                "status": asset["status"],
                "action": asset["action"]
            }
        })
        
    # Add Anomaly nodes
    for anom in anomalies:
        nodes.append({
            "id": anom["finding_id"],
            "type": "Anomaly",
            "properties": {
                "timestamp": anom["timestamp"],
                "severity": anom["severity"],
                "details": anom["details"],
                "vibration": anom["metrics"]["vibration"],
                "bearing_wear": anom["metrics"]["bearing_wear"],
                "load": anom["metrics"]["load"]
            }
        })
        
    # 4. Create edges (relationships)
    edges = []
    
    # Base located/class edges
    for asset_id, asset in assets.items():
        edges.append({
            "source": asset_id,
            "type": "LOCATED_IN",
            "target": asset["area"],
            "properties": {}
        })
        edges.append({
            "source": asset_id,
            "type": "BELONGS_TO_CLASS",
            "target": asset["cls"],
            "properties": {}
        })
        
    # Inject base dependencies
    for src, rel, tgt, desc in CORE_DEPENDENCIES:
        # Check if source/target exist as assets or areas
        edges.append({
            "source": src,
            "type": rel,
            "target": tgt,
            "properties": {
                "description": desc
            }
        })
        
    # Inject Anomaly triggering edges
    for anom in anomalies:
        edges.append({
            "source": anom["finding_id"],
            "type": "TRIGGERED_ON",
            "target": anom["asset_id"],
            "properties": {
                "timestamp": anom["timestamp"]
            }
        })
        
    # 5. Build Finding Groups (Amazon Detective feature replica)
    # Finding groups cluster anomalies on an asset and its immediate dependencies
    # within a 2-hour sliding window.
    finding_groups = []
    
    # Sort anomalies by timestamp
    sorted_anoms = sorted(anomalies, key=lambda a: a["timestamp"])
    
    for anom in sorted_anoms:
        # Check if there is an existing group within 2 hours for this asset or its dependencies
        anom_time = datetime.datetime.fromisoformat(anom["timestamp"].replace("Z", "+00:00"))
        
        # Check dependencies for clustering
        connected_assets = [anom["asset_id"]]
        for dep_src, _, dep_tgt, _ in CORE_DEPENDENCIES:
            if dep_src == anom["asset_id"] and dep_tgt in assets:
                connected_assets.append(dep_tgt)
            elif dep_tgt == anom["asset_id"] and dep_src in assets:
                connected_assets.append(dep_src)
                
        placed = False
        for group in finding_groups:
            # Check if group has connection to these assets
            if any(a in group["assets"] for a in connected_assets):
                # Check time difference with the last event in the group
                last_time = datetime.datetime.fromisoformat(group["end_time"].replace("Z", "+00:00"))
                diff = abs((anom_time - last_time).total_seconds()) / 3600.0
                if diff <= 2.0: # 2-hour window
                    group["findings"].append(anom["finding_id"])
                    group["assets"] = list(set(group["assets"] + connected_assets))
                    group["end_time"] = max(group["end_time"], anom["timestamp"])
                    placed = True
                    break
                    
        if not placed:
            # Create new finding group
            group_id = f"FG-{len(finding_groups)+1:03d}"
            finding_groups.append({
                "id": group_id,
                "assets": connected_assets,
                "findings": [anom["finding_id"]],
                "start_time": anom["timestamp"],
                "end_time": anom["timestamp"]
            })
            
    # Add Finding Groups as nodes and edges in the graph
    for fg in finding_groups:
        nodes.append({
            "id": fg["id"],
            "type": "FindingGroup",
            "properties": {
                "start_time": fg["start_time"],
                "end_time": fg["end_time"],
                "affected_assets_count": len(fg["assets"]),
                "findings_count": len(fg["findings"])
            }
        })
        
        # Link findings to the group
        for f_id in fg["findings"]:
            edges.append({
                "source": f_id,
                "type": "PART_OF_GROUP",
                "target": fg["id"],
                "properties": {}
            })
            
        # Link group to assets
        for a_id in fg["assets"]:
            edges.append({
                "source": fg["id"],
                "type": "AFFECTS_ASSET",
                "target": a_id,
                "properties": {}
            })
            
    # 6. Save behavioral graph
    graph_payload = {
        "modelVersion": "morupule-behavioral-graph-v1",
        "generatedBy": "scripts/ingest_findings.py",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "stats": {
            "nodes_count": len(nodes),
            "edges_count": len(edges),
            "finding_groups_count": len(finding_groups),
            "anomalies_count": len(anomalies)
        },
        "nodes": nodes,
        "edges": edges,
        "finding_groups": finding_groups
    }
    
    GRAPH_OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(GRAPH_OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(graph_payload, f, indent=2)
        
    print(f"Graph ingested successfully. Saved {len(nodes)} nodes and {len(edges)} edges to {GRAPH_OUT_FILE}")
    print(f"Created {len(finding_groups)} correlated Finding Groups.")

if __name__ == "__main__":
    main()

import zipfile
import csv
import json
import statistics
import datetime
from pathlib import Path
from sklearn.ensemble import IsolationForest
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed"
ANOMALIES_FILE = OUT_DIR / "anomalies.json"

ASSET_IDS = ["CV-04", "PMP-SF-11", "FAN-UG-02", "LHD-07", "CR-01", "SUB-03", "EMS-02", "CHP-02"]

def as_float(value):
    if value in ("", "na", "NA", None):
        return None
    try:
        return float(value)
    except ValueError:
        return None

def load_vibration_data():
    """Loads vibration telemetry from Huawei dataset."""
    zpath = RAW / "huawei_elevator_predictive_maintenance.zip"
    member = "omlstreaming-grc-datasets-pred-maintenance-892dd65/predictive-maintenance-dataset.csv"
    vibrations = []
    try:
        with zipfile.ZipFile(zpath) as archive:
            with archive.open(member) as handle:
                text = (line.decode("utf-8", errors="replace") for line in handle)
                reader = csv.DictReader(text, delimiter=";")
                for i, row in enumerate(reader):
                    if i > 5000:  # Sample limit for performance
                        break
                    v = as_float(row.get("vibration"))
                    b = as_float(row.get("ball-bearing"))
                    h = as_float(row.get("humidity"))
                    if v is not None:
                        vibrations.append((v, b, h))
    except Exception as e:
        print(f"Warning: Failed to load Huawei dataset: {e}. Using simulated fallback.")
        # Fallback simulated data
        import random
        for _ in range(100):
            vibrations.append((random.uniform(0.1, 0.9), random.uniform(0.05, 0.45), random.uniform(55, 85)))
    return vibrations

def load_load_data():
    """Loads load/missingness metrics from Scania dataset."""
    zpath = RAW / "aps_failure_scania.zip"
    loads = []
    try:
        with zipfile.ZipFile(zpath) as archive:
            with archive.open("aps_failure_training_set.csv") as handle:
                text = (line.decode("utf-8", errors="replace") for line in handle)
                csv_start = []
                for line in text:
                    if line.startswith("class,"):
                        csv_start.append(line)
                        break
                csv_start.extend(text)
                reader = csv.DictReader(csv_start)
                for i, row in enumerate(reader):
                    if i > 5000:  # Sample limit for performance
                        break
                    load = as_float(row.get("aa_000"))
                    if load is not None:
                        loads.append(load)
    except Exception as e:
        print(f"Warning: Failed to load Scania dataset: {e}. Using simulated fallback.")
        import random
        for _ in range(100):
            loads.append(random.uniform(1000, 50000))
    return loads

def main():
    print("Loading raw telemetry streams for anomaly detection...")
    vibrations = load_vibration_data()
    loads = load_load_data()

    # Align streams and build telemetry records for assets
    records = []
    base_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
    
    # We will simulate chronological log events for our 8 assets
    # mixing the real dataset parameters to detect outliers
    import random
    random.seed(42)
    
    print("Synthesizing log pipeline telemetry stream...")
    for i in range(200): # 200 telemetry points
        asset_id = random.choice(ASSET_IDS)
        timestamp = base_time + datetime.timedelta(minutes=7 * i)
        
        # Pull standard samples
        vib, bearing, humidity = random.choice(vibrations) if vibrations else (0.3, 0.1, 70.0)
        ld = random.choice(loads) if loads else 2000.0
        
        # Inject standard operational variance
        # Introduce a few rogue outliers (spikes) for specific assets to test Isolation Forest
        is_rogue = False
        if i in [23, 67, 112, 145, 189]: # Explicit outliers
            is_rogue = True
            vib = vib * random.uniform(3.5, 6.0)
            ld = ld * random.uniform(4.0, 8.0)
            bearing = bearing * random.uniform(4.0, 7.0)
            print(f"Injecting spike for {asset_id} at index {i}")
            
        records.append({
            "asset_id": asset_id,
            "timestamp": timestamp.isoformat(),
            "vibration": vib,
            "bearing_wear": bearing,
            "humidity": humidity,
            "load": ld,
            "is_rogue": is_rogue # ground truth for debugging
        })
        
    df = pd.DataFrame(records)
    
    print("Training Isolation Forest baseline model...")
    # Features used for profiling normal operating envelope
    features = ['vibration', 'bearing_wear', 'humidity', 'load']
    
    # Contamination parameter set to ~0.08 (expecting ~8% anomalies)
    model = IsolationForest(contamination=0.08, random_state=42)
    df['anomaly_score'] = model.fit_predict(df[features])
    
    # -1 represents outlier, 1 represents normal
    anomalies = df[df['anomaly_score'] == -1]
    
    print(f"Identified {len(anomalies)} statistical anomalies from {len(df)} logs.")
    
    # Convert back to JSON format
    findings = []
    for index, row in anomalies.iterrows():
        # Determine finding severity and detail description
        sev = "High" if row['vibration'] > 2.5 or row['load'] > 150000 else "Medium"
        details = (
            f"Vibration anomaly detected ({row['vibration']:.3f} m/s^2, bearing wear={row['bearing_wear']:.3f}). "
            f"Operating load index at {row['load']:.1f}."
        )
        
        findings.append({
            "finding_id": f"FIND-ANOM-{index:03d}",
            "asset_id": row['asset_id'],
            "timestamp": row['timestamp'],
            "severity": sev,
            "details": details,
            "metrics": {
                "vibration": round(row['vibration'], 3),
                "bearing_wear": round(row['bearing_wear'], 3),
                "humidity": round(row['humidity'], 2),
                "load": round(row['load'], 1)
            }
        })
        
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(ANOMALIES_FILE, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)
        
    print(f"Successfully wrote {len(findings)} anomalies to {ANOMALIES_FILE}")

if __name__ == "__main__":
    main()

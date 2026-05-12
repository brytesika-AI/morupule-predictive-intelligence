import csv
import json
import math
import statistics
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed" / "semantic_model.json"


ASSET_MAP = [
    ("CV-04", "Main Trunk Conveyor CV-04", "Underground", "Conveyor", 180, 182, 205, 187),
    ("PMP-SF-11", "Surface Dewatering Pump 11", "Surface", "Pump", 430, 332, 455, 337),
    ("FAN-UG-02", "Underground Ventilation Fan 02", "Underground", "Fan", 452, 156, 476, 161),
    ("LHD-07", "Load Haul Dumper LHD-07", "Mobile Fleet", "Mobile", 262, 304, 120, 307),
    ("CR-01", "Primary Crusher CR-01", "Processing", "Crusher", 496, 296, 518, 301),
    ("SUB-03", "Substation Transformer SUB-03", "Services", "Electrical", 514, 318, 536, 323),
    ("EMS-02", "Environmental Monitor EMS-02", "Services", "Electrical", 560, 182, 582, 187),
    ("CHP-02", "Coal Handling Plant Transfer CHP-02", "Processing", "Conveyor", 388, 248, 410, 253),
]


def as_float(value):
    if value in ("", "na", "NA", None):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def percentile(values, q):
    if not values:
        return 0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return ordered[idx]


def read_scania():
    zpath = RAW / "aps_failure_scania.zip"
    rows = []
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
            selected_columns = [
                "aa_000",
                "ag_004",
                "ag_005",
                "ah_000",
                "an_000",
                "ao_000",
                "ap_000",
                "bb_000",
                "bt_000",
                "ci_000",
                "cj_000",
                "ck_000",
            ]
            for row in reader:
                nums = [as_float(row.get(col)) for col in selected_columns]
                valid = [value for value in nums if value is not None]
                if not valid:
                    continue
                rows.append(
                    {
                        "label": row["class"],
                        "missing": sum(value is None for value in nums),
                        "load": statistics.fmean(valid),
                        "spread": statistics.pstdev(valid) if len(valid) > 1 else 0,
                        "max_signal": max(valid),
                    }
                )
    return rows


def read_huawei():
    zpath = RAW / "huawei_elevator_predictive_maintenance.zip"
    member = "omlstreaming-grc-datasets-pred-maintenance-892dd65/predictive-maintenance-dataset.csv"
    rows = []
    with zipfile.ZipFile(zpath) as archive:
        with archive.open(member) as handle:
            text = (line.decode("utf-8", errors="replace") for line in handle)
            reader = csv.DictReader(text, delimiter=";")
            for row in reader:
                bearing = as_float(row.get("ball-bearing"))
                humidity = as_float(row.get("humidity"))
                vibration = as_float(row.get("vibration"))
                if None in (bearing, humidity, vibration):
                    continue
                rows.append({"bearing": bearing, "humidity": humidity, "vibration": vibration})
    return rows


def chunk(values, count):
    size = max(1, len(values) // count)
    return [values[i * size : (i + 1) * size] for i in range(count)]


def build_assets(scania_rows, huawei_rows):
    positives = [row for row in scania_rows if row["label"] == "pos"]
    negatives = [row for row in scania_rows if row["label"] == "neg"]
    high_neg = sorted(negatives, key=lambda row: row["spread"], reverse=True)[: len(positives)]
    scania_groups = chunk(positives + high_neg, len(ASSET_MAP))
    huawei_groups = chunk(huawei_rows, len(ASSET_MAP))
    load_p95 = percentile([row["load"] for row in scania_rows], 0.95) or 1
    spread_p95 = percentile([row["spread"] for row in scania_rows], 0.95) or 1
    vibration_p95 = percentile([row["vibration"] for row in huawei_rows], 0.95) or 1

    assets = []
    for index, asset in enumerate(ASSET_MAP):
        asset_id, name, area, cls, x, y, label_x, label_y = asset
        srows = scania_groups[index] or scania_rows[:10]
        hrows = huawei_groups[index] or huawei_rows[:10]
        failure_rate = sum(row["label"] == "pos" for row in srows) / max(1, len(srows))
        missing_rate = statistics.fmean(row["missing"] for row in srows) / 12
        load_index = min(1.4, statistics.fmean(row["load"] for row in srows) / load_p95)
        spread_index = min(1.4, statistics.fmean(row["spread"] for row in srows) / spread_p95)
        vibration_index = min(1.4, statistics.fmean(row["vibration"] for row in hrows) / vibration_p95)
        humidity = statistics.fmean(row["humidity"] for row in hrows)

        risk = round(
            min(
                96,
                18
                + failure_rate * 46
                + missing_rate * 12
                + load_index * 10
                + spread_index * 10
                + vibration_index * 12,
            )
        )
        health = round(max(12, 100 - risk + (1 - missing_rate) * 10 - vibration_index * 4))
        rul = max(3, round(64 - risk * 0.62 - vibration_index * 8))
        esg = round(max(44, min(96, 88 - vibration_index * 8 - load_index * 7 + (humidity < 70) * 4)))
        status = "critical" if risk >= 70 else "watch" if risk >= 50 else "good"
        action = (
            "Prioritise inspection and planned intervention from real failure-risk features"
            if status == "critical"
            else "Monitor drift and prepare conditional maintenance package"
            if status == "watch"
            else "Keep on reliability watchlist and validate baseline stability"
        )

        assets.append(
            {
                "id": asset_id,
                "name": name,
                "area": area,
                "cls": cls,
                "health": health,
                "risk": risk,
                "rul": rul,
                "esg": esg,
                "status": status,
                "x": x,
                "y": y,
                "labelX": label_x,
                "labelY": label_y,
                "action": action,
                "sourceSignals": {
                    "scaniaFailureRate": round(failure_rate, 3),
                    "scaniaLoadIndex": round(load_index, 3),
                    "scaniaSignalSpread": round(spread_index, 3),
                    "huaweiVibrationIndex": round(vibration_index, 3),
                    "huaweiHumidityMean": round(humidity, 2),
                },
            }
        )
    return sorted(assets, key=lambda item: item["risk"], reverse=True)


def main():
    scania_rows = read_scania()
    huawei_rows = read_huawei()
    assets = build_assets(scania_rows, huawei_rows)
    model = {
        "modelVersion": "morupule-semantic-model-v1",
        "generatedBy": "scripts/build_semantic_model.py",
        "grain": "asset_day_proxy",
        "sources": [
            {
                "name": "APS Failure at Scania Trucks",
                "publisher": "UCI Machine Learning Repository / Scania CV AB",
                "url": "https://archive.ics.uci.edu/dataset/421/aps+failure+at+scania+trucks",
                "license": "GPL",
                "recordsUsed": len(scania_rows),
                "role": "Real heavy-duty vehicle operational failure data mapped to mobile/fixed asset risk features.",
            },
            {
                "name": "Predictive maintenance dataset",
                "publisher": "Zenodo / Huawei Munich Research Center",
                "url": "https://zenodo.org/records/3653909",
                "license": "Open",
                "recordsUsed": len(huawei_rows),
                "role": "Real IoT sensor stream used for vibration, humidity, and drift transformations.",
            },
            {
                "name": "MetroPT-3 Dataset",
                "publisher": "UCI Machine Learning Repository",
                "url": "https://archive-beta.ics.uci.edu/dataset/791/metropt+3+dataset",
                "license": "CC BY 4.0",
                "recordsUsed": 0,
                "role": "Referenced production-grade compressor schema for future direct APU sensor ingestion.",
            },
            {
                "name": "Refinery Compressor Sensor Data, One-Year Dataset",
                "publisher": "Zenodo / Motor Oil Greece",
                "url": "https://zenodo.org/records/14866092",
                "license": "CC BY 4.0",
                "recordsUsed": 0,
                "role": "Referenced rotating-equipment DCS schema for enterprise compressor/fan/pump expansion.",
            },
        ],
        "transformations": [
            "Extracted Scania APS records after source license header; converted 'na' to null.",
            "Created load, spread, max-signal, missingness and positive-failure aggregates from selected operational counters.",
            "Parsed Huawei IoT stream with semicolon delimiter and retained ball-bearing, humidity and vibration signals.",
            "Windowed both datasets into Morupule asset analogues and calculated risk, health, RUL and ESG proxy measures.",
            "Mapped semantic dimensions: asset, operating area, asset class, scenario, source system and maintenance action.",
        ],
        "measures": {
            "risk": "18 + failure_rate*46 + missing_rate*12 + load_index*10 + spread_index*10 + vibration_index*12, capped at 96",
            "health": "100 - risk + completeness uplift - vibration penalty",
            "rul": "64 - risk*0.62 - vibration_index*8, floor 3 days",
            "esg": "88 - vibration_index*8 - load_index*7 + humidity stability uplift",
        },
        "assets": assets,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(model, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} with {len(assets)} assets from {len(scania_rows)} Scania rows and {len(huawei_rows)} Huawei rows.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""把 data/ 底下的縣市檔與全國檔合併成 site/data/benefits.json，供網站讀取。

用法：python3 scripts/build.py
"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "site" / "data" / "benefits.json"

# 依行政區慣用順序排列
COUNTY_ORDER = [
    "taipei", "new-taipei", "keelung", "taoyuan", "hsinchu-city", "hsinchu-county", "miaoli",
    "taichung", "changhua", "nantou", "yunlin", "chiayi-city", "chiayi-county", "tainan",
    "kaohsiung", "pingtung", "yilan", "hualien", "taitung", "penghu", "kinmen", "lienchiang",
]
COUNTY_META_KEYS = ("county_id", "county_name", "agency", "agency_url", "phone", "collected_at", "notes")


def main():
    categories = json.loads((DATA / "categories.json").read_text(encoding="utf-8"))
    counties = []
    benefits = []
    for cid in COUNTY_ORDER:
        path = DATA / "counties" / f"{cid}.json"
        if not path.exists():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        meta = {k: doc.get(k) for k in COUNTY_META_KEYS if doc.get(k)}
        meta["count"] = len(doc["benefits"])
        counties.append(meta)
        for b in doc["benefits"]:
            benefits.append({**b, "county_id": cid, "scope": "county"})

    national = DATA / "national.json"
    if national.exists():
        for b in json.loads(national.read_text(encoding="utf-8"))["benefits"]:
            benefits.append({**b, "county_id": None})

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "generated_at": date.today().isoformat(),
                "categories": categories,
                "counties": counties,
                "benefits": benefits,
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"{OUT.relative_to(ROOT)}：{len(counties)} 個縣市、{len(benefits)} 筆")


if __name__ == "__main__":
    main()

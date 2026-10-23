#!/usr/bin/env python3
"""檢查 data/ 底下的 JSON 是否符合 data/SCHEMA.md 的格式。

用法：
  python3 scripts/validate.py              # 檢查全部
  python3 scripts/validate.py taipei.json  # 只檢查指定檔（data/counties/ 或 data/ 下的檔名）
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

COUNTIES = {
    "taipei": "臺北市", "new-taipei": "新北市", "taoyuan": "桃園市", "taichung": "臺中市",
    "tainan": "臺南市", "kaohsiung": "高雄市", "keelung": "基隆市", "hsinchu-city": "新竹市",
    "chiayi-city": "嘉義市", "hsinchu-county": "新竹縣", "miaoli": "苗栗縣", "changhua": "彰化縣",
    "nantou": "南投縣", "yunlin": "雲林縣", "chiayi-county": "嘉義縣", "pingtung": "屏東縣",
    "yilan": "宜蘭縣", "hualien": "花蓮縣", "taitung": "臺東縣", "penghu": "澎湖縣",
    "kinmen": "金門縣", "lienchiang": "連江縣",
}
CATEGORIES = {c["id"] for c in json.loads((DATA / "categories.json").read_text(encoding="utf-8"))}
LEVELS = {"central", "local", "mixed", "private"}
CONFIDENCE = {"high", "medium", "low"}
SCOPES = {"nationwide", "interop"}
TARGET_GROUPS = {
    "兒童及少年", "成年", "老年", "視覺障礙", "聽覺或平衡障礙", "聲音或語言障礙", "肢體障礙",
    "智能障礙", "精神障礙", "自閉症", "罕見疾病", "多重障礙", "低收入或中低收入", "家庭照顧者",
    "學生", "求職者",
}
SOURCE_DATE = re.compile(r"^(unknown|\d{4}(-\d{2})?)$")
URL = re.compile(r"^https?://\S+$")


def check_benefit(b, prefix, national, errors):
    where = f"{prefix} [{b.get('id', '?')}]"

    def need_str(key):
        if not isinstance(b.get(key), str) or not b[key].strip():
            errors.append(f"{where}: `{key}` 必須是非空字串")

    def need_list(key, required=True):
        v = b.get(key)
        if v is None and not required:
            return
        if not isinstance(v, list) or (required and not v) or not all(isinstance(x, str) and x.strip() for x in v):
            errors.append(f"{where}: `{key}` 必須是非空字串陣列")

    for key in ("id", "name", "summary", "benefit", "how_to_apply"):
        need_str(key)
    need_list("eligibility")
    need_list("source_urls")
    need_list("documents", required=False)
    need_list("target_groups", required=False)

    if b.get("category") not in CATEGORIES:
        errors.append(f"{where}: `category` 不在 categories.json：{b.get('category')!r}")
    if b.get("level") not in LEVELS:
        errors.append(f"{where}: `level` 必須是 {sorted(LEVELS)}：{b.get('level')!r}")
    if b.get("confidence") not in CONFIDENCE:
        errors.append(f"{where}: `confidence` 必須是 {sorted(CONFIDENCE)}：{b.get('confidence')!r}")
    if not isinstance(b.get("source_date"), str) or not SOURCE_DATE.match(b["source_date"]):
        errors.append(f"{where}: `source_date` 格式應為 YYYY、YYYY-MM 或 unknown：{b.get('source_date')!r}")
    for u in b.get("source_urls") or []:
        if isinstance(u, str) and not URL.match(u):
            errors.append(f"{where}: 來源網址格式錯誤：{u!r}")
    for t in b.get("target_groups") or []:
        if t not in TARGET_GROUPS:
            errors.append(f"{where}: `target_groups` 含未定義詞彙：{t!r}")

    if national:
        need_str("provider")
        if b.get("scope") not in SCOPES:
            errors.append(f"{where}: `scope` 必須是 {sorted(SCOPES)}：{b.get('scope')!r}")
        if b.get("scope") == "interop":
            cs = b.get("counties")
            if not isinstance(cs, list) or not cs or any(c not in COUNTIES for c in cs):
                errors.append(f"{where}: interop 項目的 `counties` 必須列出有效 county_id")


def check_file(path, errors):
    rel = path.relative_to(ROOT)
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"{rel}: JSON 解析失敗：{e}")
        return 0
    national = path.name == "national.json"
    if not national:
        cid = path.stem
        if doc.get("county_id") != cid:
            errors.append(f"{rel}: `county_id` 應為 {cid!r}")
        if doc.get("county_name") != COUNTIES.get(cid):
            errors.append(f"{rel}: `county_name` 應為 {COUNTIES.get(cid)!r}")
        for key in ("agency", "agency_url", "collected_at", "method"):
            if not isinstance(doc.get(key), str) or not doc[key].strip():
                errors.append(f"{rel}: `{key}` 必須是非空字串")
    benefits = doc.get("benefits")
    if not isinstance(benefits, list) or not benefits:
        errors.append(f"{rel}: `benefits` 必須是非空陣列")
        return 0
    ids = set()
    expected_prefix = "national-" if national else f"{path.stem}-"
    for b in benefits:
        if not isinstance(b, dict):
            errors.append(f"{rel}: benefits 內含非物件項目")
            continue
        bid = b.get("id")
        if bid in ids:
            errors.append(f"{rel}: id 重複：{bid}")
        ids.add(bid)
        if isinstance(bid, str) and not bid.startswith(expected_prefix):
            errors.append(f"{rel} [{bid}]: id 應以 {expected_prefix!r} 開頭")
        check_benefit(b, str(rel), national, errors)
    return len(benefits)


def main():
    if len(sys.argv) > 1:
        paths = []
        for name in sys.argv[1:]:
            p = DATA / "counties" / name
            paths.append(p if p.exists() else DATA / name)
    else:
        paths = sorted((DATA / "counties").glob("*.json"))
        if (DATA / "national.json").exists():
            paths.append(DATA / "national.json")
    errors = []
    total = 0
    for p in paths:
        if not p.exists():
            errors.append(f"找不到檔案：{p}")
            continue
        n = check_file(p, errors)
        total += n
        print(f"{p.relative_to(ROOT)}: {n} 筆")
    if not sys.argv[1:]:
        missing = sorted(set(COUNTIES) - {p.stem for p in paths})
        if missing:
            print(f"尚缺縣市檔：{', '.join(missing)}")
    print(f"共 {total} 筆")
    if errors:
        print(f"\n{len(errors)} 個錯誤：")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("格式檢查通過")


if __name__ == "__main__":
    main()

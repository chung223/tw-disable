# 資料格式說明

所有資料以 JSON 存放，UTF-8，2 格縮排。

- `data/categories.json`：福利類別代碼與中文名稱
- `data/counties/<county_id>.json`：各縣市福利（一縣市一檔）
- `data/national.json`：全國性（中央）福利，以及跨縣市可用／互通的資源

驗證：`python3 scripts/validate.py`

## 縣市檔 `data/counties/<county_id>.json`

```json
{
  "county_id": "taipei",
  "county_name": "臺北市",
  "agency": "臺北市政府社會局",
  "agency_url": "https://dosw.gov.taipei/",
  "phone": "1999（外縣市 02-27208889）",
  "collected_at": "2026-10-23",
  "method": "web_search",
  "notes": "蒐集過程的說明、缺漏",
  "benefits": [ /* Benefit 物件，見下 */ ]
}
```

## Benefit 物件

| 欄位 | 必填 | 型別 | 說明 |
|---|---|---|---|
| `id` | ✔ | string | `<county_id>-<英文短代號>`，全檔唯一，如 `taipei-living-allowance`；全國檔用 `national-...` |
| `name` | ✔ | string | 官方名稱（中文） |
| `category` | ✔ | string | `categories.json` 的代碼之一 |
| `level` | ✔ | string | `central`＝中央法規訂定、地方執行（各縣市大致相同）；`local`＝縣市自辦或加碼；`mixed`＝中央基準但縣市另有加碼或不同金額；`private`＝民間團體提供（多見於全國檔） |
| `summary` | ✔ | string | 1–3 句白話說明 |
| `eligibility` | ✔ | string[] | 申請資格，一條一項 |
| `benefit` | ✔ | string | 補助金額或服務內容（原文有的數字照抄，並寫出年度） |
| `how_to_apply` | ✔ | string | 申請窗口與方式（如：戶籍地區公所、線上申請） |
| `documents` |  | string[] | 應備文件 |
| `contact` |  | string | 承辦單位電話 |
| `target_groups` |  | string[] | 適用對象標籤，限用下方詞彙 |
| `source_urls` | ✔ | string[] | 至少一個來源網址，以政府官網優先 |
| `source_date` | ✔ | string | 來源資料的年份／年月（西元），如 `2025`、`2025-07`；不明寫 `unknown` |
| `confidence` | ✔ | string | `high`＝政府官網現行頁面或公告；`medium`＝官方文件但年份較舊、或只看到搜尋摘要；`low`＝新聞、民間整理等二手來源，需再核實 |
| `notes` |  | string | 注意事項、與其他縣市差異、待確認處 |

全國檔的 Benefit 另有：

| 欄位 | 必填 | 說明 |
|---|---|---|
| `provider` | ✔ | 主管機關或提供單位（如：衛福部社家署、交通部、勞動部） |
| `scope` | ✔ | `nationwide`＝全國通用、不限戶籍；`interop`＝特定縣市之間互通（如雙北復康巴士跨市） |
| `counties` |  | `scope` 為 `interop` 時，列出相關縣市的 `county_id` |

## target_groups 詞彙

`兒童及少年`、`成年`、`老年`、`視覺障礙`、`聽覺或平衡障礙`、`聲音或語言障礙`、`肢體障礙`、`智能障礙`、`精神障礙`、`自閉症`、`罕見疾病`、`多重障礙`、`低收入或中低收入`、`家庭照顧者`、`學生`、`求職者`

## county_id 對照

| id | 縣市 | id | 縣市 |
|---|---|---|---|
| taipei | 臺北市 | changhua | 彰化縣 |
| new-taipei | 新北市 | nantou | 南投縣 |
| taoyuan | 桃園市 | yunlin | 雲林縣 |
| taichung | 臺中市 | chiayi-county | 嘉義縣 |
| tainan | 臺南市 | pingtung | 屏東縣 |
| kaohsiung | 高雄市 | yilan | 宜蘭縣 |
| keelung | 基隆市 | hualien | 花蓮縣 |
| hsinchu-city | 新竹市 | taitung | 臺東縣 |
| chiayi-city | 嘉義市 | penghu | 澎湖縣 |
| hsinchu-county | 新竹縣 | kinmen | 金門縣 |
| miaoli | 苗栗縣 | lienchiang | 連江縣 |

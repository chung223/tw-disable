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
  "collected_at": "2026-10-26",
  "method": "official_site",
  "notes": "給讀者看的資料說明：哪些項目還沒查到、哪些要洽詢承辦單位",
  "benefits": [ /* Benefit 物件，見下 */ ]
}
```

- `collected_at`：最近一次整檔蒐集或核對的日期（YYYY-MM-DD）
- `method`：`official_site`＝逐頁開啟官方網站原文核對；`web_search`＝只根據搜尋結果摘要整理
- `notes`：寫給網站讀者看，簡短說明缺漏與注意事項；不要寫蒐集過程（搜尋幾次、用什麼工具）

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
| `confidence` | ✔ | string | 見下方「可信度」 |
| `verified_at` |  | string | 實際開啟來源原文、逐項核對內容的日期（YYYY-MM-DD）。`confidence` 為 `high` 時必填 |
| `criteria` |  | object | 結構化資格條件，給網站的「我可以申請什麼」篩選用，見下方 |
| `notes` |  | string | 注意事項、與其他縣市差異、待確認處 |

全國檔的 Benefit 另有：

| 欄位 | 必填 | 說明 |
|---|---|---|
| `provider` | ✔ | 主管機關或提供單位（如：衛福部社家署、交通部、勞動部） |
| `scope` | ✔ | `nationwide`＝全國通用、不限戶籍；`interop`＝特定縣市之間互通（如雙北復康巴士跨市） |
| `counties` |  | `scope` 為 `interop` 時，列出相關縣市的 `county_id` |

## 可信度 `confidence`

| 值 | 條件 |
|---|---|
| `high` | 開啟了政府官網現行頁面、現行法規或公告的原文，補助內容、資格、金額逐項核對一致，並填 `verified_at` |
| `medium` | 官方來源，但頁面沒標年度或超過兩年沒更新、原文打不開，或部分內容在原文中找不到 |
| `low` | 只有新聞、民間整理等二手來源 |

網站會把 `medium`、`low` 標示為「待核實」。

## 資格條件 `criteria`

只在原文**明確限制**時填寫；沒填的欄位代表不限。

| 欄位 | 型別 | 說明 |
|---|---|---|
| `age_min` | integer | 最低年齡（含），如「65 歲以上」填 65 |
| `age_max` | integer | 最高年齡（含），如「未滿 65 歲」填 64、「未滿 6 歲」填 5 |
| `severity` | string[] | 限定的障礙等級，從 `輕度`、`中度`、`重度`、`極重度` 選；如「中度以上」填 `["中度","重度","極重度"]` |
| `income` | string | `low`＝限列冊低收入戶；`low_mid`＝限列冊低收入戶或中低收入戶；`means_tested`＝要審查家庭收入或財產，但沒有列冊也可能符合（如生活補助） |

例：生活補助 `{"income": "means_tested"}`；照顧者津貼限中度以上、低收入或中低收入戶 `{"severity": ["中度","重度","極重度"], "income": "low_mid"}`。
金額依等級或經濟身分不同時（例如低收入戶全額、一般戶補助一部分），`income` 不填，差異寫在 `benefit`。

## target_groups 詞彙

障別標籤（`視覺障礙`、`肢體障礙`…）只在福利限定或專為該障別設計時才加，例如人工電子耳補助加 `聽覺或平衡障礙`；一般性福利不要把所有障別都列上。


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

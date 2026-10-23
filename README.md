# tw-disable：全台身心障礙福利查詢

整理全台 22 個縣市的身心障礙者福利，以及全國通用、可以跨縣市使用的資源，做成可查詢的靜態網站。

## 目錄

```
data/
  SCHEMA.md          資料格式說明
  categories.json    福利類別
  counties/*.json    各縣市福利（一縣市一檔）
  national.json      全國通用、跨縣市互通、全國性民間資源
scripts/
  validate.py        檢查資料格式
  build.py           合併資料成 site/data/benefits.json
site/                靜態網站（index.html、app.js、style.css）
```

## 使用方式

```sh
python3 scripts/validate.py          # 檢查資料
python3 scripts/build.py             # 產生 site/data/benefits.json
python3 -m http.server -d site 8000  # 本機預覽 http://localhost:8000
```

`site/` 可以直接放上 GitHub Pages 或任何靜態主機。

## 資料來源與可信度

每筆資料都附來源網址與資料年份，並標記可信度：

- `high`：政府官網現行頁面或公告
- `medium`：官方文件但年份較舊，或只取得搜尋摘要
- `low`：新聞、民間整理等二手來源

網站上 `medium`、`low` 的項目會顯示「待核實」。福利金額與資格每年調整，實際以主管機關公告為準。

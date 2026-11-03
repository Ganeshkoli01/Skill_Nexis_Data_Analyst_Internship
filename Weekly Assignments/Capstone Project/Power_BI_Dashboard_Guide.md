# SkillNexis Capstone Project - Power BI Dashboard Step-by-Step Build Guide

This guide provides end-to-end instructions for creating the Power BI Dashboard for the **Week 4 Capstone Project**.

---

## 1. Quick Data Connection (30 Seconds)
1. Open **Power BI Desktop** (Already installed on your machine at `C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe`).
2. Click **Get Data** -> **Excel Workbook**.
3. Navigate to:
   ```
   c:\Users\GANESH KOLI\OneDrive\Desktop\skillnexis data-analyst\Weekly Assignments\Capstone Project\Cleaned_Sales_Data.xlsx
   ```
4. Select `Cleaned_Sales_Data` and click **Load**.

---

## 2. Verify Column Data Types in Power BI
Ensure the fields are formatted as follows in the Data view:
- **Segment, Country, Product, Discount Band, Month Name:** Text
- **Date:** Date (`yyyy-mm-dd`)
- **Units Sold, Month Number, Year:** Whole Number
- **Sale Price, Manufacturing Price, Gross Sales, Discounts, Sales, COGS, Profit:** Currency (`$ English (United States)`)
- **Profit Margin %, Discount %:** Percentage (`0.0%`)

---

## 3. Create DAX Measures
Under **Modeling** -> **New Measure**, paste each measure from `PowerBI_DAX_Measures.dax`:
1. `Total Net Sales = SUM('Cleaned_Sales_Data'[Sales])`
2. `Total Profit = SUM('Cleaned_Sales_Data'[Profit])`
3. `Total Units Sold = SUM('Cleaned_Sales_Data'[Units Sold])`
4. `Total Discounts = SUM('Cleaned_Sales_Data'[Discounts])`
5. `Gross Profit Margin % = DIVIDE([Total Profit], [Total Net Sales], 0)`

---

## 4. Dashboard Canvas Layout (Page 1: Executive Summary)

### Top Header
- **Title Text Box:** `Financial Performance & Commercial Sales Dashboard` (Calibri 20pt Bold, Dark Blue `#1F4E79`).
- **Date Slicer:** Top right corner based on `Cleaned_Sales_Data[Date]`.

### Slicers Bar (Left or Top Panel)
Add 3 Dropdown Slicers:
1. `Segment`
2. `Country`
3. `Discount Band`

### Top Row: 5 KPI Cards
Create 5 **Card** visuals side-by-side:
| Visual | Measure Field | Callout Value Format | Color |
|---|---|---|---|
| Card 1 | `Total Net Sales` | Currency (`$118.73M`) | `#1F4E79` (Navy) |
| Card 2 | `Total Profit` | Currency (`$16.89M`) | `#2E7D32` (Green) |
| Card 3 | `Gross Profit Margin %` | Percentage (`14.23%`) | `#2E7D32` (Green) |
| Card 4 | `Total Units Sold` | Decimal (`1.13M`) | `#333F48` (Slate) |
| Card 5 | `Total Discounts` | Currency (`$9.21M`) | `#D32F2F` (Amber/Red) |

### Middle Row: 2 Key Visuals
- **Left (Area/Line Chart):** `Monthly Net Sales Trend`
  - **X-axis:** `Date` (Month/Year) or `Year_Month`
  - **Y-axis:** `Total Net Sales`
  - **Secondary Y-axis or Tooltip:** `Total Profit`
- **Right (Clustered Bar Chart):** `Sales & Profit by Segment`
  - **Y-axis:** `Segment`
  - **X-axis:** `Total Net Sales`, `Total Profit`

### Bottom Row: 2 Strategic Visuals
- **Left (Map or Clustered Horizontal Bar Chart):** `Profit Margin % by Country`
  - **Y-axis:** `Country`
  - **X-axis:** `Gross Profit Margin %`
  - **Data Labels:** On (`15.5%`, `15.7%`, etc.)
- **Right (Donut or Treemap Chart):** `Sales Breakdown by Product`
  - **Category:** `Product`
  - **Values:** `Total Net Sales`

---

## 5. Dashboard Canvas Layout (Page 2: Product & Discount Deep Dive)
- **Scatter Plot (Product Matrix):**
  - **X-axis:** `Total Units Sold`
  - **Y-axis:** `Total Profit`
  - **Size:** `Total Net Sales`
  - **Legend:** `Product`
- **Column Chart (Discount Cannibalization):**
  - **X-axis:** `Discount Band` (`None`, `Low`, `Medium`, `High`)
  - **Y-axis:** `Gross Profit Margin %`
  - Demonstrates that High discounts reduce margins from 21.9% down to 9.1%.

---

## 6. Saving the File
1. In Power BI Desktop, click **File** -> **Save As**.
2. Save file as:
   ```
   c:\Users\GANESH KOLI\OneDrive\Desktop\skillnexis data-analyst\Weekly Assignments\Capstone Project\Financial_Sales_Dashboard.pbix
   ```
3. Export report to PDF via **File** -> **Export** -> **Export to PDF** if required for submission.


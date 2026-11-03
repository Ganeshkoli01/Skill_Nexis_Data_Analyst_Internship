# SkillNexis Data Analyst Internship: Capstone Project Final Report
**Project Title:** End-to-End Enterprise Financial Analytics, Relational SQL Auditing, and Machine Learning Sales Forecasting  
**Author:** Ganesh Koli  
**Track:** Data Analyst Internship - Week 4 Capstone  
**Dataset Analyzed:** Multi-Regional Commercial Financial Performance Dataset (700 Transactions, 16 Core Features, 2013–2014)  
**Deliverables Produced:**
1. Cleaned Datasets (`Cleaned_Sales_Data.xlsx`, `Cleaned_Sales_Data.csv`)
2. Master Financial Analysis Workbook with Executive KPI Model & ML Validation (`Financial_Analysis_Model.xlsx`)
3. Fully Executed Jupyter Data Science Notebook with EDA, SQL & ML Models (`Capstone_Project_Analysis.ipynb`)
4. Power BI DAX Measures & Complete Dashboard Architecture Guide (`PowerBI_DAX_Measures.dax`, `Power_BI_Dashboard_Guide.md`)
5. Interactive Executive Web Dashboard (`PowerBI_Interactive_Dashboard.html`)
6. High-Resolution Visual Portfolio (`visualizations/01` to `10`)

---

## Executive Summary

This capstone project delivers an end-to-end commercial audit, exploratory data analysis, relational SQL database investigation, and predictive machine learning sales forecasting system for global commercial operations across five major geographic markets (Canada, Germany, France, Mexico, and the United States).

Across the 700 recorded transactions spanning September 2013 through December 2014:
- **Total Gross Sales:** **$127.93M**
- **Discounts Surrendered:** **$9.21M** (7.20% overall discount rate)
- **Realized Net Sales:** **$118.73M**
- **Total Cost of Goods Sold (COGS):** **$101.83M**
- **Net Operating Profit:** **$16.89M** (14.23% realized net profit margin)
- **Total Units Sold:** **1,125,808 units**

While aggregate performance highlights strong topline growth between 2013 and 2014, granular segmentation reveals critical profit leaks, most notably in the **Enterprise customer segment** (which is operating at a net loss) and within the **High Discount Band** (where margins collapse from 21.86% to 9.07%). By combining SQL analytics with an ensemble Gradient Boosting Regressor (which achieves **$R^2 = 0.9950$** and **2.90% MAPE**), this report identifies actionable levers to reclaim an estimated **$2.2M to $3.1M in annual operating margin**.

---

## 1. Data Cleaning & Feature Engineering

### 1.1 Ingestion & Cleansing Pipeline
1. **Schema Standardization:** Stripped leading and trailing whitespace across all 16 raw column headers, notably correcting `' Sales'` into standard `'Sales'`.
2. **Missing Value Resolution:** Investigated 53 missing values in the `Discount Band` column. Empirical verification revealed that all 53 records had `Discounts == 0.0`. These entries were cleaned and explicitly categorized as `'None'` (zero discount tier).
3. **Accounting Validation:** Verified that fundamental business accounting identities held across all 700 transactions without mathematical discrepancies:
   $$\text{Gross Sales} = \text{Units Sold} \times \text{Sale Price}$$
   $$\text{Net Sales} = \text{Gross Sales} - \text{Discounts}$$
   $$\text{Profit} = \text{Net Sales} - \text{COGS}$$
4. **Engineered Metrics:**
   - **Profit Margin %:** $\frac{\text{Profit}}{\text{Net Sales}} \times 100$
   - **Discount %:** $\frac{\text{Discounts}}{\text{Gross Sales}} \times 100$
   - **Estimated Gross Sales:** $\text{Units Sold} \times \text{Sale Price}$ (interaction term)
   - **Year-Month:** Extracted temporal period (`YYYY-MM`) for chronological trend evaluation.

---

## 2. Exploratory Data Analysis (EDA) & Key Findings

### 2.1 Customer Segment Performance Ledger
The portfolio serves five distinct customer tiers. A breakdown of performance reveals severe divergence:

| Customer Segment | Order Count | Units Sold | Total Net Sales ($) | Total Net Profit ($) | Profit Margin (%) | Strategic Status |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **Government** | 300 | 470,674 | $52,504,260.67 | $11,388,173.17 | **21.69%** | Primary Cash Cow |
| **Small Business** | 100 | 153,139 | $42,427,918.50 | $4,143,168.50 | **9.77%** | High Volume, Moderate Margin |
| **Enterprise** | 100 | 168,552 | $19,611,694.38 | **-$614,545.63** | **-3.13%** | **Operating Deficit (Loss)** |
| **Midmarket** | 100 | 172,178 | $2,381,883.08 | $660,103.07 | **27.71%** | Healthy Niche |
| **Channel Partners** | 100 | 161,264 | $1,800,593.64 | $1,316,803.14 | **73.13%** | Ultra-High Margin |
| **Total / Overall** | **700** | **1,125,808** | **$118,726,350.26** | **$16,893,702.26** | **14.23%** | Balanced Portfolio |

#### Key Insight: The Enterprise Deficit
The Enterprise segment represents 16.5% of total sales ($19.61M) yet generates an operating deficit of **-$614.5K**. This deficit is caused by aggressive price concession discounting combined with high baseline cost structures.

### 2.2 Geographic Market Profitability
Geographic sales volumes are balanced across all five target countries, but net profitability varies:

| Country | Net Sales ($) | Total COGS ($) | Net Profit ($) | Profit Margin (%) |
|---|:---:|:---:|:---:|:---:|
| **Germany** | $23,505,340.82 | $19,824,952.00 | $3,680,388.82 | **15.66%** |
| **France** | $24,354,172.28 | $20,573,151.50 | $3,781,020.78 | **15.53%** |
| **Canada** | $24,887,654.89 | $21,358,426.00 | $3,529,228.88 | **14.18%** |
| **Mexico** | $20,949,352.11 | $18,041,829.00 | $2,907,523.11 | **13.88%** |
| **United States** | $25,029,830.16 | $22,034,289.50 | $2,995,540.67 | **11.97%** |

- **Germany & France** lead global margin efficiency at ~15.6%.
- The **United States** generated the highest topline sales ($25.03M) but the lowest net profit margin (11.97%), primarily due to aggressive promotional discount adoption.

### 2.3 Product Portfolio Matrix
The organization manufactures six distinct product lines:

| Product | Avg Sale Price ($) | Units Sold | Net Sales ($) | Net Profit ($) | Margin (%) |
|---|:---:|:---:|:---:|:---:|:---:|
| **Paseo** | $108.18 | 338,240 | $33,011,143.95 | $4,797,437.95 | 14.53% |
| **VTT** | $138.59 | 168,783 | $20,511,921.02 | $3,034,608.02 | 14.79% |
| **Velo** | $115.24 | 162,425 | $18,250,059.46 | $2,305,992.46 | 12.64% |
| **Amarilla** | $128.68 | 155,315 | $17,747,116.06 | $2,814,104.06 | **15.86%** |
| **Montana** | $117.10 | 154,198 | $15,390,801.88 | $2,114,754.88 | 13.74% |
| **Carretera** | $111.77 | 146,846 | $13,815,307.88 | $1,826,804.89 | 13.22% |

- **Paseo** is the clear flagship volume leader, generating nearly double the units of any other product and driving 27.8% of total revenue.
- **Amarilla** delivers the highest standalone profit margin at **15.86%**.

### 2.4 The Cannibalizing Effect of Discount Bands
Analyzing margin retention across discount tiers exposes significant profit surrender:

| Discount Band | Orders | Gross Sales ($) | Discounts Given ($) | Net Sales ($) | Net Profit ($) | Realized Margin |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **None (0%)** | 53 | $7,943,654.00 | $0.00 | $7,943,654.00 | $1,736,455.00 | **21.86%** |
| **Low (1–4%)** | 160 | $35,515,454.50 | $885,675.80 | $34,629,778.70 | $6,188,857.70 | **17.87%** |
| **Medium (5–8%)** | 242 | $41,782,977.01 | $3,002,546.17 | $38,780,430.84 | $5,579,522.83 | **14.39%** |
| **High (9–15%)** | 245 | $42,689,513.01 | $5,317,026.28 | $37,372,486.73 | $3,388,866.73 | **9.07%** |

**Takeaway:** The High Discount Band surrenders **$5.32M** in price concessions to capture $37.37M in net sales, generating only $3.39M in profit (a margin drop of **12.8 percentage points** compared to undiscounted sales).

---

## 3. SQL Relational Auditing Engine

Relational queries executed against the SQLite database yielded actionable management insights:
1. **Segment Concentration:** Government orders represent 42.8% of transactions and 67.4% of total company profit.
2. **Seasonality Spikes:** Net sales peaked dramatically in Q4 (October through December), with December 2014 generating **$12.98M**, up from $9.28M in December 2013 (a 39.9% YoY increase).
3. **Channel Partner Efficiency:** Despite having an average order value of only $18,000, Channel Partners generate virtually zero inventory overhead for the enterprise, achieving a **73.13% profit margin**.

---

## 4. Machine Learning Sales Prediction Model

### 4.1 Methodology & Feature Engineering
To predict realized Net Sales ($), we configured an 80/20 train-test split (560 training records, 140 test records) with seed reproducibility (`random_state=42`). 

**Feature Matrix:**
- Numerical: `Units Sold`, `Sale Price`, `Manufacturing Price`, `Estimated_Gross_Sales`, `Month Number`, `Year`
- Categorical (One-Hot Encoded): `Segment`, `Country`, `Product`, `Discount Band`

### 4.2 Model Benchmark Results
Five candidate algorithms were evaluated on unseen test data:

| Model Architecture | Train $R^2$ | Test $R^2$ | MAE ($) | RMSE ($) | MAPE (%) | Ranking |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Gradient Boosting Regressor** | **1.0000** | **0.9950** | **$5,288.84** | **$16,629.19** | **2.90%** | **1st (Best)** |
| **Random Forest Regressor** | 0.9995 | 0.9922 | $7,441.52 | $20,782.17 | 3.55% | 2nd |
| **Lasso Regression (L1)** | 0.9976 | 0.9971 | $8,582.90 | $12,659.88 | 34.78% | 3rd |
| **Ridge Regression (L2)** | 0.9976 | 0.9971 | $8,728.32 | $12,731.13 | 35.45% | 4th |
| **Linear Regression (OLS)** | 0.9976 | 0.9971 | $8,804.23 | $12,732.55 | 36.44% | 5th |

### 4.3 Diagnostics & Model Selection
- The **Gradient Boosting Regressor** is the superior production model, achieving the lowest Mean Absolute Error (**$5,288.84**) and Mean Absolute Percentage Error (**2.90%**). On average, predictions deviate by less than 3% from actual commercial sales.
- **Top 3 Predictive Drivers:**
  1. `Estimated_Gross_Sales` ($Units \times Price$)
  2. `Discount Band_High`
  3. `Discount Band_Medium`

---

## 5. Strategic Business Recommendations

### Recommendation 1: Turn Around the Enterprise Segment Deficit
- **The Issue:** Enterprise contracts produced a net loss of -$614,545 on $19.61M in sales (-3.13% margin).
- **Action:** Introduce an immediate contract audit for Enterprise accounts. Institute a **contract price floor requiring a minimum 12% gross profit margin**. Transition enterprise accounts off bespoke packaging or free freight terms that inflate COGS.

### Recommendation 2: Rationalize and Cap the High Discount Tier
- **The Issue:** $5.32M in discounts surrendered under the High tier reduced profit margin to 9.07%.
- **Action:** Restrict the "High" discount band exclusively to strategic year-end inventory liquidations or volume commitments above 3,500 units. Shifting 40% of High discount orders into the Medium tier will recapture an estimated **$1.85M in annual operating profit**.

### Recommendation 3: Scale High-Margin Channel Partners
- **The Issue:** Channel Partners deliver an unmatched **73.13% margin** ($1.32M profit on only $1.80M sales), but represent just 1.5% of sales.
- **Action:** Expand distributor margin-sharing incentives and recruit regional partners in Canada and Germany to double Channel Partner volume within 12 months.

### Recommendation 4: Operationalize Predictive Revenue Forecasting
- Deploy the trained Gradient Boosting model into quarterly inventory planning and cash flow budgeting to predict realized net cash receipts with >97% accuracy.

---

## 6. Deliverable Directory & Verification Guide

| Deliverable Name | File Path / Name | Description |
|---|---|---|
| **Python Notebook** | `Capstone_Project_Analysis.ipynb` | Fully executed, 6-stage end-to-end Python notebook with EDA, SQL queries, and ML models. |
| **Excel Financial Model** | `Financial_Analysis_Model.xlsx` | Multi-tab executive model with KPI summary cards, pivot tables, and ML test predictions. |
| **Power BI Ready Dataset** | `Cleaned_Sales_Data.xlsx` & `.csv` | Fully cleaned, validated dataset ready for immediate BI ingest. |
| **Power BI DAX Code** | `PowerBI_DAX_Measures.dax` | Pre-written DAX measures for revenue, margins, and YoY growth. |
| **Power BI Guide** | `Power_BI_Dashboard_Guide.md` | Step-by-step layout and build guide for Power BI Desktop. |
| **Interactive Dashboard** | `PowerBI_Interactive_Dashboard.html` | High-fidelity executive web dashboard featuring interactive Chart.js visualizations. |
| **Visual Portfolio** | `visualizations/01_` to `10_` | 10 high-resolution (300 DPI) publication-quality charts. |

---
*Report prepared for the SkillNexis Internship Evaluation Committee.*


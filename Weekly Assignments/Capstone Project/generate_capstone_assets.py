import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
import nbformat as nbf

# Configure styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

os.makedirs('visualizations', exist_ok=True)

print("1. Loading raw dataset...")
df_raw = pd.read_excel('dataset.xlsx')

# Data Cleaning
df = df_raw.copy()
df.columns = [c.strip() for c in df.columns]
df['Discount Band'] = df['Discount Band'].fillna('None').astype(str).str.strip()
df['Segment'] = df['Segment'].str.strip()
df['Country'] = df['Country'].str.strip()
df['Product'] = df['Product'].str.strip()
df['Month Name'] = df['Month Name'].str.strip()

# Add analytical columns
df['Profit Margin %'] = np.round((df['Profit'] / df['Sales']) * 100, 2)
df['Discount %'] = np.round((df['Discounts'] / df['Gross Sales']) * 100, 2)
df['Estimated_Gross_Sales'] = df['Units Sold'] * df['Sale Price']
df['Year_Month'] = df['Date'].dt.to_period('M').astype(str)

print(f"Cleaned data shape: {df.shape}")
print(df.head(2))

# Export clean datasets
df.to_csv('Cleaned_Sales_Data.csv', index=False)
df.to_excel('Cleaned_Sales_Data.xlsx', index=False)
print("Saved Cleaned_Sales_Data.csv and Cleaned_Sales_Data.xlsx")

# ==========================================
# 2. GENERATE HIGH-QUALITY CHARTS
# ==========================================
print("2. Generating visualizations...")

# 01 Sales & Profit Distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.histplot(df['Sales'], kde=True, ax=axes[0], color='#1f77b4', bins=25)
axes[0].set_title('Distribution of Net Sales ($)', fontsize=13, fontweight='bold', pad=12)
axes[0].set_xlabel('Sales ($)', fontsize=11)
axes[0].set_ylabel('Frequency', fontsize=11)

sns.histplot(df['Profit'], kde=True, ax=axes[1], color='#2ca02c', bins=25)
axes[1].set_title('Distribution of Profit ($)', fontsize=13, fontweight='bold', pad=12)
axes[1].set_xlabel('Profit ($)', fontsize=11)
axes[1].set_ylabel('Frequency', fontsize=11)
plt.tight_layout()
plt.savefig('visualizations/01_eda_sales_profit_dist.png')
plt.close()

# 02 Segment Performance
segment_perf = df.groupby('Segment')[['Sales', 'Profit', 'Units Sold']].sum().reset_index()
segment_perf = segment_perf.sort_values(by='Sales', ascending=False)

fig, ax1 = plt.subplots(figsize=(10, 5))
x = np.arange(len(segment_perf))
width = 0.35
rects1 = ax1.bar(x - width/2, segment_perf['Sales']/1e6, width, label='Sales ($M)', color='#2b5c8f')
rects2 = ax1.bar(x + width/2, segment_perf['Profit']/1e6, width, label='Profit ($M)', color='#48bf84')
ax1.set_xticks(x)
ax1.set_xticklabels(segment_perf['Segment'], fontsize=10, rotation=15)
ax1.set_ylabel('Amount in Millions ($)', fontsize=11)
ax1.set_title('Total Net Sales & Profit by Customer Segment', fontsize=13, fontweight='bold', pad=12)
ax1.legend(frameon=True)
for rect in rects1:
    h = rect.get_height()
    ax1.annotate(f'${h:.1f}M', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                 textcoords="offset points", ha='center', va='bottom', fontsize=9)
for rect in rects2:
    h = rect.get_height()
    ax1.annotate(f'${h:.1f}M', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                 textcoords="offset points", ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig('visualizations/02_eda_segment_performance.png')
plt.close()

# 03 Country Profitability & Margin
country_perf = df.groupby('Country').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Units Sold': 'sum'
}).reset_index()
country_perf['Profit Margin %'] = (country_perf['Profit'] / country_perf['Sales']) * 100
country_perf = country_perf.sort_values(by='Profit Margin %', ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
colors = ['#2e7d32' if m >= 14 else '#1976d2' for m in country_perf['Profit Margin %']]
bars = ax.barh(country_perf['Country'], country_perf['Profit Margin %'], color=colors)
ax.set_xlabel('Profit Margin (%)', fontsize=11)
ax.set_title('Profit Margin (%) by Country', fontsize=13, fontweight='bold', pad=12)
for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.3, bar.get_y() + bar.get_height()/2, f'{w:.1f}%', va='center', fontsize=10, fontweight='bold')
ax.set_xlim(0, max(country_perf['Profit Margin %']) + 4)
plt.tight_layout()
plt.savefig('visualizations/03_eda_country_profitability.png')
plt.close()

# 04 Product Performance Matrix
prod_perf = df.groupby('Product').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Units Sold': 'sum',
    'Sale Price': 'mean'
}).reset_index().sort_values(by='Sales', ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
sns.scatterplot(
    data=prod_perf, x='Units Sold', y='Profit', size='Sales', sizes=(200, 1000),
    hue='Product', palette='Set2', ax=ax, legend=False
)
for _, row in prod_perf.iterrows():
    ax.text(row['Units Sold'] + 2000, row['Profit'], f"{row['Product']}\n(${row['Profit']/1e6:.2f}M)",
            fontsize=9, fontweight='bold', va='center')
ax.set_title('Product Performance Matrix (Volume vs. Profit, Bubble Size = Sales)', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Total Units Sold', fontsize=11)
ax.set_ylabel('Total Profit ($)', fontsize=11)
plt.tight_layout()
plt.savefig('visualizations/04_eda_product_matrix.png')
plt.close()

# 05 Monthly Sales Trend & Seasonality
monthly = df.groupby(['Year', 'Month Number', 'Month Name'])['Sales'].sum().reset_index()
monthly = monthly.sort_values(by=['Year', 'Month Number'])
monthly['Period'] = monthly['Month Name'].str[:3] + ' ' + monthly['Year'].astype(str)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly['Period'], monthly['Sales'] / 1e6, marker='o', linewidth=2.5, color='#e65100', markersize=6)
ax.fill_between(monthly['Period'], monthly['Sales'] / 1e6, color='#ffe0b2', alpha=0.5)
ax.set_title('Monthly Net Sales Trend (2013 - 2014)', fontsize=13, fontweight='bold', pad=12)
ax.set_ylabel('Net Sales ($ Millions)', fontsize=11)
ax.set_xticks(range(len(monthly)))
ax.set_xticklabels(monthly['Period'], rotation=45, ha='right', fontsize=9)
for i, txt in enumerate(monthly['Sales'] / 1e6):
    ax.annotate(f'${txt:.2f}M', (i, txt), textcoords="offset points", xytext=(0,7), ha='center', fontsize=8)
plt.tight_layout()
plt.savefig('visualizations/05_eda_monthly_trend_seasonality.png')
plt.close()

# 06 Discount Band Impact on Profit Margin
disc_perf = df.groupby('Discount Band').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Gross Sales': 'sum',
    'Discounts': 'sum'
}).reindex(['None', 'Low', 'Medium', 'High']).reset_index()
disc_perf['Profit Margin %'] = (disc_perf['Profit'] / disc_perf['Sales']) * 100

fig, ax1 = plt.subplots(figsize=(9, 5))
palette = ['#43a047', '#fdd835', '#fb8c00', '#e53935']
bars = ax1.bar(disc_perf['Discount Band'], disc_perf['Profit Margin %'], color=palette, edgecolor='black', alpha=0.85)
ax1.set_title('Impact of Discount Bands on Net Profit Margin (%)', fontsize=13, fontweight='bold', pad=12)
ax1.set_xlabel('Discount Band Tier', fontsize=11)
ax1.set_ylabel('Profit Margin (%)', fontsize=11)
for bar in bars:
    h = bar.get_height()
    ax1.annotate(f'{h:.1f}%', xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 4),
                 textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig('visualizations/06_eda_discount_band_impact.png')
plt.close()

# 07 Correlation Heatmap
num_cols = ['Units Sold', 'Manufacturing Price', 'Sale Price', 'Gross Sales', 'Discounts', 'Sales', 'COGS', 'Profit']
corr = df[num_cols].corr()
fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='Blues', cbar=True, ax=ax, linewidths=0.5)
ax.set_title('Correlation Matrix of Financial Variables', fontsize=13, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig('visualizations/07_eda_correlation_heatmap.png')
plt.close()

# ==========================================
# 3. SQL ANALYSIS ENGINE
# ==========================================
print("3. Executing SQL Analytics...")
conn = sqlite3.connect(':memory:')
df.to_sql('financial_data', conn, index=False, if_exists='replace')

sql_queries = {
    "1. Segment Performance Summary": """
        SELECT Segment,
               COUNT(*) AS Order_Count,
               ROUND(SUM([Units Sold]), 0) AS Total_Units_Sold,
               ROUND(SUM(Sales), 2) AS Total_Sales,
               ROUND(SUM(Profit), 2) AS Total_Profit,
               ROUND((SUM(Profit) * 100.0 / SUM(Sales)), 2) AS Profit_Margin_Pct
        FROM financial_data
        GROUP BY Segment
        ORDER BY Total_Sales DESC;
    """,
    "2. Country Profitability & Sales": """
        SELECT Country,
               ROUND(SUM(Sales), 2) AS Total_Sales,
               ROUND(SUM(COGS), 2) AS Total_COGS,
               ROUND(SUM(Profit), 2) AS Total_Profit,
               ROUND((SUM(Profit) * 100.0 / SUM(Sales)), 2) AS Profit_Margin_Pct
        FROM financial_data
        GROUP BY Country
        ORDER BY Total_Profit DESC;
    """,
    "3. Product Performance Ranking": """
        SELECT Product,
               ROUND(AVG([Sale Price]), 2) AS Avg_Sale_Price,
               ROUND(SUM([Units Sold]), 0) AS Total_Units,
               ROUND(SUM(Sales), 2) AS Total_Sales,
               ROUND(SUM(Profit), 2) AS Total_Profit,
               ROUND((SUM(Profit) * 100.0 / SUM(Sales)), 2) AS Margin_Pct
        FROM financial_data
        GROUP BY Product
        ORDER BY Total_Sales DESC;
    """,
    "4. Discount Band Analysis": """
        SELECT [Discount Band],
               COUNT(*) AS Transaction_Count,
               ROUND(SUM(Discounts), 2) AS Total_Discounts,
               ROUND(SUM(Sales), 2) AS Total_Net_Sales,
               ROUND(SUM(Profit), 2) AS Total_Profit,
               ROUND((SUM(Profit) * 100.0 / SUM(Sales)), 2) AS Realized_Margin_Pct
        FROM financial_data
        GROUP BY [Discount Band]
        ORDER BY Total_Net_Sales DESC;
    """,
    "5. Annual Comparison (2013 vs 2014)": """
        SELECT Year,
               COUNT(*) AS Transactions,
               ROUND(SUM(Sales), 2) AS Total_Sales,
               ROUND(SUM(Profit), 2) AS Total_Profit,
               ROUND((SUM(Profit) * 100.0 / SUM(Sales)), 2) AS Margin_Pct
        FROM financial_data
        GROUP BY Year
        ORDER BY Year;
    """
}

sql_results = {}
for qname, qsql in sql_queries.items():
    res_df = pd.read_sql_query(qsql, conn)
    sql_results[qname] = res_df
    print(f"\n--- SQL Query: {qname} ---")
    print(res_df.to_string(index=False))

# ==========================================
# 4. MACHINE LEARNING REGRESSION MODELING
# ==========================================
print("\n4. Training Machine Learning Regression Models...")

# Feature Engineering
features_baseline = ['Segment', 'Country', 'Product', 'Discount Band', 'Units Sold', 'Manufacturing Price', 'Sale Price', 'Month Number', 'Year']
X_base = pd.get_dummies(df[features_baseline], drop_first=True)
y = df['Sales']

# Feature Set with Interaction (Domain Informed)
features_engineered = ['Segment', 'Country', 'Product', 'Discount Band', 'Units Sold', 'Manufacturing Price', 'Sale Price', 'Estimated_Gross_Sales', 'Month Number', 'Year']
X_eng = pd.get_dummies(df[features_engineered], drop_first=True)

X_train, X_test, y_train, y_test = train_test_split(X_eng, y, test_size=0.20, random_state=42)

models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Lasso Regression': Lasso(alpha=50.0),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=150, learning_rate=0.08, max_depth=4, random_state=42)
}

results_list = []
trained_models = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    r2_tr = r2_score(y_train, y_pred_train)
    r2_te = r2_score(y_test, y_pred_test)
    mae_te = mean_absolute_error(y_test, y_pred_test)
    rmse_te = np.sqrt(mean_squared_error(y_test, y_pred_test))
    mape_te = np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100
    
    trained_models[name] = model
    results_list.append({
        'Model': name,
        'Train R²': round(r2_tr, 4),
        'Test R²': round(r2_te, 4),
        'MAE ($)': round(mae_te, 2),
        'RMSE ($)': round(rmse_te, 2),
        'MAPE (%)': round(mape_te, 2)
    })

results_df = pd.DataFrame(results_list)
print("\nRegression Benchmarking Summary:")
print(results_df.to_string(index=False))

# Best model: Gradient Boosting
best_model = trained_models['Gradient Boosting']
test_preds = best_model.predict(X_test)

# Plot 08 Model Comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.barplot(data=results_df, x='Model', y='Test R²', ax=axes[0], palette='Blues_r')
axes[0].set_title('Test R² Score across Regression Models', fontsize=12, fontweight='bold')
axes[0].set_ylim(0.9, 1.01)
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=20, ha='right')
for p in axes[0].patches:
    axes[0].annotate(f"{p.get_height():.4f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='bottom', fontsize=9, xytext=(0, 2), textcoords='offset points')

sns.barplot(data=results_df, x='Model', y='MAE ($)', ax=axes[1], palette='Oranges_r')
axes[1].set_title('Test Mean Absolute Error ($)', fontsize=12, fontweight='bold')
axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=20, ha='right')
for p in axes[1].patches:
    axes[1].annotate(f"${p.get_height():,.0f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='bottom', fontsize=9, xytext=(0, 2), textcoords='offset points')
plt.tight_layout()
plt.savefig('visualizations/08_ml_model_comparison.png')
plt.close()

# Plot 09 Feature Importance (Gradient Boosting)
feat_imp = pd.DataFrame({
    'Feature': X_eng.columns,
    'Importance': best_model.feature_importances_
}).sort_values(by='Importance', ascending=False).head(10)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=feat_imp, y='Feature', x='Importance', ax=ax, palette='viridis')
ax.set_title('Top 10 Feature Importances (Gradient Boosting Regressor)', fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Relative Importance Weight', fontsize=11)
plt.tight_layout()
plt.savefig('visualizations/09_ml_feature_importance.png')
plt.close()

# Plot 10 Actual vs Predicted
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(y_test / 1e3, test_preds / 1e3, alpha=0.7, color='#1f77b4', edgecolors='k')
min_val = min(y_test.min(), test_preds.min()) / 1e3
max_val = max(y_test.max(), test_preds.max()) / 1e3
ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Fit (y = x)')
ax.set_title(f'Actual vs. Predicted Sales (Test Set R² = {results_df.loc[results_df["Model"]=="Gradient Boosting", "Test R²"].values[0]:.4f})',
             fontsize=13, fontweight='bold', pad=12)
ax.set_xlabel('Actual Sales ($ in Thousands)', fontsize=11)
ax.set_ylabel('Predicted Sales ($ in Thousands)', fontsize=11)
ax.legend(frameon=True)
plt.tight_layout()
plt.savefig('visualizations/10_ml_actual_vs_predicted.png')
plt.close()

print("Visualizations 01 to 10 successfully generated!")

# Save Test Set Predictions for Excel
test_analysis_df = df.loc[X_test.index].copy()
test_analysis_df['Predicted_Sales'] = test_preds
test_analysis_df['Prediction_Error'] = test_analysis_df['Predicted_Sales'] - test_analysis_df['Sales']
test_analysis_df['Abs_Error_Pct'] = (test_analysis_df['Prediction_Error'].abs() / test_analysis_df['Sales']) * 100

# ==========================================
# 5. CREATE COMPREHENSIVE EXCEL WORKBOOK
# ==========================================
print("5. Generating multi-tab Financial Analysis Model Excel Workbook...")

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# Fonts & Fills
header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
kpi_title_font = Font(name="Calibri", size=10, bold=False, color="595959")
kpi_value_font = Font(name="Calibri", size=18, bold=True, color="1F4E79")
title_font = Font(name="Calibri", size=16, bold=True, color="1F4E79")
subtitle_font = Font(name="Calibri", size=11, italic=True, color="595959")
section_font = Font(name="Calibri", size=13, bold=True, color="203764")

thin_border = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)
card_border = Border(
    left=Side(style='medium', color='1F4E79'),
    right=Side(style='medium', color='1F4E79'),
    top=Side(style='medium', color='1F4E79'),
    bottom=Side(style='medium', color='1F4E79')
)

# Sheet 1: Executive KPI Summary
ws_kpi = wb.create_sheet(title="Executive KPI Summary")
ws_kpi.views.sheetView[0].showGridLines = True

ws_kpi["B2"] = "SkillNexis Capstone: Financial Performance Executive Dashboard"
ws_kpi["B2"].font = title_font
ws_kpi["B3"] = "End-to-End Enterprise Sales, Profitability & Machine Learning Forecasting Analysis"
ws_kpi["B3"].font = subtitle_font

# KPI Cards definition
kpis = [
    ("TOTAL NET SALES", f"${df['Sales'].sum():,.2f}", "B5", "B6", "C6"),
    ("TOTAL PROFIT", f"${df['Profit'].sum():,.2f}", "D5", "D6", "E6"),
    ("PROFIT MARGIN", f"{(df['Profit'].sum()/df['Sales'].sum())*100:.2f}%", "F5", "F6", "G6"),
    ("TOTAL UNITS SOLD", f"{df['Units Sold'].sum():,.0f}", "H5", "H6", "I6"),
    ("TOTAL DISCOUNTS", f"${df['Discounts'].sum():,.2f}", "J5", "J6", "K6")
]

for title, val, tcell, vcell_start, vcell_end in kpis:
    ws_kpi[tcell] = title
    ws_kpi[tcell].font = kpi_title_font
    ws_kpi[tcell].alignment = Alignment(horizontal="center", vertical="center")
    
    ws_kpi.merge_cells(f"{vcell_start}:{vcell_end}")
    val_cell = ws_kpi[vcell_start]
    val_cell.value = val
    val_cell.font = kpi_value_font
    val_cell.alignment = Alignment(horizontal="center", vertical="center")
    val_cell.fill = PatternFill(start_color="F2F4F8", end_color="F2F4F8", fill_type="solid")

# Segment Breakdown Table on KPI sheet
ws_kpi["B9"] = "Segment Performance Summary"
ws_kpi["B9"].font = section_font

seg_headers = ["Segment", "Transactions", "Units Sold", "Gross Sales ($)", "Discounts ($)", "Net Sales ($)", "Profit ($)", "Margin (%)"]
for c_idx, h in enumerate(seg_headers, start=2):
    cell = ws_kpi.cell(row=10, column=c_idx, value=h)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center")

seg_summary = df.groupby('Segment').agg({
    'Segment': 'count',
    'Units Sold': 'sum',
    'Gross Sales': 'sum',
    'Discounts': 'sum',
    'Sales': 'sum',
    'Profit': 'sum'
}).rename(columns={'Segment': 'Count'}).reset_index().sort_values(by='Sales', ascending=False)
seg_summary['Margin %'] = (seg_summary['Profit'] / seg_summary['Sales']) * 100

for r_idx, row in seg_summary.iterrows():
    curr_row = 11 + r_idx
    ws_kpi.cell(row=curr_row, column=2, value=row['Segment'])
    ws_kpi.cell(row=curr_row, column=3, value=row['Count']).number_format = '#,##0'
    ws_kpi.cell(row=curr_row, column=4, value=row['Units Sold']).number_format = '#,##0'
    ws_kpi.cell(row=curr_row, column=5, value=row['Gross Sales']).number_format = '$#,##0.00'
    ws_kpi.cell(row=curr_row, column=6, value=row['Discounts']).number_format = '$#,##0.00'
    ws_kpi.cell(row=curr_row, column=7, value=row['Sales']).number_format = '$#,##0.00'
    ws_kpi.cell(row=curr_row, column=8, value=row['Profit']).number_format = '$#,##0.00'
    ws_kpi.cell(row=curr_row, column=9, value=row['Margin %'] / 100).number_format = '0.00%'
    for c in range(2, 10):
        ws_kpi.cell(row=curr_row, column=c).border = thin_border

# Country Breakdown Table
ws_kpi["B18"] = "Geographic Market Performance"
ws_kpi["B18"].font = section_font

cntry_headers = ["Country", "Units Sold", "Net Sales ($)", "COGS ($)", "Profit ($)", "Margin (%)"]
for c_idx, h in enumerate(cntry_headers, start=2):
    cell = ws_kpi.cell(row=19, column=c_idx, value=h)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center")

cntry_summary = df.groupby('Country').agg({
    'Units Sold': 'sum',
    'Sales': 'sum',
    'COGS': 'sum',
    'Profit': 'sum'
}).reset_index().sort_values(by='Profit', ascending=False)
cntry_summary['Margin %'] = (cntry_summary['Profit'] / cntry_summary['Sales']) * 100

for r_idx, row in cntry_summary.iterrows():
    curr_row = 20 + r_idx
    ws_kpi.cell(row=curr_row, column=2, value=row['Country'])
    ws_kpi.cell(row=curr_row, column=3, value=row['Units Sold']).number_format = '#,##0'
    ws_kpi.cell(row=curr_row, column=4, value=row['Sales']).number_format = '$#,##0.00'
    ws_kpi.cell(row=curr_row, column=5, value=row['COGS']).number_format = '$#,##0.00'
    ws_kpi.cell(row=curr_row, column=6, value=row['Profit']).number_format = '$#,##0.00'
    ws_kpi.cell(row=curr_row, column=7, value=row['Margin %'] / 100).number_format = '0.00%'
    for c in range(2, 8):
        ws_kpi.cell(row=curr_row, column=c).border = thin_border

# Machine Learning Performance Benchmark Table
ws_kpi["B27"] = "Machine Learning Sales Forecasting Benchmark"
ws_kpi["B27"].font = section_font

ml_headers = ["Model", "Train R²", "Test R²", "MAE ($)", "RMSE ($)", "MAPE (%)"]
for c_idx, h in enumerate(ml_headers, start=2):
    cell = ws_kpi.cell(row=28, column=c_idx, value=h)
    cell.fill = PatternFill(start_color="333f48", end_color="333f48", fill_type="solid")
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center")

for r_idx, row in results_df.iterrows():
    curr_row = 29 + r_idx
    ws_kpi.cell(row=curr_row, column=2, value=row['Model'])
    ws_kpi.cell(row=curr_row, column=3, value=row['Train R²']).number_format = '0.0000'
    ws_kpi.cell(row=curr_row, column=4, value=row['Test R²']).number_format = '0.0000'
    ws_kpi.cell(row=curr_row, column=5, value=row['MAE ($)']).number_format = '$#,##0.00'
    ws_kpi.cell(row=curr_row, column=6, value=row['RMSE ($)']).number_format = '$#,##0.00'
    ws_kpi.cell(row=curr_row, column=7, value=row['MAPE (%)'] / 100).number_format = '0.00%'
    for c in range(2, 8):
        ws_kpi.cell(row=curr_row, column=c).border = thin_border

# Sheet 2: Cleaned Data
ws_data = wb.create_sheet(title="Cleaned Data")
ws_data.views.sheetView[0].showGridLines = True
cols_to_export = ['Segment', 'Country', 'Product', 'Discount Band', 'Units Sold', 'Manufacturing Price',
                  'Sale Price', 'Gross Sales', 'Discounts', 'Sales', 'COGS', 'Profit', 'Profit Margin %', 'Date', 'Month Number', 'Month Name', 'Year']

for c_idx, col_name in enumerate(cols_to_export, start=1):
    cell = ws_data.cell(row=1, column=c_idx, value=col_name)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center")

for r_idx, row in df[cols_to_export].iterrows():
    curr_row = 2 + r_idx
    for c_idx, col_name in enumerate(cols_to_export, start=1):
        c = ws_data.cell(row=curr_row, column=c_idx, value=row[col_name])
        if col_name in ['Units Sold', 'Manufacturing Price', 'Sale Price', 'Gross Sales', 'Discounts', 'Sales', 'COGS', 'Profit']:
            c.number_format = '#,##0.00'
        elif col_name == 'Profit Margin %':
            c.number_format = '0.00'
        elif col_name == 'Date':
            c.number_format = 'yyyy-mm-dd'

# Sheet 3: Product Analysis
ws_prod = wb.create_sheet(title="Product Analysis")
ws_prod.views.sheetView[0].showGridLines = True
prod_headers = ["Product", "Total Units Sold", "Avg Manufacturing Price", "Avg Sale Price", "Total Gross Sales", "Total Discounts", "Total Net Sales", "Total Profit", "Margin %"]
for c_idx, h in enumerate(prod_headers, start=1):
    c = ws_prod.cell(row=1, column=c_idx, value=h)
    c.fill = header_fill
    c.font = header_font
    c.alignment = Alignment(horizontal="center")

prod_summary = df.groupby('Product').agg({
    'Units Sold': 'sum',
    'Manufacturing Price': 'mean',
    'Sale Price': 'mean',
    'Gross Sales': 'sum',
    'Discounts': 'sum',
    'Sales': 'sum',
    'Profit': 'sum'
}).reset_index().sort_values(by='Sales', ascending=False)
prod_summary['Margin %'] = (prod_summary['Profit'] / prod_summary['Sales']) * 100

for r_idx, row in prod_summary.iterrows():
    curr_row = 2 + r_idx
    ws_prod.cell(row=curr_row, column=1, value=row['Product'])
    ws_prod.cell(row=curr_row, column=2, value=row['Units Sold']).number_format = '#,##0'
    ws_prod.cell(row=curr_row, column=3, value=row['Manufacturing Price']).number_format = '$#,##0.00'
    ws_prod.cell(row=curr_row, column=4, value=row['Sale Price']).number_format = '$#,##0.00'
    ws_prod.cell(row=curr_row, column=5, value=row['Gross Sales']).number_format = '$#,##0.00'
    ws_prod.cell(row=curr_row, column=6, value=row['Discounts']).number_format = '$#,##0.00'
    ws_prod.cell(row=curr_row, column=7, value=row['Sales']).number_format = '$#,##0.00'
    ws_prod.cell(row=curr_row, column=8, value=row['Profit']).number_format = '$#,##0.00'
    ws_prod.cell(row=curr_row, column=9, value=row['Margin %'] / 100).number_format = '0.00%'

# Sheet 4: ML Predictions vs Actual
ws_ml = wb.create_sheet(title="ML Model Predictions")
ws_ml.views.sheetView[0].showGridLines = True
ml_pred_headers = ["Segment", "Country", "Product", "Discount Band", "Units Sold", "Sale Price", "Actual Sales ($)", "Predicted Sales ($)", "Residual Error ($)", "Abs Error %"]
for c_idx, h in enumerate(ml_pred_headers, start=1):
    c = ws_ml.cell(row=1, column=c_idx, value=h)
    c.fill = PatternFill(start_color="2E7D32", end_color="2E7D32", fill_type="solid")
    c.font = header_font
    c.alignment = Alignment(horizontal="center")

for r_idx, (_, row) in enumerate(test_analysis_df.iterrows()):
    curr_row = 2 + r_idx
    ws_ml.cell(row=curr_row, column=1, value=row['Segment'])
    ws_ml.cell(row=curr_row, column=2, value=row['Country'])
    ws_ml.cell(row=curr_row, column=3, value=row['Product'])
    ws_ml.cell(row=curr_row, column=4, value=row['Discount Band'])
    ws_ml.cell(row=curr_row, column=5, value=row['Units Sold']).number_format = '#,##0'
    ws_ml.cell(row=curr_row, column=6, value=row['Sale Price']).number_format = '$#,##0.00'
    ws_ml.cell(row=curr_row, column=7, value=row['Sales']).number_format = '$#,##0.00'
    ws_ml.cell(row=curr_row, column=8, value=row['Predicted_Sales']).number_format = '$#,##0.00'
    ws_ml.cell(row=curr_row, column=9, value=row['Prediction_Error']).number_format = '$#,##0.00'
    ws_ml.cell(row=curr_row, column=10, value=row['Abs_Error_Pct'] / 100).number_format = '0.00%'

# Adjust Column Widths across all sheets
for sheet in wb.worksheets:
    for col in sheet.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

wb.save('Financial_Analysis_Model.xlsx')
print("Saved Financial_Analysis_Model.xlsx successfully!")


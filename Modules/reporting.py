import pandas as pd

def generate_pnl(df):
    pnl = df.groupby("Type")["Amount"].sum()
    return pnl

def monthly_summary(df):
    monthly = df.groupby([df["Date"].dt.to_period("M"), "Type"])["Amount"].sum().unstack()
    monthly = monthly.fillna(0)
    monthly["Profit"] = monthly.get("Revenue", 0) + monthly.get("Expense", 0)
    return monthly

def variance_analysis(monthly_df):
    variance = monthly_df.pct_change() * 100
    return variance
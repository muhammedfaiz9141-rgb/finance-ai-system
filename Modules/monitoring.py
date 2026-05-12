import pandas as pd

def detect_duplicates(df):
    duplicates = df[df.duplicated(subset=["Date", "Description", "Amount"], keep=False)]
    return duplicates


def detect_large_transactions(df, threshold_multiplier=2):
    # Calculate average absolute amount
    avg_amount = df["Amount"].abs().mean()

    # Flag transactions larger than threshold × average
    df["Large_Flag"] = df["Amount"].abs() > (avg_amount * threshold_multiplier)

    large_transactions = df[df["Large_Flag"] == True]

    return large_transactions, avg_amount


def category_variance_alert(df):
    # Monthly category total
    monthly = df.groupby([df["Date"].dt.to_period("M"), "Category"])["Amount"].sum()

    # Convert to DataFrame
    monthly_df = monthly.reset_index()

    alerts = []

    for category in monthly_df["Category"].unique():
        cat_data = monthly_df[monthly_df["Category"] == category]

        if len(cat_data) > 1:
            variance = cat_data["Amount"].pct_change() * 100
            if abs(variance.iloc[-1]) > 30:  # 30% threshold
                alerts.append({
                    "Category": category,
                    "Variance %": variance.iloc[-1]
                })

    return alerts
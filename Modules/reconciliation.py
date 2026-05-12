import pandas as pd

def load_bank_data():
    bank_df = pd.read_excel("Data/bank_statement.xlsx")
    bank_df["Date"] = pd.to_datetime(bank_df["Date"])
    return bank_df

def reconcile_cash(journal_df):

    # Filter only cash entries
    cash_entries = journal_df[journal_df["GL_Name"] == "Cash"].copy()

    # Convert to signed book amount
    cash_entries["Book_Amount"] = cash_entries["Debit"] - cash_entries["Credit"]

    bank_df = load_bank_data()

    bank_df["Matched"] = False
    cash_entries["Matched"] = False

    # Matching logic
    for i, bank_row in bank_df.iterrows():
        for j, book_row in cash_entries.iterrows():
            if (
                bank_row["Amount"] == book_row["Book_Amount"]
                and not book_row["Matched"]
            ):
                bank_df.at[i, "Matched"] = True
                cash_entries.at[j, "Matched"] = True
                break

    # Summary
    summary = {
        "Total Bank Transactions": len(bank_df),
        "Matched Bank Transactions": bank_df["Matched"].sum(),
        "Unmatched Bank Transactions": len(bank_df) - bank_df["Matched"].sum(),
        "Total Book Cash Entries": len(cash_entries),
        "Unmatched Book Entries": len(cash_entries) - cash_entries["Matched"].sum(),
    }

    return bank_df, cash_entries, summary
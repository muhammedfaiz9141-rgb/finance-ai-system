from Modules.chatbot import ask_finance_question
from Modules.monitoring import detect_duplicates, detect_large_transactions, category_variance_alert
from Modules.reconciliation import reconcile_cash
from Modules.journal import auto_generate_journal, create_formatted_journal
import pandas as pd
from Modules.reporting import generate_pnl, monthly_summary, variance_analysis
from Modules.journal import auto_generate_journal

def load_data():
    df = pd.read_excel("Data/transactions.xlsx")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

if __name__ == "__main__":
    
    # Load Data
    df = load_data()
    print("✅ Data Loaded Successfully\n")

    # -----------------------------
    # 📊 REPORTING MODULE
    # -----------------------------
    
    pnl = generate_pnl(df)
    print("📊 P&L Summary:")
    print(pnl, "\n")

    monthly = monthly_summary(df)
    print("📅 Monthly Summary:")
    print(monthly, "\n")

    variance = variance_analysis(monthly)
    print("📈 Variance Analysis (%):")
    print(variance, "\n")

       # -----------------------------
    # 📘 JOURNAL AUTOMATION MODULE
    # -----------------------------

    print("📘 Auto Journal Entries:")
    journal_df_raw = auto_generate_journal(df)
    
    # Get formatted journal and summary
    formatted_journal, journal_summary = create_formatted_journal(journal_df_raw)

    print("\n--- Formatted Journal Entries ---")
    print(formatted_journal)

    print("\n--- Journal Entry Summary ---")
    for key, value in journal_summary.items():
        print(f"{key}: {value}")
            # -----------------------------
        # -----------------------------
    # 🏦 RECONCILIATION MODULE
    # -----------------------------

    print("\n🏦 Bank Reconciliation:")

    bank_df, book_cash, recon_summary = reconcile_cash(formatted_journal)

    print("\n--- Bank Statement ---")
    print(bank_df)

    print("\n--- Book Cash Entries ---")
    print(book_cash[["Date", "Book_Amount", "Matched"]])

    print("\n--- Reconciliation Summary ---")
    for key, value in recon_summary.items():
        print(f"{key}: {value}")
            # -----------------------------
    # 🔎 DATA QUALITY MONITORING
    # -----------------------------

    print("\n🔎 Data Quality Monitoring:")

    # 1️⃣ Duplicates
    duplicates = detect_duplicates(df)
    print("\n--- Duplicate Transactions ---")
    if duplicates.empty:
        print("No duplicates found ✅")
    else:
        print(duplicates)

    # 2️⃣ Large Transactions
    large_tx, avg_amt = detect_large_transactions(df)

    print("\n--- Large Transactions ---")
    print(f"Average Transaction Amount: {avg_amt:.2f}")
    if large_tx.empty:
        print("No unusually large transactions ✅")
    else:
        print(large_tx[["Date", "Description", "Amount"]])

    # 3️⃣ Category Variance Alerts
    alerts = category_variance_alert(df)

    print("\n--- Category Variance Alerts ---")
    if not alerts:
        print("No significant category variance ✅")
    else:
        for alert in alerts:
            print(alert)
                # -----------------------------
        # -----------------------------
    # 🤖 FINANCE CHATBOT (LOCAL)
    # -----------------------------

    print("\n🤖 Finance Chatbot")

    question = input("\nAsk a finance question: ")

    answer = ask_finance_question(df, monthly, question)

    print("\nResponse:")
    print(answer)
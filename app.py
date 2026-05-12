import streamlit as st
import pandas as pd
import io

# Import your modules
from Modules.reporting import generate_pnl, monthly_summary, variance_analysis
from Modules.journal import auto_generate_journal, create_formatted_journal
from Modules.reconciliation import reconcile_cash
from Modules.monitoring import detect_duplicates, detect_large_transactions, category_variance_alert
from Modules.chatbot import ask_finance_question

st.set_page_config(page_title="Finance AI System", layout="wide")

st.title("💼 Finance AI Integrated System")

# -------------------------------------------------
# 📥 Helper Function: Export to Excel
# -------------------------------------------------

def download_excel(data_dict, file_name="report.xlsx"):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in data_dict.items():
            df.to_excel(writer, sheet_name=sheet_name)

    output.seek(0)

    st.download_button(
        label="📥 Download Excel Report",
        data=output,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -------------------------------------------------
# 📂 FILE UPLOAD
# -------------------------------------------------

uploaded_file = st.sidebar.file_uploader(
    "Upload Transactions Excel File",
    type=["xlsx"]
)

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
else:
    df = pd.read_excel("Data/transactions.xlsx")

df["Date"] = pd.to_datetime(df["Date"])

# -------------------------------------------------
# 📊 KPI CARDS
# -------------------------------------------------

total_revenue = df[df["Type"] == "Revenue"]["Amount"].sum()
total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
net_profit = total_revenue + total_expense

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
col2.metric("💸 Total Expenses", f"${abs(total_expense):,.2f}")
col3.metric("📈 Net Profit", f"${net_profit:,.2f}")

st.markdown("---")

# -------------------------------------------------
# 📌 SIDEBAR NAVIGATION
# -------------------------------------------------

menu = st.sidebar.selectbox(
    "Select Module",
    [
        "Reporting",
        "Journal Automation",
        "Reconciliation",
        "Data Monitoring",
        "Finance Chatbot"
    ]
)

# -------------------------------------------------
# 📊 REPORTING MODULE
# -------------------------------------------------

if menu == "Reporting":

    st.header("📊 Financial Reporting")

    pnl = generate_pnl(df)
    monthly = monthly_summary(df)
    variance = variance_analysis(monthly)

    st.subheader("P&L Summary")
    st.dataframe(pnl)

    st.subheader("Monthly Summary")
    st.dataframe(monthly)

    st.subheader("Profit Chart")
    st.bar_chart(monthly["Profit"])

    st.subheader("Variance (%)")
    st.dataframe(variance)

    st.subheader("Export Report")
    download_excel(
        {
            "P&L": pnl.to_frame(),
            "Monthly Summary": monthly,
            "Variance": variance
        },
        file_name="financial_reporting.xlsx"
    )

# -------------------------------------------------
# 📘 JOURNAL AUTOMATION
# -------------------------------------------------

elif menu == "Journal Automation":

    st.header("📘 Journal Automation")

    journal_df = auto_generate_journal(df)
    formatted_journal, summary = create_formatted_journal(journal_df)

    st.subheader("Generated Journal Entries")
    st.dataframe(formatted_journal)

    st.subheader("Journal Summary")
    st.json(summary)

    st.subheader("Export Journal")
    download_excel(
        {"Journal Entries": formatted_journal},
        file_name="journal_entries.xlsx"
    )

# -------------------------------------------------
# 🏦 RECONCILIATION
# -------------------------------------------------

elif menu == "Reconciliation":

    st.header("🏦 Bank Reconciliation")

    journal_df = auto_generate_journal(df)
    formatted_journal, _ = create_formatted_journal(journal_df)

    bank_df, book_cash, summary = reconcile_cash(formatted_journal)

    st.subheader("Bank Statement")
    st.dataframe(bank_df)

    st.subheader("Book Cash Entries")
    st.dataframe(book_cash)

    st.subheader("Reconciliation Summary")
    st.json(summary)

    st.subheader("Export Reconciliation")
    download_excel(
        {
            "Bank Statement": bank_df,
            "Book Cash Entries": book_cash,
        },
        file_name="reconciliation_report.xlsx"
    )

# -------------------------------------------------
# 🔎 DATA MONITORING
# -------------------------------------------------

elif menu == "Data Monitoring":

    st.header("🔎 Data Quality Monitoring")

    duplicates = detect_duplicates(df)
    large_tx, avg_amt = detect_large_transactions(df)
    alerts = category_variance_alert(df)

    st.subheader("Duplicate Transactions")
    if duplicates.empty:
        st.success("No duplicates found ✅")
    else:
        st.dataframe(duplicates)

    st.subheader("Large Transactions")
    st.write(f"Average Transaction Amount: {avg_amt:.2f}")
    if large_tx.empty:
        st.success("No unusually large transactions ✅")
    else:
        st.dataframe(large_tx)

    st.subheader("Category Variance Alerts")
    if not alerts:
        st.success("No significant category variance ✅")
    else:
        st.write(alerts)

# -------------------------------------------------
# 🤖 FINANCE CHATBOT
# -------------------------------------------------

elif menu == "Finance Chatbot":

    st.header("🤖 Finance Chatbot")

    monthly = monthly_summary(df)

    question = st.text_input("Ask a finance question:")

    if st.button("Submit"):
        answer = ask_finance_question(df, monthly, question)
        st.success(answer)
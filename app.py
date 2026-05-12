import streamlit as st
import pandas as pd
import io

# Import modules
from Modules.reporting import generate_pnl, monthly_summary, variance_analysis
from Modules.journal import auto_generate_journal, create_formatted_journal
from Modules.reconciliation import reconcile_cash
from Modules.monitoring import detect_duplicates, detect_large_transactions, category_variance_alert
from Modules.chatbot import ask_finance_question

# PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Finance AI System", layout="wide")

st.title("💼 Finance AI Integrated System")

# -------------------------------------------------
# ✅ Helper: Excel Export
# -------------------------------------------------

def download_excel(data_dict, file_name="report.xlsx"):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df_data in data_dict.items():
            df_data.to_excel(writer, sheet_name=sheet_name)

    output.seek(0)

    st.download_button(
        label="📥 Download Excel Report",
        data=output,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -------------------------------------------------
# ✅ Helper: PDF Export
# -------------------------------------------------

def download_pdf_report(pnl, monthly, net_profit):

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 40

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Financial Report")
    y -= 40

    c.setFont("Helvetica", 12)

    # P&L Section
    c.drawString(50, y, "P&L Summary:")
    y -= 20

    for index, value in pnl.items():
        c.drawString(70, y, f"{index}: {value:,.2f}")
        y -= 18

    y -= 20

    # Net Profit
    c.drawString(50, y, f"Net Profit: {net_profit:,.2f}")
    y -= 30

    # Monthly Summary
    c.drawString(50, y, "Monthly Summary:")
    y -= 20

    monthly_reset = monthly.reset_index()

    for _, row in monthly_reset.iterrows():
        row_text = " | ".join([str(item) for item in row])
        c.drawString(70, y, row_text)
        y -= 15

        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 40

    c.save()
    buffer.seek(0)

    st.download_button(
        label="📄 Download PDF Report",
        data=buffer,
        file_name="financial_report.pdf",
        mime="application/pdf"
    )

# -------------------------------------------------
# ✅ Multi-File Upload
# -------------------------------------------------

uploaded_files = st.sidebar.file_uploader(
    "Upload One or More Transaction Files",
    type=["xlsx"],
    accept_multiple_files=True
)

if uploaded_files:
    df_list = [pd.read_excel(file) for file in uploaded_files]
    df = pd.concat(df_list, ignore_index=True)
    st.sidebar.success(f"{len(uploaded_files)} file(s) uploaded ✅")
else:
    df = pd.read_excel("Data/transactions.xlsx")

# -------------------------------------------------
# ✅ Data Cleaning
# -------------------------------------------------

df.columns = df.columns.str.strip()

required_columns = ["Date", "Description", "Vendor", "Category", "Amount"]

missing_cols = [col for col in required_columns if col not in df.columns]

if missing_cols:
    st.error(f"Missing required columns: {missing_cols}")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"])

if "Type" not in df.columns:
    df["Type"] = df["Amount"].apply(lambda x: "Revenue" if x > 0 else "Expense")

# -------------------------------------------------
# ✅ KPI Cards
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
# ✅ Sidebar Navigation
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
# ✅ REPORTING
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

    st.subheader("Export Options")

    download_excel(
        {
            "P&L": pnl.to_frame(),
            "Monthly Summary": monthly,
            "Variance": variance
        },
        file_name="financial_reporting.xlsx"
    )

    download_pdf_report(pnl, monthly, net_profit)

# -------------------------------------------------
# ✅ JOURNAL
# -------------------------------------------------

elif menu == "Journal Automation":

    st.header("📘 Journal Automation")

    journal_df = auto_generate_journal(df)
    formatted_journal, summary = create_formatted_journal(journal_df)

    st.dataframe(formatted_journal)
    st.json(summary)

    download_excel(
        {"Journal Entries": formatted_journal},
        file_name="journal_entries.xlsx"
    )

# -------------------------------------------------
# ✅ RECONCILIATION
# -------------------------------------------------

elif menu == "Reconciliation":

    st.header("🏦 Bank Reconciliation")

    journal_df = auto_generate_journal(df)
    formatted_journal, _ = create_formatted_journal(journal_df)

    bank_df, book_cash, summary = reconcile_cash(formatted_journal)

    st.dataframe(bank_df)
    st.dataframe(book_cash)
    st.json(summary)

    download_excel(
        {
            "Bank Statement": bank_df,
            "Book Cash Entries": book_cash,
        },
        file_name="reconciliation_report.xlsx"
    )

# -------------------------------------------------
# ✅ MONITORING
# -------------------------------------------------

elif menu == "Data Monitoring":

    st.header("🔎 Data Quality Monitoring")

    duplicates = detect_duplicates(df)
    large_tx, avg_amt = detect_large_transactions(df)
    alerts = category_variance_alert(df)

    if duplicates.empty:
        st.success("No duplicates found ✅")
    else:
        st.dataframe(duplicates)

    st.write(f"Average Transaction Amount: {avg_amt:,.2f}")

    if large_tx.empty:
        st.success("No unusually large transactions ✅")
    else:
        st.dataframe(large_tx)

    if not alerts:
        st.success("No significant category variance ✅")
    else:
        st.write(alerts)

# -------------------------------------------------
# ✅ CHATBOT
# -------------------------------------------------

elif menu == "Finance Chatbot":

    st.header("🤖 Finance Chatbot")

    monthly = monthly_summary(df)

    question = st.text_input("Ask a finance question:")

    if st.button("Submit"):
        answer = ask_finance_question(df, monthly, question)
        st.success(answer)
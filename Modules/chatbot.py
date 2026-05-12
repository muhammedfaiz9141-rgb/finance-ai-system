def ask_finance_question(df, monthly_df, question):

    q = question.lower().strip()

    total_revenue = df[df["Type"] == "Revenue"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    net_profit = total_revenue + total_expense

    if "revenue" in q:
        return f"📊 Total Revenue: ${total_revenue:,.2f}"

    elif "expense" in q:
        return f"💸 Total Expenses: ${abs(total_expense):,.2f}"

    elif "profit" in q:
        return f"💰 Net Profit: ${net_profit:,.2f}"

    elif "summary" in q or "performance" in q:
        return f"""
📈 Financial Performance Summary:
--------------------------------
✅ Total Revenue:    ${total_revenue:,.2f}
✅ Total Expenses:   ${abs(total_expense):,.2f}
✅ Net Profit:       ${net_profit:,.2f}

Overall, the business is profitable with a very healthy margin.
"""

    elif "largest" in q or "biggest" in q:
        largest = df.loc[df["Amount"].abs().idxmax()]
        return f"🔍 Largest transaction: {largest['Description']} - ${largest['Amount']:,.2f}"

    else:
        return """
I can answer:
- What is total revenue?
- What are total expenses?
- What is net profit?
- Summarize financial performance
- Show largest transaction
"""
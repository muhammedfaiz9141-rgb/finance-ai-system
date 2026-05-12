import pandas as pd

CASH_GL = 1000
CASH_NAME = "Cash"

def load_gl_mapping():
    gl_map = pd.read_excel("Data/gl_mapping.xlsx")
    return gl_map

def auto_generate_journal(df):
    gl_map = load_gl_mapping()

    journal_entries = []

    for _, row in df.iterrows():
        gl_account = None
        gl_name = None
        status = "Unmatched"

        # Match GL
        for _, gl_row in gl_map.iterrows():
            if gl_row["Keyword"].lower() in row["Description"].lower():
                gl_account = gl_row["GL_Account"]
                gl_name = gl_row["GL_Name"]
                status = "Matched"
                break

        amount = row["Amount"]

        if gl_account is not None:
            if amount < 0:  # Expense
                # Debit Expense
                journal_entries.append({
                    "Date": row["Date"],
                    "Description": row["Description"],
                    "GL_Account": gl_account,
                    "GL_Name": gl_name,
                    "Debit": abs(amount),
                    "Credit": 0,
                    "Status": status
                })

                # Credit Cash
                journal_entries.append({
                    "Date": row["Date"],
                    "Description": row["Description"],
                    "GL_Account": CASH_GL,
                    "GL_Name": CASH_NAME,
                    "Debit": 0,
                    "Credit": abs(amount),
                    "Status": status
                })

            else:  # Revenue
                # Debit Cash
                journal_entries.append({
                    "Date": row["Date"],
                    "Description": row["Description"],
                    "GL_Account": CASH_GL,
                    "GL_Name": CASH_NAME,
                    "Debit": amount,
                    "Credit": 0,
                    "Status": status
                })

                # Credit Revenue
                journal_entries.append({
                    "Date": row["Date"],
                    "Description": row["Description"],
                    "GL_Account": gl_account,
                    "GL_Name": gl_name,
                    "Debit": 0,
                    "Credit": amount,
                    "Status": status
                })

    journal_df = pd.DataFrame(journal_entries)
    return journal_df


def create_formatted_journal(journal_df):

    summary = {
        "Total Lines": len(journal_df),
        "Total Debit": journal_df["Debit"].sum(),
        "Total Credit": journal_df["Credit"].sum(),
        "Is Balanced": journal_df["Debit"].sum() == journal_df["Credit"].sum()
    }

    return journal_df, summary
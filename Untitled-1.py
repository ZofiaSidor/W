#!/usr/bin/env python3
"""
Simple interactive app to count costs from an Excel file.

Dependencies:
    pip install pandas openpyxl

Usage:
    Run the script and follow prompts to load an Excel file, choose sheet/columns,
    optionally filter by date, view totals by category, and export results.
"""

import sys
import os
from datetime import datetime

try:
    import pandas as pd
except Exception:
    print("Missing dependency: pandas. Install with 'pip install pandas openpyxl'")
    sys.exit(1)


def prompt_file():
    while True:
        path = input("Enter path to Excel file (or 'q' to quit): ").strip()
        if path.lower() in ("q", "quit", "exit"):
            return None
        if os.path.isfile(path):
            return path
        print("File not found. Try again.")


def choose_sheet(xl):
    sheets = xl.sheet_names
    if not sheets:
        raise RuntimeError("No sheets found in workbook.")
    print("\nAvailable sheets:")
    for i, s in enumerate(sheets, 1):
        print(f"  {i}. {s}")
    while True:
        sel = input("Choose sheet by number or name (default 1): ").strip()
        if not sel:
            return sheets[0]
        if sel.isdigit():
            idx = int(sel) - 1
            if 0 <= idx < len(sheets):
                return sheets[idx]
        elif sel in sheets:
            return sel
        print("Invalid selection.")


def pick_column(df, prompt_text, allow_empty=False):
    cols = list(df.columns)
    print("\nColumns:")
    for i, c in enumerate(cols, 1):
        print(f"  {i}. {c}")
    while True:
        sel = input(f"{prompt_text} (name or number){' [empty allowed]' if allow_empty else ''}: ").strip()
        if allow_empty and sel == "":
            return None
        if sel.isdigit():
            idx = int(sel) - 1
            if 0 <= idx < len(cols):
                return cols[idx]
        elif sel in cols:
            return sel
        print("Invalid column. Try again.")


def parse_date_column(df, date_col):
    try:
        return pd.to_datetime(df[date_col], errors="coerce")
    except Exception:
        return pd.to_datetime(df[date_col].astype(str), errors="coerce")


def main():
    print("Excel Cost Counter — interactive CLI\n")
    while True:
        path = prompt_file()
        if path is None:
            print("Goodbye.")
            return

        try:
            xl = pd.ExcelFile(path, engine="openpyxl")
        except Exception as e:
            print("Failed to open Excel file:", e)
            continue

        sheet = choose_sheet(xl)
        try:
            df = xl.parse(sheet)
        except Exception as e:
            print("Failed to read sheet:", e)
            continue

        if df.empty:
            print("Selected sheet is empty.")
            continue

        print("\nSheet preview (first 8 rows):")
        print(df.head(8).to_string(index=False))

        amt_col = pick_column(df, "Select AMOUNT column")
        cat_col = pick_column(df, "Select CATEGORY column (or press Enter to treat all as one category)", allow_empty=True)
        date_col = pick_column(df, "Select DATE column for optional filtering (or press Enter to skip)", allow_empty=True)

        # Prepare amount
        df["_amount_raw"] = df[amt_col]
        df["_amount"] = pd.to_numeric(df["_amount_raw"], errors="coerce")
        non_numeric = df[["_amount_raw", "_amount"]].loc[df["_amount"].isna()]
        if not non_numeric.empty:
            print(f"\nWarning: {len(non_numeric)} rows have non-numeric amounts and will be ignored.")
        df = df.dropna(subset=["_amount"]).copy()

        # Optional date filter
        if date_col:
            dates = parse_date_column(df, date_col)
            if dates.isna().all():
                print("Warning: could not parse any dates from the selected date column; skipping date filter.")
            else:
                df["_date"] = dates
                print("\nEnter date range to filter (YYYY-MM-DD). Leave blank to skip.")
                start = input("  start date: ").strip()
                end = input("  end date: ").strip()
                try:
                    if start:
                        start_dt = datetime.fromisoformat(start)
                        df = df[df["_date"] >= start_dt]
                    if end:
                        end_dt = datetime.fromisoformat(end)
                        df = df[df["_date"] <= end_dt]
                except Exception:
                    print("Invalid date(s) entered; skipping date filter.")

        # Grouping and totals
        if cat_col:
            summary = df.groupby(df[cat_col].fillna("Unspecified"))["_amount"].sum().sort_values(ascending=False)
            print("\nTotals by category:")
            print(summary.to_string())
            grand_total = summary.sum()
        else:
            grand_total = df["_amount"].sum()
            print(f"\nGrand total: {grand_total:.2f}")

        print(f"\nGrand total: {grand_total:.2f}")

        # Export option
        export = input("Export summary? (csv/xlsx/none) [none]: ").strip().lower()
        if export in ("csv", "xlsx"):
            default_name = os.path.join(os.path.dirname(path) or ".", f"cost_summary.{export}")
            out = input(f"Output file path [{default_name}]: ").strip()
            out = out if out else default_name
            try:
                if export == "csv":
                    if cat_col:
                        summary.reset_index().rename(columns={cat_col: "category", "_amount": "amount"}).to_csv(out, index=False)
                    else:
                        pd.DataFrame({"total": [grand_total]}).to_csv(out, index=False)
                else:  # xlsx
                    if cat_col:
                        summary.reset_index().to_excel(out, index=False)
                    else:
                        pd.DataFrame({"total": [grand_total]}).to_excel(out, index=False)
                print("Exported to", out)
            except Exception as e:
                print("Failed to export:", e)

        again = input("\nProcess another file? (y/N): ").strip().lower()
        if again != "y":
            print("Done.")
            return


if __name__ == "__main__":
    main()
# This is a simple Python script that prints "Hello, world!" to the console.
# It defines a main function and calls it when the script is executed directly.
# The shebang line at the top allows the script to be run as an executable on Unix-like systems.
# The script follows best practices by using the __name__ == "__main__" construct.
# The script is compatible with Python 3 and does not require any external libraries.
# It serves as a basic template for creating Python scripts.
# The script is easy to read and understand, making it suitable for beginners learning Python.
# It can be expanded with additional functionality as needed.





# End of script# Additional comments explaining the code:
# - The main function is defined to encapsulate the primary logic of the script.
# - The print function is used to output text to the console.
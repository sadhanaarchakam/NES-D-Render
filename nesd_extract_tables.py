import pandas as pd

# experimental data tables used:
files = [
    "2017-nes-d-experimental-tables.xlsx",
    "2018-nes-d-experimental-tables.xlsx",
    "2019-nes-d-experimental-tables.xlsx"
]

# adding tables you want (table_5 + table_O1)
target_tables = ["table_5", "table_O1"]

# Loop through tables
for t in target_tables:
    all_years = []

    for f in files:
        year = f[:4]
        sheets = pd.read_excel(f, sheet_name=None)

        if t in sheets:  
            df = sheets[t].dropna(how="all")
            df = df[~df.apply(lambda row: row.astype(str).str.contains("Meaning|code", case=False).any(), axis=1)]
            df.insert(0, "YEAR", year)

            # create avg receipts per firm col:
            if "RCPNOPD" in df.columns and "FIRMNOPD" in df.columns:
                df["AVG_RECEIPTS_PER_FIRM"] = df["RECEIPTS"] / df["FIRMS"].replace(0, pd.NA)

            all_years.append(df)

    # combine years for selected tables
    if all_years:
        combined_df = pd.concat(all_years, ignore_index=True)
        # name as _new.xlsx
        out_file = f"{t}_new.xlsx"
        combined_df.to_excel(out_file, sheet_name=t, index=False)
        print(f"Saved {out_file}")
    else: # check
        print(f"Not found for {t}")
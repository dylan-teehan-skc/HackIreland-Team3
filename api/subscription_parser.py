import pandas as pd
from datetime import timedelta
import re

# Load the Excel file
file_path = "Spending_data.xlsx"
df = pd.read_excel(file_path, sheet_name="ViewTxns_XLS", skiprows=12)  # Skip rows to start data

# Manually set the correct column names
df.columns = ["Date", "Date 2", "Description", "Money In", "Money Out", "Money Out 2", "Balance"]

# Convert "Money Out" columns to numeric, forcing errors to NaN
df["Money Out"] = pd.to_numeric(df["Money Out"], errors='coerce')
df["Money Out 2"] = pd.to_numeric(df["Money Out 2"], errors='coerce')

# Combine the "Money Out" columns
df["Money Out"] = df["Money Out"].fillna(0) + df["Money Out 2"].fillna(0)

# Drop the extra "Money Out 2" column
df = df.drop(columns=["Money Out 2"])
df = df.drop(columns=["Date 2"])

# Remove trailing dates from the "Description" column
df["Description"] = df["Description"].apply(lambda x: re.sub(r'\s\d{2}/\d{2}.*$', '', str(x)))

# Print the entire DataFrame
print("Full DataFrame:")
print(df.to_string())

# Check if the "Money Out" column exists
if "Money Out" in df.columns:
    # Filter only "Money Out" transactions
    df = df[df["Money Out"] > 0]  # Ensure we only consider positive "Money Out" values
else:
    print("The 'Money Out' column is missing from the data.")
    df = pd.DataFrame()  # Create an empty DataFrame to avoid further errors

# Convert the "Date" column to datetime format
if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")

    # Group transactions by description and amount to identify recurring patterns
    subscriptions = []
    for (description, amount), group in df.groupby(["Description", "Money Out"]):
        group = group.sort_values(by="Date")  # Sort by date
        if len(group) > 1:  # Recurring transactions must occur more than once
            date_diffs = group["Date"].diff().dropna()  # Calculate time differences between transactions
            # Check if the time differences are approximately monthly (within a tolerance)
            is_monthly = all(
                timedelta(days=25) <= diff <= timedelta(days=35) for diff in date_diffs
            )
            if is_monthly:
                # Calculate the average time between transactions
                avg_time_between = date_diffs.mean()
                # Estimate the next transaction date
                last_date = group["Date"].iloc[-1]
                estimated_next_date = last_date + avg_time_between
                group["Estimated_Next"] = None
                group.loc[group.index[-1], "Estimated_Next"] = estimated_next_date
                group = group.assign(Time_Between=date_diffs)
                subscriptions.append(group)

    # Combine all subscription transactions into a single DataFrame
    if subscriptions:
        subscriptions_df = pd.concat(subscriptions)
        # Print the subscription details
        print("Subscriptions found:")
        print(subscriptions_df[["Date", "Description", "Money Out", "Time_Between", "Estimated_Next"]])
    else:
        print("No subscriptions found.")
else:
    print("No data to process.")
import pandas as pd
from datetime import timedelta
import re
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

def load_data(file_path):
    logger.info(f"Loading data from {file_path}")
    df = pd.read_excel(file_path, sheet_name="ViewTxns_XLS", skiprows=12)
    df.columns = ["Date","Description", "Money In", "Money Out", "Balance"]
    return df

def preprocess_data(df):
    logger.info("Preprocessing data")
    df["Money Out"] = pd.to_numeric(df["Money Out"], errors='coerce')
    df["Money Out"] = df["Money Out"].fillna(0) 
    df["Description"] = df["Description"].apply(lambda x: re.sub(r'\s\d{2}/\d{2}.*$', '', str(x)))
    df = df[df["Money Out"] > 0]
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
    return df

def find_subscriptions(df):
    logger.info("Finding subscriptions")
    subscriptions = []
    for (description, amount), group in df.groupby(["Description", "Money Out"]):
        group = group.sort_values(by="Date")
        if len(group) > 1:
            date_diffs = group["Date"].diff().dropna()
            is_monthly = all(timedelta(days=25) <= diff <= timedelta(days=35) for diff in date_diffs)
            if is_monthly:
                avg_time_between = date_diffs.mean()
                last_date = group["Date"].iloc[-1]
                estimated_next_date = (last_date + avg_time_between).date().isoformat()
                formatted_dates = [d.date().isoformat() for d in group["Date"]]
                subscriptions.append({
                    "Description": description,
                    "Amount": amount,
                    "Dates": formatted_dates,
                    "Estimated_Next": estimated_next_date
                })
    logger.info(f"Found {len(subscriptions)} subscriptions")
    return json.dumps(subscriptions, indent=4)

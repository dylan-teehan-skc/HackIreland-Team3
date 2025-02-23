import pandas as pd
from datetime import timedelta
import re
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def load_data(file_path):
    logger.info(f"Loading data from {file_path}")
    try:
        df = pd.read_excel(file_path, sheet_name="Sheet1")
        df.columns = ["Date", "Description", "Money In", "Money Out", "Balance"]
        logger.debug(f"Data loaded with shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

def preprocess_data(df):
    logger.info("Preprocessing data")
    try:
        df["Money Out"] = pd.to_numeric(df["Money Out"].str.replace('€', '').str.replace(',', ''), errors='coerce')
        df["Money Out"] = df["Money Out"].fillna(0)
        df["Description"] = df["Description"].apply(lambda x: re.sub(r'\s\d{2}/\d{2}.*$', '', str(x)))
        df = df[df["Money Out"] > 0]
        df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")
        logger.debug(f"Data preprocessed with {len(df)} records")
        return df
    except Exception as e:
        logger.error(f"Error preprocessing data: {str(e)}")
        raise

def find_subscriptions(df):
    logger.info("Finding subscriptions")
    subscriptions = []
    try:
        for (description, amount), group in df.groupby(["Description", "Money Out"]):
            group = group.sort_values(by="Date")
            if len(group) > 1:
                date_diffs = group["Date"].diff().dropna()
                is_monthly = all(timedelta(days=25) <= diff <= timedelta(days=35) for diff in date_diffs)
                if is_monthly:
                    last_date = group["Date"].iloc[-1]
                    # Calculate the estimated next date by adding one month
                    estimated_next_date = (last_date + pd.DateOffset(months=1)).strftime('%Y-%m-%d')
                    logger.debug(f"Last date: {last_date}, Estimated next date: {estimated_next_date}")
                    formatted_dates = [d.strftime('%Y-%m-%d') for d in group["Date"]]
                    subscriptions.append({
                        "Description": description,
                        "Amount": amount,
                        "Dates": formatted_dates,
                        "Estimated_Next": estimated_next_date
                    })
        logger.info(f"Found {len(subscriptions)} subscriptions")
        return subscriptions
    except Exception as e:
        logger.error(f"Error finding subscriptions: {str(e)}")
        raise

def process_subscriptions(file_path):
    """Process the subscriptions from the given file path."""
    df = load_data(file_path)
    df = preprocess_data(df)
    return find_subscriptions(df)

def get_subscriptions_sorted_by_date(file_path):
    """Get individual subscription transactions sorted by date."""
    subscriptions = process_subscriptions(file_path)
    individual_transactions = []

    for subscription in subscriptions:
        for date in subscription["Dates"]:
            individual_transactions.append({
                "Description": subscription["Description"],
                "Amount": subscription["Amount"],
                "Date": date,
                "Estimated_Next": subscription["Estimated_Next"]
            })

    # Sort individual transactions by date
    sorted_transactions = sorted(individual_transactions, key=lambda x: x["Date"])
    logger.debug(f"Sorted {len(sorted_transactions)} transactions by date")
    return sorted_transactions 
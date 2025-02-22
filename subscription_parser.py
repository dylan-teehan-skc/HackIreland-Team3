import csv
from collections import defaultdict
import re

def is_subscription(description):
    # Define a pattern to identify potential subscriptions
    subscription_keywords = ['monthly', 'subscription', 'fee', 'charge', 'recurring']
    return any(keyword in description.lower() for keyword in subscription_keywords)

def parse_spending_data(file_path):
    subscriptions = defaultdict(list)

    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, skipinitialspace=True)
        for row in reader:
            description = row['Description']
            money_out = row['Money Out (€)']
            date = row['Date']

            if money_out and is_subscription(description):
                # Clean the money out value
                money_out_value = float(re.sub(r'[^\d.]', '', money_out))
                subscriptions[description].append((date, money_out_value))

    return subscriptions

def main():
    file_path = 'api/spending_data.csv'
    subscriptions = parse_spending_data(file_path)

    print("Recurring Subscriptions:")
    for description, transactions in subscriptions.items():
        print(f"\nDescription: {description}")
        for date, cost in transactions:
            print(f"  Date: {date}, Cost: €{cost:.2f}")

if __name__ == "__main__":
    main() 
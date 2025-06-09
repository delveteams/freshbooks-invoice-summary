#!/usr/bin/env python3
"""
Process FreshBooks invoice details CSV files.
Sums line items by invoice and combines EUR and USD reports.
"""

import pandas as pd
import sys
from decimal import Decimal, ROUND_HALF_UP

def process_invoice_csv(file_path):
    """Process a single invoice details CSV file."""
    
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Convert Date Paid NaN to empty string for grouping consistency
    df['Date Paid'] = df['Date Paid'].fillna('')
    
    # Group by invoice and sum the line totals
    grouped = df.groupby([
        'Client Name', 
        'Invoice #', 
        'Date Issued', 
        'Invoice Status', 
        'Date Paid',
        'Currency'
    ]).agg({
        'Line Total': 'sum'
    }).reset_index()
    
    # Rename column for clarity
    grouped = grouped.rename(columns={'Line Total': 'Total Amount'})
    
    # Round amounts to 2 decimal places
    grouped['Total Amount'] = grouped['Total Amount'].round(2)
    
    # Set payment status based on whether Date Paid is filled
    # If Date Paid is empty, use the original Invoice Status
    # If Date Paid has a value, status should be 'paid'
    grouped['Payment Status'] = grouped.apply(lambda row: 
        'paid' if row['Date Paid'] != '' and str(row['Date Paid']).strip() != '' 
        else row['Invoice Status'], axis=1)
    
    # Convert empty Date Paid back to NaN for cleaner output
    grouped['Date Paid'] = grouped['Date Paid'].replace('', pd.NA)
    
    return grouped

def combine_reports(eur_file, usd_file, output_file):
    """Combine EUR and USD invoice reports into a single file."""
    
    print(f"Processing {eur_file}...")
    eur_invoices = process_invoice_csv(eur_file)
    print(f"Found {len(eur_invoices)} EUR invoices")
    
    print(f"Processing {usd_file}...")
    usd_invoices = process_invoice_csv(usd_file)
    print(f"Found {len(usd_invoices)} USD invoices")
    
    # Combine both datasets
    combined = pd.concat([eur_invoices, usd_invoices], ignore_index=True)
    
    # Sort by invoice number (descending)
    # Ensure Invoice # is string type first
    combined['Invoice #'] = combined['Invoice #'].astype(str)
    combined['Invoice Number'] = combined['Invoice #'].str.extract(r'(\d+)').astype(int)
    combined = combined.sort_values('Invoice Number', ascending=False)
    combined = combined.drop('Invoice Number', axis=1)
    
    # Reorder columns to match your requirements
    column_order = [
        'Client Name',
        'Invoice #', 
        'Date Issued',
        'Total Amount',
        'Currency',
        'Payment Status',
        'Date Paid'
    ]
    combined = combined[column_order]
    
    # Rename columns to match your preferred format
    combined = combined.rename(columns={
        'Client Name': 'client',
        'Invoice #': 'invoice_number',
        'Date Issued': 'issued_date',
        'Total Amount': 'amount',
        'Currency': 'currency',
        'Payment Status': 'payment_status',
        'Date Paid': 'date_paid'
    })
    
    # Save to CSV
    combined.to_csv(output_file, index=False)
    print(f"Combined {len(combined)} invoices saved to {output_file}")
    
    return combined

def print_summary(df):
    """Print a summary of the processed invoices."""
    
    print(f"\nSummary:")
    print(f"Total invoices: {len(df)}")
    
    # Group by currency
    currency_summary = df.groupby('currency').agg({
        'amount': ['count', 'sum']
    }).round(2)
    currency_summary.columns = ['Count', 'Total Amount']
    print(f"\nBy currency:")
    print(currency_summary)
    
    # Group by status
    status_summary = df.groupby('payment_status').size()
    print(f"\nBy status:")
    print(status_summary)
    
    print(f"\nFirst 5 invoices:")
    print(df.head()[['client', 'invoice_number', 'issued_date', 'amount', 'currency', 'payment_status']].to_string(index=False))

def main():
    """Main function."""
    
    eur_file = "invoice_details_EUR.csv"
    usd_file = "invoice_details_USD.csv" 
    output_file = "combined_invoices.csv"
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        eur_file = sys.argv[1]
    if len(sys.argv) > 2:
        usd_file = sys.argv[2]
    if len(sys.argv) > 3:
        output_file = sys.argv[3]
    
    try:
        combined_df = combine_reports(eur_file, usd_file, output_file)
        print_summary(combined_df)
        
    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
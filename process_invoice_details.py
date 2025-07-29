#!/usr/bin/env python3
"""
Process FreshBooks invoice details CSV files.
Sums line items by invoice and combines EUR and USD reports.
"""

import pandas as pd
import sys
import argparse

def process_invoice_csv(file_path):
    """Process a single invoice details CSV file."""
    
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Convert Date Paid NaN to empty string for grouping consistency
    df['Date Paid'] = df['Date Paid'].fillna('')
    
    # Calculate total tax amount per line
    df['Total Tax'] = df['Tax 1 Amount'].fillna(0) + df['Tax 2 Amount'].fillna(0)
    
    # Group by invoice and sum the amounts
    grouped = df.groupby([
        'Client Name', 
        'Invoice #', 
        'Date Issued', 
        'Invoice Status', 
        'Date Paid',
        'Currency'
    ]).agg({
        'Line Subtotal': 'sum',
        'Total Tax': 'sum',
        'Line Total': 'sum'
    }).reset_index()
    
    # Rename columns for clarity
    grouped = grouped.rename(columns={
        'Line Subtotal': 'Amount Pre-Tax',
        'Total Tax': 'Tax Amount',
        'Line Total': 'Total Amount'
    })
    
    # Round amounts to 2 decimal places
    grouped['Amount Pre-Tax'] = grouped['Amount Pre-Tax'].round(2)
    grouped['Tax Amount'] = grouped['Tax Amount'].round(2)
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

def combine_reports(input_files, output_file):
    """Combine invoice reports from multiple files into a single file."""
    
    all_invoices = []
    
    for file_path in input_files:
        print(f"Processing {file_path}...")
        invoices = process_invoice_csv(file_path)
        print(f"Found {len(invoices)} invoices")
        all_invoices.append(invoices)
    
    # Combine all datasets
    combined = pd.concat(all_invoices, ignore_index=True) if all_invoices else pd.DataFrame()
    
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
        'Amount Pre-Tax',
        'Tax Amount',
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
        'Amount Pre-Tax': 'amount_pre_tax',
        'Tax Amount': 'tax',
        'Total Amount': 'total_amount',
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
        'amount_pre_tax': ['count', 'sum'],
        'tax': 'sum',
        'total_amount': 'sum'
    }).round(2)
    currency_summary.columns = ['Count', 'Pre-Tax Total', 'Tax Total', 'Grand Total']
    print(f"\nBy currency:")
    print(currency_summary)
    
    # Group by status
    status_summary = df.groupby('payment_status').size()
    print(f"\nBy status:")
    print(status_summary)
    
    print(f"\nFirst 5 invoices:")
    print(df.head()[['client', 'invoice_number', 'issued_date', 'amount_pre_tax', 'tax', 'total_amount', 'currency', 'payment_status']].to_string(index=False))

def main():
    """Main function."""
    
    parser = argparse.ArgumentParser(
        description='Process FreshBooks invoice details CSV files and combine reports.'
    )
    
    parser.add_argument(
        'input_files',
        nargs='+',
        help='Input CSV files to process'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='combined_invoices.csv',
        help='Output CSV file (default: combined_invoices.csv)'
    )
    
    args = parser.parse_args()
    
    try:
        combined_df = combine_reports(args.input_files, args.output)
        print_summary(combined_df)
        
    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

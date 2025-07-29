# FreshBooks Invoice Details Processor

Process FreshBooks "Invoice Details" reports - sums line items by invoice and combines multiple currency reports.

## Source Data

Generate "Invoice Details" reports from FreshBooks:
1. Go to Reports → Invoice Details 
2. Filter by currency (EUR/USD) and export each as CSV - More Actions → Export for Excel
3. Save as `invoice_details_EUR.csv` and `invoice_details_USD.csv`

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Process one or more CSV files
python process_invoice_details.py invoice_details_EUR.csv invoice_details_USD.csv

# Specify custom output file
python process_invoice_details.py -o custom_output.csv invoice_details_EUR.csv invoice_details_USD.csv

# Process single file
python process_invoice_details.py invoice_details_EUR.csv
```

## Output

Generates a CSV with: client, invoice_number, issued_date, amount_pre_tax, tax, total_amount, currency, payment_status, date_paid

- Payment status is determined by whether "Date Paid" field is filled
- Invoices are sorted by invoice number (descending)
- Line items are summed by invoice
- Tax amounts are calculated from Tax 1 and Tax 2 fields
- Includes summary statistics by currency and payment status
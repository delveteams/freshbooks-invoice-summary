# FreshBooks Invoice Details Processor

Process FreshBooks "Invoice Details" reports - sums line items by invoice and combines EUR/USD reports.

## Source Data

Generate "Invoice Details" reports from FreshBooks:
1. Go to Reports → Invoice Details 
2. Filter by currency (EUR/USD) and export each as CSV
3. Save as `invoice_details_EUR.csv` and `invoice_details_USD.csv`

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default files (invoice_details_EUR.csv, invoice_details_USD.csv)
python process_invoice_details.py

# Or specify custom files
python process_invoice_details.py eur_file.csv usd_file.csv output.csv
```

## Output

Generates a CSV with: client, invoice_number, issued_date, amount, currency, payment_status, date_paid

Payment status is determined by whether "Date Paid" field is filled.
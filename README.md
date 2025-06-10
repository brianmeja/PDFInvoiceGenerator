# PDF Invoice Generator

Generate custom PDF invoices with a logo, table, and QR code using Python.

## Features
- Add your own logo (or use a placeholder)
- Customizable invoice table
- QR code for payment (any string or link)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the example:
   ```bash
   python pdf_invoice_generator.py
   ```
   This will generate `invoice_example.pdf` in the current directory.

## Custom Usage

You can import and use `generate_invoice` in your own scripts, or modify the example at the bottom of `pdf_invoice_generator.py`:

```python
from pdf_invoice_generator import generate_invoice

generate_invoice(
    output_path="my_invoice.pdf",
    logo_path="path/to/logo.png",  # Set to None for placeholder
    qr_data="https://your-payment-link.com",
    invoice_items=[
        ["Item", "Description", "Quantity", "Unit Price", "Total"],
        ["001", "Service X", "3", "$50.00", "$150.00"],
        ["", "", "", "Total", "$150.00"]
    ],
    company_name="My Company",
    customer_name="Client Name",
    customer_address="123 Main St, City, Country"
)
```

## Notes
- The QR code can encode any string (e.g., payment link, bank details, etc.).
- The logo should be a PNG or JPG file. If not provided, a placeholder is used. 
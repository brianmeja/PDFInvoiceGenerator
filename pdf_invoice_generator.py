import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Image
from reportlab.lib.units import mm
from PIL import Image as PILImage
import qrcode


def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    return filename


def generate_invoice(
    output_path,
    logo_path=None,
    qr_data="https://example.com/pay",
    invoice_items=None,
    invoice_title="INVOICE",
    company_name="Your Company Name",
    invoice_number="0001",
    invoice_date="2024-01-01",
    due_date="2024-01-15",
    customer_name="Customer Name",
    customer_address="123 Customer St, City, Country",
    custom_fields=None,
    theme_color="#4F8EF7",
    font_size=10,
    currency="$",
    vat_percentage=0.0,
    subtotal=0.0,
    vat_total=0.0,
    grand_total=0.0
):
    if invoice_items is None:
        invoice_items = [
            ["Item", "Description", "Quantity", "Unit Price", "Total (excl. VAT)", "VAT", "Total (incl. VAT)"],
            ["001", "Product A", "2", "$10.00", "$20.00", "$3.20", "$23.20"],
            ["002", "Product B", "1", "$15.00", "$15.00", "$2.40", "$17.40"],
            ["", "", "", "Subtotal", "$35.00", "", ""],
            ["", "", "", "VAT (16.0%)", "$5.60", "", ""],
            ["", "", "", "Grand Total", "$40.60", "", ""]
        ]
    if custom_fields is None:
        custom_fields = []

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Company name header (centered, bold, top)
    c.setFont("Helvetica-Bold", int(font_size * 2.2))
    c.setFillColor(theme_color)
    c.drawCentredString(width / 2, height - 40, company_name)
    c.setFillColor(colors.black)

    # Invoice title (centered, bold, below company name)
    c.setFont("Helvetica-Bold", int(font_size * 1.8))
    c.drawCentredString(width / 2, height - 70, invoice_title)

    y = height - 100

    # Add logo (left, below header)
    if logo_path and os.path.exists(logo_path):
        c.drawImage(logo_path, 40, y - 10, width=100, height=50, preserveAspectRatio=True)
    else:
        c.setFont("Helvetica-Bold", font_size)
        c.drawString(40, y + 20, "[LOGO PLACEHOLDER]")

    # Company and invoice details
    c.setFont("Helvetica", font_size)
    c.drawString(40, y - 30, f"From: {company_name}")
    c.drawString(40, y - 45, f"Invoice #: {invoice_number}")
    c.drawString(40, y - 60, f"Date: {invoice_date}")
    c.drawString(40, y - 75, f"Due Date: {due_date}")

    c.drawString(350, y - 30, f"Bill To: {customer_name}")
    c.drawString(350, y - 45, customer_address)

    # Custom fields
    y_custom = y - 95
    for field in custom_fields:
        if field.get("label"):
            c.drawString(40, y_custom, f"{field['label']}: {field.get('value', '')}")
            y_custom -= (font_size + 5)

    # Table
    table = Table(invoice_items, colWidths=[50, 120, 50, 70, 70, 70, 80])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), theme_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), font_size),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, theme_color),
    ])
    table.setStyle(style)
    table.wrapOn(c, width, height)
    table.drawOn(c, 40, y - 220)

    # Totals (bottom right)
    c.setFont("Helvetica-Bold", font_size)
    c.drawString(width - 220, 120, f"Subtotal: {currency}{subtotal:.2f}")
    c.drawString(width - 220, 100, f"VAT ({vat_percentage:.1f}%): {currency}{vat_total:.2f}")
    c.drawString(width - 220, 80, f"Grand Total: {currency}{grand_total:.2f}")

    # QR code (bottom left)
    qr_filename = "temp_qr.png"
    generate_qr_code(qr_data, qr_filename)
    c.drawImage(qr_filename, 40, 60, width=100, height=100)
    c.setFont("Helvetica", int(font_size * 0.8))
    c.drawString(40, 55, "Scan to pay")
    os.remove(qr_filename)

    c.save()

    # Add company emblem at the bottom center
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2, 30, "©2025 MEJA TECH SOLUTIONS")
    c.setFillColor(colors.black)
    c.save()
    print(f"Invoice saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    generate_invoice(
        output_path="invoice_example.pdf",
        logo_path=None,  # Replace with path to your logo file
        qr_data="Pay to: 1234567890",  # This can be any string or payment link
    ) 
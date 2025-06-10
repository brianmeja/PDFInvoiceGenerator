import streamlit as st
import tempfile
import os
from pdf_invoice_generator import generate_invoice, generate_qr_code
from PIL import Image

st.set_page_config(page_title="PDF Invoice Generator", layout="centered")
st.title("PDF Invoice Generator")

# --- Sidebar for Styling and Currency ---
st.sidebar.header("Invoice Style & Settings")
world_currencies = [
    ("USD", "$"), ("EUR", "€"), ("GBP", "£"), ("KES", "Ksh"), ("INR", "₹"), ("JPY", "¥"), ("CNY", "¥"), ("NGN", "₦"), ("RUB", "₽"), ("KRW", "₩"), ("TRY", "₺"), ("UAH", "₴"), ("VND", "₫"), ("PYG", "₲"), ("ILS", "₪"), ("PHP", "₱"), ("THB", "฿"), ("CRC", "₡"), ("GHS", "₵"), ("KZT", "₸"), ("LAK", "₭"), ("MNT", "₮"), ("PKR", "₨"), ("AZN", "₼"), ("GEL", "₾"), ("BTC", "₿"), ("ZAR", "R"), ("AUD", "$"), ("CAD", "$"), ("SGD", "$"), ("CHF", "Fr"), ("SEK", "kr"), ("NOK", "kr"), ("DKK", "kr"), ("PLN", "zł"), ("CZK", "Kč"), ("HUF", "Ft"), ("BRL", "R$"), ("MXN", "$"), ("CLP", "$"), ("COP", "$"), ("ARS", "$"), ("EGP", "E£"), ("SAR", "ر.س"), ("AED", "د.إ"), ("QAR", "ر.ق"), ("BHD", ".د.ب"), ("OMR", "ر.ع."), ("KWD", "د.ك"), ("JOD", "د.ا"), ("LBP", "ل.ل"), ("TND", "د.ت"), ("MAD", "د.م."), ("DZD", "دج"), ("TWD", "NT$"), ("HKD", "HK$"), ("MYR", "RM"), ("IDR", "Rp"), ("BDT", "৳"), ("LKR", "₨"), ("NPR", "₨"), ("MMK", "K"), ("THB", "฿"), ("SGD", "$"), ("NZD", "$"), ("FJD", "$"), ("PGK", "K"), ("SBD", "$"), ("VUV", "Vt"), ("WST", "WS$"), ("TOP", "T$"), ("TMT", "m"), ("UZS", "so'm"), ("KGS", "лв"), ("AFN", "؋"), ("IRR", "﷼"), ("IQD", "ع.د"), ("SYP", "£S"), ("YER", "﷼"), ("SDG", "ج.س."), ("SOS", "S"), ("TZS", "TSh"), ("UGX", "USh"), ("RWF", "FRw"), ("BIF", "FBu"), ("MWK", "MK"), ("ZMW", "ZK"), ("MZN", "MT"), ("AOA", "Kz"), ("XOF", "CFA"), ("XAF", "FCFA"), ("XPF", "₣"), ("Custom", "Custom")
]
currency_options = [f"{code} ({symbol})" for code, symbol in world_currencies]
currency_selection = st.sidebar.selectbox("Currency", currency_options)
if currency_selection == "Custom (Custom)":
    currency = st.sidebar.text_input("Enter custom currency code or symbol", "¤")
else:
    idx = currency_options.index(currency_selection)
    currency = world_currencies[idx][1]

theme_color = st.sidebar.color_picker("Theme Color", "#4F8EF7")
font_size = st.sidebar.slider("Font Size (pt)", 8, 20, 10)

# --- Logo Upload ---
logo_file = st.file_uploader("Upload your logo (PNG/JPG)", type=["png", "jpg", "jpeg"])

# --- Invoice Details ---
st.header("Invoice Details")
company_name = st.text_input("Company Name", "Your Company Name")
customer_name = st.text_input("Customer Name", "Customer Name")
customer_address = st.text_area("Customer Address", "123 Customer St, City, Country")
invoice_number = st.text_input("Invoice Number", "0001")
invoice_date = st.date_input("Invoice Date")
due_date = st.date_input("Due Date")

# --- Custom Invoice Fields ---
st.subheader("Custom Invoice Fields")
if "custom_fields" not in st.session_state:
    st.session_state.custom_fields = [{"label": "PO Number", "value": ""}]

custom_fields = st.session_state.custom_fields
for i, field in enumerate(custom_fields):
    cols = st.columns([3, 4, 1])
    field["label"] = cols[0].text_input(f"Field Label {i+1}", value=field["label"], key=f"label_{i}")
    field["value"] = cols[1].text_input(f"Field Value {i+1}", value=field["value"], key=f"value_{i}")
    if cols[2].button("Remove", key=f"remove_{i}"):
        custom_fields.pop(i)
        st.experimental_rerun()
if st.button("Add Custom Field"):
    custom_fields.append({"label": "", "value": ""})
    st.experimental_rerun()

# --- Product Table ---
st.header("Products/Services")
def_currency = currency if currency else "$"
products = st.data_editor([
    {"Item": "001", "Description": "Product A", "Quantity": 2, "Unit Price": 10.0},
    {"Item": "002", "Description": "Product B", "Quantity": 1, "Unit Price": 15.0},
], num_rows="dynamic", use_container_width=True, key="products")

# --- VAT Section ---
st.header("VAT Settings")
vat_percentage = st.number_input("VAT Percentage (%)", min_value=0.0, max_value=100.0, value=16.0, step=0.1)

# --- QR Code Data ---
st.header("QR Code for Payment")
qr_data = st.text_input("Enter payment link or details", "Pay to: 1234567890")

# --- Export Directory and Filename ---
st.header("Export Options")
save_dir = st.text_input("Optional: Enter directory path to save PDF invoice (leave blank to skip)")
custom_filename = st.text_input("Enter PDF filename (default: invoice.pdf)", value="invoice.pdf")

# --- Calculate Totals ---
subtotal = 0.0
vat_total = 0.0
invoice_items = [["Item", "Description", "Quantity", "Unit Price", "Total (excl. VAT)", f"VAT ({vat_percentage:.1f}%)", "Total (incl. VAT)"]]
for row in products:
    qty = float(row["Quantity"])
    price = float(row["Unit Price"])
    line_total = qty * price
    line_vat = line_total * (vat_percentage / 100)
    line_total_incl_vat = line_total + line_vat
    subtotal += line_total
    vat_total += line_vat
    invoice_items.append([
        row["Item"],
        row["Description"],
        str(qty),
        f"{currency}{price:.2f}",
        f"{currency}{line_total:.2f}",
        f"{currency}{line_vat:.2f}",
        f"{currency}{line_total_incl_vat:.2f}"
    ])
grand_total = subtotal + vat_total
invoice_items.append(["", "", "", "Subtotal", f"{currency}{subtotal:.2f}", "", ""])
invoice_items.append(["", "", "", f"VAT ({vat_percentage:.1f}%)", f"{currency}{vat_total:.2f}", "", ""])
invoice_items.append(["", "", "", "Grand Total", f"{currency}{grand_total:.2f}", "", ""])

# --- Show Totals ---
st.markdown(f"**Subtotal:** {currency}{subtotal:.2f}")
st.markdown(f"**Total VAT ({vat_percentage:.1f}%):** {currency}{vat_total:.2f}")
st.markdown(f"**Grand Total:** {currency}{grand_total:.2f}")

# --- Export Button ---
if st.button("Export Invoice PDF and QR Code"):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save logo if uploaded
        logo_path = None
        if logo_file is not None:
            logo_path = os.path.join(tmpdir, logo_file.name)
            with open(logo_path, "wb") as f:
                f.write(logo_file.read())
        # Ensure filename ends with .pdf
        filename = custom_filename.strip()
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"
        # Output paths
        pdf_path = os.path.join(tmpdir, filename)
        qr_path = os.path.join(tmpdir, "qr.png")
        # Generate files
        generate_invoice(
            output_path=pdf_path,
            logo_path=logo_path,
            qr_data=qr_data,
            invoice_items=invoice_items,
            company_name=company_name,
            invoice_number=invoice_number,
            invoice_date=str(invoice_date),
            due_date=str(due_date),
            customer_name=customer_name,
            customer_address=customer_address,
            custom_fields=custom_fields,
            theme_color=theme_color,
            font_size=font_size,
            currency=currency,
            vat_percentage=vat_percentage,
            subtotal=subtotal,
            vat_total=vat_total,
            grand_total=grand_total
        )
        generate_qr_code(qr_data, qr_path)
        # Download buttons
        with open(pdf_path, "rb") as f:
            st.download_button("Download Invoice PDF", f, file_name=filename, mime="application/pdf")
        with open(qr_path, "rb") as f:
            st.download_button("Download QR Code Image", f, file_name="qr.png", mime="image/png")
        # Save to user directory if provided
        if save_dir:
            try:
                user_pdf_path = os.path.join(save_dir, filename)
                with open(pdf_path, "rb") as src, open(user_pdf_path, "wb") as dst:
                    dst.write(src.read())
                st.success(f"Invoice PDF also saved to: {user_pdf_path}")
            except Exception as e:
                st.error(f"Failed to save PDF to directory: {e}") 
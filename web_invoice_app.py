import streamlit as st
import tempfile
import os
from pdf_invoice_generator import generate_invoice, generate_qr_code
from PIL import Image

st.set_page_config(page_title="PDF Invoice Generator", layout="centered")
st.title("PDF Invoice Generator")

# --- Sidebar for Styling and Currency ---
st.sidebar.header("Invoice Style & Settings")
currency = st.sidebar.selectbox("Currency Symbol", ["$", "€", "£", "₹", "¥", "₦", "₽", "₩", "₺", "₴", "₫", "₲", "₪", "₱", "฿", "₡", "₵", "₸", "₭", "₮", "₦", "₨", "₩", "₸", "₺", "₼", "₾", "₿"])
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
products = st.experimental_data_editor([
    {"Item": "001", "Description": "Product A", "Quantity": 2, "Unit Price": 10.0},
    {"Item": "002", "Description": "Product B", "Quantity": 1, "Unit Price": 15.0},
], num_rows="dynamic", use_container_width=True, key="products")

# --- QR Code Data ---
st.header("QR Code for Payment")
qr_data = st.text_input("Enter payment link or details", "Pay to: 1234567890")

# --- Export Button ---
if st.button("Export Invoice PDF and QR Code"):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save logo if uploaded
        logo_path = None
        if logo_file is not None:
            logo_path = os.path.join(tmpdir, logo_file.name)
            with open(logo_path, "wb") as f:
                f.write(logo_file.read())
        # Prepare invoice items
        invoice_items = [["Item", "Description", "Quantity", "Unit Price", "Total"]]
        total = 0.0
        for row in products:
            qty = float(row["Quantity"])
            price = float(row["Unit Price"])
            line_total = qty * price
            total += line_total
            invoice_items.append([
                row["Item"],
                row["Description"],
                str(qty),
                f"{currency}{price:.2f}",
                f"{currency}{line_total:.2f}"
            ])
        invoice_items.append(["", "", "", "Total", f"{currency}{total:.2f}"])
        # Output paths
        pdf_path = os.path.join(tmpdir, "invoice.pdf")
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
            currency=currency
        )
        generate_qr_code(qr_data, qr_path)
        # Download buttons
        with open(pdf_path, "rb") as f:
            st.download_button("Download Invoice PDF", f, file_name="invoice.pdf", mime="application/pdf")
        with open(qr_path, "rb") as f:
            st.download_button("Download QR Code Image", f, file_name="qr.png", mime="image/png") 
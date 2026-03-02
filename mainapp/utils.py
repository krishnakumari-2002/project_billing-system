from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_bill_pdf(purchase, file_path):
    """
    Create a PDF bill for a given purchase and save to file_path
    """
    c = canvas.Canvas(file_path, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, f"Bill ID: {purchase.id}")
    c.drawString(50, 730, f"Customer Email: {purchase.customer_email}")
    c.drawString(50, 710, f"Net Total: {purchase.rounded_total}")

    y = 690
    for item in purchase.items.all():
        c.drawString(50, y, f"{item.product.name} - Qty: {item.quantity} - Total: {item.total_price}")
        y -= 20

    c.drawString(50, y-20, f"Thank you for shopping!")
    c.save()
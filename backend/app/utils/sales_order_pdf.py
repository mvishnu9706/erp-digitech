from io import BytesIO
from decimal import Decimal
from datetime import timedelta
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class SalesOrderPDFGenerator:
    """
    Invoice PDF generator.

    The layout is designed to match the supplied reference:
    - Tax Invoice + Original for Recipient header
    - Company logo/details
    - Bill To / Ship To / Invoice Details
    - Large product area
    - Tax + Amounts
    - Invoice Amount In Words + Payment Mode
    - Bank Details + QR
    - Terms and Conditions
    - Authorized Signatory
    - Footer
    """

    # =====================================================
    # COMPANY DETAILS
    # =====================================================

    COMPANY_NAME = "DIGITECH IMAGING SOLUTIONS"

    COMPANY_ADDRESS = (
        "No.1676, 2nd cross, 14th main, Prakash Nagar, "
        "Bangalore, Karnataka - 560 021"
    )

    COMPANY_PHONE = "080-41440252"
    COMPANY_EMAIL = "info@digitechimaging.com"
    COMPANY_GSTIN = "29BLPS29761R1ZG"
    COMPANY_STATE = "29-Karnataka"

    # =====================================================
    # BANK DETAILS
    # =====================================================

    BANK_NAME = "AXIS BANK, RAJAJINAGAR"
    ACCOUNT_NUMBER = "916020034360576"
    IFSC_CODE = "UTIB0000559"
    ACCOUNT_HOLDER = "DIGITECH IMAGING SOLUTIONS"

    # =====================================================
    # TERMS
    # =====================================================

    TERMS = [
        "1. Goods once sold cannot be taken back.",
        "2. Our responsibility ceases as goods leave our premises.",
        "3. Interest @24% will be charged on all overdue bills.",
        "4. We reserve the right to demand payment of the bill at any time.",
        "5. Delivery charges - Extra as applicable.",
    ]

    # =====================================================
    # PROJECT / ASSET PATHS
    # =====================================================

    # Current file:
    # backend/app/utils/sales_order_pdf.py
    APP_DIR = Path(__file__).resolve().parent.parent
    BACKEND_DIR = APP_DIR.parent
    PROJECT_ROOT = BACKEND_DIR.parent

    # Your logo is in:
    # digitech-erp-frontend/public/digitechlogo.png
    FRONTEND_PUBLIC_DIR = PROJECT_ROOT / "digitech-erp-frontend" / "public"

    LOGO_PATH = FRONTEND_PUBLIC_DIR / "digitechlogo.png"

    # PDF assets
    ASSETS_DIR = APP_DIR / "assets"
    QR_PATH = ASSETS_DIR / "digitech_qr.png"
    SIGNATURE_PATH = ASSETS_DIR / "authorized_signature.png"

    # =====================================================
    # FONT SETUP
    # =====================================================

    FONT_REGULAR = "Arial"
    FONT_BOLD = "Arial-Bold"

    @classmethod
    def register_fonts(cls):
        """Register Windows Arial font so ₹ renders correctly."""
        if cls.FONT_REGULAR in pdfmetrics.getRegisteredFontNames():
            return
            
        try:
            # Point directly to the standard Windows font directory
            pdfmetrics.registerFont(TTFont(cls.FONT_REGULAR, "C:/Windows/Fonts/arial.ttf"))
            pdfmetrics.registerFont(TTFont(cls.FONT_BOLD, "C:/Windows/Fonts/arialbd.ttf"))
        except Exception as e:
            raise RuntimeError(
                f"Could not load Windows Arial font. Make sure you are on a Windows machine. Error: {str(e)}"
            )

    # =====================================================
    # BASIC HELPERS
    # =====================================================

    @staticmethod
    def safe(value, default="-"):
        if value is None:
            return default

        value = str(value).strip()

        if not value:
            return default

        return value

    @staticmethod
    def money(value):
        value = Decimal(value or 0)
        return f"₹ {value:,.2f}"

    @staticmethod
    def html(value):
        return escape(SalesOrderPDFGenerator.safe(value))

    @staticmethod
    def paragraph(value, style):
        value = SalesOrderPDFGenerator.safe(value)
        value = escape(value).replace("\n", "<br/>")
        return Paragraph(value, style)

    # =====================================================
    # RELATIONSHIP SAFE VALUE
    # =====================================================

    @staticmethod
    def relation_value(value, attributes):
        if value is None:
            return "-"

        if not isinstance(value, str):
            for attribute in attributes:
                result = getattr(value, attribute, None)
                if result is not None and str(result).strip():
                    return str(result).strip()

        return str(value).strip() or "-"

    # =====================================================
    # NUMBER TO WORDS
    # =====================================================

    @staticmethod
    def number_to_words(number):
        number = int(Decimal(number or 0))

        if number == 0:
            return "Zero"

        ones = [
            "",
            "One",
            "Two",
            "Three",
            "Four",
            "Five",
            "Six",
            "Seven",
            "Eight",
            "Nine",
        ]

        teens = [
            "Ten",
            "Eleven",
            "Twelve",
            "Thirteen",
            "Fourteen",
            "Fifteen",
            "Sixteen",
            "Seventeen",
            "Eighteen",
            "Nineteen",
        ]

        tens = [
            "",
            "",
            "Twenty",
            "Thirty",
            "Forty",
            "Fifty",
            "Sixty",
            "Seventy",
            "Eighty",
            "Ninety",
        ]

        def two_digit(n):
            if n < 10:
                return ones[n]

            if n < 20:
                return teens[n - 10]

            result = tens[n // 10]

            if n % 10:
                result += " " + ones[n % 10]

            return result

        def three_digit(n):
            result = ""

            if n >= 100:
                result += ones[n // 100] + " Hundred"
                n %= 100

            if n:
                if result:
                    result += " "
                result += two_digit(n)

            return result

        crore = number // 10000000
        number %= 10000000

        lakh = number // 100000
        number %= 100000

        thousand = number // 1000
        number %= 1000

        parts = []

        if crore:
            parts.append(f"{three_digit(crore)} Crore")

        if lakh:
            parts.append(f"{three_digit(lakh)} Lakh")

        if thousand:
            parts.append(f"{three_digit(thousand)} Thousand")

        if number:
            parts.append(three_digit(number))

        return " ".join(parts)

    @staticmethod
    def amount_in_words(amount):
        amount = Decimal(amount or 0)

        rupees = int(amount)
        paise = int(round((amount - rupees) * 100))

        result = (
            SalesOrderPDFGenerator.number_to_words(rupees)
            + " Rupees"
        )

        if paise:
            result += (
                " and "
                + SalesOrderPDFGenerator.number_to_words(paise)
                + " Paise"
            )

        return result + " only"

    # =====================================================
    # ADDRESS
    # =====================================================

    @staticmethod
    def build_address(customer, address):
        parts = []

        if address:
            parts.append(str(address).strip())

        for field in ("city", "state", "pincode", "country"):
            value = getattr(customer, field, None)

            if value:
                parts.append(str(value).strip())

        return "<br/>".join(parts) if parts else "-"

    # =====================================================
    # GENERATE PDF
    # =====================================================

    @classmethod
    def generate(cls, sales_order):
        cls.register_fonts()

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=10 * mm,
            leftMargin=10 * mm,
            topMargin=6 * mm,
            bottomMargin=6 * mm,
            title=f"Tax Invoice - {sales_order.so_number}",
            author=cls.COMPANY_NAME,
        )

        styles = getSampleStyleSheet()

        # =================================================
        # COLORS
        # =================================================

        GREY = colors.HexColor("#A6A6A6")
        BORDER = colors.HexColor("#666666")
        TEXT = colors.HexColor("#202020")
        WHITE = colors.white

        # =================================================
        # STYLES
        # =================================================

        base = ParagraphStyle(
            "Base",
            parent=styles["Normal"],
            fontName=cls.FONT_REGULAR,
            fontSize=6.6,
            leading=8.0,
            textColor=TEXT,
            spaceAfter=0,
            spaceBefore=0,
        )

        small = ParagraphStyle(
            "Small",
            parent=base,
            fontSize=6.2,
            leading=7.6,
        )

        tiny = ParagraphStyle(
            "Tiny",
            parent=base,
            fontSize=5.5,
            leading=6.6,
        )

        bold = ParagraphStyle(
            "Bold",
            parent=base,
            fontName=cls.FONT_BOLD,
        )

        white_bold = ParagraphStyle(
            "WhiteBold",
            parent=bold,
            textColor=WHITE,
        )

        center = ParagraphStyle(
            "Center",
            parent=base,
            alignment=TA_CENTER,
        )

        center_bold = ParagraphStyle(
            "CenterBold",
            parent=center,
            fontName=cls.FONT_BOLD,
        )

        right = ParagraphStyle(
            "Right",
            parent=base,
            alignment=TA_RIGHT,
        )

        right_bold = ParagraphStyle(
            "RightBold",
            parent=right,
            fontName=cls.FONT_BOLD,
        )

        company = ParagraphStyle(
            "Company",
            parent=base,
            fontName=cls.FONT_BOLD,
            fontSize=11.8,
            leading=13.2,
            alignment=TA_RIGHT,
        )

        company_small = ParagraphStyle(
            "CompanySmall",
            parent=base,
            fontSize=5.7,
            leading=6.7,
            alignment=TA_RIGHT,
        )

        section = ParagraphStyle(
            "Section",
            parent=base,
            fontName=cls.FONT_BOLD,
            fontSize=6.6,
            leading=7.8,
        )

        amount_words = ParagraphStyle(
            "AmountWords",
            parent=base,
            alignment=TA_CENTER,
            fontSize=6.2,
            leading=7.5,
        )

        title_style = ParagraphStyle(
            "InvoiceTitle",
            parent=base,
            fontName=cls.FONT_BOLD,
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
        )

        original_style = ParagraphStyle(
            "Original",
            parent=base,
            fontSize=6.4,
            leading=8,
            alignment=TA_RIGHT,
        )

        # =================================================
        # STORY
        # =================================================

        story = []

        customer = getattr(sales_order, "customer", None)

        customer_name = (
            getattr(customer, "customer_name", None)
            if customer
            else None
        )

        customer_phone = (
            getattr(customer, "phone", None)
            if customer
            else None
        )

        billing_address = (
            getattr(customer, "billing_address", None)
            if customer
            else None
        )

        shipping_address = (
            getattr(customer, "shipping_address", None)
            if customer
            else None
        )

        customer_state = (
            getattr(customer, "state", None)
            if customer
            else None
        )

        customer_gstin = (
            getattr(customer, "gstin", None)
            if customer
            else None
        )

        # =================================================
        # TOP TITLE
        # =================================================

        top_title = Table(
            [[
                Paragraph("Tax Invoice", title_style),
                Paragraph("ORIGINAL FOR RECIPIENT", original_style),
            ]],
            colWidths=[95 * mm, 95 * mm],
        )

        top_title.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ]
            )
        )

        story.append(top_title)
        story.append(Spacer(1, 2.5 * mm))

        # =================================================
        # COMPANY HEADER
        # =================================================

        logo = None

        if cls.LOGO_PATH.exists():
            logo = Image(
                str(cls.LOGO_PATH),
                width=27 * mm,
                height=17 * mm,
                kind="proportional",
            )
        else:
            # Fallback if frontend public logo is not found.
            logo = Paragraph("<b>DIGITECH</b>", bold)

        company_block = [
            Paragraph(cls.COMPANY_NAME, company),
            Paragraph(cls.COMPANY_ADDRESS, company_small),
            Paragraph(
                f"Phone no.: {cls.COMPANY_PHONE} "
                f"Email: {cls.COMPANY_EMAIL}",
                company_small,
            ),
            Paragraph(
                f"GSTIN: {cls.COMPANY_GSTIN}, "
                f"State: {cls.COMPANY_STATE}",
                company_small,
            ),
        ]

        header = Table(
            [[logo, company_block]],
            colWidths=[55 * mm, 135 * mm],
        )

        header.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 1),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 1),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ]
            )
        )

        # =================================================
        # BILL / SHIP / INVOICE DETAILS
        # =================================================

        order_date = getattr(sales_order, "order_date", None)

        date_text = (
            order_date.strftime("%d-%m-%Y")
            if order_date
            else "-"
        )

        credit_days = int(
            getattr(customer, "credit_days", 0) or 0
        )

        due_date = (
            order_date + timedelta(days=credit_days)
            if order_date and credit_days > 0
            else None
        )

        due_date_text = (
            due_date.strftime("%d-%m-%Y")
            if due_date
            else "-"
        )

        billing_html = (
            cls.build_address(customer, billing_address)
            if customer
            else "-"
        )

        shipping_html = (
            cls.build_address(
                customer,
                shipping_address or billing_address,
            )
            if customer
            else "-"
        )

        warehouse = getattr(sales_order, "warehouse", None)

        warehouse_name = (
            cls.relation_value(
                warehouse,
                ["name", "warehouse_name", "code"],
            )
            if warehouse
            else "-"
        )

        payment_status = (
            getattr(sales_order, "payment_status", None)
            or "PENDING"
        )

        bill_content = [
            Paragraph(
                f"<b>{cls.html(customer_name)}</b>",
                base,
            ),
            Spacer(1, 1.2 * mm),
            Paragraph(billing_html, small),
            Spacer(1, 1 * mm),
            Paragraph(
                f"Contact No. : {cls.html(customer_phone)}",
                small,
            ),
            Spacer(1, 0.8 * mm),
            Paragraph(
                f"GSTIN : {cls.html(customer_gstin)}",
                small,
            ),
            Spacer(1, 0.8 * mm),
            Paragraph(
                f"State : {cls.html(customer_state)}",
                small,
            ),
        ]

        ship_content = [
            Paragraph(shipping_html, small),
        ]

        invoice_content = [
            Paragraph(
                f"Invoice No. : <b>{cls.html(sales_order.so_number)}</b>",
                small,
            ),
            Spacer(1, 1.3 * mm),
            Paragraph(f"Date : {date_text}", small),
            Spacer(1, 1.3 * mm),
            Paragraph(
                f"Place of supply : {cls.html(customer_state)}",
                small,
            ),
            Spacer(1, 1.3 * mm),
            Paragraph(f"Due Date : {due_date_text}", small),
            Spacer(1, 1.3 * mm),
            Paragraph(
                f"Warehouse : {cls.html(warehouse_name)}",
                small,
            ),
            Spacer(1, 1.3 * mm),
            Paragraph(
                f"Payment : {cls.html(payment_status)}",
                small,
            ),
        ]

        invoice_header = Table(
            [
                [
                    Paragraph("<b>Bill To</b>", center_bold),
                    Paragraph("<b>Ship To</b>", center_bold),
                    Paragraph("<b>Invoice Details</b>", center_bold),
                ],
                [
                    bill_content,
                    ship_content,
                    invoice_content,
                ],
            ],
            colWidths=[63 * mm, 63 * mm, 64 * mm],
        )

        invoice_header.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), GREY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("GRID", (0, 0), (-1, -1), 0.55, BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2.5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
                    ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                ]
            )
        )

        header_section = Table(
            [[header], [invoice_header]],
            colWidths=[190 * mm],
        )

        header_section.setStyle(
            TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )

        # =================================================
        # PRODUCTS
        # =================================================

        product_data = [
            [
                Paragraph("<b>#</b>", center),
                Paragraph("<b>Item name</b>", center),
                Paragraph("<b>HSN/ SAC</b>", center),
                Paragraph("<b>Qty</b>", center),
                Paragraph("<b>Unit</b>", center),
                Paragraph("<b>Price/ Unit</b>", center),
                Paragraph("<b>Amount</b>", center),
            ]
        ]

        product_row_heights = [None]  # Header row height

        total_quantity = 0

        items = getattr(sales_order, "items", []) or []

        # 1. ACTUAL PRODUCT ROWS (Dynamic Natural Height)
        for index, item in enumerate(items, start=1):
            quantity = int(
                getattr(item, "quantity", 0) or 0
            )

            total_quantity += quantity

            product = getattr(item, "product", None)

            hsn = (
                getattr(item, "hsn_sac", None)
                or getattr(item, "hsn_code", None)
                or (
                    getattr(product, "hsn_sac", None)
                    if product
                    else None
                )
                or (
                    getattr(product, "hsn_code", None)
                    if product
                    else None
                )
                or "-"
            )

            unit = (
                getattr(item, "unit", None)
                or (
                    getattr(product, "unit", None)
                    if product
                    else None
                )
            )

            unit_text = cls.relation_value(
                unit,
                ["name", "unit_name", "code", "symbol"],
            )

            selling_price = Decimal(
                getattr(item, "selling_price", 0) or 0
            )

            line_total = Decimal(
                getattr(item, "line_total", 0) or 0
            )

            product_name = (
                getattr(item, "product_name", None)
                or (
                    getattr(product, "product_name", None)
                    if product
                    else None
                )
                or "-"
            )

            product_data.append(
                [
                    Paragraph(str(index), center),
                    Paragraph(cls.html(product_name), small),
                    Paragraph(cls.html(hsn), small),
                    Paragraph(str(quantity), center),
                    Paragraph(cls.html(unit_text), center),
                    Paragraph(cls.money(selling_price), right),
                    Paragraph(cls.money(line_total), right),
                ]
            )
            product_row_heights.append(None)  # Add natural height for this specific item

        # 2. FILLER ROW (Creates the empty space without causing overflow page-breaks)
        product_data.append(["", "", "", "", "", "", ""])
        product_row_heights.append(25 * mm)  # Adjust this value if you need more/less empty space

        # 3. TOTAL ROW
        subtotal_value = Decimal(
            getattr(sales_order, "subtotal", 0) or 0
        )

        product_data.append(
            [
                "",
                Paragraph("<b>Total</b>", bold),
                "",
                Paragraph(f"<b>{total_quantity}</b>", right),
                "",
                "",
                Paragraph(
                    f"<b>{cls.money(subtotal_value)}</b>",
                    right,
                ),
            ]
        )
        product_row_heights.append(None)

        products_table = Table(
            product_data,
            colWidths=[
                8 * mm,
                65 * mm,
                28 * mm,
                12 * mm,
                18 * mm,
                31 * mm,
                28 * mm,
            ],
            rowHeights=product_row_heights,
            repeatRows=1,
        )

        products_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), GREY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("ALIGN", (3, 1), (3, -1), "CENTER"),
                    ("ALIGN", (4, 1), (4, -1), "CENTER"),
                    ("ALIGN", (5, 1), (-1, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                    ("VALIGN", (0, -1), (-1, -1), "MIDDLE"),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F4F4F4")),
                    ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
                ]
            )
        )

        # =================================================
        # FINANCIAL VALUES
        # =================================================

        subtotal = Decimal(
            getattr(sales_order, "subtotal", 0) or 0
        )

        gst_total = Decimal(
            getattr(sales_order, "gst_amount", 0) or 0
        )

        grand_total = Decimal(
            getattr(sales_order, "grand_total", 0) or 0
        )
        
        # Note: Discount, Other Charges, and Paid Amount removed from the display below as requested

        taxable_amount = subtotal

        # =================================================
        # LEFT SIDE: TAX + WORDS + PAYMENT
        # =================================================

        state_text = str(customer_state or "").strip().lower()

        if state_text == "karnataka":
            sgst = gst_total / 2
            cgst = gst_total / 2
            igst = Decimal("0")

            rate = (
                (sgst / taxable_amount * 100)
                if taxable_amount
                else Decimal("0")
            )
        else:
            sgst = Decimal("0")
            cgst = Decimal("0")
            igst = gst_total

            rate = (
                (igst / taxable_amount * 100)
                if taxable_amount
                else Decimal("0")
            )

        tax_data = [
            [
                Paragraph("<b>Tax type</b>", center),
                Paragraph("<b>Taxable amount</b>", center),
                Paragraph("<b>Rate</b>", center),
                Paragraph("<b>Tax amount</b>", center),
            ]
        ]

        if igst > 0:
            tax_data.append(
                [
                    Paragraph("IGST", small),
                    Paragraph(cls.money(taxable_amount), right),
                    Paragraph(f"{rate:.0f}%", center),
                    Paragraph(cls.money(igst), right),
                ]
            )
        else:
            tax_data.extend(
                [
                    [
                        Paragraph("SGST", small),
                        Paragraph(cls.money(taxable_amount), right),
                        Paragraph(f"{rate:.0f}%", center),
                        Paragraph(cls.money(sgst), right),
                    ],
                    [
                        Paragraph("CGST", small),
                        Paragraph(cls.money(taxable_amount), right),
                        Paragraph(f"{rate:.0f}%", center),
                        Paragraph(cls.money(cgst), right),
                    ],
                ]
            )

        tax_table = Table(
            tax_data,
            colWidths=[
                18 * mm,
                38 * mm,
                15 * mm,
                24 * mm,
            ],
        )

        tax_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), GREY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                    ("INNERGRID", (0, 0), (-1, -1), 0.6, BORDER),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    ("ALIGN", (2, 1), (2, -1), "CENTER"),
                    ("ALIGN", (3, 1), (3, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2.2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )

        words = cls.amount_in_words(grand_total)

        words_table = Table(
            [
                [
                    Paragraph(
                        "<b>Invoice Amount In Words</b>",
                        center_bold,
                    )
                ],
                [
                    Paragraph(words, amount_words)
                ],
            ],
            colWidths=[95 * mm],
            rowHeights=[7 * mm, 7 * mm],
        )

        words_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), GREY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                    ("INNERGRID", (0, 0), (-1, -1), 0.6, BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 1.5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
                ]
            )
        )

        payment_mode = (
            getattr(sales_order, "payment_method", None)
            or "Credit"
        )

        payment_table = Table(
            [
                [
                    Paragraph(
                        "<b>Payment mode</b>",
                        center_bold,
                    )
                ],
                [
                    Paragraph(
                        cls.html(payment_mode),
                        center,
                    )
                ],
            ],
            colWidths=[95 * mm],
            rowHeights=[7 * mm, 7 * mm],
        )

        payment_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), GREY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                    ("INNERGRID", (0, 0), (-1, -1), 0.6, BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 1.5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
                ]
            )
        )

        # Stack them perfectly tight on the left column
        left_stack = Table(
            [
                [tax_table],
                [words_table],
                [payment_table]
            ],
            colWidths=[95 * mm],
        )
        
        left_stack.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )

        # =================================================
        # RIGHT SIDE: AMOUNTS
        # =================================================

        tax_label = (
            f"Tax ({(rate * 2 if igst == 0 else rate):.0f}%)"
            if gst_total
            else "Tax"
        )

        # Discount, Other Charges, and Received removed as requested
        amounts_data = [
            [
                Paragraph("<b>Amounts</b>", center),
                "",
            ],
            [
                Paragraph("Sub Total", small),
                Paragraph(cls.money(subtotal), right),
            ],
            [
                Paragraph(tax_label, small),
                Paragraph(cls.money(gst_total), right),
            ],
            [
                Paragraph("<b>Total</b>", bold),
                Paragraph(
                    f"<b>{cls.money(grand_total)}</b>",
                    right_bold,
                ),
            ],
        ]

        amounts_table = Table(
            amounts_data,
            colWidths=[55 * mm, 40 * mm],
        )

        # Removed BOX and INNERGRID from here so there are no gridlines between the rows.
        # Kept LINEABOVE to draw a single line above the Total row.
        amounts_table.setStyle(
            TableStyle(
                [
                    ("SPAN", (0, 0), (1, 0)),
                    ("BACKGROUND", (0, 0), (-1, 0), GREY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("LINEBELOW", (0, 0), (1, 0), 0.6, BORDER),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LINEABOVE", (0, 3), (1, 3), 0.6, BORDER), # Line separating Tax and Total
                    ("TOPPADDING", (0, 0), (-1, -1), 2.2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )

        # =================================================
        # FINANCIAL MASTER CONTAINER
        # =================================================

        financial_and_words = Table(
            [[left_stack, amounts_table]],
            colWidths=[95 * mm, 95 * mm],
        )

        financial_and_words.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    
                    # This is the magic that draws the outer box and perfect middle divider 
                    # stretching down equally, regardless of which column is taller.
                    ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                    ("INNERGRID", (0, 0), (-1, -1), 0.6, BORDER),
                ]
            )
        )

        # =================================================
        # BOTTOM: BANK / TERMS / SIGNATURE
        # =================================================

        bank_content = [
            Paragraph("<b>Bank Details</b>", section),
            Spacer(1, 1.2 * mm),
        ]

        bank_text = [
            Paragraph(
                f"Name : {cls.html(cls.BANK_NAME)}",
                small,
            ),
            Spacer(1, 1.2 * mm),
            Paragraph(
                f"Account No. : {cls.html(cls.ACCOUNT_NUMBER)}",
                small,
            ),
            Spacer(1, 1.2 * mm),
            Paragraph(
                f"IFSC code : {cls.html(cls.IFSC_CODE)}",
                small,
            ),
            Spacer(1, 1.2 * mm),
            Paragraph(
                f"Account holder's name : "
                f"{cls.html(cls.ACCOUNT_HOLDER)}",
                small,
            ),
        ]

        if cls.QR_PATH.exists():
            qr = Image(
                str(cls.QR_PATH),
                width=21 * mm,
                height=21 * mm,
                kind="proportional",
            )

            bank_body = Table(
                [[qr, bank_text]],
                colWidths=[24 * mm, 34 * mm],
            )

            bank_body.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 1),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )

            bank_content.append(bank_body)
        else:
            bank_content.extend(bank_text)

        terms_content = [
            Paragraph("<b>Terms and Conditions</b>", section),
            Spacer(1, 1.2 * mm),
        ]

        for term in cls.TERMS:
            terms_content.append(
                Paragraph(cls.html(term), small)
            )
            terms_content.append(Spacer(1, 1.1 * mm))

        signature_content = [
            Paragraph(
                f"<b>For : {cls.COMPANY_NAME}</b>",
                center,
            ),
            Spacer(1, 5 * mm),
        ]

        if cls.SIGNATURE_PATH.exists():
            signature_content.append(
                Image(
                    str(cls.SIGNATURE_PATH),
                    width=35 * mm,
                    height=20 * mm,
                    kind="proportional",
                )
            )
        else:
            signature_content.append(Spacer(1, 20 * mm))

        signature_content.append(Spacer(1, 2 * mm))

        signature_content.append(
            Paragraph(
                "<b>Authorized Signatory</b>",
                center,
            )
        )

        bottom = Table(
            [
                [
                    bank_content,
                    terms_content,
                    signature_content,
                ]
            ],
            colWidths=[
                63 * mm,
                63 * mm,
                64 * mm,
        ],
        )

        bottom.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.6, BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("MINHEIGHT", (0, 0), (-1, -1), 40 * mm),
                ]
            )
        )

        # =================================================
        # MASTER INVOICE OUTER BORDER
        # =================================================

        invoice_rows = [
            [header_section],
            [products_table],
            [financial_and_words],
            [bottom],
        ]

        remarks = getattr(sales_order, "remarks", None)
        
        if remarks:
            remarks_table = Table(
                [[Paragraph("<b>Remarks :</b> " + cls.html(remarks), small)]],
                colWidths=[190 * mm]
            )
            remarks_table.setStyle(
                TableStyle([
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ])
            )
            invoice_rows.append([remarks_table])

        invoice_frame = Table(
            invoice_rows,
            colWidths=[190 * mm],
        )
        
        invoice_frame.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.8, BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )

        story.append(invoice_frame)
        
        # =================================================
        # FOOTER
        # =================================================

        story.append(Spacer(1, 1.5 * mm))

        footer = Table(
            [
                [
                    Paragraph(
                        "This is a computer-generated document.",
                        tiny,
                    ),
                    Paragraph(
                        "Thank you for your business.",
                        center_bold,
                    ),
                ]
            ],
            colWidths=[
                95 * mm,
                95 * mm,
            ],
        )

        footer.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (-1, 0), 0.5, colors.HexColor("#999999")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )

        story.append(footer)

        # =================================================
        # BUILD PDF
        # =================================================

        document.build(story)

        buffer.seek(0)

        return buffer
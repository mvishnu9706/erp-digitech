from io import BytesIO
from decimal import Decimal

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
    HRFlowable,
)


# ============================================================
# Helper
# ============================================================

def money(value):
    """
    Format amount as Indian Rupees.
    """

    if value is None:
        value = Decimal("0")

    return f"₹{Decimal(str(value)):,.2f}"


# ============================================================
# Generate Sales PDF
# ============================================================

def generate_sales_pdf(sale):
    """
    Generate PDF for a sales order.

    Returns:
        BytesIO
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    # ========================================================
    # Styles
    # ========================================================

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        alignment=TA_LEFT,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#64748b"),
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#172033"),
        spaceBefore=8,
        spaceAfter=6,
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#64748b"),
    )

    right_style = ParagraphStyle(
        "RightStyle",
        parent=normal_style,
        alignment=TA_RIGHT,
    )

    # ========================================================
    # Story
    # ========================================================

    story = []

    # ========================================================
    # Company Header
    # ========================================================

    story.append(
        Paragraph(
            "DIGITECH",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Imaging Solutions",
            subtitle_style,
        )
    )

    story.append(Spacer(1, 6 * mm))

    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#e5e7eb"),
        )
    )

    story.append(Spacer(1, 5 * mm))

    # ========================================================
    # Sales Order Title
    # ========================================================

    sale_number = getattr(
        sale,
        "order_number",
        None,
    ) or getattr(
        sale,
        "sale_number",
        None,
    ) or "N/A"

    sale_date = getattr(
        sale,
        "sale_date",
        None,
    )

    if sale_date:
        sale_date_text = sale_date.strftime("%d-%m-%Y")
    else:
        sale_date_text = "N/A"

    story.append(
        Paragraph(
            "SALES ORDER",
            section_style,
        )
    )

    # ========================================================
    # Order Information
    # ========================================================

    customer = getattr(
        sale,
        "customer",
        None,
    )

    customer_name = (
        getattr(customer, "customer_name", None)
        if customer
        else None
    )

    warehouse = getattr(
        sale,
        "warehouse",
        None,
    )

    warehouse_name = (
        getattr(warehouse, "name", None)
        if warehouse
        else None
    )

    order_info = [
        [
            Paragraph("<b>Order No.</b>", normal_style),
            Paragraph(str(sale_number), normal_style),
            Paragraph("<b>Sales Date</b>", normal_style),
            Paragraph(sale_date_text, normal_style),
        ],
        [
            Paragraph("<b>Customer</b>", normal_style),
            Paragraph(customer_name or "N/A", normal_style),
            Paragraph("<b>Warehouse</b>", normal_style),
            Paragraph(warehouse_name or "N/A", normal_style),
        ],
    ]

    order_table = Table(
        order_info,
        colWidths=[
            28 * mm,
            62 * mm,
            28 * mm,
            62 * mm,
        ],
    )

    order_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#f8fafc"),
                ),
                (
                    "BACKGROUND",
                    (2, 0),
                    (2, -1),
                    colors.HexColor("#f8fafc"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e5e7eb"),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e5e7eb"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(order_table)

    story.append(Spacer(1, 7 * mm))

    # ========================================================
    # Products
    # ========================================================

    story.append(
        Paragraph(
            "Products",
            section_style,
        )
    )

    items = getattr(
        sale,
        "items",
        []
    ) or []

    product_data = [
        [
            Paragraph("<b>#</b>", small_style),
            Paragraph("<b>Product</b>", small_style),
            Paragraph("<b>Qty</b>", small_style),
            Paragraph("<b>Price</b>", small_style),
            Paragraph("<b>Discount</b>", small_style),
            Paragraph("<b>GST</b>", small_style),
            Paragraph("<b>Total</b>", small_style),
        ]
    ]

    for index, item in enumerate(items, start=1):

        product = getattr(
            item,
            "product",
            None,
        )

        product_name = (
            getattr(product, "name", None)
            if product
            else None
        )

        quantity = getattr(
            item,
            "quantity",
            0,
        )

        selling_price = getattr(
            item,
            "selling_price",
            0,
        )

        discount = getattr(
            item,
            "discount",
            0,
        )

        gst = getattr(
            item,
            "gst",
            0,
        )

        total = getattr(
            item,
            "total",
            0,
        )

        product_data.append(
            [
                str(index),
                product_name or "N/A",
                str(quantity),
                money(selling_price),
                money(discount),
                money(gst),
                money(total),
            ]
        )

    if not items:
        product_data.append(
            [
                "",
                "No products",
                "",
                "",
                "",
                "",
                "",
            ]
        )

    product_table = Table(
        product_data,
        colWidths=[
            8 * mm,
            65 * mm,
            15 * mm,
            27 * mm,
            27 * mm,
            22 * mm,
            30 * mm,
        ],
        repeatRows=1,
    )

    product_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#f8fafc"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#475569"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e5e7eb"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (2, 1),
                    (-1, -1),
                    "RIGHT",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(product_table)

    story.append(Spacer(1, 7 * mm))

    # ========================================================
    # Summary
    # ========================================================

    subtotal = getattr(
        sale,
        "subtotal",
        0,
    )

    discount_total = getattr(
        sale,
        "discount",
        0,
    )

    taxable_amount = getattr(
        sale,
        "taxable_amount",
        0,
    )

    gst_total = getattr(
        sale,
        "gst",
        0,
    )

    grand_total = getattr(
        sale,
        "grand_total",
        0,
    )

    summary_data = [
        [
            Paragraph("Subtotal", normal_style),
            Paragraph(money(subtotal), right_style),
        ],
        [
            Paragraph("Discount", normal_style),
            Paragraph(money(discount_total), right_style),
        ],
        [
            Paragraph("Taxable Amount", normal_style),
            Paragraph(money(taxable_amount), right_style),
        ],
        [
            Paragraph("GST", normal_style),
            Paragraph(money(gst_total), right_style),
        ],
        [
            Paragraph("<b>Grand Total</b>", normal_style),
            Paragraph(
                f"<b>{money(grand_total)}</b>",
                right_style,
            ),
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            130 * mm,
            64 * mm,
        ],
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#e5e7eb"),
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -2),
                    0.5,
                    colors.HexColor("#eef2f7"),
                ),
                (
                    "BACKGROUND",
                    (0, -1),
                    (-1, -1),
                    colors.HexColor("#f8fafc"),
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(summary_table)

    # ========================================================
    # Remarks
    # ========================================================

    remarks = getattr(
        sale,
        "remarks",
        None,
    )

    if remarks:

        story.append(
            Spacer(1, 7 * mm)
        )

        story.append(
            Paragraph(
                "Remarks",
                section_style,
            )
        )

        story.append(
            Paragraph(
                str(remarks),
                normal_style,
            )
        )

    # ========================================================
    # Footer
    # ========================================================

    story.append(
        Spacer(1, 15 * mm)
    )

    story.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#e5e7eb"),
        )
    )

    story.append(
        Spacer(1, 3 * mm)
    )

    story.append(
        Paragraph(
            "© Digitech ERP | Generated Sales Document",
            small_style,
        )
    )

    # ========================================================
    # Build PDF
    # ========================================================

    document.build(story)

    buffer.seek(0)

    return buffer
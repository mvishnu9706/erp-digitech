from io import BytesIO

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font


class ExcelHelper:

    HEADERS = [

        "Product Name",
        "Model No",
        "SKU",
        "Barcode",
        "Category",
        "Brand",
        "Unit",
        "Warehouse",
        "Cost Price",
        "DTP Price",
        "Retail Price",
        "Margin %",
        "GST %",
        "HSN Code",
        "Minimum Stock",
        "Status"

    ]

    # ======================================================
    # Product Template
    # ======================================================

    @staticmethod
    def create_template():

        workbook = Workbook()

        sheet = workbook.active

        sheet.title = "Products"

        for column, header in enumerate(
            ExcelHelper.HEADERS,
            start=1
        ):

            cell = sheet.cell(
                row=1,
                column=column
            )

            cell.value = header

            cell.font = Font(bold=True)

        output = BytesIO()

        workbook.save(output)

        output.seek(0)

        return output

    # ======================================================
    # Read Excel
    # ======================================================

    @staticmethod
    def read_excel(file):

        workbook = openpyxl.load_workbook(file)

        sheet = workbook.active

        rows = []

        headers = []

        for cell in sheet[1]:

            headers.append(cell.value)

        for row in sheet.iter_rows(

            min_row=2,

            values_only=True

        ):

            rows.append(

                dict(

                    zip(headers, row)

                )

            )

        return rows

    # ======================================================
    # Export Products
    # ======================================================

    @staticmethod
    def export_products(products):

        workbook = Workbook()

        sheet = workbook.active

        sheet.title = "Products"

        for column, header in enumerate(

            ExcelHelper.HEADERS,

            start=1

        ):

            cell = sheet.cell(

                row=1,

                column=column

            )

            cell.value = header

            cell.font = Font(bold=True)

        row_number = 2

        for product in products:

            sheet.cell(row=row_number, column=1).value = product.product_name
            sheet.cell(row=row_number, column=2).value = product.model_no
            sheet.cell(row=row_number, column=3).value = product.sku
            sheet.cell(row=row_number, column=4).value = product.barcode

            sheet.cell(
                row=row_number,
                column=5
            ).value = (
                product.category.name
                if product.category
                else ""
            )

            sheet.cell(
                row=row_number,
                column=6
            ).value = (
                product.brand.name
                if product.brand
                else ""
            )

            sheet.cell(
                row=row_number,
                column=7
            ).value = (
                product.unit.name
                if product.unit
                else ""
            )

            sheet.cell(
                row=row_number,
                column=8
            ).value = (
                product.warehouse.warehouse_name
                if product.warehouse
                else ""
            )

            sheet.cell(row=row_number, column=9).value = float(product.cost_price)
            sheet.cell(row=row_number, column=10).value = float(product.dtp_price)
            sheet.cell(row=row_number, column=11).value = float(product.retail_price)
            sheet.cell(row=row_number, column=12).value = float(product.margin_percentage)
            sheet.cell(row=row_number, column=13).value = float(product.gst_percentage)
            sheet.cell(row=row_number, column=14).value = product.hsn_code
            sheet.cell(row=row_number, column=15).value = product.minimum_stock
            sheet.cell(row=row_number, column=16).value = product.status

            row_number += 1

        output = BytesIO()

        workbook.save(output)

        output.seek(0)

        return output
from decimal import Decimal
from pydantic import BaseModel


class DashboardResponse(BaseModel):

    total_customers: int

    total_suppliers: int

    total_products: int

    total_warehouses: int

    total_sales: Decimal

    total_purchases: Decimal

    total_customer_receivable: Decimal

    total_supplier_payable: Decimal

    inventory_value: Decimal

    cash_balance: Decimal

    monthly_sales: Decimal

    monthly_purchase: Decimal

    monthly_collection: Decimal

    monthly_payment: Decimal

    gross_profit: Decimal

    net_profit: Decimal
from decimal import Decimal
from types import SimpleNamespace

import app.services.customer_ledger_service as customer_ledger_service_module


def test_customer_ledger_service_builds_running_balance(monkeypatch):
    customer = SimpleNamespace(id=1, customer_name="ABC Ltd", opening_balance=Decimal("100"))

    monkeypatch.setattr(
        customer_ledger_service_module.CustomerRepository,
        "get_by_id",
        lambda db, customer_id: customer,
    )
    monkeypatch.setattr(
        customer_ledger_service_module.CustomerLedgerRepository,
        "get_opening_balance",
        lambda db, customer_id, from_date: Decimal("100"),
    )
    monkeypatch.setattr(
        customer_ledger_service_module.CustomerLedgerRepository,
        "get_transactions",
        lambda db, customer_id, from_date, to_date: [
            {
                "date": "2024-01-01",
                "voucher_type": "Sales Invoice",
                "voucher_number": "INV-001",
                "debit": Decimal("50"),
                "credit": Decimal("0"),
            },
            {
                "date": "2024-01-02",
                "voucher_type": "Customer Payment",
                "voucher_number": "PAY-001",
                "debit": Decimal("0"),
                "credit": Decimal("20"),
            },
        ],
    )

    response = customer_ledger_service_module.CustomerLedgerService.get_ledger(object(), 1)

    assert response.customer_name == "ABC Ltd"
    assert response.opening_balance == Decimal("100")
    assert response.entries[0].balance == Decimal("150")
    assert response.entries[1].balance == Decimal("130")
    assert response.closing_balance == Decimal("130")

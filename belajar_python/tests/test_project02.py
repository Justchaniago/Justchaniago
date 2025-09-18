import os
from belajar_python import project02_expense as exp


def setup_function():
    # Bersihkan file sebelum setiap test
    if exp.DATA_FILE.exists():
        os.remove(exp.DATA_FILE)


def test_add_and_total():
    exp.add_expense("2025-09-18", "Kopi", 20000, "Makan")
    exp.add_expense("2025-09-19", "Grab", 30000, "Transport")

    assert exp.get_total() == 50000


def test_filter_date_and_category():
    exp.add_expense("2025-09-18", "Kopi", 20000, "Makan")
    exp.add_expense("2025-09-18", "Nasi Goreng", 25000, "Makan")
    exp.add_expense("2025-09-19", "Grab", 30000, "Transport")

    # filter tanggal
    by_date = exp.get_expenses_by_date("2025-09-18")
    assert len(by_date) == 2

    # total kategori
    assert exp.get_total_by_category("Makan") == 45000
    assert exp.get_total_by_category("Transport") == 30000

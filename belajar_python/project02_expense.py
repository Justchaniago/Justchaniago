import json
from pathlib import Path

# file JSON untuk simpan data
DATA_FILE = Path(__file__).parent / "expense_data.json"


def load_data():
    """Membaca semua transaksi dari file JSON."""
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:  # jika file kosong
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        # kalau file kosong/rusak, mulai dari list kosong
        return []


def save_data(data):
    """Menyimpan semua transaksi ke file JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_expense(date, description, amount, category):
    """Tambah transaksi baru ke file JSON."""
    data = load_data()
    data.append({
        "date": date,
        "description": description,
        "amount": amount,
        "category": category,
    })
    save_data(data)
    return data


def get_total():
    """Hitung total semua pengeluaran."""
    data = load_data()
    return sum(item["amount"] for item in data)


def get_expenses_by_date(date):
    """Ambil semua transaksi pada tanggal tertentu (YYYY-MM-DD)."""
    data = load_data()
    return [item for item in data if item["date"] == date]


def get_total_by_category(category):
    """Hitung total pengeluaran berdasarkan kategori."""
    data = load_data()
    return sum(item["amount"] for item in data if item["category"].lower() == category.lower())


# ====================
# CLI INTERAKTIF
# ====================
if __name__ == "__main__":
    while True:
        print("\n=== Expense Tracker ===")
        print("1. Tambah transaksi")
        print("2. Lihat semua transaksi")
        print("3. Total pengeluaran")
        print("4. Lihat transaksi berdasarkan tanggal")
        print("5. Total pengeluaran berdasarkan kategori")
        print("0. Keluar")
        choice = input("Pilih menu: ").strip()

        if choice == "1":
            date = input("Tanggal (YYYY-MM-DD): ")
            desc = input("Deskripsi: ")
            amount = float(input("Nominal: "))
            category = input("Kategori: ")
            add_expense(date, desc, amount, category)
            print("✅ Transaksi tersimpan.")

        elif choice == "2":
            data = load_data()
            if not data:
                print("Belum ada transaksi.")
            else:
                print("\nDaftar Transaksi:")
                for d in data:
                    print(f"{d['date']} - {d['description']} - Rp{d['amount']} ({d['category']})")

        elif choice == "3":
            print(f"Total pengeluaran: Rp{get_total()}")

        elif choice == "4":
            date = input("Tanggal (YYYY-MM-DD): ")
            results = get_expenses_by_date(date)
            if not results:
                print("Tidak ada transaksi pada tanggal tersebut.")
            else:
                for d in results:
                    print(f"{d['date']} - {d['description']} - Rp{d['amount']} ({d['category']})")

        elif choice == "5":
            cat = input("Kategori: ")
            total = get_total_by_category(cat)
            print(f"Total pengeluaran kategori {cat}: Rp{total}")

        elif choice == "0":
            print("Keluar dari program. 👋")
            break

        else:
            print("Menu tidak dikenal.")

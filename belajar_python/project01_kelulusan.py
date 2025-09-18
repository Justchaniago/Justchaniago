def status_kelulusan(masa_studi_th, ipk, punya_nilai_e):
    # ... (logika kamu di sini)
    ...

if __name__ == "__main__":
    # HANYA jalan saat dieksekusi langsung, TIDAK saat diimport test
    masa_studi = float(input("Masa studi (tahun): "))
    ipk = float(input("IPK: "))
    ada_e = input("Ada nilai E? (y/n): ").lower() == "y"
    print("Hasil kelulusan:", status_kelulusan(masa_studi, ipk, ada_e))


def status_kelulusan(masa_studi_th, ipk, punya_nilai_e):
    #Aturan 1
    if masa_studi_th <=7:
        if ipk >= 2.75 and not punya_nilai_e:
            return "Lulus"
        else :
            return "Tidak Lulus"
        
    #Aturan 2
    elif masa_studi_th <=8:
        if ipk >= 3.00 and not punya_nilai_e:
            return "Lulus (Terlambat)"
        else :
            return "Tidak Lulus"
        
    #Aturan Lain
    else:
        return "Tidak Lulus"

if __name__=="__main__":
    print("=== Student Tracker ===")

    masa_studi = float(input("Masa Studi (Tahun):"))
    ipk = float(input("IPK: "))
    ada_e = input("Apakah ada nilai E? (y/n): ").strip().lower() == "y"

    hasil = status_kelulusan(masa_studi, ipk, ada_e)
    print(f"Hasil Kelulusan:{hasil}")


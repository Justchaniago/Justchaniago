import sys, pathlib
# Tambahkan path root repo agar bisa import student_tracker
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import pytest
from student_tracker.project import status_kelulusan

def test_lulus_normal():
    assert status_kelulusan(6.5, 3.0, False) == "Lulus"

def test_lulus_terlambat():
    assert status_kelulusan(7.5, 3.2, False) == "Lulus (Terlambat)"

def test_tidak_lulus_karena_e():
    assert status_kelulusan(6.0, 3.5, True) == "Tidak Lulus"

def test_tidak_lulus_karena_ipk_rendah():
    assert status_kelulusan(6.0, 2.0, False) == "Tidak Lulus"

def test_tidak_lulus_karena_masa_studi_lebih_8():
    assert status_kelulusan(8.5, 4.0, False) == "Tidak Lulus"

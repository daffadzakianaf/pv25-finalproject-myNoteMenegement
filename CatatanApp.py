import sys
import sqlite3
import csv
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QTableWidgetItem, QDialog
)
from PyQt6.QtCore import Qt

class CatatanApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("project_akhir.ui", self)
        self.setWindowTitle("Aplikasi Manajemen Catatan Pribadi")

        # Sebagai setup StatusBar
        self.statusBar().showMessage("Nama: Muhammad Daffa Dzaki Ahnaf | NIM: F1D022142")

        # Database
        self.conn = sqlite3.connect("catatan.db")
        self.cursor = self.conn.cursor()
        self.setup_database()

        self.Kategori.addItems(["Pribadi", "Pekerjaan", "Akademik", "Lainnya"])
        self.Status.addItems(["Draft", "Selesai", "Tertunda"])

        self.tabelCatatan.setColumnCount(5)
        self.tabelCatatan.setHorizontalHeaderLabels(["Judul", "Kategori", "Tanggal", "Status", "Isi"])

        # Connect tombol
        self.Simpan.clicked.connect(self.tambah_catatan)
        self.Hapus.clicked.connect(self.hapus_catatan)
        self.Edit.clicked.connect(self.edit_catatan)
        self.ExportCsv.clicked.connect(self.export_csv)
        self.Pencarian.textChanged.connect(self.cari_catatan)

        # MenuBar actions 
        self.actionOpen.triggered.connect(self.menu_open)
        self.actionSave.triggered.connect(self.export_csv)
        self.actionSaveAss.triggered.connect(self.export_csv)
        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.menu_about)

        self.load_data()

    def setup_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS catatan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT,
                kategori TEXT,
                tanggal TEXT,
                status TEXT,
                isi TEXT
            )
        ''')
        self.conn.commit()

    def tambah_catatan(self):
        try:
            judul = self.Judul.text()
            kategori = self.Kategori.currentText()
            tanggal = self.tanggalCatatan.date().toString("yyyy-MM-dd")
            status = self.Status.currentText()
            isi = self.Catatan.toPlainText()

            if not judul or not kategori or not status or not tanggal or not isi:
                QMessageBox.warning(self, "Validasi", "Semua kolom harus diisi.")
                return
            
            self.cursor.execute(
                "INSERT INTO catatan (judul, kategori, tanggal, status, isi) VALUES (?, ?, ?, ?, ?)",
                (judul, kategori, tanggal, status, isi)
            )

            self.conn.commit()
            self.load_data()
            self.clear_form()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan saat menyimpan:\n{str(e)}")


    def load_data(self, query="SELECT * FROM catatan"):
        self.tabelCatatan.setRowCount(0)
        self.cursor.execute(query)
        for row_data in self.cursor.fetchall():
            row = self.tabelCatatan.rowCount()
            self.tabelCatatan.insertRow(row)
            for column, data in enumerate(row_data[1:]):  
                self.tabelCatatan.setItem(row, column, QTableWidgetItem(str(data)))

    def clear_form(self):
        self.Judul.clear()
        self.Catatan.clear()
        self.Kategori.setCurrentIndex(0)
        self.Status.setCurrentIndex(0)

    def hapus_catatan(self):
        row = self.tabelCatatan.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih baris yang akan dihapus.")
            return

        judul = self.tabelCatatan.item(row, 0).text()
        self.cursor.execute("DELETE FROM catatan WHERE judul=?", (judul,))
        self.conn.commit()
        self.load_data()
        self.clear_form()

    def edit_catatan(self):
        row = self.tabelCatatan.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih baris yang akan diedit.")
            return

        judul_baru = self.Judul.text()
        kategori = self.Kategori.currentText()
        tanggal = self.tanggalCatatan.date().toString("yyyy-MM-dd")
        status = self.Status.currentText()
        isi = self.Catatan.toPlainText()

        if not judul_baru or not kategori or not status or not tanggal or not isi:
            QMessageBox.warning(self, "Validasi", "Semua kolom harus diisi.")
            return

        judul_lama = self.tabelCatatan.item(row, 0).text()
        self.cursor.execute("""
            UPDATE catatan SET judul=?, kategori=?, tanggal=?, status=?, isi=?
            WHERE judul=?
        """, (judul_baru, kategori, tanggal, status, isi, judul_lama))
        self.conn.commit()
        self.load_data()
        self.clear_form()

    def cari_catatan(self):
        keyword = self.Pencarian.text()
        query = f"SELECT * FROM catatan WHERE judul LIKE '%{keyword}%'"
        self.load_data(query)

    def export_csv(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Simpan File", "", "CSV Files (*.csv)")
        if filename:
            self.cursor.execute("SELECT * FROM catatan")
            data = self.cursor.fetchall()
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Judul", "Kategori", "Tanggal", "Status", "Isi"])
                for row in data:
                    writer.writerow(row[1:])
            QMessageBox.information(self, "Export", "Data berhasil diekspor ke CSV.")

    def menu_open(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Buka File", "", "CSV Files (*.csv)")
        if filename:
            try:
                with open(filename, mode='r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader)  
                    for row in reader:
                        if len(row) == 5:
                            self.cursor.execute("INSERT INTO catatan (judul, kategori, tanggal, status, isi) VALUES (?, ?, ?, ?, ?)", tuple(row))
                    self.conn.commit()
                self.load_data()
                QMessageBox.information(self, "Open", "File berhasil dimuat dan data disimpan ke database.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal membuka file: {str(e)}")

    def menu_about(self):
        QMessageBox.information(self, "Tentang", "Aplikasi Manajemen Catatan Pribadi:\nmerupakan aplikasi yang digunakan untuk mencatat, menyimpan, dan mengelola catatan harian atau tugas.\nAplikasi ini mendukung fitur Create, Read, Update, Delete dengan penyimpanan lokal menggunakan SQLite.")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CatatanApp()
    window.show()
    sys.exit(app.exec())



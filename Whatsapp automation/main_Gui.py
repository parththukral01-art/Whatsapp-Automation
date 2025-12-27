import sys
import sqlite3
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QDateTimeEdit, QFileDialog, QMessageBox)
from PySide6.QtCore import QDateTime
import scheduler_helper

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WhatsApp Automation Pro")
        self.resize(900, 600)
        self.db_init()
        
        # Setup UI
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Input Area
        input_card = QHBoxLayout()
        self.phone = QLineEdit(placeholderText="Phone (+1234...)")
        self.msg = QLineEdit(placeholderText="Message content")
        self.dt_edit = QDateTimeEdit(QDateTime.currentDateTime().addSecs(600))
        self.dt_edit.setCalendarPopup(True)
        
        self.attached_file = None
        self.file_btn = QPushButton("📎 Attach")
        self.file_btn.clicked.connect(self.get_file)
        
        add_btn = QPushButton("Schedule")
        add_btn.setStyleSheet("background-color: #075E54; color: white; padding: 5px;")
        add_btn.clicked.connect(self.schedule_job)

        input_card.addWidget(self.phone)
        input_card.addWidget(self.msg)
        input_card.addWidget(self.dt_edit)
        input_card.addWidget(self.file_btn)
        input_card.addWidget(add_btn)
        main_layout.addLayout(input_card)

        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Recipient", "Schedule Time", "File", "Actions"])
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table)

        self.load_data()

    def db_init(self):
        self.conn = sqlite3.connect("jobs.db")
        self.conn.execute("CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, phone TEXT, msg TEXT, time TEXT, file TEXT)")
        self.conn.commit()

    def get_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Attachment")
        if file:
            self.attached_file = file
            self.file_btn.setText("✔ Attached")

    def schedule_job(self):
        phone, msg = self.phone.text(), self.msg.text()
        time_str = self.dt_edit.dateTime().toString("HH:mm")
        
        if not phone or not msg:
            return QMessageBox.critical(self, "Error", "Fill phone and message")

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO jobs (phone, msg, time, file) VALUES (?,?,?,?)", 
                       (phone, msg, time_str, self.attached_file))
        job_id = cursor.lastrowid
        self.conn.commit()

        try:
            scheduler_helper.register_windows_task(job_id, time_str, phone, msg, self.attached_file)
            self.load_data()
            self.phone.clear(); self.msg.clear()
            self.attached_file = None
            self.file_btn.setText("📎 Attach")
        except Exception as e:
            QMessageBox.critical(self, "OS Error", f"Scheduler Error: {e}")

    def load_data(self):
        self.table.setRowCount(0)
        cursor = self.conn.execute("SELECT id, phone, time, file FROM jobs")
        for r_idx, row in enumerate(cursor.fetchall()):
            self.table.insertRow(r_idx)
            for c_idx, val in enumerate(row):
                self.table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))
            
            del_btn = QPushButton("Cancel")
            del_btn.clicked.connect(lambda _, tid=row[0]: self.delete_job(tid))
            self.table.setCellWidget(r_idx, 4, del_btn)

    def delete_job(self, tid):
        scheduler_helper.cancel_task(tid)
        self.conn.execute("DELETE FROM jobs WHERE id=?", (tid,))
        self.conn.commit()
        self.load_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())

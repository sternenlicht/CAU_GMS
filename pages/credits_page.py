import os
import sqlite3
from PyQt5 import uic
from PyQt5.QtGui import QTextOption
from PyQt5.QtWidgets import QDialog, QTextBrowser
from PyQt5.QtCore import Qt

def resource_path(relative_path):
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

ui_file = resource_path("../ui/credits_page.ui")
form_class = uic.loadUiType(ui_file)[0]

class CreditsPage(QDialog, form_class):
    def __init__(self, parent_geometry, main_window):
        super().__init__()
        self.text_browsers = {}
        self.setupUi(self)

        for i in range(1, 26):
            self.text_browsers[i] = self.findChild(QTextBrowser, f"textBrowser{i}")
        for browser in self.text_browsers.values():
            if browser:
                browser.setAlignment(Qt.AlignHCenter)
                doc = browser.document()
                doc.setDefaultTextOption(QTextOption(Qt.AlignCenter))
        
        self.setGeometry(parent_geometry)
        self.main_window = main_window
        self.to_mainButton.clicked.connect(self.to_main)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.load_personal_info()
        self.calculate_semester_count()

    def load_personal_info(self):
        # personal_info.txt에서 데이터 읽기
        try:
            with open(resource_path("../data/personal_info.txt"), "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) == 3:
                    department = lines[0].strip()
                    major = lines[1].strip()
                    admission_year = lines[2].strip()
                    self.textBrowser1.setText(f"{department} {major} (입학 연도: {admission_year})")
        except Exception as e:
            print(f"Error loading personal_info.txt: {e}")

    def calculate_semester_count(self):
        try:
            conn = sqlite3.connect(resource_path("../data/transcript.db"))
            cursor = conn.cursor()

            query = """
                SELECT DISTINCT year, semester
                FROM transcript
                WHERE semester IN ('1', '2', '여름', '겨울')
            """
            cursor.execute(query)
            semesters = cursor.fetchall()

            valid_semesters = set()
            for year, semester in semesters:
                if semester == '여름':
                    valid_semesters.add((year, '1'))
                elif semester == '겨울':
                    valid_semesters.add((year, '2'))
                elif semester in ['1', '2']:
                    valid_semesters.add((year, semester))

            semester_count = len(valid_semesters)
            self.textBrowser2.setText(str(semester_count))

            conn.close()
        except sqlite3.Error as e:
            print(f"Error accessing the database: {e}")

    def to_main(self):
        self.main_window.last_geometry = self.geometry()
        self.hide()
        self.main_window.setGeometry(self.geometry())
        self.main_window.show()

    def closeEvent(self, event):
        self.main_window.close()
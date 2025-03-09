import os
import sqlite3
import math
from PyQt5 import uic
from PyQt5.QtGui import QTextOption
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QTextBrowser
from PyQt5.QtCore import Qt

class SemesterGpaPage(QDialog):
    def __init__(self, parent_geometry, main_window):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "../ui/semester_gpa_page.ui")
        uic.loadUi(ui_path, self)
        self.setGeometry(parent_geometry)
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        self.text_browsers = {}
        for i in range(1, 113):
            self.text_browsers[i] = self.findChild(QTextBrowser, f"textBrowser{i}")
        for browser in self.text_browsers.values():
            if browser:
                browser.setAlignment(Qt.AlignHCenter)
                doc = browser.document()
                doc.setDefaultTextOption(QTextOption(Qt.AlignCenter))
        
        self.transcript_data = self.fetch_transcript_data()
        self.semester_list, self.sem_type = self.calculate_column1(self.transcript_data)
        self.calculate_column2(self.transcript_data)
        self.calculate_column3(self.transcript_data)
        self.calculate_column4()
        self.calculate_column5()
        self.calculate_column6()
        self.calculate_column7()
        self.calculate_column8()
        self.calculate_column9()
        self.gpaConvertButton.clicked.connect(self.convert_gpa)
        self.copyButton.clicked.connect(self.copy_to_clipboard)
        self.to_mainButton.clicked.connect(self.return_to_main)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def fetch_transcript_data(self):
        transcript_db = os.path.join(os.path.dirname(__file__), "../data/transcript.db")
        conn = sqlite3.connect(transcript_db)
        cursor = conn.cursor()
        cursor.execute("SELECT year, semester, category, lecture_code, lecture_name, credit, rank, grade, is_pass_fail, is_fail, is_major, retaken, included_in_gpa FROM transcript")
        data = cursor.fetchall()
        conn.close()
        return [list(row) for row in data]
    
    def max_min_gpa(self, value):
        if value == 0 or value == 4.5:
            return value
        return round(value, 2)
    
    def convert_semester(self, semester):
        return "여름" if semester == "S" else "겨울" if semester == "W" else semester
    
    def floor_decimal(self, value, decimal_places):
        factor = 10 ** decimal_places
        return math.floor(value * factor) / factor

    def calculate_column1(self, list_transcript):  # 수강학기가 15개 이상인 경우를 나타내지 못함(업데이트 예정)
        semester_order = {'1': 1, '여름': 2, '2': 3, '겨울': 4}
        semester_list = sorted(
            {f"{row[0]}-{self.convert_semester(row[1])}" for row in list_transcript}, 
            key=lambda x: (int(x.split('-')[0]), semester_order.get(x.split('-')[1], 0))
        )
        sem_type = "A"
        """
        if len(semester_list) >= 15:
            semester_list = [s for s in semester_list if "여름" not in s and "겨울" not in s] + ["계절학기"]
            sem_type = "B"
            if len(semester_list) >= 15:
                semester_list = sorted({row[0] for row in list_transcript}) + ["계절학기"]
                sem_type = "C"
        else:
        """
        semester_list = [s.replace("여름", "S").replace("겨울", "W") for s in semester_list]
        for idx, sem in enumerate(semester_list[:14]):
            self.text_browsers[9 * idx + 1].setText(sem)
        return semester_list, sem_type
    
    def calculate_column2(self, transcript_data, return_values=False):
        results = []
        for idx, sem in enumerate(self.semester_list):
            year, semester = sem.split('-')
            semester = self.convert_semester(semester)
            
            filtered_courses = [row for row in transcript_data if row[0] == year and row[1] == semester and not row[8] == 1]
            total_weighted_grade = sum(float(course[5]) * float(course[7]) for course in filtered_courses)
            total_credits = sum(float(course[5]) for course in filtered_courses)
            
            gpa = self.floor_decimal(total_weighted_grade / total_credits, 2) if total_credits > 0 else 0
            self.text_browsers[9 * idx + 2].setText(
                f"{gpa:.2f}" if gpa not in [0, 4.5] else str(int(gpa) if gpa == 0 else gpa)
            )
            results.append((total_weighted_grade, total_credits))

        if return_values:
            return results

    def calculate_column3(self, transcript_data, return_values=False):
        results = []
        for idx, sem in enumerate(self.semester_list):
            year, semester = sem.split('-')
            filtered_courses = [row for row in transcript_data if row[0] == year and row[1] == semester and row[10] and not row[9]]
            
            total_weighted_grade = 0
            total_credits = 0
            
            for course in filtered_courses:
                credit, grade, is_pass_fail = float(course[5]), float(course[7]), course[8]
                
                if not is_pass_fail:
                    total_weighted_grade += credit * grade
                    total_credits += credit
            
            gpa = self.floor_decimal(total_weighted_grade / total_credits, 2) if total_credits > 0 else 0.00
            self.text_browsers[9 * idx + 3].setText(
                f"{gpa:.2f}" if gpa not in [0, 4.5] else str(int(gpa) if gpa == 0 else gpa)
            )
            results.append((total_weighted_grade, total_credits))
        
        if return_values:
            return results
        
    def calculate_column4(self):
        cumulative_numerator = 0
        cumulative_denominator = 0
        results = []
        
        for idx, sem in enumerate(self.semester_list):
            year, semester = sem.split('-')
            semester = self.convert_semester(semester)
            
            semester_data = [
                row for row in self.transcript_data 
                if row[0] == year and row[1] == semester and row[12] == 1 and row[9] == 0
            ]
            
            total_weighted_grade = sum(float(course[5]) * float(course[7]) for course in semester_data if course[8] == 0)
            total_credits = sum(float(course[5]) for course in semester_data if course[8] == 0)
            
            gpa = self.floor_decimal(total_weighted_grade / total_credits, 2) if total_credits > 0 else 0
            self.text_browsers[9 * idx + 4].setText(
                f"{gpa:.2f}" if gpa not in [0, 4.5] else str(int(gpa) if gpa == 0 else gpa)
            )
            
            results.append((total_weighted_grade, total_credits))
        
        return results

    def calculate_column5(self):
        cumulative_numerator = 0
        cumulative_denominator = 0
        for idx, sem in enumerate(self.semester_list):
            numerator, denominator = self.calculate_column2(self.transcript_data, return_values=True)[idx]
            cumulative_numerator += numerator
            cumulative_denominator += denominator
            gpa = self.floor_decimal(cumulative_numerator / cumulative_denominator, 2) if cumulative_denominator != 0 else 0
            self.text_browsers[9 * idx + 5].setText(
                f"{gpa:.2f}" if gpa not in [0, 4.5] else str(int(gpa) if gpa == 0 else gpa)
            )
        return cumulative_numerator, cumulative_denominator
    
    def calculate_column6(self):
        cumulative_numerator = 0
        cumulative_denominator = 0
        for idx, sem in enumerate(self.semester_list):
            numerator, denominator = self.calculate_column4()[idx]
            cumulative_numerator += numerator
            cumulative_denominator += denominator
            gpa = self.floor_decimal(cumulative_numerator / cumulative_denominator, 2) if cumulative_denominator != 0 else 0
            self.text_browsers[9 * idx + 6].setText(
                f"{gpa:.2f}" if gpa not in [0, 4.5] else str(int(gpa) if gpa == 0 else gpa)
            )
        return cumulative_numerator, cumulative_denominator

    def calculate_column7(self):
        cumulative_numerator = 0
        cumulative_denominator = 0
        for idx, sem in enumerate(self.semester_list):
            numerator, denominator = self.calculate_column3(self.transcript_data, return_values=True)[idx]
            cumulative_numerator += numerator
            cumulative_denominator += denominator
            gpa = self.floor_decimal(cumulative_numerator / cumulative_denominator, 2) if cumulative_denominator != 0 else 0
            self.text_browsers[9 * idx + 7].setText(
                f"{gpa:.2f}" if gpa not in [0, 4.5] else str(int(gpa) if gpa == 0 else gpa)
            )

    def calculate_column8(self):
        cumulative_numerator = 0
        cumulative_denominator = 0
        
        for idx, sem in enumerate(self.semester_list):
            year, semester = sem.split('-')
            semester = self.convert_semester(semester)
            
            semester_data = [
                row for row in self.transcript_data 
                if row[0] == year and row[1] == semester and row[12] == 1 and row[9] == 0 and row[10] == 1
            ]
            
            total_weighted_grade = sum(float(course[5]) * float(course[7]) for course in semester_data if course[8] == 0)
            total_credits = sum(float(course[5]) for course in semester_data if course[8] == 0)
            
            cumulative_numerator += total_weighted_grade
            cumulative_denominator += total_credits
            
            gpa = self.floor_decimal(cumulative_numerator / cumulative_denominator, 2) if cumulative_denominator != 0 else 0
            
            self.text_browsers[9 * idx + 8].setText(
                f"{gpa:.2f}" if gpa not in [0, 4.5] else str(int(gpa) if gpa == 0 else gpa)
            )

    def calculate_column9(self):
        for idx, semester in enumerate(self.semester_list):
            year, sem = semester.split('-')
            sem = self.convert_semester(sem)

            semester_data = [
                row for row in self.transcript_data
                if row[0] == year and row[1] == sem
            ]

            raw_credits = sum(float(course[5]) for course in semester_data if course[9] == 0)
            adjusted_credits = sum(float(course[5]) for course in semester_data if course[12] == 1)
            raw_credits = round(raw_credits, 1)
            adjusted_credits = round(adjusted_credits, 1)

            raw_credits_int = int(raw_credits) if abs(raw_credits - round(raw_credits)) < 1e-9 else raw_credits
            adjusted_credits_int = int(adjusted_credits) if abs(adjusted_credits - round(adjusted_credits)) < 1e-9 else adjusted_credits

            self.text_browsers[9 * idx + 9].setText(
                f"{raw_credits_int}-{adjusted_credits_int}"
            )

    def copy_to_clipboard(self):
        header = "학기\t당학기GPA(열람)\t당학기GPA(열람, 전공)\t당학기GPA(반영)\t누적GPA(열람)\t누적GPA(반영)\t누적GPA(열람, 전공)\t누적GPA(반영, 전공)\t취득학점(열람-취업)"
        table_data = [header]
        for row in range(14):
            row_values = [self.text_browsers[row * 9 + col + 1].toPlainText().strip() for col in range(9)]
            if any(row_values):
                table_data.append("\t".join(row_values))
            else:
                break
        QApplication.clipboard().setText("\n".join(table_data))
        QMessageBox.information(self, "복사 완료", "데이터가 클립보드에 복사되었습니다.")

    def convert_gpa(self):
        indices = [9 * k + col for k in range(14) for col in range(2, 9)]
        
        for idx in indices:
            text_browser = self.text_browsers.get(idx)
            if not text_browser:
                continue
            
            text = text_browser.toPlainText().strip()
            if not text or not text.replace('.', '', 1).isdigit():
                continue
            
            try:
                value = float(text)
                converted_value = self.floor_decimal((value - 55) / 10, 2) if value >= 55 else 55 + 10 * value
                
                if value >= 55:
                    if converted_value == 0:
                        formatted_value = "0"
                    elif converted_value == 4.5:
                        formatted_value = "4.5"
                    else:
                        formatted_value = f"{max(0, min(4.5, converted_value)):.2f}"
                else:
                    converted_value = min(100, converted_value)
                    if converted_value == 55:
                        formatted_value = "55"
                    elif converted_value == 100:
                        formatted_value = "100"
                    else:
                        formatted_value = f"{converted_value:.1f}"
                
                text_browser.setPlainText(formatted_value)
            except ValueError:
                continue
    
    def return_to_main(self):
        self.main_window.last_geometry = self.geometry()
        self.hide()
        self.main_window.setGeometry(self.geometry())
        self.main_window.show()

    def closeEvent(self, event):
        self.main_window.close()
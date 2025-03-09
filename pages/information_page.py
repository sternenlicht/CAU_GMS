import os
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QComboBox, QMessageBox
from PyQt5.QtCore import Qt
from collections import defaultdict

class InformationPage(QDialog):
    def __init__(self, parent_geometry, main_window):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "../ui/information_page.ui")
        uic.loadUi(ui_path, self)
        self.setGeometry(parent_geometry)
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        self.combo1: QComboBox = self.findChild(QComboBox, "comboBox1")
        self.combo2: QComboBox = self.findChild(QComboBox, "comboBox2")
        self.combo3: QComboBox = self.findChild(QComboBox, "comboBox3")
        self.combo1.currentIndexChanged.connect(self.update_combo2)
        self.saveButton.clicked.connect(self.save_text)
        self.to_mainButton.clicked.connect(self.to_main)
        self.options = {
            "인문대학": ["국어국문학과", "독일어문학전공", "러시아어문학전공", "역사학과", "영어영문학과", "일본어문학전공", "중국어문학전공", "철학과", "프랑스어문학전공"], 
            "사회과학대학": ["공공인재학부", "도시계획부동산학과", "디지털미디어콘텐츠전공", "문헌정보학과", "사회복지전공", "사회학과", "심리학과", "언론정보전공", "정치국제학과"], 
            "사범대학": ["교육학과", "영어교육과", "유아교육과", "체육교육과"], 
            "자연과학대학": ["물리학과", "생명과학과", "수학과", "화학과"], 
            "공과대학": ["건설환경플랜트공학전공", "건축공학전공", "건축학전공", "기계공학부", "도시시스템공학전공", "발전기계전공", "발전전기전공", "원자력전공", "첨단소재공학과", "화학공학과"], 
            "창의ICT공과대학": ["나노소재공학전공", "바이오메디컬공학전공", "전자전기공학부"], 
            "소프트웨어대학": ["소프트웨어학부", "AI학과"], 
            "경영경제대학": ["경영학전공", "경제학부", "광고홍보학과", "국제물류학과", "글로벌금융전공", "산업보안학과", "응용통계학과", "지식경영학부"], 
            "의과대학": ["의학부"], 
            "약학대학": ["약학전공", "제약학전공"], 
            "적십자간호대학": ["간호학과"], 
            "예술대학": ["공간연출전공", "연극전공", "영화전공", "게임콘텐츠애니메이션전공", "공예전공", "관현악전공", "무용전공", "문예창작전공", "사진전공", "산업디자인전공", "서양화전공", "성악전공", "시각디자인전공", "실내환경디자인전공", "실용음악전공", "연희예술전공", "음악예술전공", "작곡전공", "조소전공", "패션전공", "피아노전공", "한국화전공", "TV방송연예전공"], 
            "생명공학대학": ["동물생명공학전공", "시스템생명공학과", "식물생명공학전공", 
            "식품공학전공", "식품영양전공"], 
            "예술공학대학": ["예술공학부"], 
            "체육대학": ["골프전공", "생활레저스포츠전공", "스포츠산업전공"]
        }
        self.setAttribute(Qt.WA_DeleteOnClose)

    @staticmethod
    def show_error(message):
        QMessageBox.warning(None, "오류", message)

    @staticmethod
    def grade_to_numeric(grade):
        grade_map = {
            "A+": 4.5, "A": 4.0,
            "B+": 3.5, "B": 3.0,
            "C+": 2.5, "C": 2.0,
            "D+": 1.5, "D": 1.0,
            "F": 0.0,
            "P": 4.5 , "NP": 0.0
        }
        return grade_map.get(grade, 0.0)

    @staticmethod
    def load_equivalent_courses(filename):
        equivalent_courses = defaultdict(set)
        
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line[0] == "#":
                    continue

                course_codes = line.split()
                for code in course_codes:
                    equivalent_courses[code].update(course_codes)
        
        return equivalent_courses
    
    @staticmethod
    def _save_file(file_path, content):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def save_text(self):
        selected_college = self.combo1.currentText()
        selected_major = self.combo2.currentText()
        selected_year = self.combo3.currentText()

        if selected_college == "단과대학 선택":
            self.show_error("소속된 단과대학 및 학부(과)/전공이 선택되지 않았습니다.")
            return

        try:
            personal_info_path = os.path.join(os.path.dirname(__file__), "../data/personal_info.txt")
            content_personal_info = f"{selected_college}\n{selected_major}\n{selected_year}"
            self._save_file(personal_info_path, content_personal_info)
        except Exception as e:
            self.show_error(f"파일 저장 중 오류가 발생했습니다.: {e}")
            return

        user_input = self.plainTextEdit.toPlainText().strip("\n")
        if not user_input:
            self.show_error("입력된 성적 내역이 없습니다.")
            return

        if user_input.startswith("년도") or user_input.startswith("year"):
            lines = user_input.splitlines()[9:]
            user_input = "\n".join(lines)

        try:
            self._data_processing(user_input)
        except Exception as e:
            self.show_error(f"데이터베이스 처리 중 오류가 발생했습니다.: {e}")
            return

        QMessageBox.information(self, "저장 완료", "데이터가 성공적으로 저장되었습니다.")

    def detect_retake_courses(self, gpa_data, equivalent_courses):
        course_history = defaultdict(list)
        retake_courses = set()

        for entry in gpa_data:
            year, semester, category, full_code, title, credits, grade, gpa = entry
            course_code = full_code[:5]

            course_history[course_code].append(entry)
            if len(course_history[course_code]) > 1:
                retake_courses.add(course_code)

        for course_code in course_history:
            for equivalent in equivalent_courses.get(course_code, []):
                if equivalent in course_history and equivalent != course_code:
                    retake_courses.add(course_code)
                    retake_courses.add(equivalent)

        return retake_courses
    
    def determine_included_courses(self, processed_data, equivalent_courses):
        course_records = {}

        for row in processed_data:
            try:
                year, semester, category, lecture_code, lecture_name, credit, rank, grade = row
            except ValueError:
                continue
            
            base_code = lecture_code[:5]
            equivalent_set = equivalent_courses.get(base_code, {base_code})
            equivalent_set.add(base_code)

            group_key = sorted(equivalent_set)[0]  

            if group_key not in course_records:
                course_records[group_key] = []
            course_records[group_key].append((year, semester, grade, row))

        included_gpa = set()

        for group_key, records in course_records.items():
            records.sort(key=lambda x: (-InformationPage.grade_to_numeric(x[2]), x[0], x[1]))
            selected_course = records[0][3]
            included_gpa.add(selected_course)

        return included_gpa

    def _data_processing(self, user_input):
        transcript_path = os.path.join(os.path.dirname(__file__), "../data/transcript.db")
        os.makedirs(os.path.dirname(transcript_path), exist_ok=True)
        conn = sqlite3.connect(transcript_path)
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS transcript")
        cursor.execute(f"""
        CREATE TABLE transcript (
            year TEXT,
            semester TEXT,
            category TEXT,
            lecture_code TEXT,
            lecture_name TEXT,
            credit REAL,
            rank TEXT,
            grade TEXT,
            is_pass_fail INTEGER,
            is_fail INTEGER,
            is_major INTEGER,
            retaken INTEGER,
            included_in_gpa INTEGER
        )
        """)
        conn.commit()

        lines = user_input.splitlines()
        processed_data = []
        current_row = []

        for value in lines:
            if value.isdigit() and len(value) == 4:
                if current_row:
                    if len(current_row) == 9:
                        current_row.pop()
                    processed_data.append(tuple(current_row))
                current_row = [value]
            else:
                current_row.append(value)

        if current_row:
            if len(current_row) == 9:
                current_row.pop()
            processed_data.append(tuple(current_row))

        equivalent_courses_path = os.path.join(os.path.dirname(__file__), "../equivalent_courses.txt")
        equivalent_courses = InformationPage.load_equivalent_courses(equivalent_courses_path)

        retake_courses = self.detect_retake_courses(processed_data, equivalent_courses)

        updated_data = []
        for row in processed_data:
            year, semester, category, lecture_code, lecture_name, credit, rank, grade = row

            is_pass_fail = 1 if grade == "P/F" else 0
            is_fail = 1 if rank == "F" else 0
            is_major = 1 if category in ["전공기초", "전공필수", "전공"] else 0

            base_code = lecture_code[:5]
            retaken = 1 if base_code in retake_courses else 0
            included_in_gpa = 1 if retaken == 0 or not(row in self.determine_included_courses(processed_data, equivalent_courses)) else 0

            updated_data.append((
                year, semester, category, lecture_code, lecture_name, credit, rank, grade,
                is_pass_fail, is_fail, is_major, retaken, included_in_gpa
            ))

        cursor.executemany(f"""
        INSERT INTO transcript (
            year, semester, category, lecture_code, lecture_name, credit, rank, grade,
            is_pass_fail, is_fail, is_major, retaken, included_in_gpa
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, updated_data)

        conn.commit()
        conn.close()

    def to_main(self):
        self.main_window.last_geometry = self.geometry()
        self.hide()
        self.main_window.setGeometry(self.geometry())
        self.main_window.show()

    def update_combo2(self):
        selected_major = self.combo1.currentText()
        self.combo2.clear()
        if selected_major in self.options:
            self.combo2.addItems(self.options[selected_major])
        else:
            self.combo2.addItem("학부(과)/전공 선택")

    def closeEvent(self, event):
        self.main_window.close()
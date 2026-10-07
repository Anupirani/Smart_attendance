import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import re
from datetime import datetime
from pathlib import Path


# ============================================================
# SMART ATTENDANCE MANAGEMENT SYSTEM
# Single-file Python application
#
# Features:
#   - SQLite database (created automatically)
#   - Student registration
#   - Bulk student import from CSV/TXT
#   - Bulk attendance: paste many IDs at once
#   - Accepts newline, comma, semicolon, space, or tab separated IDs
#   - Duplicate attendance prevention per student per day
#   - Dashboard with present/absent/percentage
#   - Search students and attendance
#   - Today's attendance table
#   - Export attendance to CSV
#   - No third-party packages required
# ============================================================


APP_TITLE = "Smart Attendance Management System"
DB_FILE = Path("attendance.db")


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL DEFAULT '',
            email TEXT NOT NULL DEFAULT ''
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Present',
            UNIQUE(student_id, date),
            FOREIGN KEY(student_id) REFERENCES students(id)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def today():
    return datetime.now().strftime("%Y-%m-%d")


def now_time():
    return datetime.now().strftime("%H:%M:%S")


# ============================================================
# APPLICATION
# ============================================================

class SmartAttendanceApp:

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1250x860")
        self.root.minsize(1050, 760)

        initialize_database()
        self.setup_style()
        self.create_ui()

        self.refresh_all()

    # --------------------------------------------------------
    # STYLE
    # --------------------------------------------------------

    def setup_style(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 23, "bold")
        )

        style.configure(
            "Heading.TLabel",
            font=("Segoe UI", 16, "bold")
        )

        style.configure(
            "Action.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=(12, 8)
        )

        style.configure(
            "Treeview",
            rowheight=30,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold")
        )

    # --------------------------------------------------------
    # MAIN UI
    # --------------------------------------------------------

    def create_ui(self):
        header = tk.Frame(self.root, bg="#17365D", height=75)
        header.pack(fill="x")

        tk.Label(
            header,
            text="SMART ATTENDANCE SYSTEM",
            bg="#17365D",
            fg="white",
            font=("Segoe UI", 23, "bold")
        ).pack(side="left", padx=25, pady=18)

        self.clock_label = tk.Label(
            header,
            bg="#17365D",
            fg="white",
            font=("Segoe UI", 10)
        )
        self.clock_label.pack(side="right", padx=25)

        self.update_clock()

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=12, pady=12)

        self.dashboard_tab = ttk.Frame(notebook)
        self.attendance_tab = ttk.Frame(notebook)
        self.students_tab = ttk.Frame(notebook)
        self.records_tab = ttk.Frame(notebook)

        notebook.add(self.dashboard_tab, text="  Dashboard  ")
        notebook.add(self.attendance_tab, text="  Mark Attendance  ")
        notebook.add(self.students_tab, text="  Students  ")
        notebook.add(self.records_tab, text="  Records  ")

        self.create_dashboard()
        self.create_attendance_tab()
        self.create_students_tab()
        self.create_records_tab()

    def update_clock(self):
        self.clock_label.config(
            text=datetime.now().strftime("%d %B %Y   %I:%M:%S %p")
        )
        self.root.after(1000, self.update_clock)

    # ========================================================
    # DASHBOARD
    # ========================================================

    def create_dashboard(self):
        ttk.Label(
            self.dashboard_tab,
            text="Attendance Dashboard",
            style="Heading.TLabel"
        ).pack(anchor="w", padx=25, pady=(20, 10))

        stats = tk.Frame(self.dashboard_tab)
        stats.pack(fill="x", padx=20, pady=5)

        self.total_label = self.create_stat_card(
            stats, "TOTAL STUDENTS", "0"
        )
        self.present_label = self.create_stat_card(
            stats, "PRESENT TODAY", "0"
        )
        self.absent_label = self.create_stat_card(
            stats, "ABSENT TODAY", "0"
        )
        self.percent_label = self.create_stat_card(
            stats, "ATTENDANCE %", "0%"
        )

        ttk.Label(
            self.dashboard_tab,
            text="Today's Attendance",
            style="Heading.TLabel"
        ).pack(anchor="w", padx=25, pady=(20, 5))

        frame = ttk.Frame(self.dashboard_tab)
        frame.pack(fill="both", expand=True, padx=25, pady=10)

        columns = ("ID", "Name", "Class", "Date", "Time", "Status")

        self.dashboard_tree = ttk.Treeview(
            frame, columns=columns, show="headings"
        )

        widths = {
            "ID": 130,
            "Name": 220,
            "Class": 140,
            "Date": 130,
            "Time": 120,
            "Status": 120
        }

        for col in columns:
            self.dashboard_tree.heading(col, text=col)
            self.dashboard_tree.column(
                col, width=widths[col], anchor="center"
            )

        scroll = ttk.Scrollbar(
            frame, orient="vertical",
            command=self.dashboard_tree.yview
        )
        self.dashboard_tree.configure(yscrollcommand=scroll.set)

        self.dashboard_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def create_stat_card(self, parent, title, value):
        card = tk.Frame(
            parent,
            bd=1,
            relief="solid",
            padx=18,
            pady=12
        )
        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        tk.Label(
            card,
            text=title,
            font=("Segoe UI", 10, "bold")
        ).pack()

        value_label = tk.Label(
            card,
            text=value,
            font=("Segoe UI", 25, "bold")
        )
        value_label.pack(pady=5)

        return value_label

    # ========================================================
    # ATTENDANCE TAB
    # ========================================================

    def create_attendance_tab(self):
        ttk.Label(
            self.attendance_tab,
            text="Mark Attendance",
            style="Heading.TLabel"
        ).pack(anchor="w", padx=25, pady=(20, 5))

        ttk.Label(
            self.attendance_tab,
            text=(
                "Paste or type multiple Student IDs below. "
                "One ID per line is recommended. "
                "You can also paste directly from Excel."
            ),
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=25, pady=5)

        input_frame = ttk.LabelFrame(
            self.attendance_tab,
            text="Student IDs - Bulk Attendance"
        )
        input_frame.pack(
            fill="x",
            expand=False,
            padx=25,
            pady=10
        )

        self.bulk_text = tk.Text(
            input_frame,
            font=("Consolas", 14),
            wrap="none",
            height=12
        )
        self.bulk_text.pack(
            side="left",
            fill="both",
            expand=True,
            padx=12,
            pady=12
        )

        yscroll = ttk.Scrollbar(
            input_frame,
            orient="vertical",
            command=self.bulk_text.yview
        )
        yscroll.pack(side="right", fill="y", pady=12)
        self.bulk_text.configure(yscrollcommand=yscroll.set)

        button_frame = ttk.Frame(self.attendance_tab)
        button_frame.pack(fill="x", padx=25, pady=5)

        ttk.Button(
            button_frame,
            text="✓  MARK ALL PRESENT",
            style="Action.TButton",
            command=self.mark_bulk_attendance
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="CLEAR",
            command=self.clear_attendance_input
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="LOAD ALL STUDENTS",
            command=self.load_all_ids_into_attendance
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="LOAD ABSENT STUDENTS",
            command=self.load_absent_ids_into_attendance
        ).pack(side="left", padx=5)

        ttk.Label(
            self.attendance_tab,
            text=(
                "Accepted formats: S101↵S102↵S103   |   "
                "S101, S102, S103   |   S101 S102 S103   |   "
                "Excel/Tab separated"
            ),
            font=("Segoe UI", 9)
        ).pack(anchor="w", padx=30, pady=5)

    def clear_attendance_input(self):
        self.bulk_text.delete("1.0", tk.END)

    def load_all_ids_into_attendance(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM students ORDER BY id")
        ids = [row[0] for row in cur.fetchall()]
        conn.close()

        self.bulk_text.delete("1.0", tk.END)
        self.bulk_text.insert(tk.END, "\n".join(ids))

    def load_absent_ids_into_attendance(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT s.id
            FROM students s
            LEFT JOIN attendance a
              ON s.id = a.student_id
             AND a.date = ?
            WHERE a.student_id IS NULL
            ORDER BY s.id
        """, (today(),))

        ids = [row[0] for row in cur.fetchall()]
        conn.close()

        self.bulk_text.delete("1.0", tk.END)
        self.bulk_text.insert(tk.END, "\n".join(ids))

    # ========================================================
    # ATTENDANCE PROCESSING
    # ========================================================

    @staticmethod
    def parse_student_ids(raw_text):
        """
        Accept:
          S101
          S101, S102
          S101 S102
          S101;S102
          Excel tab-separated values
          Any mixture of the above.
        """
        ids = re.split(r"[\s,;]+", raw_text.strip())

        cleaned = []
        seen = set()

        for student_id in ids:
            student_id = student_id.strip()

            if student_id and student_id not in seen:
                cleaned.append(student_id)
                seen.add(student_id)

        return cleaned

    def mark_student(self, student_id):
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "SELECT id FROM students WHERE id = ?",
                (student_id,)
            )

            if cur.fetchone() is None:
                return "not_found"

            cur.execute("""
                SELECT attendance_id
                FROM attendance
                WHERE student_id = ?
                  AND date = ?
            """, (student_id, today()))

            if cur.fetchone() is not None:
                return "duplicate"

            cur.execute("""
                INSERT INTO attendance
                    (student_id, date, time, status)
                VALUES (?, ?, ?, 'Present')
            """, (student_id, today(), now_time()))

            conn.commit()
            return "marked"

        except sqlite3.IntegrityError:
            conn.rollback()
            return "duplicate"

        finally:
            conn.close()

    def mark_bulk_attendance(self):
        raw_text = self.bulk_text.get("1.0", tk.END).strip()

        if not raw_text:
            messagebox.showwarning(
                "No Student IDs",
                "Please enter or paste at least one Student ID."
            )
            return

        student_ids = self.parse_student_ids(raw_text)

        if not student_ids:
            messagebox.showwarning(
                "No Valid IDs",
                "No valid Student IDs were found."
            )
            return

        marked = []
        duplicate = []
        not_found = []

        for student_id in student_ids:
            result = self.mark_student(student_id)

            if result == "marked":
                marked.append(student_id)
            elif result == "duplicate":
                duplicate.append(student_id)
            elif result == "not_found":
                not_found.append(student_id)

        self.show_bulk_result(
            student_ids,
            marked,
            duplicate,
            not_found
        )

        self.clear_attendance_input()
        self.refresh_all()

    def show_bulk_result(
        self,
        all_ids,
        marked,
        duplicate,
        not_found
    ):
        win = tk.Toplevel(self.root)
        win.title("Attendance Result")
        win.geometry("650x600")
        win.transient(self.root)
        win.grab_set()

        ttk.Label(
            win,
            text="Attendance Processing Complete",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=18)

        summary = (
            f"Total IDs processed: {len(all_ids)}\n"
            f"Successfully marked: {len(marked)}\n"
            f"Already marked today: {len(duplicate)}\n"
            f"Not registered: {len(not_found)}"
        )

        ttk.Label(
            win,
            text=summary,
            font=("Segoe UI", 12)
        ).pack(pady=8)

        text = tk.Text(
            win,
            width=70,
            height=22,
            font=("Consolas", 10)
        )
        text.pack(fill="both", expand=True, padx=20, pady=10)

        if marked:
            text.insert(tk.END, "SUCCESSFULLY MARKED\n")
            text.insert(tk.END, "=" * 35 + "\n")
            for sid in marked:
                text.insert(tk.END, f"✓ {sid}\n")
            text.insert(tk.END, "\n")

        if duplicate:
            text.insert(tk.END, "ALREADY MARKED TODAY\n")
            text.insert(tk.END, "=" * 35 + "\n")
            for sid in duplicate:
                text.insert(tk.END, f"⚠ {sid}\n")
            text.insert(tk.END, "\n")

        if not_found:
            text.insert(tk.END, "NOT REGISTERED\n")
            text.insert(tk.END, "=" * 35 + "\n")
            for sid in not_found:
                text.insert(tk.END, f"✗ {sid}\n")
            text.insert(tk.END, "\n")

        text.config(state="disabled")

        ttk.Button(
            win,
            text="CLOSE",
            command=win.destroy
        ).pack(pady=12)

    # ========================================================
    # STUDENTS TAB
    # ========================================================

    def create_students_tab(self):
        ttk.Label(
            self.students_tab,
            text="Student Management",
            style="Heading.TLabel"
        ).pack(anchor="w", padx=25, pady=(20, 5))

        form = ttk.LabelFrame(
            self.students_tab,
            text="Register One Student"
        )
        form.pack(fill="x", padx=25, pady=10)

        ttk.Label(form, text="Student ID").grid(
            row=0, column=0, padx=8, pady=12
        )

        self.student_id_entry = ttk.Entry(form, width=18)
        self.student_id_entry.grid(
            row=0, column=1, padx=8
        )

        ttk.Label(form, text="Name").grid(
            row=0, column=2, padx=8
        )

        self.student_name_entry = ttk.Entry(form, width=25)
        self.student_name_entry.grid(
            row=0, column=3, padx=8
        )

        ttk.Label(form, text="Class").grid(
            row=0, column=4, padx=8
        )

        self.student_class_entry = ttk.Entry(form, width=18)
        self.student_class_entry.grid(
            row=0, column=5, padx=8
        )

        ttk.Button(
            form,
            text="ADD STUDENT",
            style="Action.TButton",
            command=self.add_student
        ).grid(row=0, column=6, padx=12)

        # Bulk import section
        bulk = ttk.LabelFrame(
            self.students_tab,
            text="Bulk Student Import"
        )
        bulk.pack(fill="x", padx=25, pady=8)

        ttk.Label(
            bulk,
            text=(
                "Import CSV with columns: StudentID, Name, Class. "
                "Email is optional."
            )
        ).pack(side="left", padx=12, pady=12)

        ttk.Button(
            bulk,
            text="IMPORT CSV",
            command=self.import_students_csv
        ).pack(side="right", padx=12)

        # Search
        search_frame = ttk.Frame(self.students_tab)
        search_frame.pack(fill="x", padx=25, pady=8)

        ttk.Label(
            search_frame,
            text="Search:"
        ).pack(side="left")

        self.student_search = ttk.Entry(
            search_frame,
            width=35
        )
        self.student_search.pack(side="left", padx=8)

        ttk.Button(
            search_frame,
            text="SEARCH",
            command=self.search_students
        ).pack(side="left")

        ttk.Button(
            search_frame,
            text="SHOW ALL",
            command=self.load_students
        ).pack(side="left", padx=5)

        # Student table
        frame = ttk.Frame(self.students_tab)
        frame.pack(fill="both", expand=True, padx=25, pady=8)

        columns = ("ID", "Name", "Class", "Email")

        self.student_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        widths = {
            "ID": 150,
            "Name": 260,
            "Class": 180,
            "Email": 300
        }

        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(
                col, width=widths[col]
            )

        scroll = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.student_tree.yview
        )
        self.student_tree.configure(
            yscrollcommand=scroll.set
        )

        self.student_tree.pack(
            side="left",
            fill="both",
            expand=True
        )
        scroll.pack(side="right", fill="y")

    def add_student(self):
        student_id = self.student_id_entry.get().strip()
        name = self.student_name_entry.get().strip()
        class_name = self.student_class_entry.get().strip()

        if not student_id or not name:
            messagebox.showwarning(
                "Missing Information",
                "Student ID and Name are required."
            )
            return

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO students
                    (id, name, class_name)
                VALUES (?, ?, ?)
            """, (student_id, name, class_name))

            conn.commit()

            messagebox.showinfo(
                "Success",
                f"{student_id} registered successfully."
            )

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Duplicate Student",
                f"Student ID {student_id} already exists."
            )

        finally:
            conn.close()

        self.student_id_entry.delete(0, tk.END)
        self.student_name_entry.delete(0, tk.END)
        self.student_class_entry.delete(0, tk.END)

        self.refresh_all()

    def import_students_csv(self):
        filename = filedialog.askopenfilename(
            title="Select Student CSV",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if not filename:
            return

        inserted = 0
        updated = 0
        skipped = 0

        conn = get_connection()
        cur = conn.cursor()

        try:
            with open(
                filename,
                "r",
                newline="",
                encoding="utf-8-sig"
            ) as file:
                reader = csv.DictReader(file)

                if not reader.fieldnames:
                    raise ValueError("The file has no header row.")

                normalized = {
                    h.strip().lower(): h
                    for h in reader.fieldnames
                    if h
                }

                id_key = None
                name_key = None
                class_key = None
                email_key = None

                for candidate in (
                    "studentid",
                    "student_id",
                    "id"
                ):
                    if candidate in normalized:
                        id_key = normalized[candidate]
                        break

                for candidate in ("name", "studentname", "student_name"):
                    if candidate in normalized:
                        name_key = normalized[candidate]
                        break

                for candidate in ("class", "class_name", "classname"):
                    if candidate in normalized:
                        class_key = normalized[candidate]
                        break

                for candidate in ("email", "email_id"):
                    if candidate in normalized:
                        email_key = normalized[candidate]
                        break

                if not id_key or not name_key:
                    raise ValueError(
                        "CSV must contain StudentID/ID and Name columns."
                    )

                for row in reader:
                    sid = (row.get(id_key) or "").strip()
                    name = (row.get(name_key) or "").strip()
                    class_name = (
                        (row.get(class_key) or "").strip()
                        if class_key else ""
                    )
                    email = (
                        (row.get(email_key) or "").strip()
                        if email_key else ""
                    )

                    if not sid or not name:
                        skipped += 1
                        continue

                    cur.execute(
                        "SELECT id FROM students WHERE id = ?",
                        (sid,)
                    )

                    exists = cur.fetchone()

                    if exists:
                        cur.execute("""
                            UPDATE students
                            SET name = ?,
                                class_name = ?,
                                email = ?
                            WHERE id = ?
                        """, (name, class_name, email, sid))
                        updated += 1
                    else:
                        cur.execute("""
                            INSERT INTO students
                                (id, name, class_name, email)
                            VALUES (?, ?, ?, ?)
                        """, (sid, name, class_name, email))
                        inserted += 1

            conn.commit()

        except Exception as exc:
            conn.rollback()
            messagebox.showerror(
                "Import Error",
                f"Could not import the file.\n\n{exc}"
            )
            conn.close()
            return

        conn.close()

        messagebox.showinfo(
            "Import Complete",
            f"New students: {inserted}\n"
            f"Updated students: {updated}\n"
            f"Skipped rows: {skipped}"
        )

        self.refresh_all()

    def load_students(self):
        if not hasattr(self, "student_tree"):
            return

        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, class_name, email
            FROM students
            ORDER BY id
        """)

        rows = cur.fetchall()
        conn.close()

        for row in rows:
            self.student_tree.insert(
                "",
                tk.END,
                values=row
            )

    def search_students(self):
        keyword = self.student_search.get().strip()

        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, class_name, email
            FROM students
            WHERE id LIKE ?
               OR name LIKE ?
               OR class_name LIKE ?
               OR email LIKE ?
            ORDER BY id
        """, (
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        ))

        rows = cur.fetchall()
        conn.close()

        for row in rows:
            self.student_tree.insert(
                "",
                tk.END,
                values=row
            )

    # ========================================================
    # RECORDS TAB
    # ========================================================

    def create_records_tab(self):
        ttk.Label(
            self.records_tab,
            text="Attendance Records",
            style="Heading.TLabel"
        ).pack(anchor="w", padx=25, pady=(20, 5))

        filter_frame = ttk.Frame(self.records_tab)
        filter_frame.pack(fill="x", padx=25, pady=8)

        ttk.Label(
            filter_frame,
            text="Student ID:"
        ).pack(side="left")

        self.record_search = ttk.Entry(
            filter_frame,
            width=25
        )
        self.record_search.pack(side="left", padx=8)

        ttk.Button(
            filter_frame,
            text="SEARCH",
            command=self.search_records
        ).pack(side="left")

        ttk.Button(
            filter_frame,
            text="SHOW ALL",
            command=self.load_all_records
        ).pack(side="left", padx=5)

        ttk.Button(
            filter_frame,
            text="TODAY",
            command=self.load_today_records
        ).pack(side="left", padx=5)

        ttk.Button(
            filter_frame,
            text="EXPORT CSV",
            command=self.export_csv
        ).pack(side="right")

        frame = ttk.Frame(self.records_tab)
        frame.pack(fill="both", expand=True, padx=25, pady=8)

        columns = (
            "ID", "Name", "Class",
            "Date", "Time", "Status"
        )

        self.record_tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        widths = {
            "ID": 140,
            "Name": 240,
            "Class": 150,
            "Date": 130,
            "Time": 120,
            "Status": 120
        }

        for col in columns:
            self.record_tree.heading(col, text=col)
            self.record_tree.column(
                col,
                width=widths[col],
                anchor="center"
            )

        scroll = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.record_tree.yview
        )

        self.record_tree.configure(
            yscrollcommand=scroll.set
        )

        self.record_tree.pack(
            side="left",
            fill="both",
            expand=True
        )
        scroll.pack(side="right", fill="y")

    def get_record_rows(self, where="", params=()):
        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT
                a.student_id,
                COALESCE(s.name, ''),
                COALESCE(s.class_name, ''),
                a.date,
                a.time,
                a.status
            FROM attendance a
            LEFT JOIN students s
                ON a.student_id = s.id
        """

        if where:
            query += " WHERE " + where

        query += """
            ORDER BY a.date DESC, a.time DESC
        """

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        return rows

    def display_record_rows(self, rows):
        for item in self.record_tree.get_children():
            self.record_tree.delete(item)

        for row in rows:
            self.record_tree.insert(
                "",
                tk.END,
                values=row
            )

    def load_all_records(self):
        rows = self.get_record_rows()
        self.display_record_rows(rows)

    def load_today_records(self):
        rows = self.get_record_rows(
            "a.date = ?",
            (today(),)
        )
        self.display_record_rows(rows)

    def search_records(self):
        keyword = self.record_search.get().strip()

        rows = self.get_record_rows(
            "a.student_id LIKE ?",
            (f"%{keyword}%",)
        )

        self.display_record_rows(rows)

    def export_csv(self):
        filename = filedialog.asksaveasfilename(
            title="Export Attendance",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not filename:
            return

        rows = self.get_record_rows()

        try:
            with open(
                filename,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:
                writer = csv.writer(file)

                writer.writerow([
                    "Student ID",
                    "Name",
                    "Class",
                    "Date",
                    "Time",
                    "Status"
                ])

                writer.writerows(rows)

            messagebox.showinfo(
                "Export Complete",
                f"Attendance exported to:\n{filename}"
            )

        except Exception as exc:
            messagebox.showerror(
                "Export Error",
                str(exc)
            )

    # ========================================================
    # DASHBOARD DATA
    # ========================================================

    def refresh_dashboard(self):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM students")
        total = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE date = ?
        """, (today(),))
        present = cur.fetchone()[0]

        absent = max(total - present, 0)

        percentage = (
            (present / total) * 100
            if total else 0
        )

        cur.execute("""
            SELECT
                a.student_id,
                COALESCE(s.name, ''),
                COALESCE(s.class_name, ''),
                a.date,
                a.time,
                a.status
            FROM attendance a
            LEFT JOIN students s
                ON a.student_id = s.id
            WHERE a.date = ?
            ORDER BY a.time DESC
        """, (today(),))

        rows = cur.fetchall()
        conn.close()

        self.total_label.config(text=str(total))
        self.present_label.config(text=str(present))
        self.absent_label.config(text=str(absent))
        self.percent_label.config(text=f"{percentage:.1f}%")

        for item in self.dashboard_tree.get_children():
            self.dashboard_tree.delete(item)

        for row in rows:
            self.dashboard_tree.insert(
                "",
                tk.END,
                values=row
            )

    # ========================================================
    # REFRESH EVERYTHING
    # ========================================================

    def refresh_all(self):
        self.refresh_dashboard()
        self.load_students()
        self.load_all_records()


# ============================================================
# START PROGRAM
# ============================================================

def main():
    initialize_database()

    root = tk.Tk()
    SmartAttendanceApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


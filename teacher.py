import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from db_config import connect_db
from tkcalendar import DateEntry
import datetime
from face_capture_tab import show_face_capture_tab


def run_teacher(root_login, user_id):
    root = tk.Toplevel()
    root.title("Giáo viên - Quản lý lớp học")
    root.geometry("900x600")
    root.configure(bg="#f5f5f5")

    # Lấy teacher_id từ user_id
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT teacher_id FROM teachers WHERE user_id = :1", (user_id,))
        result = cursor.fetchone()
        if result:
            teacher_id = result[0]
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy thông tin giáo viên.")
            return
    except Exception as e:
        messagebox.showerror("Lỗi kết nối", str(e))
        return
    finally:
        cursor.close()
        conn.close()

    # ========== SIDEBAR ==========
    sidebar = tk.Frame(root, bg="#2c3e50", width=200)
    sidebar.pack(side="left", fill="y")

    main_frame = tk.Frame(root, bg="#ecf0f1")
    main_frame.pack(side="right", fill="both", expand=True)

    def switch_tab(tab_name):
        for widget in main_frame.winfo_children():
            widget.destroy()
        if tab_name == "classes":
            show_class_tab()
        elif tab_name == "students":
            show_students_tab()
        elif tab_name == "history":
            show_attendance_history_tab()
        elif tab_name == "face_capture":
            show_face_capture_tab(main_frame, teacher_id)

    buttons = [
        ("Quản lý lớp học", "classes"),
        ("Danh sách sinh viên", "students"),
        ("Lịch sử điểm danh", "history"),
        ("Lấy khuôn mặt", "face_capture"),
        ("Tài khoản", "account")
    ]

    for text, value in buttons:
        btn = tk.Button(sidebar, text=text, font=("Helvetica", 11), fg="white", bg="#34495e", bd=0,
                        activebackground="#16a085", anchor="w", padx=20,
                        command=(lambda v=value: show_account_tab() if v == "account" else switch_tab(v)))
        btn.pack(fill="x", pady=5)

    def show_account_tab():
        for widget in main_frame.winfo_children():
            widget.destroy()

        tk.Label(main_frame, text="Thông tin tài khoản", font=("Helvetica", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        info_frame = tk.Frame(main_frame, bg="#ecf0f1")
        info_frame.pack(pady=10)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.name, u.username 
                FROM teachers t 
                JOIN users u ON t.user_id = u.user_id 
                WHERE t.teacher_id = :1
            """, (teacher_id,))
            row = cursor.fetchone()
            if row:
                name, username = row
                tk.Label(info_frame, text=f"Họ tên: {name}", font=("Helvetica", 12), bg="#ecf0f1").pack(anchor="w")
                tk.Label(info_frame, text=f"Tên đăng nhập: {username}", font=("Helvetica", 12), bg="#ecf0f1").pack(
                    anchor="w")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        finally:
            cursor.close()
            conn.close()

        tk.Label(main_frame, text="Đổi mật khẩu", font=("Helvetica", 13, "bold"), bg="#ecf0f1").pack(pady=10)

        form = tk.Frame(main_frame, bg="#ecf0f1")
        form.pack()

        tk.Label(form, text="Mật khẩu cũ:", bg="#ecf0f1").grid(row=0, column=0, sticky="e")
        old_pass = tk.Entry(form, show="*")
        old_pass.grid(row=0, column=1)

        def toggle_old():
            old_pass.config(show="" if show_old.get() else "*")

        show_old = tk.BooleanVar()
        tk.Checkbutton(form, text="👁", variable=show_old, command=toggle_old, bg="#ecf0f1").grid(row=0, column=2)

        tk.Label(form, text="Mật khẩu mới:", bg="#ecf0f1").grid(row=1, column=0, sticky="e")
        new_pass = tk.Entry(form, show="*")
        new_pass.grid(row=1, column=1)

        def toggle_new():
            new_pass.config(show="" if show_new.get() else "*")

        show_new = tk.BooleanVar()
        tk.Checkbutton(form, text="👁", variable=show_new, command=toggle_new, bg="#ecf0f1").grid(row=1, column=2)

        def change_password():
            old = old_pass.get()
            new = new_pass.get()
            if not old or not new:
                messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ mật khẩu.")
                return
            try:
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE user_id = :1", (user_id,))
                current = cursor.fetchone()
                if current and current[0] == old:
                    cursor.execute("UPDATE users SET password = :1 WHERE user_id = :2", (new, user_id))
                    conn.commit()
                    messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!")
                    old_pass.delete(0, tk.END)
                    new_pass.delete(0, tk.END)
                else:
                    messagebox.showerror("Sai mật khẩu", "Mật khẩu cũ không đúng.")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
            finally:
                cursor.close()
                conn.close()

        tk.Button(main_frame, text="Đổi mật khẩu", command=change_password).pack(pady=10)
        tk.Button(main_frame, text="Đăng xuất 🚪", bg="#e74c3c", fg="white", command=logout).pack(pady=5)

    def show_class_tab():
        tk.Label(main_frame, text="Danh sách lớp bạn phụ trách", font=("Helvetica", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        tree = ttk.Treeview(main_frame, columns=("ID", "Tên lớp"), show="headings")
        tree.heading("ID", text="Mã lớp")
        tree.heading("Tên lớp", text="Tên lớp")
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT class_id, class_name FROM classes WHERE teacher_id = :1", (teacher_id,))
            for row in cursor:
                tree.insert("", "end", values=row)
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def show_students_tab():
        tk.Label(main_frame, text="Chọn lớp học để xem danh sách sinh viên", font=("Helvetica", 13, "bold"), bg="#ecf0f1").pack(pady=10)

        combo = ttk.Combobox(main_frame)
        combo.pack(pady=5)

        table = ttk.Treeview(main_frame, columns=("ID", "Tên"), show="headings")
        table.heading("ID", text="Mã sinh viên")
        table.heading("Tên", text="Tên sinh viên")
        table.pack(fill="both", expand=True, padx=20, pady=10)

        def load_students(event=None):
            table.delete(*table.get_children())
            if not combo.get(): return
            class_id = combo.get().split(" - ")[0]
            try:
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("SELECT student_id, name FROM students WHERE class_id = :1", (class_id,))
                for row in cursor:
                    table.insert("", "end", values=row)
                cursor.close()
                conn.close()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

        ttk.Button(main_frame, text="🔄 Làm mới", command=load_students).pack(pady=5)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT class_id, class_name FROM classes WHERE teacher_id = :1", (teacher_id,))
            classes = [f"{row[0]} - {row[1]}" for row in cursor]
            combo['values'] = classes
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

        combo.bind("<<ComboboxSelected>>", load_students)

    import os

    def show_attendance_history_tab():
        import io
        tk.Label(main_frame, text="Lịch sử điểm danh", font=("Helvetica", 13, "bold"), bg="#ecf0f1").pack(pady=10)

        top_frame = tk.Frame(main_frame, bg="#ecf0f1")
        top_frame.pack()

        class_combobox = ttk.Combobox(top_frame)
        class_combobox.pack(side="left", padx=5)

        date_entry = DateEntry(top_frame, date_pattern="yyyy-mm-dd")
        date_entry.set_date(datetime.date.today())
        date_entry.pack(side="left", padx=5)

        status_combobox = ttk.Combobox(top_frame, values=["Tất cả", "Có mặt", "Vắng", "Muộn"])
        status_combobox.set("Tất cả")
        status_combobox.pack(side="left", padx=5)

        tree = ttk.Treeview(main_frame, columns=("Tên", "Thời gian", "Trạng thái"), show="headings", height=12)
        tree.heading("Tên", text="Tên sinh viên")
        tree.heading("Thời gian", text="Thời gian điểm danh")
        tree.heading("Trạng thái", text="Trạng thái")
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        def load_history():
            tree.delete(*tree.get_children())
            date_str = date_entry.get_date().strftime('%Y-%m-%d')
            status_filter = status_combobox.get()
            class_info = class_combobox.get()

            if not class_info:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn lớp học.")
                return

            class_id = class_info.split(" - ")[0]

            try:
                conn = connect_db()
                cursor = conn.cursor()
                sql = """
                    SELECT 
                        s.name,
                        a.checkin_time,
                        NVL(a.status, 'Vắng') AS status,
                        a.attendance_id
                    FROM students s
                    LEFT JOIN attendance a
                        ON s.student_id = a.student_id
                        AND TRUNC(a.checkin_time) = TO_DATE(:date_str, 'YYYY-MM-DD')
                    WHERE s.class_id = :class_id
                    ORDER BY a.checkin_time NULLS LAST
                """
                cursor.execute(sql, {'class_id': class_id, 'date_str': date_str})
                for row in cursor:
                    name, checkin_time, status, attendance_id = row
                    if status_filter == "Tất cả" or status == status_filter:
                        tag = str(attendance_id) if attendance_id else "None"
                        tree.insert("", "end", values=(name, checkin_time if checkin_time else "", status), tags=(tag,))
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
            finally:
                cursor.close()
                conn.close()

        def view_photo():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Chọn dòng", "Vui lòng chọn một dòng để xem chi tiết.")
                return

            attendance_id = tree.item(selected[0])['tags'][0]
            if attendance_id == "None":
                messagebox.showinfo("Thông báo", "Sinh viên này chưa điểm danh ngày hôm đó.")
                return

            try:
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("SELECT photo_captured FROM attendance WHERE attendance_id = :id", {'id': attendance_id})
                row = cursor.fetchone()
                if row and row[0]:
                    image_data = row[0].read()
                    image = Image.open(io.BytesIO(image_data))
                    image = image.resize((300, 300))
                    top = tk.Toplevel()
                    top.title("Ảnh điểm danh")
                    photo = ImageTk.PhotoImage(image)
                    label = tk.Label(top, image=photo)
                    label.image = photo
                    label.pack()
                else:
                    messagebox.showinfo("Thông báo", "Không có ảnh điểm danh.")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
            finally:
                cursor.close()
                conn.close()

        # Nút thao tác
        btn_frame = tk.Frame(main_frame, bg="#ecf0f1")
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="🔄 Tải lịch sử", command=load_history).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="👁 Xem chi tiết ảnh", command=view_photo).pack(side="left", padx=5)

        # Lấy danh sách lớp từ DB
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT class_id, class_name FROM classes WHERE teacher_id = :1", (teacher_id,))
            classes = [f"{row[0]} - {row[1]}" for row in cursor]
            class_combobox['values'] = classes
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def logout():
        root.destroy()
        root_login.deiconify()

    switch_tab("classes")
    root.mainloop()
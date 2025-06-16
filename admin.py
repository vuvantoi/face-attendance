import tkinter as tk
from tkinter import ttk, messagebox
from db_config import connect_db

def run(login_window):
    admin_win = tk.Toplevel()
    admin_win.title("Trang quản trị - Admin")
    admin_win.geometry("750x520")
    admin_win.configure(bg="#f0f4f8")

    def logout():
        admin_win.destroy()
        login_window.deiconify()

    # Nút đăng xuất
    tk.Button(admin_win, text="Đăng xuất", bg="red", fg="white", command=logout).pack(anchor='ne', padx=10, pady=5)

    notebook = ttk.Notebook(admin_win)
    notebook.pack(fill='both', expand=True)

    # ===================== TAB QUẢN LÝ GIÁO VIÊN =====================
    tab_teacher = tk.Frame(notebook)
    notebook.add(tab_teacher, text="Quản lý giáo viên")

    def reset_teacher_form():
        username_entry.config(state="normal")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        teacher_name_entry.delete(0, tk.END)

    # Khung nhập liệu
    teacher_form_frame = tk.LabelFrame(tab_teacher, text="Thông tin giáo viên", padx=10, pady=10)
    teacher_form_frame.pack(fill="x", padx=10, pady=10)

    tk.Label(teacher_form_frame, text="Tên đăng nhập:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    username_entry = tk.Entry(teacher_form_frame)
    username_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    tk.Label(teacher_form_frame, text="Mật khẩu:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    password_entry = tk.Entry(teacher_form_frame, show="*")
    password_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

    tk.Label(teacher_form_frame, text="Tên giáo viên:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    teacher_name_entry = tk.Entry(teacher_form_frame)
    teacher_name_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

    # Khung nút
    teacher_btn_frame = tk.Frame(teacher_form_frame)
    teacher_btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

    tk.Button(teacher_btn_frame, text="Thêm giáo viên", command=lambda: add_teacher(), width=15).grid(row=0, column=0,
                                                                                                      padx=5)
    tk.Button(teacher_btn_frame, text="Sửa giáo viên", command=lambda: edit_teacher(), width=15).grid(row=0, column=1,
                                                                                                      padx=5)
    tk.Button(teacher_btn_frame, text="Xóa giáo viên", command=lambda: delete_teacher(), width=15).grid(row=0, column=2,
                                                                                                        padx=5)
    tk.Button(teacher_btn_frame, text="Reset", command=reset_teacher_form, width=15).grid(row=0, column=3, padx=5)

    # Treeview
    teacher_tree_frame = tk.LabelFrame(tab_teacher, text="Danh sách giáo viên", padx=10, pady=10)
    teacher_tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

    teacher_tree = ttk.Treeview(teacher_tree_frame, columns=("ID", "Tên", "Tài khoản"), show="headings")
    teacher_tree.heading("ID", text="ID")
    teacher_tree.heading("Tên", text="Tên giáo viên")
    teacher_tree.heading("Tài khoản", text="Tên đăng nhập")
    teacher_tree.column("ID", width=50, anchor="center")
    teacher_tree.column("Tên", width=200)
    teacher_tree.column("Tài khoản", width=150)
    teacher_tree.pack(fill="both", expand=True)

    # ===================== HÀM XỬ LÝ =====================

    def reset_teacher_form():
        username_entry.config(state="normal")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        teacher_name_entry.delete(0, tk.END)

    def load_teachers():
        teacher_tree.delete(*teacher_tree.get_children())
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.teacher_id, t.name, u.username
                FROM teachers t
                JOIN users u ON t.user_id = u.user_id
            """)
            for row in cursor.fetchall():
                teacher_tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_teacher_select(event):
        selected = teacher_tree.selection()
        if selected:
            values = teacher_tree.item(selected[0])['values']
            teacher_id, name, username = values
            username_entry.config(state="normal")
            username_entry.delete(0, tk.END)
            username_entry.insert(0, username)
            username_entry.config(state="disabled")
            password_entry.delete(0, tk.END)
            teacher_name_entry.delete(0, tk.END)
            teacher_name_entry.insert(0, name)

    def add_teacher():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        teacher_name = teacher_name_entry.get().strip()

        if not username or not password or not teacher_name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ thông tin.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Kiểm tra username trùng
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = :1", (username,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại.")
                conn.close()
                return

            # Thêm user
            cursor.execute("INSERT INTO users (username, password, role) VALUES (:1, :2, 'teacher')",
                           (username, password))

            # Lấy user_id mới tạo
            cursor.execute("SELECT user_id FROM users WHERE username = :1", (username,))
            user_id = cursor.fetchone()[0]

            # Thêm giáo viên
            cursor.execute("INSERT INTO teachers (name, user_id) VALUES (:1, :2)", (teacher_name, user_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Thành công", "Đã thêm giáo viên.")
            load_teachers()
            load_teacher_combobox()
            reset_teacher_form()

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def edit_teacher():
        selected = teacher_tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn giáo viên để sửa.")
            return

        teacher_id = teacher_tree.item(selected[0])['values'][0]
        new_name = teacher_name_entry.get().strip()
        new_password = password_entry.get().strip()

        if not new_name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên giáo viên.")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Cập nhật tên giáo viên
            cursor.execute("UPDATE teachers SET name = :1 WHERE teacher_id = :2", (new_name, teacher_id))

            # Nếu có mật khẩu mới thì cập nhật
            if new_password:
                cursor.execute("SELECT user_id FROM teachers WHERE teacher_id = :1", (teacher_id,))
                user_id = cursor.fetchone()[0]
                cursor.execute("UPDATE users SET password = :1 WHERE user_id = :2", (new_password, user_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Thành công", "Đã cập nhật giáo viên.")
            load_teachers()
            reset_teacher_form()

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def delete_teacher():
        selected = teacher_tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn giáo viên để xóa.")
            return

        result = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa giáo viên này không?")
        if not result:
            return

        teacher_id = teacher_tree.item(selected[0])['values'][0]

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Kiểm tra giáo viên có phụ trách lớp không
            cursor.execute("SELECT COUNT(*) FROM classes WHERE teacher_id = :1", (teacher_id,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Không thể xóa", "Giáo viên đang phụ trách lớp học. Vui lòng chuyển lớp trước.")
                conn.close()
                return

            # Lấy user_id liên kết
            cursor.execute("SELECT user_id FROM teachers WHERE teacher_id = :1", (teacher_id,))
            user_id = cursor.fetchone()[0]

            # Xóa giáo viên
            cursor.execute("DELETE FROM teachers WHERE teacher_id = :1", (teacher_id,))
            cursor.execute("DELETE FROM users WHERE user_id = :1", (user_id,))

            conn.commit()
            conn.close()

            messagebox.showinfo("Thành công", "Đã xóa giáo viên.")
            load_teachers()
            load_teacher_combobox()
            reset_teacher_form()

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    teacher_tree.bind("<<TreeviewSelect>>", on_teacher_select)

    # Gọi khi khởi động
    load_teachers()

    # TAB 2: QUẢN LÝ SINH VIÊN
    tab_student = ttk.Frame(notebook)
    notebook.add(tab_student, text="Quản lý sinh viên")

    # ---------- RESET FORM ----------
    def reset_student_form():
        student_name_entry.delete(0, tk.END)
        student_username_entry.delete(0, tk.END)
        student_password_entry.delete(0, tk.END)
        class_combo.set("-- Chọn lớp --")

    # ---------- GIAO DIỆN NHẬP LIỆU ----------
    tk.Label(tab_student, text="Tên sinh viên").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    student_name_entry = tk.Entry(tab_student)
    student_name_entry.grid(row=0, column=1)

    tk.Label(tab_student, text="Tên đăng nhập").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    student_username_entry = tk.Entry(tab_student)
    student_username_entry.grid(row=1, column=1)

    tk.Label(tab_student, text="Mật khẩu").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    student_password_entry = tk.Entry(tab_student, show="*")
    student_password_entry.grid(row=2, column=1)

    tk.Label(tab_student, text="Lớp học").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    class_combo = ttk.Combobox(tab_student, state="readonly")
    class_combo.grid(row=3, column=1)

    # ---------- COMBOBOX TÌM KIẾM ----------
    tk.Label(tab_student, text="Tìm kiếm theo lớp").grid(row=4, column=0, padx=5, pady=5, sticky="w")
    search_class_combo = ttk.Combobox(tab_student, state="readonly")
    search_class_combo.grid(row=4, column=1, sticky="w")
    tk.Button(tab_student, text="Tìm kiếm", command=lambda: search_students_by_class()).grid(row=4, column=2, padx=5)

    # ---------- DANH SÁCH SINH VIÊN ----------
    student_tree = ttk.Treeview(tab_student, columns=("ID", "Tên", "Username", "Lớp"), show="headings")
    student_tree.heading("ID", text="Mã SV")
    student_tree.heading("Tên", text="Tên sinh viên")
    student_tree.heading("Username", text="Tên đăng nhập")
    student_tree.heading("Lớp", text="Lớp")
    student_tree.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=10)

    # ---------- NÚT CHỨC NĂNG ----------
    button_frame = tk.Frame(tab_student)
    button_frame.grid(row=6, column=0, columnspan=3, pady=5)

    tk.Button(button_frame, text="Thêm sinh viên", command=lambda: add_student()).grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Xóa sinh viên", command=lambda: delete_student()).grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text="Sửa sinh viên", command=lambda: edit_student()).grid(row=0, column=2, padx=5)
    tk.Button(button_frame, text="Reset", command=reset_student_form).grid(row=0, column=3, padx=5)

    # ---------- TẢI DỮ LIỆU COMBOBOX ----------
    def load_class_combobox():
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT class_id, class_name FROM classes")
            rows = cursor.fetchall()
            values = ["-- Chọn lớp --"] + [f"{row[0]} - {row[1]}" for row in rows]
            class_combo['values'] = values
            class_combo.set("-- Chọn lớp --")
            search_class_combo['values'] = ["-- Tất cả --"] + values[1:]
            search_class_combo.set("-- Tất cả --")
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # ---------- TẢI DANH SÁCH SINH VIÊN ----------
    def load_students():
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.student_id, s.name, u.username, c.class_name
                FROM students s
                JOIN users u ON s.user_id = u.user_id
                LEFT JOIN classes c ON s.class_id = c.class_id
            """)
            rows = cursor.fetchall()
            student_tree.delete(*student_tree.get_children())
            for row in rows:
                student_tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi tải danh sách", str(e))

    # ---------- THÊM SINH VIÊN ----------
    def add_student():
        name = student_name_entry.get().strip()
        username = student_username_entry.get().strip()
        password = student_password_entry.get().strip()
        selected_class = class_combo.get()

        if not (name and username and password):
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ họ tên, tên đăng nhập và mật khẩu.")
            return

        if selected_class == "-- Chọn lớp --":
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn lớp học.")
            return

        try:
            class_id = int(selected_class.split(" - ")[0])
            conn = connect_db()
            cursor = conn.cursor()

            # Kiểm tra username trùng
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = :1", (username,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Trùng tên đăng nhập", "Tên đăng nhập đã tồn tại.")
                return

            cursor.execute("INSERT INTO users (username, password, role) VALUES (:1, :2, 'student')",
                           (username, password))
            cursor.execute("SELECT user_id FROM users WHERE username = :1", (username,))
            user_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO students (student_id, name, user_id, class_id)
                VALUES (:1, :2, :3, :4)
            """, (user_id, name, user_id, class_id))

            conn.commit()
            conn.close()
            messagebox.showinfo("Thành công", "Đã thêm sinh viên.")
            load_students()
            reset_student_form()

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # ---------- XÓA SINH VIÊN ----------
    def delete_student():
        selected = student_tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn sinh viên để xóa.")
            return
        result = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa sinh viên này không?")
        if not result:
            return

        student_id = student_tree.item(selected[0])['values'][0]
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE student_id = :1", (student_id,))
            cursor.execute("DELETE FROM users WHERE user_id = :1", (student_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Thành công", "Đã xóa sinh viên.")
            load_students()
            reset_student_form()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # ---------- SỬA SINH VIÊN ----------
    def edit_student():
        selected = student_tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn sinh viên để sửa.")
            return

        student_id = student_tree.item(selected[0])['values'][0]
        name = student_name_entry.get().strip()
        password = student_password_entry.get().strip()
        selected_class = class_combo.get()

        if not name or selected_class == "-- Chọn lớp --":
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên và chọn lớp.")
            return

        try:
            class_id = int(selected_class.split(" - ")[0])
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE students SET name = :1, class_id = :2 WHERE student_id = :3",
                           (name, class_id, student_id))

            if password:
                cursor.execute("UPDATE users SET password = :1 WHERE user_id = :2", (password, student_id))

            conn.commit()
            conn.close()
            messagebox.showinfo("Thành công", "Đã cập nhật sinh viên.")
            load_students()
            reset_student_form()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))



    # ---------- CHỌN TRÊN BẢNG ----------
    def on_student_select(event):
        selected = student_tree.selection()
        if not selected:
            return
        values = student_tree.item(selected[0])['values']
        student_id, name, username, class_name = values
        student_name_entry.delete(0, tk.END)
        student_name_entry.insert(0, name)
        student_username_entry.delete(0, tk.END)
        student_username_entry.insert(0, username)
        student_password_entry.delete(0, tk.END)
        for v in class_combo['values']:
            if v.endswith(f"- {class_name}"):
                class_combo.set(v)
                break

    student_tree.bind("<<TreeviewSelect>>", on_student_select)

    # ---------- TÌM KIẾM THEO LỚP ----------
    def search_students_by_class():
        selected_class = search_class_combo.get()
        try:
            conn = connect_db()
            cursor = conn.cursor()
            if selected_class == "-- Tất cả --":
                cursor.execute("""
                    SELECT s.student_id, s.name, u.username, c.class_name
                    FROM students s
                    JOIN users u ON s.user_id = u.user_id
                    LEFT JOIN classes c ON s.class_id = c.class_id
                """)
            else:
                class_id = int(selected_class.split(" - ")[0])
                cursor.execute("""
                    SELECT s.student_id, s.name, u.username, c.class_name
                    FROM students s
                    JOIN users u ON s.user_id = u.user_id
                    LEFT JOIN classes c ON s.class_id = c.class_id
                    WHERE s.class_id = :1
                """, (class_id,))
            rows = cursor.fetchall()
            student_tree.delete(*student_tree.get_children())
            for row in rows:
                student_tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi tìm kiếm", str(e))

    # ---------- KHỞI TẠO ----------
    load_class_combobox()
    load_students()

    # ===================== TAB 3: QUẢN LÝ LỚP HỌC =====================
    tab_class = ttk.Frame(notebook)
    notebook.add(tab_class, text="Quản lý lớp học")

    tk.Label(tab_class, text="Tên lớp:").grid(row=0, column=0, padx=5, pady=5)
    class_name_entry = tk.Entry(tab_class)
    class_name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(tab_class, text="Giáo viên phụ trách:").grid(row=1, column=0, padx=5, pady=5)
    teacher_combo = ttk.Combobox(tab_class, state="readonly")
    teacher_combo.grid(row=1, column=1, padx=5, pady=5)

    def load_teacher_combobox():
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT teacher_id, name FROM teachers")
            rows = cursor.fetchall()
            teacher_combo['values'] = [f"{row[0]} - {row[1]}" for row in rows]
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    load_teacher_combobox()

    # Treeview hiển thị danh sách lớp
    class_tree = ttk.Treeview(tab_class, columns=("ID", "Tên lớp", "Giáo viên"), show="headings")
    class_tree.heading("ID", text="Mã lớp")
    class_tree.heading("Tên lớp", text="Tên lớp")
    class_tree.heading("Giáo viên", text="Giáo viên phụ trách")
    class_tree.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
    class_tree.column("ID", width=80, anchor="center")

    # Load danh sách lớp
    def load_classes():
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.class_id, c.class_name, t.name
                FROM classes c
                JOIN teachers t ON c.teacher_id = t.teacher_id
            """)
            rows = cursor.fetchall()
            class_tree.delete(*class_tree.get_children())
            for row in rows:
                class_tree.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # Reset form nhập liệu
    def reset_class_form():
        class_name_entry.delete(0, tk.END)
        teacher_combo.set("")
        class_tree.selection_remove(class_tree.selection())

    # Thêm lớp mới
    def add_class():
        class_name = class_name_entry.get().strip()
        selected = teacher_combo.get()

        if not class_name or not selected:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên lớp và chọn giáo viên.")
            return

        try:
            teacher_id = int(selected.split(" - ")[0])
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO classes (class_name, teacher_id) VALUES (:1, :2)", (class_name, teacher_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Thành công", "Đã thêm lớp.")
            load_classes()
            reset_class_form()

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # Chọn lớp từ bảng
    def on_class_select(event):
        selected = class_tree.selection()
        if selected:
            values = class_tree.item(selected[0])['values']
            class_id, class_name, teacher_name = values
            class_name_entry.delete(0, tk.END)
            class_name_entry.insert(0, class_name)
            # Tìm lại chuỗi "teacher_id - teacher_name" từ tên giáo viên
            for item in teacher_combo['values']:
                if item.endswith(f"- {teacher_name}"):
                    teacher_combo.set(item)
                    break

    # Sửa lớp
    def edit_class():
        selected = class_tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn lớp cần sửa.")
            return

        class_id = class_tree.item(selected[0])['values'][0]
        new_name = class_name_entry.get().strip()
        selected_teacher = teacher_combo.get()

        if not new_name or not selected_teacher:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin.")
            return

        try:
            teacher_id = int(selected_teacher.split(" - ")[0])
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE classes
                SET class_name = :1, teacher_id = :2
                WHERE class_id = :3
            """, (new_name, teacher_id, class_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Thành công", "Đã cập nhật lớp học.")
            load_classes()
            reset_class_form()

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # Xóa lớp
    def delete_class():
        selected = class_tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn lớp để xóa.")
            return

        result = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa lớp này không?")
        if not result:
            return

        class_id = class_tree.item(selected[0])['values'][0]

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Kiểm tra xem lớp có sinh viên không
            cursor.execute("SELECT COUNT(*) FROM students WHERE class_id = :1", (class_id,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Không thể xóa", "Lớp đang có sinh viên. Vui lòng chuyển sinh viên trước.")
                conn.close()
                return

            cursor.execute("DELETE FROM classes WHERE class_id = :1", (class_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Thành công", "Đã xóa lớp.")
            load_classes()
            reset_class_form()

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # Gán sự kiện chọn dòng
    class_tree.bind("<<TreeviewSelect>>", on_class_select)

    # Các nút thao tác
    button_frame = tk.Frame(tab_class)
    button_frame.grid(row=4, column=0, columnspan=3, pady=10)

    tk.Button(button_frame, text="Thêm lớp", width=12, command=add_class).grid(row=0, column=0, padx=5)
    tk.Button(button_frame, text="Sửa lớp", width=12, command=edit_class).grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text="Xóa lớp", width=12, command=delete_class).grid(row=0, column=2, padx=5)
    tk.Button(button_frame, text="Reset", width=12, command=reset_class_form).grid(row=0, column=3, padx=5)

    # Tải dữ liệu ban đầu
    load_classes()


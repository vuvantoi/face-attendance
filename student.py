import tkinter as tk
from tkinter import ttk, messagebox
from db_config import connect_db
from attendance_face_capture import open_attendance_window


def run_student(root_login, user_id):
    root = tk.Toplevel()
    root.title("Sinh viên - Hệ thống điểm danh")
    root.geometry("900x600")
    root.configure(bg="#f5f5f5")

    def logout():
        root.destroy()
        root_login.deiconify()

    # ---------- Tải thông tin sinh viên ----------
    def load_student_info():
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.name, u.username, c.class_name
                FROM students s
                JOIN users u ON s.user_id = u.user_id
                JOIN classes c ON s.class_id = c.class_id
                WHERE u.user_id = :1
            """, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            if result:
                name, username, class_name = result
                lbl_name_value.config(text=name)
                lbl_username_value.config(text=username)
                lbl_class_value.config(text=class_name)
            else:
                messagebox.showerror("Lỗi", "Không tìm thấy thông tin sinh viên")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # ---------- Đổi mật khẩu ----------
    def change_password():
        old_pw = entry_old_pw.get()
        new_pw = entry_new_pw.get()

        if not old_pw or not new_pw:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ mật khẩu cũ và mới")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE user_id = :1", (user_id,))
            current_pw = cursor.fetchone()[0]

            if old_pw != current_pw:
                messagebox.showerror("Sai mật khẩu", "Mật khẩu cũ không đúng")
                return

            cursor.execute("UPDATE users SET password = :1 WHERE user_id = :2", (new_pw, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Thành công", "Đổi mật khẩu thành công")
            entry_old_pw.delete(0, tk.END)
            entry_new_pw.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # ---------- Lịch sử điểm danh ----------
    def load_attendance():
        for row in tree.get_children():
            tree.delete(row)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.attendance_id, a.checkin_time, a.status
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE s.user_id = :1
                ORDER BY a.checkin_time DESC
            """, (user_id,))
            for aid, checkin_time, status in cursor.fetchall():
                tree.insert('', 'end', iid=aid, values=(checkin_time.strftime("%Y-%m-%d %H:%M:%S"), status))
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def view_attendance_detail():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Chọn bản ghi", "Vui lòng chọn bản ghi để xem chi tiết")
            return
        aid = selected
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT photo_captured FROM attendance WHERE attendance_id = :1", (aid,))
            result = cursor.fetchone()
            if result and result[0]:
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(result[0].read()))
                img.show()
            else:
                messagebox.showinfo("Không có ảnh", "Không tìm thấy ảnh điểm danh")
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    # ---------- Tạo giao diện ----------
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Tab 1: Tài khoản
    tab_info = tk.Frame(notebook, bg="white")
    notebook.add(tab_info, text="Tài khoản")

    # Thông tin
    frame_info = tk.Frame(tab_info, bg="white", pady=10)
    frame_info.pack()

    tk.Label(frame_info, text="Tên sinh viên:", bg="white", font=("Helvetica", 11)).grid(row=0, column=0, sticky="e", padx=10, pady=5)
    lbl_name_value = tk.Label(frame_info, text="", bg="white", font=("Helvetica", 11, "bold"))
    lbl_name_value.grid(row=0, column=1, sticky="w")

    tk.Label(frame_info, text="Tên đăng nhập:", bg="white", font=("Helvetica", 11)).grid(row=1, column=0, sticky="e", padx=10, pady=5)
    lbl_username_value = tk.Label(frame_info, text="", bg="white", font=("Helvetica", 11, "bold"))
    lbl_username_value.grid(row=1, column=1, sticky="w")
    tk.Label(frame_info, text="Lớp học:", bg="white", font=("Helvetica", 11)).grid(row=2, column=0, sticky="e", padx=10,
                                                                                   pady=5)
    lbl_class_value = tk.Label(frame_info, text="", bg="white", font=("Helvetica", 11, "bold"))
    lbl_class_value.grid(row=2, column=1, sticky="w")

    # Đổi mật khẩu
    frame_pw = tk.LabelFrame(tab_info, text="Đổi mật khẩu", bg="white", font=("Helvetica", 12, "bold"), fg="blue", padx=10, pady=10)
    frame_pw.pack(padx=20, pady=20, fill="x")

    tk.Label(frame_pw, text="Mật khẩu cũ:", bg="white").pack(anchor="w")
    entry_old_pw = tk.Entry(frame_pw, show="*")
    entry_old_pw.pack(fill="x")

    tk.Label(frame_pw, text="Mật khẩu mới:", bg="white").pack(anchor="w", pady=(10, 0))
    frame_newpw = tk.Frame(frame_pw, bg="white")
    frame_newpw.pack(fill="x")

    entry_new_pw = tk.Entry(frame_newpw, show="*")
    entry_new_pw.pack(side="left", fill="x", expand=True)

    show_pw = tk.BooleanVar(value=False)
    def toggle_pw():
        if show_pw.get():
            entry_new_pw.config(show="*")
            btn_eye.config(text="👁")
            show_pw.set(False)
        else:
            entry_new_pw.config(show="")
            btn_eye.config(text="🙈")
            show_pw.set(True)
    btn_eye = tk.Button(frame_newpw, text="👁", bg="white", command=toggle_pw)
    btn_eye.pack(side="right")

    tk.Button(frame_pw, text="Đổi mật khẩu", bg="#4CAF50", fg="white", command=change_password).pack(pady=10)

    # Tab 2: Điểm danh
    tab_att = tk.Frame(notebook, bg="white")
    notebook.add(tab_att, text="Điểm danh")

    tk.Button(tab_att, text="📸 Mở giao diện điểm danh", bg="#2196F3", fg="white",
              font=("Helvetica", 11, "bold"),
              command=lambda: open_attendance_window(user_id, load_attendance)).pack(pady=15)

    frame_tree = tk.Frame(tab_att, bg="white")
    frame_tree.pack(fill="both", expand=True, padx=10)

    tree = ttk.Treeview(frame_tree, columns=("time", "status"), show="headings", height=12)
    tree.heading("time", text="Thời gian")
    tree.heading("status", text="Trạng thái")
    tree.column("time", width=200)
    tree.column("status", width=100)
    tree.pack(fill="both", expand=True, pady=5)

    tk.Button(tab_att, text="👁 Xem chi tiết điểm danh", command=view_attendance_detail).pack(pady=10)

    # Đăng xuất
    tk.Button(root, text="Đăng xuất", bg="#e53935", fg="white", font=("Helvetica", 10),
              command=logout).pack(side="bottom", anchor="e", padx=10, pady=5)

    # Gọi hàm khởi tạo
    load_student_info()
    load_attendance()
    root.mainloop()


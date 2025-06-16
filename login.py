import tkinter as tk
from tkinter import messagebox
from db_config import connect_db

def login(root, entry_username, entry_password):
    username = entry_username.get()
    password = entry_password.get()

    try:
        conn = connect_db()
        cursor = conn.cursor()

        # ✅ LẤY THÊM user_id BÊN CẠNH role
        cursor.execute("SELECT user_id, role FROM users WHERE username = :1 AND password = :2", (username, password))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            user_id, role = result
            messagebox.showinfo("Đăng nhập thành công", f"Chào {role.capitalize()}!")

            entry_username.delete(0, tk.END)
            entry_password.delete(0, tk.END)
            root.withdraw()

            if role == "admin":
                import admin
                admin.run(root)
            elif role == "teacher":
                import teacher
                teacher.run_teacher(root, user_id)  # ✅ truyền đúng user_id
            elif role == "student":
                import student
                student.run_student(root, user_id)
        else:
            messagebox.showerror("Lỗi", "Sai tài khoản hoặc mật khẩu!")

    except Exception as e:
        messagebox.showerror("Lỗi kết nối", str(e))


def show_login():
    root = tk.Tk()
    root.title("Đăng nhập hệ thống điểm danh")
    root.geometry("400x300")
    root.resizable(False, False)
    root.configure(bg="#f0f4f8")

    title = tk.Label(root, text="ĐĂNG NHẬP", font=("Helvetica", 18, "bold"), bg="#f0f4f8", fg="#333")
    title.pack(pady=20)

    frame = tk.Frame(root, bg="white", bd=2, relief=tk.GROOVE)
    frame.pack(padx=30, pady=10, fill=tk.BOTH, expand=True)

    tk.Label(frame, text="Tên đăng nhập", font=("Helvetica", 11), bg="white", anchor="w").pack(pady=(15, 0), padx=20, fill="x")
    entry_username = tk.Entry(frame, font=("Helvetica", 11))
    entry_username.pack(padx=20, fill="x")

    tk.Label(frame, text="Mật khẩu", font=("Helvetica", 11), bg="white", anchor="w").pack(pady=(15, 0), padx=20, fill="x")
    pw_frame = tk.Frame(frame, bg="white")
    pw_frame.pack(padx=20, fill="x")

    entry_password = tk.Entry(pw_frame, font=("Helvetica", 11), show="*")
    entry_password.pack(side="left", fill="x", expand=True)

    show_password = tk.BooleanVar(value=False)

    def toggle_password():
        if show_password.get():
            entry_password.config(show="*")
            toggle_button.config(text="👁")
            show_password.set(False)
        else:
            entry_password.config(show="")
            toggle_button.config(text="🙈")
            show_password.set(True)

    toggle_button = tk.Button(pw_frame, text="👁", command=toggle_password, relief="flat", bg="white")
    toggle_button.pack(side="right")

    login_btn = tk.Button(frame, text="Đăng nhập", font=("Helvetica", 11, "bold"),
                          bg="#4CAF50", fg="white", activebackground="#45a049",
                          command=lambda: login(root, entry_username, entry_password))
    login_btn.pack(pady=20, padx=20, fill="x")

    entry_password.bind("<Return>", lambda event: login(root, entry_username, entry_password))
    root.mainloop()


if __name__ == "__main__":
    show_login()

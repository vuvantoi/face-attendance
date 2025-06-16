import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import face_recognition
from db_config import connect_db

def show_face_capture_tab(main_frame, teacher_id):
    for widget in main_frame.winfo_children():
        widget.destroy()

    tk.Label(main_frame, text="Quản lý khuôn mặt sinh viên", font=("Helvetica", 14, "bold"), bg="#ecf0f1").pack(pady=10)

    frm_top = tk.Frame(main_frame, bg="#ecf0f1")
    frm_top.pack(pady=5)

    tk.Label(frm_top, text="Chọn lớp học:", bg="#ecf0f1").pack(side="left", padx=5)
    cb_class = ttk.Combobox(frm_top, state="readonly", width=40)
    cb_class.pack(side="left", padx=5)

    columns = ("student_id", "name", "has_face")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=10)
    tree.heading("student_id", text="Mã SV")
    tree.heading("name", text="Tên sinh viên")
    tree.heading("has_face", text="Khuôn mặt")

    tree.column("student_id", width=100)
    tree.column("name", width=200)
    tree.column("has_face", width=100)

    tree.pack(pady=10)

    class_map = {}

    def load_students(class_id):
        for i in tree.get_children():
            tree.delete(i)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT student_id, name, image_encoding
                FROM students
                WHERE class_id = :1
            """, (class_id,))
            for sid, name, encoding in cursor.fetchall():
                status = "Đã có" if encoding else "Chưa có"
                tree.insert("", "end", values=(sid, name, status))
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        finally:
            cursor.close()
            conn.close()

    def on_class_selected(event=None):
        selected = cb_class.get()
        if selected:
            class_id = class_map[selected]
            load_students(class_id)

    cb_class.bind("<<ComboboxSelected>>", on_class_selected)

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT class_id, class_name FROM classes WHERE teacher_id = :1", (teacher_id,))
        classes = cursor.fetchall()
        class_map = {name: cid for cid, name in classes}
        cb_class["values"] = list(class_map.keys())
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))
    finally:
        cursor.close()
        conn.close()

    frm_btn = tk.Frame(main_frame, bg="#ecf0f1")
    frm_btn.pack(pady=10)

    def get_selected_student():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Chọn sinh viên", "Vui lòng chọn một sinh viên.")
            return None
        return tree.item(selected[0])["values"][0]

    def capture_face():
        student_id = get_selected_student()
        if not student_id:
            return

        cam_window = tk.Toplevel()
        cam_window.title("Chụp khuôn mặt")
        cam_window.geometry("700x650")
        cam_window.configure(bg="white")

        lbl_info = tk.Label(cam_window, text="Đảm bảo chỉ có 1 khuôn mặt rõ ràng trong khung!", bg="white", fg="blue")
        lbl_info.pack(pady=5)

        video_label = tk.Label(cam_window)
        video_label.pack(pady=10)

        btn_frame = tk.Frame(cam_window, bg="white")
        btn_frame.pack(pady=10)

        cap = cv2.VideoCapture(1)
        running = [True]

        def show_frame():
            if not running[0]:
                return
            ret, frame = cap.read()
            if not ret:
                return

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(rgb)

            for top, right, bottom, left in faces:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (640, 480))
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)

            cam_window.after(10, show_frame)

        def save_face():
            ret, frame = cap.read()
            if not ret:
                messagebox.showerror("Lỗi", "Không đọc được hình ảnh từ webcam.")
                return

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(rgb)
            if len(faces) != 1:
                messagebox.showerror("Lỗi", "Phải có đúng 1 khuôn mặt.")
                return

            # Lấy encoding và ảnh
            enc = face_recognition.face_encodings(rgb, faces)[0]
            _, buffer = cv2.imencode(".jpg", frame)

            # Chuyển encoding từ bytes -> string (latin1) để lưu CLOB
            img_encoded_str = enc.tobytes().decode('latin1')  # CLOB
            img_captured_blob = buffer.tobytes()  # BLOB

            try:
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE students
                    SET image_encoding = :1, face_image = :2
                    WHERE student_id = :3
                """, (img_encoded_str, img_captured_blob, student_id))
                conn.commit()
                messagebox.showinfo("Thành công", "Lưu khuôn mặt thành công!")
                running[0] = False
                cap.release()
                cam_window.destroy()
                on_class_selected()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
            finally:
                cursor.close()
                conn.close()

        def cancel_capture():
            running[0] = False
            cap.release()
            cam_window.destroy()
            cv2.destroyAllWindows()

        def on_close():
            running[0] = False
            cap.release()
            cam_window.destroy()
            cv2.destroyAllWindows()

        tk.Button(btn_frame, text="✅ Lấy khuôn mặt", bg="#2ecc71", fg="white", command=save_face).pack(side="left",
                                                                                                       padx=10)
        tk.Button(btn_frame, text="❌ Hủy", bg="#e74c3c", fg="white", command=cancel_capture).pack(side="left", padx=10)

        cam_window.protocol("WM_DELETE_WINDOW", on_close)
        show_frame()

    def view_face():
        student_id = get_selected_student()
        if not student_id:
            return
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT face_image FROM students WHERE student_id = :1", (student_id,))
            row = cursor.fetchone()
            if row and row[0]:
                blob_data = row[0].read()  # 🔧 Đọc nội dung từ LOB
                nparr = np.frombuffer(blob_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                cv2.imshow("Khuôn mặt đã lưu", img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                messagebox.showinfo("Thông báo", "Chưa có khuôn mặt được lưu.")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        finally:
            cursor.close()
            conn.close()

    tk.Button(frm_btn, text="📷 Thêm / Cập nhật khuôn mặt", command=capture_face).pack(side="left", padx=10)
    tk.Button(frm_btn, text="👁 Xem khuôn mặt đã lưu", command=view_face).pack(side="left", padx=10)

    if cb_class["values"]:
        cb_class.current(0)
        on_class_selected()

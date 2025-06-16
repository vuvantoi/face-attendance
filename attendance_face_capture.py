import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
import face_recognition
import datetime
from db_config import connect_db
from PIL import Image, ImageTk


def open_attendance_window(user_id, refresh_attendance_callback):
    cam_window = tk.Toplevel()
    cam_window.title("Điểm danh bằng khuôn mặt")
    cam_window.geometry("800x600")

    video_label = tk.Label(cam_window)
    video_label.pack(pady=10)

    btn_frame = tk.Frame(cam_window)
    btn_frame.pack()

    capture_flag = {'running': True}
    cap = cv2.VideoCapture(1)

    def update_frame():
        if not capture_flag['running']:
            return

        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (640, 480))
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_frame)

            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img_tk = ImageTk.PhotoImage(image=image)
            video_label.imgtk = img_tk
            video_label.config(image=img_tk)

        cam_window.after(30, update_frame)

    def process_attendance():
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute

        if hour < 7 or (hour == 7 and minute < 30):
            messagebox.showinfo("Thông báo", "Chưa đến giờ điểm danh")
            return

        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Lỗi", "Không thể chụp ảnh từ webcam")
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if len(face_locations) == 0:
            messagebox.showwarning("Không phát hiện khuôn mặt", "Vui lòng đảm bảo khuôn mặt nằm trong khung hình")
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()

            # ✅ Kiểm tra đã điểm danh hôm nay chưa
            cursor.execute("""
                SELECT COUNT(*) FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE s.user_id = :1 AND TRUNC(a.checkin_time) = TRUNC(SYSDATE)
            """, (user_id,))
            count_today = cursor.fetchone()[0]

            if count_today > 0:
                messagebox.showinfo("Thông báo", "Bạn đã điểm danh hôm nay rồi")
                return

            # ✅ Lấy encoding từ CLOB
            cursor.execute("SELECT image_encoding FROM students WHERE user_id = :1", (user_id,))
            result = cursor.fetchone()
            if not result or not result[0]:
                messagebox.showerror("Lỗi", "Không có dữ liệu khuôn mặt")
                return

            encoding_clob = result[0].read()
            known_encoding = np.frombuffer(encoding_clob.encode('latin1'), dtype=np.float64)

            unknown_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            match = face_recognition.compare_faces([known_encoding], unknown_encoding)[0]

            if match:
                # ✅ Encode ảnh và chuyển thành BLOB
                _, buffer = cv2.imencode('.jpg', frame)
                photo_blob = buffer.tobytes()

                # ✅ Xác định trạng thái
                if hour == 7 and minute <= 59:
                    status = 'Có mặt'
                    messagebox.showinfo("Điểm danh", "Điểm danh thành công!")
                elif hour >= 8:
                    status = 'Muộn'
                    messagebox.showinfo("Điểm danh", "Bạn đã điểm danh muộn")
                else:
                    status = 'Không xác định'

                # ✅ Chuẩn bị định nghĩa input size để lưu BLOB
                import cx_Oracle
                cursor.setinputsizes(None, cx_Oracle.BLOB, None)

                # ✅ Thêm bản ghi điểm danh
                cursor.execute("""
                    INSERT INTO attendance (student_id, status, photo_captured)
                    SELECT student_id, :1, :2 FROM students WHERE user_id = :3
                """, (status, photo_blob, user_id))

                conn.commit()
                refresh_attendance_callback()
            else:
                messagebox.showwarning("Khuôn mặt không khớp", "Không thể xác minh danh tính")

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass

    def on_close():
        capture_flag['running'] = False
        cap.release()
        cam_window.destroy()

    btn_capture = tk.Button(btn_frame, text="✅ Điểm danh", font=("Helvetica", 11), bg="#4CAF50", fg="white", command=process_attendance)
    btn_capture.pack(side="left", padx=10)

    btn_cancel = tk.Button(btn_frame, text="❌ Hủy", font=("Helvetica", 11), bg="#e53935", fg="white", command=on_close)
    btn_cancel.pack(side="left", padx=10)

    update_frame()
    cam_window.protocol("WM_DELETE_WINDOW", on_close)

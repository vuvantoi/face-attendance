from db_config import connect_db

def get_teacher_id_by_user(user_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT teacher_id FROM teachers WHERE user_id = :1", (user_id,))
        teacher = cursor.fetchone()
        return teacher[0] if teacher else None
    except Exception as e:
        print("❌ Lỗi khi lấy teacher_id:", str(e))
        return None
    finally:
        cursor.close()
        conn.close()

def get_classes_by_teacher(teacher_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT class_id, class_name FROM classes WHERE teacher_id = :1", (teacher_id,))
        rows = cursor.fetchall()
        if rows:
            print(f"✅ Lớp của giáo viên ID {teacher_id}:")
            for row in rows:
                print(f"- {row[0]} | {row[1]}")
        else:
            print("⚠️ Không có lớp nào.")
    except Exception as e:
        print("❌ Lỗi truy vấn lớp:", str(e))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    user_id = 2  # ID của giáo viên
    teacher_id = get_teacher_id_by_user(user_id)
    if teacher_id:
        get_classes_by_teacher(teacher_id)
    else:
        print("❌ Không tìm thấy teacher_id ứng với user_id =", user_id)

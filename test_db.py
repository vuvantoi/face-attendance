from db_config import connect_db

try:
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    for row in cursor:
        print("Dòng dữ liệu:", row)

    cursor.close()
    conn.close()
    print("✅ Kết nối Oracle thành công và truy vấn dữ liệu thành công.")
except Exception as e:
    print("❌ Lỗi khi kết nối Oracle:", e)

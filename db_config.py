# db_config.py
import cx_Oracle

def connect_db():
    dsn = cx_Oracle.makedsn("localhost", 1522, sid="xe")  # Dùng SID thay vì service_name
    conn = cx_Oracle.connect(user="FACE", password="123", dsn=dsn)
    return conn

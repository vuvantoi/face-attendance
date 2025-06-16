-- Sequence cho user_id
CREATE SEQUENCE seq_user_id START WITH 1 INCREMENT BY 1;

-- Bảng USERS
CREATE TABLE users (
    user_id NUMBER PRIMARY KEY,
    username VARCHAR2(50) UNIQUE NOT NULL,
    password VARCHAR2(100) NOT NULL,
    role VARCHAR2(20) CHECK (role IN ('admin', 'teacher', 'student'))
);

-- Trigger tự động tăng user_id
CREATE OR REPLACE TRIGGER trg_user_id
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    SELECT seq_user_id.NEXTVAL INTO :NEW.user_id FROM dual;
END;
/

-- Bảng TEACHERS
CREATE TABLE teachers (
    teacher_id NUMBER PRIMARY KEY,
    name VARCHAR2(100) NOT NULL,
    user_id NUMBER UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
CREATE SEQUENCE seq_teacher_id START WITH 1 INCREMENT BY 1;

-- Trigger tự động tăng TEACHER_ID
CREATE OR REPLACE TRIGGER trg_teacher_id
BEFORE INSERT ON teachers
FOR EACH ROW
BEGIN
    SELECT seq_teacher_id.NEXTVAL INTO :NEW.teacher_id FROM dual;
END;

-- Bảng CLASSES
CREATE TABLE classes (
    class_id NUMBER PRIMARY KEY,
    class_name VARCHAR2(100) NOT NULL,
    teacher_id NUMBER,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
);
CREATE SEQUENCE seq_class_id
START WITH 1
INCREMENT BY 1
NOCACHE
NOCYCLE;

CREATE OR REPLACE TRIGGER trg_class_id
BEFORE INSERT ON classes
FOR EACH ROW
BEGIN
  SELECT seq_class_id.NEXTVAL
  INTO :NEW.class_id
  FROM dual;
END;
/


-- Bảng STUDENTS
CREATE TABLE students (
    student_id NUMBER PRIMARY KEY,
    name VARCHAR2(100) NOT NULL,
    image_encoding BLOB,
    user_id NUMBER UNIQUE,
    class_id NUMBER,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
);
select * from students
ALTER TABLE students DROP COLUMN image_encoding;
ALTER TABLE students ADD (
    face_image      BLOB,  -- ảnh khuôn mặt .jpg dùng để xem lại
    image_encoding  CLOB   
);


CREATE SEQUENCE seq_student_id
START WITH 20250001
INCREMENT BY 1
NOCACHE
NOCYCLE;

CREATE OR REPLACE TRIGGER trg_student_id
BEFORE INSERT ON students
FOR EACH ROW
BEGIN
    SELECT seq_student_id.NEXTVAL INTO :NEW.student_id FROM dual;
END;
/

SELECT column_name, data_type, data_length
FROM user_tab_columns
WHERE table_name = 'STUDENTS';
-- Sequence cho attendance_id
CREATE SEQUENCE seq_attendance_id START WITH 1 INCREMENT BY 1;



-- Bảng ATTENDANCE
CREATE TABLE attendance (
    attendance_id NUMBER PRIMARY KEY,
    student_id NUMBER,
    checkin_time TIMESTAMP DEFAULT SYSTIMESTAMP,
    status VARCHAR2(20),
    photo_captured BLOB,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);
ALTER TABLE attendance
ADD CONSTRAINT chk_attendance_status
CHECK (status IN ('Có mặt', 'Vắng', 'Muộn'));

-- Trigger tự tăng ID điểm danh
CREATE OR REPLACE TRIGGER trg_attendance_id
BEFORE INSERT ON attendance
FOR EACH ROW
BEGIN
    SELECT seq_attendance_id.NEXTVAL INTO :NEW.attendance_id FROM dual;
END;
/
DESC attendance;

select * from users;
select * from teachers;
select * from classes;
select * from students;
select * from attendance

SELECT column_name, data_type, data_length 
FROM user_tab_columns 
WHERE table_name = 'ATTENDANCE';
-- Xoá cột sai kiểu
ALTER TABLE attendance DROP COLUMN photo_captured;

-- Tạo lại đúng kiểu BLOB
ALTER TABLE attendance ADD photo_captured BLOB;

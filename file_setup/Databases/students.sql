-- สร้างฐานข้อมูล
CREATE DATABASE IF NOT EXISTS student_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ใช้ฐานข้อมูล
USE student_db;

-- สร้างตารางนักเรียน
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    student_nickname VARCHAR(50) NOT NULL,
    parent_name VARCHAR(100) NOT NULL,
    parent_car_plate VARCHAR(20),
    parent_phone VARCHAR(20),
    status TINYINT(1) NOT NULL DEFAULT 1  -- 0 = โดนลบ, 1 = ยังไม่โดนลบ
);

-- สร้างตารางเก็บการมาเรียน
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date DATE NOT NULL,
    status TINYINT(1) NOT NULL DEFAULT 0,  -- 0 = ไม่มา, 1 = มา 
    FOREIGN KEY (student_id) REFERENCES students(id)
        ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (student_id, date)
);

-- เพิ่มข้อมูลนักเรียน
INSERT INTO students (student_name, student_nickname, parent_name, parent_car_plate, parent_phone, status) VALUES
('ชื่อทดสอบ ลำดับหนึ่ง', 'ทดลอง', 'ทดสอบนะ ครับ', 'ชย3487เชียงใหม่', '0888888888', 1);

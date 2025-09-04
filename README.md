# Student Name Announcement System

โปรเจคนี้พัฒนาโดยใช้ **Python** และ **PyQt5** สำหรับระบบประกาศรายชื่อนักเรียน
รองรับการติดตั้ง library ผ่าน `requirements.txt` เพื่อให้ใช้งานได้เหมือนกันทุกเครื่อง

---

## 🚀 การติดตั้งและใช้งาน

เปิด Windows (CMD)

### 1. Clone โปรเจค
git clone https://github.com/phithak1602/Student_Name_Announcement_System.git

cd Student_Name_Announcement_System

### 2. สร้าง Virtual Environment (venv)
python -m venv venv

### 3. เปิดใช้งาน venv
Windows (CMD): venv\Scripts\activate.bat

หลังจาก activate สำเร็จ จะเห็น (venv) นำหน้าบรรทัดคำสั่ง

(วิธีปิด venv: deactivate)

### 4. ติดตั้ง dependencies
pip install -r requirements.txt

### 5. เปิด XAMPP
ในโปรแกรม XAMPP ให้เปิด Apache และ Mysql

### 6. นำเข้า Databases
Import students.sql จาก Student_Name_Announcement_System\file_setup\Databases ผ่าน http://localhost/phpmyadmin

### 7. รันโปรแกรม
pythonw GUI_main.pyw

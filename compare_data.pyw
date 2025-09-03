import mysql.connector
import time 
from datetime import date
import os

# ✅ รายชื่อจังหวัดทั้งหมดในประเทศไทย
PROVINCES = [
    "กรุงเทพมหานคร", "กระบี่", "กาญจนบุรี", "กาฬสินธุ์", "กำแพงเพชร", "ขอนแก่น", "จันทบุรี", "ฉะเชิงเทรา",
    "ชลบุรี", "ชัยนาท", "ชัยภูมิ", "ชุมพร", "เชียงราย", "เชียงใหม่", "ตรัง", "ตราด", "ตาก", "นครนายก",
    "นครปฐม", "นครพนม", "นครราชสีมา", "นครศรีธรรมราช", "นครสวรรค์", "นนทบุรี", "นราธิวาส", "น่าน",
    "บึงกาฬ", "บุรีรัมย์", "ปทุมธานี", "ประจวบคีรีขันธ์", "ปราจีนบุรี", "ปัตตานี", "พระนครศรีอยุธยา",
    "พังงา", "พัทลุง", "พิจิตร", "พิษณุโลก", "เพชรบุรี", "เพชรบูรณ์", "แพร่", "พะเยา", "ภูเก็ต",
    "มหาสารคาม", "มุกดาหาร", "แม่ฮ่องสอน", "ยโสธร", "ยะลา", "ร้อยเอ็ด", "ระนอง", "ระยอง",
    "ราชบุรี", "ลพบุรี", "ลำปาง", "ลำพูน", "เลย", "ศรีสะเกษ", "สกลนคร", "สงขลา", "สตูล", "สมุทรปราการ",
    "สมุทรสงคราม", "สมุทรสาคร", "สระแก้ว", "สระบุรี", "สิงห์บุรี", "สุโขทัย", "สุพรรณบุรี", "สุราษฎร์ธานี",
    "สุรินทร์", "หนองคาย", "หนองบัวลำภู", "อ่างทอง", "อุดรธานี", "อุทัยธานี", "อุตรดิตถ์", "อุบลราชธานี", "อำนาจเจริญ"
]

# ✅ ฟังก์ชันลบชื่อจังหวัดออกจากทะเบียน
def clean_plate(plate):
    for province in PROVINCES:
        if province in plate:
            plate = plate.replace(province, '')
    return plate.strip()

# ✅ ฟังก์ชันดึงจังหวัดจากทะเบียน
def extract_province(plate):
    for province in PROVINCES:
        if province in plate:
            return province
    return None

# ✅ ฟังก์ชันเปรียบเทียบแบบตัวต่อตัวและให้คะแนน พร้อมตรวจกับจังหวัด
def is_similar_custom(a, b, threshold=0.80):
    a_clean = clean_plate(a)
    b_clean = clean_plate(b)

    # ถ้าความยาวต่างกันเกินไป → ตัดทิ้ง
    if abs(len(a_clean) - len(b_clean)) > 3:
        return False

    max_len = max(len(a_clean), len(b_clean))
    a_clean = a_clean.ljust(max_len)
    b_clean = b_clean.ljust(max_len)

    match_score = sum(1 for i in range(max_len) if a_clean[i] == b_clean[i])
    similarity = match_score / max_len

    if similarity < threshold:
        return False

    if similarity >= 0.90:
        province_a = extract_province(a)
        province_b = extract_province(b)

        if province_a and province_b:
            return province_a == province_b
        else:
            # อย่างน้อยหนึ่งทะเบียนไม่มีจังหวัด → ถือว่าเหมือนกัน
            return True

    return True

# ✅ เชื่อมต่อกับฐานข้อมูล
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='student_db'
    )
    cursor = conn.cursor()
    
    # ถ้าเชื่อมต่อสำเร็จ เขียนค่า 1
    with open("txt_file/databases_status.txt", "w") as f:
        f.write("1")

except mysql.connector.Error:
    # ถ้าเชื่อมต่อไม่ได้ เขียนค่า 0
    with open("txt_file/databases_status.txt", "w") as f:
        f.write("0")

seen_plates = set()
print("📢 เริ่มตวรจจับไฟล์ car_plate.txt...")

try:
    while True:
        if os.path.exists('txt_file/car_plate.txt'):
            with open('txt_file/car_plate.txt', 'r', encoding='utf-8') as f:
                car_plates = [line.strip() for line in f if line.strip()]

            new_plates = [plate for plate in car_plates if plate not in seen_plates]
            matched_nicknames = []

            # ✅ ดึงข้อมูลทะเบียนและชื่อเล่น+ID จากฐานข้อมูล
            cursor.execute("SELECT id, parent_car_plate, student_nickname FROM students WHERE status = 1")
            students = cursor.fetchall()

            for plate in new_plates:
                found_match = False
                for student_id, db_plate, nickname in students:
                    if is_similar_custom(plate, db_plate):
                        matched_nicknames.append(nickname)
                        print(f"✔ ใกล้เคียงกับทะเบียน {db_plate} -> บันทึกชื่อเล่น: {nickname} (ป้อน: {plate})")

                        # ✅ อัปเดตสถานะเซอร์โว
                        with open('txt_file/servo_state.txt', 'w') as f:
                            f.write('1')

                        # ✅ บันทึกการมารับนักเรียนวันนี้
                        today = date.today()
                        cursor.execute("""SELECT id FROM attendance WHERE student_id = %s AND date = %s""", (student_id, today))
                        result = cursor.fetchone()

                        if result is None:
                            cursor.execute("""INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, 1)""", (student_id, today))
                            conn.commit()
                            print(f"📝 บันทึกการมารับของ {nickname} แล้ว")
                        else:
                            print(f"⚠ {nickname} มีบันทึกวันนี้อยู่แล้ว")

                        found_match = True
                        break

                if not found_match:
                    print(f"✘ ไม่พบทะเบียน {plate} ที่คล้ายกันในฐานข้อมูล")
                seen_plates.add(plate)

            if matched_nicknames:
                with open('txt_file/names.txt', 'a', encoding='utf-8') as f:
                    for name in matched_nicknames:
                        f.write(name + '\n')

        time.sleep(3)

except KeyboardInterrupt:
    print("\n🛑 หยุดการตรวจสอบแล้ว")

finally:
    cursor.close()
    conn.close()
    print("✅ ปิดการเชื่อมต่อฐานข้อมูลแล้ว")

import cv2
from ultralytics import YOLO
import os

# === โหลดโมเดล YOLO สำหรับป้ายทะเบียน ===
plate_model = YOLO(r"model/plate.pt")

with open("txt_file/rtsp_url.txt", "r") as f:
    url = f.read().strip()
'''url = "rtsp://admin:Nice1234@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0"'''
cap = cv2.VideoCapture("video_test/video_CCTV_test3.mp4")
'''cap = cv2.VideoCapture(url)'''
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# === โฟลเดอร์สำหรับบันทึกภาพ ===
output_dir = r"result_plate"
os.makedirs(output_dir, exist_ok=True)
idx = 1
MAX_IMAGE = 20

# === กำหนดเส้นตรวจจับแบบอิสระ (เฉียงก็ได้) ===
line_start = (472, 571)
line_end = (1300, 561)

# === ตัวแปรช่วยตรวจสอบ ===
plate_positions = {}           # เก็บตำแหน่งล่าสุดของแต่ละ track_id
triggered_plates = set()       # บันทึกว่าเคยตัดเส้นแล้ว
frame_count = 0

# === ไฟล์สำหรับแชร์กับ GUI ===
os.makedirs("temp", exist_ok=True)
temp_frame_path = "temp/temp_frame.jpg"

# === ฟังก์ชันตรวจสอบว่ามีการตัดเส้นหรือไม่ ===
def lines_intersect(p1, p2, q1, q2):
    def ccw(a, b, c):
        return (c[1]-a[1]) * (b[0]-a[0]) > (b[1]-a[1]) * (c[0]-a[0])
    return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)

print("🚀 เริ่มต้น License Plate Detection System")
print("📺 กำลังประมวลผลวิดีโอ...")
print("🖥️ สามารถเปิด GUI_main.py ได้แล้วเพื่อดูผลลัพธ์")

while True:
    for _ in range(3): cap.read()
    ret, frame = cap.read()
    if not ret:
        print("🔄 วิดีโอจบแล้ว หรือไม่สามารถอ่านเฟรมได้")
        break

    frame_count += 1
    clean_frame = frame.copy()
    display_frame = frame.copy()

    # 🔶 วาดเส้นตรวจจับ
    cv2.line(display_frame, line_start, line_end, (0, 255, 255), 2)

    # 🔍 ตรวจจับป้ายทะเบียนด้วย YOLO
    plate_results = plate_model.track(frame, persist=True, stream=True, conf=0.6)

    for result in plate_results:
        if result.boxes is not None:
            for box in result.boxes:
                px1, py1, px2, py2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                track_id = int(box.id[0]) if box.id is not None else None
                cx, cy = int((px1 + px2) / 2), int((py1 + py2) / 2)

                cv2.rectangle(display_frame, (px1, py1), (px2, py2), (0, 0, 255), 2)
                cv2.circle(display_frame, (cx, cy), 4, (255, 0, 0), -1)
                label = f"plate {conf:.2f}"
                if track_id is not None:
                    label += f" ID:{track_id}"
                cv2.putText(display_frame, label, (px1, py1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                if track_id is not None:
                    # เก็บตำแหน่ง (cx, cy)
                    if track_id not in plate_positions:
                        plate_positions[track_id] = []
                    plate_positions[track_id].append((cx, cy, frame_count))
                    if len(plate_positions[track_id]) > 10:
                        plate_positions[track_id].pop(0)

                    # ตรวจสอบว่ามีการตัดเส้นหรือไม่
                    if (len(plate_positions[track_id]) >= 2 and
                        track_id not in triggered_plates):

                        prev = plate_positions[track_id][-2][:2]
                        curr = plate_positions[track_id][-1][:2]

                        if lines_intersect(prev, curr, line_start, line_end):
                            triggered_plates.add(track_id)
                            print(f"✅ ป้ายทะเบียน ID {track_id} ตัดผ่านเส้น!")

                            # 📸 แคปภาพ
                            plate_crop = clean_frame[py1:py2, px1:px2]
                            if plate_crop.size > 0:
                                filename = os.path.join(output_dir, f"plate_{idx}.jpg")
                                cv2.imwrite(filename, plate_crop)
                                print(f"💾 บันทึกป้ายทะเบียน: {filename}")
                                idx = (idx % MAX_IMAGE) + 1

                                # ✅ วาดกรอบพิเศษ
                                cv2.rectangle(display_frame, (px1, py1), (px2, py2), (0, 255, 0), 3)
                                cv2.putText(display_frame, "CAPTURED!", (px1, py1 - 30),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                else:
                    print(f"⚠️ ป้ายทะเบียนไม่มี Track ID (conf={conf:.2f})")

    # 🧹 ลบข้อมูล track เก่า
    if frame_count % 100 == 0:
        old_tracks = []
        for track_id, positions in plate_positions.items():
            if positions and frame_count - positions[-1][2] > 50:
                old_tracks.append(track_id)
        for track_id in old_tracks:
            del plate_positions[track_id]
            triggered_plates.discard(track_id)

    # 📤 บันทึกเฟรมสำหรับ GUI
    resized = cv2.resize(display_frame, (1080, 640))
    cv2.imwrite(temp_frame_path, resized)
    
    # Debug: แสดงสถานะทุก 100 เฟรม
    if frame_count % 100 == 0:
        print(f"📤 Frame {frame_count} saved to {temp_frame_path}")
    
    # แสดงผลหน้าต่างของ line_detected_plate.py (ถ้าต้องการ)
    '''cv2.imshow("License Plate Detection", resized)'''
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ลบไฟล์ temp เมื่อจบ
if os.path.exists(temp_frame_path):
    os.remove(temp_frame_path)

cap.release()
cv2.destroyAllWindows()
print("🛑 License Plate Detection System หยุดทำงาน")
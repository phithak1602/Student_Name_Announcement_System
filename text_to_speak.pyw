from gtts import gTTS
import pygame
import threading
import queue
import time
import os
from datetime import datetime

# Initialize pygame mixer
pygame.mixer.init()

FILENAME = 'txt_file/names.txt'
LOGFILE = 'txt_file/log.txt'
MAX_LINES = 20
last_index = 0

# สร้าง queue สำหรับจัดคิวเสียง
audio_queue = queue.Queue()
is_playing = False

print("📢 เริ่มตรวจจับไฟล์ names.txt และบันทึก log...")

def get_file_mtime(path):
    try:
        return os.path.getmtime(path)
    except FileNotFoundError:
        return None

def audio_player_worker():
    """Worker thread สำหรับเล่นเสียงทีละไฟล์"""
    global is_playing
    
    while True:
        try:
            # รอรับไฟล์เสียงจาก queue
            mp3_filename = audio_queue.get(timeout=1)
            
            if mp3_filename is None:  # Signal to stop
                break
                
            is_playing = True
            #print(f"🎵 กำลังเล่นเสียง: {os.path.basename(mp3_filename)}")
            
            # เล่นเสียง
            pygame.mixer.music.load(mp3_filename)
            pygame.mixer.music.play()
            
            # รอให้เสียงเล่นจบ
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # หยุด music
            pygame.mixer.music.stop()
            
            is_playing = False
            audio_queue.task_done()
            
        except queue.Empty:
            # ไม่มีไฟล์ใน queue รอต่อ
            continue
        except Exception as e:
            print(f"❗ เกิดข้อผิดพลาดในการเล่นเสียง: {e}")
            is_playing = False
            if 'mp3_filename' in locals():
                audio_queue.task_done()

def add_to_audio_queue(mp3_filename):
    """เพิ่มไฟล์เสียงเข้า queue"""
    audio_queue.put(mp3_filename)
    queue_size = audio_queue.qsize()
    #print(f"📋 เพิ่มเข้าคิว: {os.path.basename(mp3_filename)} (คิวที่ {queue_size})")

# เริ่ม worker thread สำหรับเล่นเสียง
audio_thread = threading.Thread(target=audio_player_worker, daemon=True)
audio_thread.start()

while True:
    try:
        #print("🔍 ตรวจสอบไฟล์...")
        
        # บันทึกเวลาแก้ไขก่อนอ่าน
        before_read_mtime = get_file_mtime(FILENAME)

        with open(FILENAME, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file if line.strip()]

        #print(f"📖 อ่านได้ {len(lines)} บรรทัด, ตำแหน่งปัจจุบัน: {last_index}")
        
        # แสดงสถานะคิวเสียง
        queue_size = audio_queue.qsize()
        playing_status = "กำลังเล่น" if is_playing else "ว่าง"
        #print(f"🎵 สถานะเสียง: {playing_status}, คิวรอ: {queue_size} ไฟล์")

        # บรรทัดใหม่
        if last_index < len(lines):
            new_lines = lines[last_index:]
            print(f"🆕 พบชื่อใหม่ {len(new_lines)} ชื่อ")
            
            for name in new_lines:
                full_text = f"น้อง {name} ผู้ปกครองมารับแล้ว"
                print(f"🔊 กำลังสร้างเสียง: {full_text}")

                try:
                    # สร้างไฟล์เสียง
                    tts = gTTS(full_text, lang='th')
                    # สร้างโฟลเดอร์ temp ถ้ายังไม่มี
                    os.makedirs("temp", exist_ok=True)
                    mp3_filename = os.path.join("temp", f"voice_{int(time.time())}_{hash(name)}.mp3")
                    tts.save(mp3_filename)
                    
                    #print(f"💾 บันทึกไฟล์: {mp3_filename}")

                    # เพิ่มเข้าคิวเสียง (จะเล่นทีละไฟล์)
                    add_to_audio_queue(mp3_filename)

                    # บันทึก log
                    with open(LOGFILE, 'a', encoding='utf-8') as log:
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        log.write(f"[{timestamp}] ผู้ปกครองของน้อง {name}\n")
                    
                    print(f"📝 บันทึก log: {name}")
                    
                except Exception as e:
                    print(f"❌ เกิดข้อผิดพลาดกับ {name}: {e}")

            last_index = len(lines)
            #print(f"📍 อัปเดตตำแหน่งเป็น: {last_index}")

        # ตรวจสอบเงื่อนไขรีเซ็ต
        if len(lines) >= MAX_LINES:
            # ตรวจสอบว่าไม่มีการเปลี่ยนแปลงไฟล์ระหว่างอ่าน
            after_read_mtime = get_file_mtime(FILENAME)
            if before_read_mtime == after_read_mtime:
                print(f"⚠️ ครบ {MAX_LINES} บรรทัดแล้ว กำลังรีเซ็ต names.txt")
                with open(FILENAME, 'w', encoding='utf-8') as f:
                    f.write("")
                last_index = 0
                print("🔄 รีเซ็ตเสร็จแล้ว")
            else:
                print("⏳ ตรวจพบการแก้ไขไฟล์ระหว่างเตรียมลบ — ยกเลิกการรีเซ็ตชั่วคราว")

    except FileNotFoundError:
        print("❗ ไม่พบไฟล์ names.txt รอการสร้างใหม่...")
        # สร้างไฟล์เปล่าถ้าไม่มี
        os.makedirs('txt_file', exist_ok=True)
        with open(FILENAME, 'w', encoding='utf-8') as f:
            f.write("")
    except Exception as e:
        print(f"💥 เกิดข้อผิดพลาดใน main loop: {e}")

    time.sleep(2)
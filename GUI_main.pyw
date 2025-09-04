import sys
import cv2
import subprocess
import webbrowser
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QFrame,QMessageBox)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont
import os
import time

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    time.sleep(2)
    def __init__(self):
        super().__init__()
        self.running = False
        
        # ใช้วิธีแชร์ผ่านไฟล์ภาพ
        os.makedirs("temp", exist_ok=True)
        self.temp_frame_path = "temp/temp_frame.jpg"
        
        # ลบไฟล์เก่า
        self.clear_files()

    def clear_files(self):
        """Clear text files and result plate images"""
        # Clear text files
        with open('txt_file/car_plate.txt', 'w') as f:
            f.truncate(0)
        with open('txt_file/names.txt', 'w') as f:
            f.truncate(0)
        
        # Clear result plate images
        os.makedirs("result_plate", exist_ok=True)
        if os.path.exists('result_plate'):
            for filename in os.listdir('result_plate'):
                file_path = os.path.join('result_plate', filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        os.makedirs("temp", exist_ok=True)
        if os.path.exists('temp'):
            for filename in os.listdir('temp'):
                file_path = os.path.join('temp', filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)            
        # Clear temp frame
        if os.path.exists(self.temp_frame_path):
            os.remove(self.temp_frame_path)

    def run(self):
        self.running = True
        print("GUI VideoThread started - reading from temp file")
        frame_count = 0
        last_modified = 0
        
        while self.running:
            try:
                # ตรวจสอบว่าไฟล์ temp_frame.jpg มีการอัพเดทหรือไม่
                if os.path.exists(self.temp_frame_path):
                    current_modified = os.path.getmtime(self.temp_frame_path)
                    
                    # อ่านไฟล์เฉพาะเมื่อมีการอัพเดท
                    if current_modified != last_modified:
                        last_modified = current_modified
                        
                        # อ่านภาพ
                        frame = cv2.imread(self.temp_frame_path)
                        if frame is not None and frame.size > 0:
                            # Convert frame to Qt format
                            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            h, w, ch = rgb_image.shape
                            bytes_per_line = ch * w
                            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                            
                            # Scale image to desired size
                            scaled_image = qt_image.scaled(720, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            
                            # Emit signal with the processed image
                            self.change_pixmap_signal.emit(scaled_image)
                            frame_count += 1
                            
                            if frame_count % 100 == 0:
                                print(f"GUI received {frame_count} frames")
                        else:
                            print("Warning: Could not read temp frame file")
                            
                else:
                    # ถ้ายังไม่มีไฟล์
                    if frame_count % 50 == 0:
                        print("Waiting for temp_frame.jpg from line_detected_plate.py...")
                    time.sleep(0.1)
                    frame_count += 1
                    continue
                    
            except Exception as e:
                print(f"Error reading temp frame: {e}")
                time.sleep(0.1)
                continue
            
            # Small delay
            time.sleep(0.033)  # ~30 FPS
    
    def stop(self):
        """Stop the video thread"""
        self.running = False
        print("GUI VideoThread stopped")
        self.wait()
    
    def get_current_frame(self):
        """Get current frame for processing"""
        if os.path.exists(self.temp_frame_path):
            return cv2.imread(self.temp_frame_path)
        return None
    
    def is_camera_connected(self):
        """Check if camera is connected"""
        return os.path.exists(self.temp_frame_path)
    
class ModernButton(QPushButton):
    def __init__(self, text, color_scheme="primary"):
        super().__init__(text)
        self.color_scheme = color_scheme
        self.setStyleSheet(self.get_style())
        
    def get_style(self):
        if self.color_scheme == "success":
            return """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #4CAF50, stop:1 #45a049);
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    font-size: 14px;
                    font-weight: 600;
                    border-radius: 8px;
                    min-width: 140px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #5CBF60, stop:1 #4CAF50);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #3d8b40, stop:1 #2e7d32);
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #666666;
                }
            """
        elif self.color_scheme == "danger":
            return """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #f44336, stop:1 #d32f2f);
                    color: white;
                    border: none;
                    padding: 12px 25px;
                    font-size: 14px;
                    font-weight: 600;
                    border-radius: 8px;
                    min-width: 140px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #f66356, stop:1 #f44336);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #c62828, stop:1 #b71c1c);
                }
            """
        else:  # warning/yellow
            return """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #FF9800, stop:1 #F57C00);
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    font-size: 12px;
                    font-weight: 600;
                    border-radius: 6px;
                    min-width: 280px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #FFB74D, stop:1 #FF9800);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #E65100, stop:1 #BF360C);
                }
            """

class SystemGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ระบบเรียกชื่อนักเรียนจากป้ายทะเบียนรถผู้ปกครอง")
        # เพิ่มขนาดหน้าต่างให้ใหญ่ขึ้นเพื่อรองรับกล้องที่ใหญ่ขึ้น
        self.setGeometry(100, 100, 1400, 900)
        
        # เก็บ process ที่รันอยู่
        self.running_processes = []
        
        # สร้าง video thread
        self.video_thread = VideoThread()
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        
        # ตั้งค่าธีมสีเข้ม (ปรับปรุงแล้ว - ลบ properties ที่ไม่รองรับออก)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460);
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout หลัก
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header Section (ปรับปรุงแล้ว - เพิ่มความสูงและปรับฟอนต์)
        header_frame = QFrame()
        header_frame.setFixedHeight(60)  # ลดจาก 100 เป็น 60
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
                margin: 3px;
            }
        """)

        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 5, 10, 5)  # ลด margin
        title_label = QLabel("📢 ระบบเรียกชื่อนักเรียนจากป้ายทะเบียนรถผู้ปกครอง")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
                background: transparent;
                padding: 5px;
                line-height: 1.2;
            }
        """)
        header_layout.addWidget(title_label)
        main_layout.addWidget(header_frame)
        
        # Content Layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # ส่วนซ้าย - Camera Section (ขยายขนาด)
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        # Camera Title
        camera_title = QLabel("📹 ภาพทะเบียนรถ (สด)")
        camera_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #ffffff;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        """)
        camera_title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(camera_title)
        
        # สร้าง container สำหรับ camera เพื่อจัดให้อยู่ตรงกลาง
        camera_container = QWidget()
        camera_container_layout = QHBoxLayout(camera_container)
        camera_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # เพิ่ม spacer ด้านซ้าย
        camera_container_layout.addStretch()
        
        # กรอบแสดงกล้อง (ขยายขนาดใหม่ให้ใหญ่ขึ้นมาก)
        self.camera_label = QLabel("📷 กำลังรอภาพจากกล้อง...")
        self.camera_label.setFixedSize(720, 480)  # ขยายจาก 580x360 เป็น 720x480
        self.camera_label.setStyleSheet("""
            QLabel {
                border: 3px solid #4CAF50;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #2c3e50, stop:1 #34495e);
                border-radius: 12px;
                font-size: 16px;
                color: #ecf0f1;
                font-weight: 500;
                padding: 20px;
            }
        """)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setScaledContents(True)  # ให้ภาพขยายเต็มกรอบ
        camera_container_layout.addWidget(self.camera_label)
        
        # เพิ่ม spacer ด้านขวา
        camera_container_layout.addStretch()
        
        left_layout.addWidget(camera_container)
        
        # เพิ่ม MQTT Broker IP Section
        mqtt_section = QFrame()
        mqtt_section.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.15);
                margin: 5px 0px;
            }
        """)
        mqtt_layout = QVBoxLayout(mqtt_section)
        mqtt_layout.setContentsMargins(15, 10, 15, 10)
        mqtt_layout.setSpacing(8)

        # หัวข้อ MQTT
        mqtt_title = QLabel("🌐 IP ของเซิร์ฟเวอร์ MQTT")
        mqtt_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #ffffff;
                padding: 5px;
            }
        """)
        mqtt_title.setAlignment(Qt.AlignCenter)
        mqtt_layout.addWidget(mqtt_title)

        # แสดง IP Address และปุ่ม Refresh ในบรรทัดเดียวกัน
        ip_control_layout = QHBoxLayout()
        ip_control_layout.setSpacing(10)

        # แสดง IP Address
        self.mqtt_ip_label = QLabel("Loading IP...")
        self.mqtt_ip_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: 500;
                color: #00ff88;
                padding: 8px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 6px;
                border: 1px solid #00ff88;
                font-family: 'Consolas', 'Monaco', monospace;
                min-width: 150px;
            }
        """)
        self.mqtt_ip_label.setAlignment(Qt.AlignCenter)
        ip_control_layout.addWidget(self.mqtt_ip_label)

        # ปุ่ม Refresh IP
        self.refresh_ip_button = QPushButton("🔄 รีเฟรช IP")
        self.refresh_ip_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2196F3, stop:1 #1976D2);
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 11px;
                font-weight: 600;
                border-radius: 6px;
                min-width: 80px;
                max-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #42A5F5, stop:1 #2196F3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #1565C0, stop:1 #0D47A1);
            }
        """)
        self.refresh_ip_button.clicked.connect(self.run_ipv4_script)
        ip_control_layout.addWidget(self.refresh_ip_button)

        mqtt_layout.addLayout(ip_control_layout)
        left_layout.addWidget(mqtt_section)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # เพิ่ม spacer เพื่อจัดปุ่มให้อยู่ตรงกลาง
        button_layout.addStretch()
        
        # ปุ่มเริ่มโปรแกรม
        self.start_button = ModernButton("🚀 เริ่มต้นระบบ", "success")
        self.start_button.clicked.connect(self.start_program)
        button_layout.addWidget(self.start_button)
        
        # ปุ่มปิดโปรแกรม
        self.stop_button = ModernButton("🛑 หยุดระบบ", "danger")
        self.stop_button.clicked.connect(self.stop_program)
        button_layout.addWidget(self.stop_button)
        
        # เพิ่ม spacer เพื่อจัดปุ่มให้อยู่ตรงกลาง
        button_layout.addStretch()
        
        left_layout.addLayout(button_layout)
        content_layout.addWidget(left_frame)
        
        # ส่วนขวา - Information Panel
        right_frame = QFrame()
        right_frame.setFixedWidth(350)
        right_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setSpacing(15)
        right_layout.setContentsMargins(20, 20, 20, 20)
        
        # กรอบแสดงข้อมูล Log
        log_title = QLabel("📝 ประวัติการมารับนักเรียน")
        log_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #ffffff;
                padding: 5px;
            }
        """)
        right_layout.addWidget(log_title)
        
        self.text_display = QTextEdit()
        self.text_display.setFixedHeight(380)  # เพิ่มความสูงให้สอดคล้องกับกล้องที่ใหญ่ขึ้น
        self.text_display.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 0, 0, 0.3);
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 15px;
                font-size: 11px;
                font-family: 'Consolas', 'Monaco', monospace;
                color: #00ff00;
                line-height: 1.2;
            }
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.1);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #4CAF50;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #66BB6A;
            }
        """)
        self.text_display.setPlaceholderText("📄 Waiting for log data from txt_file/log.txt...")
        right_layout.addWidget(self.text_display)
        
        # Database Manager Section
        self.phpmyadmin_button = ModernButton("🗄️ จัดการข้อมูลนักเรียน", "warning")
        self.phpmyadmin_button.clicked.connect(lambda: self.open_url("http://localhost/website"))
        right_layout.addWidget(self.phpmyadmin_button)
        
        # Student attendance statistics Section  
        self.youtube_button = ModernButton("📈 สถิติการมารับนักเรียน", "warning")
        self.youtube_button.clicked.connect(lambda: self.open_url("http://localhost/website/statistics.php"))
        right_layout.addWidget(self.youtube_button)
        
        # Setting Camera Section
        self.camera_setting_button = QPushButton("📷  ตั้งค่าระยะตรวจจับป้ายทะเบียน")
        self.camera_setting_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #6C63FF, stop:1 #5A52FF);
                color: white;
                border: none;
                padding: 10px 15px;
                font-size: 12px;
                font-weight: 600;
                border-radius: 6px;
                min-width: 280px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #7C73FF, stop:1 #6C63FF);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4A42FF, stop:1 #3A32FF);
            }
        """)
        self.camera_setting_button.clicked.connect(self.run_camera_setting)
        right_layout.addWidget(self.camera_setting_button)
        
        # Delay Servo Section
        delay_servo_section = QFrame()
        delay_servo_section.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.15);
                margin: 5px 0px;
            }
        """)
        delay_servo_layout = QVBoxLayout(delay_servo_section)
        delay_servo_layout.setContentsMargins(15, 10, 15, 10)
        delay_servo_layout.setSpacing(8)

        # หัวข้อ delay_servo
        delay_servo_title = QLabel("⏱️ หน่วงเวลาการปิดไม้กั้น")
        delay_servo_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #ffffff;
                padding: 5px;
            }
        """)
        delay_servo_title.setAlignment(Qt.AlignCenter)
        delay_servo_layout.addWidget(delay_servo_title)

        # Input และปุ่ม Save ในบรรทัดเดียวกัน
        delay_control_layout = QHBoxLayout()
        delay_control_layout.setSpacing(10)

        # Input สำหรับ delay_servo
        from PyQt5.QtWidgets import QLineEdit
        self.delay_servo_input = QLineEdit()
        self.delay_servo_input.setPlaceholderText("5")
        self.delay_servo_input.setStyleSheet("""
            QLineEdit {
                font-size: 12px;
                font-weight: 500;
                color: #ffffff;
                padding: 8px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 6px;
                border: 1px solid #00ff88;
                font-family: 'Consolas', 'Monaco', monospace;
                min-width: 60px;
                max-width: 80px;
            }
            QLineEdit:focus {
                border: 2px solid #00ff88;
            }
        """)
        delay_control_layout.addWidget(self.delay_servo_input)

        # Label "Second"
        second_label = QLabel("วินาที")
        second_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: 500;
                color: #ffffff;
                padding: 5px;
            }
        """)
        delay_control_layout.addWidget(second_label)

        # ปุ่ม Save
        self.save_delay_button = QPushButton("💾 บันทึก")
        self.save_delay_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 11px;
                font-weight: 600;
                border-radius: 6px;
                min-width: 60px;
                max-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #5CBF60, stop:1 #4CAF50);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #3d8b40, stop:1 #2e7d32);
            }
        """)
        self.save_delay_button.clicked.connect(self.save_delay_servo)
        delay_control_layout.addWidget(self.save_delay_button)

        delay_servo_layout.addLayout(delay_control_layout)
        right_layout.addWidget(delay_servo_section)
        
        # Status Indicator
        self.status_label = QLabel("⚡ สถานะระบบ: พร้อมทำงาน")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: 600;
                color: #4CAF50;
                padding: 8px;
                background: rgba(76, 175, 80, 0.2);
                border-radius: 6px;
                border: 1px solid #4CAF50;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.status_label)
        
        content_layout.addWidget(right_frame)
        main_layout.addLayout(content_layout)
        
        central_widget.setLayout(main_layout)
        
        # เริ่มแสดงกล้อง
        # self.video_thread.start()

        # Timer สำหรับอัพเดทข้อมูลจากไฟล์ .txt
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_text_display)
        self.timer.timeout.connect(self.update_mqtt_ip_display)  # เพิ่มการอัพเดท MQTT IP
        self.timer.timeout.connect(self.load_delay_servo_value)  # เพิ่มการโหลดค่า delay_servo
        self.timer.start(1000)  # อัพเดททุก 1 วินาที
        
        # อัพเดท MQTT IP และ delay_servo ทันทีเมื่อเริ่มโปรแกรม
        self.update_mqtt_ip_display()
        self.load_delay_servo_value()

    def run_camera_setting(self):
        """รันไฟล์ camera.py สำหรับตั้งค่ากล้อง"""
        try:
            if os.path.exists('GUI_line_detected_plate.pyw'):
                venv_python = os.path.join("venv", "Scripts", "pythonw.exe")
                process = subprocess.Popen([venv_python, "GUI_line_detected_plate.pyw"])
                print(f"✅ เริ่มรัน GUI_line_detected_plate.pyw - PID: {process.pid}")
            else:
                print("❌ ไม่พบไฟล์ GUI_line_detected_plate.pyw")
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการรัน camera.py: {e}")

    def save_delay_servo(self):
        """บันทึกค่า delay_servo ลงไฟล์ delay_servo.txt"""
        try:
            # อ่านค่าจาก input field
            delay_value = self.delay_servo_input.text().strip()
            
            if not delay_value:
                print("❌ กรุณากรอกค่า delay_servo")
                return
            
            # ตรวจสอบว่าเป็นตัวเลขหรือไม่
            try:
                delay_seconds = float(delay_value)
                delay_milliseconds = int(delay_seconds * 1000)  # แปลงเป็น milliseconds
            except ValueError:
                print("❌ กรุณากรอกตัวเลขที่ถูกต้อง")
                from PyQt5.QtWidgets import QMessageBox
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Invalid Input")
                msg.setText("กรุณากรอกตัวเลขที่ถูกต้อง")
                msg.exec_()
                return
            
            # สร้างโฟลเดอร์ txt_file ถ้ายังไม่มี
            if not os.path.exists('txt_file'):
                os.makedirs('txt_file')
            
            # บันทึกค่าลงไฟล์
            with open('txt_file/delay_servo.txt', 'w', encoding='utf-8') as f:
                f.write(str(delay_milliseconds))
            
            print(f"✅ บันทึกค่า delay_servo: {delay_seconds} วินาที ({delay_milliseconds} milliseconds)")
            
            # แสดงข้อความยืนยัน
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Save Successful")
            msg.setText(f"บันทึกค่า เรียบร้อย ✅")
            msg.exec_()
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการบันทึก delay_servo: {e}")

    def load_delay_servo_value(self):
        """โหลดค่า delay_servo จากไฟล์แสดงใน input field"""
        try:
            if os.path.exists('txt_file/delay_servo.txt'):
                with open('txt_file/delay_servo.txt', 'r', encoding='utf-8') as f:
                    delay_ms = f.read().strip()
                    if delay_ms:
                        # แปลงจาก milliseconds เป็น seconds
                        delay_seconds = int(delay_ms) / 1000
                        # แสดงใน input field (ถ้าไม่มีการแก้ไขอยู่)
                        if not self.delay_servo_input.hasFocus():
                            self.delay_servo_input.setText(str(delay_seconds))
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการโหลด delay_servo: {e}")
        
    def update_image(self, cv_img):
        """อัพเดทภาพจากกล้อง - ปรับปรุงให้แสดงผลเต็มกรอบ"""
        # สร้าง QPixmap จาก QImage
        pixmap = QPixmap.fromImage(cv_img)
        
        # ปรับขนาดให้เต็มกรอบแต่คงอัตราส่วน
        scaled_pixmap = pixmap.scaled(
            self.camera_label.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
  
        self.camera_label.setPixmap(scaled_pixmap)
        
    def run_ipv4_script(self):
        """รันไฟล์ IPv4_Address.py เพื่ออัพเดท IP Address"""
        try:
            # เปลี่ยนข้อความปุ่มขณะกำลังประมวลผล
            self.refresh_ip_button.setText("⏳ Getting IP...")
            self.refresh_ip_button.setEnabled(False)
            
            # รันไฟล์ IPv4_Address.py
            if os.path.exists('IPv4_Address.pyw'):
                process = subprocess.Popen(['python', 'IPv4_Address.pyw'])
                process.wait()  # รอให้เสร็จ
                
                # อัพเดทการแสดงผลทันที
                self.update_mqtt_ip_display()
                
                print("✅ IPv4_Address.pyw executed successfully")
            else:
                print("❌ IPv4_Address.pyw not found")
                self.mqtt_ip_label.setText("❌ IPv4_Address.py not found")
                self.mqtt_ip_label.setStyleSheet("""
                    QLabel {
                        font-size: 12px;
                        font-weight: 500;
                        color: #ff4444;
                        padding: 8px;
                        background: rgba(0, 0, 0, 0.3);
                        border-radius: 6px;
                        border: 1px solid #ff4444;
                        font-family: 'Consolas', 'Monaco', monospace;
                    }
                """)
            
        except Exception as e:
            print(f"❌ Error running IPv4_Address.pyw: {e}")
            self.mqtt_ip_label.setText(f"❌ Error: {str(e)}")
            self.mqtt_ip_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    font-weight: 500;
                    color: #ff4444;
                    padding: 8px;
                    background: rgba(0, 0, 0, 0.3);
                    border-radius: 6px;
                    border: 1px solid #ff4444;
                    font-family: 'Consolas', 'Monaco', monospace;
                }
            """)
        finally:
            # เปลี่ยนข้อความปุ่มกลับ
            self.refresh_ip_button.setText("🔄 Get IPv4")
            self.refresh_ip_button.setEnabled(True)
    
    def update_mqtt_ip_display(self):
        """อัพเดทการแสดงผล MQTT Broker IP จากไฟล์"""
        try:
            if os.path.exists('txt_file/mqtt_broker_ip.txt'):
                with open('txt_file/mqtt_broker_ip.txt', 'r', encoding='utf-8') as file:
                    ip_content = file.read().strip()
                    if ip_content:
                        self.mqtt_ip_label.setText(f"📡 {ip_content}")
                        self.mqtt_ip_label.setStyleSheet("""
                            QLabel {
                                font-size: 12px;
                                font-weight: 500;
                                color: #00ff88;
                                padding: 8px;
                                background: rgba(0, 0, 0, 0.3);
                                border-radius: 6px;
                                border: 1px solid #00ff88;
                                font-family: 'Consolas', 'Monaco', monospace;
                            }
                        """)
                    else:
                        self.mqtt_ip_label.setText("📡 No IP found")
                        self.mqtt_ip_label.setStyleSheet("""
                            QLabel {
                                font-size: 12px;
                                font-weight: 500;
                                color: #ffaa00;
                                padding: 8px;
                                background: rgba(0, 0, 0, 0.3);
                                border-radius: 6px;
                                border: 1px solid #ffaa00;
                                font-family: 'Consolas', 'Monaco', monospace;
                            }
                        """)
            else:
                self.mqtt_ip_label.setText("📡 mqtt_broker_ip.txt not found")
                self.mqtt_ip_label.setStyleSheet("""
                    QLabel {
                        font-size: 12px;
                        font-weight: 500;
                        color: #ffaa00;
                        padding: 8px;
                        background: rgba(0, 0, 0, 0.3);
                        border-radius: 6px;
                        border: 1px solid #ffaa00;
                        font-family: 'Consolas', 'Monaco', monospace;
                    }
                """)
        except Exception as e:
            self.mqtt_ip_label.setText(f"❌ Error reading IP: {str(e)[:20]}...")
            self.mqtt_ip_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    font-weight: 500;
                    color: #ff4444;
                    padding: 8px;
                    background: rgba(0, 0, 0, 0.3);
                    border-radius: 6px;
                    border: 1px solid #ff4444;
                    font-family: 'Consolas', 'Monaco', monospace;
                }
            """)

    def start_program(self):
        """เริ่มโปรแกรม - รันไฟล์ทั้งหมด"""
        # path ไปยัง pythonw.exe ใน venv
        venv_python = os.path.join("venv", "Scripts", "pythonw.exe")
        process = subprocess.Popen([venv_python, "compare_data.pyw"])
        while True:
            if os.path.exists("txt_file/databases_status.txt"):
                with open("txt_file/databases_status.txt") as f:
                    c = f.read().strip()
                    if c in ("0","1"):
                        break
        try:
            with open("txt_file/databases_status.txt", "r") as f:
                if f.read().strip() == "0":
                    with open("txt_file/databases_status.txt", "w") as f:
                        f.truncate(0)
                    QMessageBox.critical(None, "ข้อผิดพลาด", "ไม่สามารถเข้าถึงฐานข้อมูลได้\nโปรดเปิดโปรแกรม Xampp")
                    return  # ❌ หยุดการทำงานของฟังก์ชันทันที
        except:
            QMessageBox.critical(None, "ข้อผิดพลาด", "")
            return
        try:
            
            # ปิด process เก่าก่อน (ถ้ามี)
            self.stop_program()

            with open('txt_file/car_plate.txt', 'w') as f:
                f.truncate(0)
            with open('txt_file/names.txt', 'w') as f:
                f.truncate(0)

            for filename in os.listdir('result_plate'):
                file_path = os.path.join('result_plate', filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            # เริ่ม video thread
            if not self.video_thread.isRunning():
                self.video_thread.start()
                print("✅ เริ่มกล้อง")
            
            # รันไฟล์ python แต่ละตัว
            files_to_run = [
                'line_detected_plate.pyw',
                'arduino_connect.pyw',
                'detected_caracter.pyw',
                'text_to_speak.pyw'
            ]

            self.running_processes = []

            for file_name in files_to_run:
                if os.path.exists(file_name):
                    process = subprocess.Popen([venv_python, file_name])
                    self.running_processes.append(process)

                    print(f"✅ เริ่มรัน {file_name} - PID: {process.pid}")
                else:
                    print(f"❌ ไม่พบไฟล์ {file_name}")
            
            # แสดงสถานะ
            if self.running_processes:
                self.start_button.setText("🔄 ระบบกำลังทำงาน...")
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.status_label.setText("🟢  สถานะระบบ: ทำงานอยู่")
                self.status_label.setStyleSheet("""
                    QLabel {
                        font-size: 12px;
                        font-weight: 600;
                        color: #4CAF50;
                        padding: 8px;
                        background: rgba(76, 175, 80, 0.3);
                        border-radius: 6px;
                        border: 1px solid #4CAF50;
                    }
                """)
            else:
                self.status_label.setText("🔴  สถานะระบบ: ไม่ได้ทำงาน")
                self.status_label.setStyleSheet("""
                    QLabel {
                        font-size: 12px;
                        font-weight: 600;
                        color: #f44336;
                        padding: 8px;
                        background: rgba(244, 67, 54, 0.2);
                        border-radius: 6px;
                        border: 1px solid #f44336;
                    }
                """)
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการเริ่มโปรแกรม: {e}")
            self.status_label.setText("🔴 สถานะระบบ: เกิดข้อผิดพลาด")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    font-weight: 600;
                    color: #f44336;
                    padding: 8px;
                    background: rgba(244, 67, 54, 0.2);
                    border-radius: 6px;
                    border: 1px solid #f44336;
                }
            """)
    
    def stop_program(self):
        """ปิดโปรแกรม - หยุดการทำงานของไฟล์ต่างๆ"""
        with open("txt_file/databases_status.txt", "w") as f:
                f.truncate(0)
        try:
            
            # หยุด video thread
            if self.video_thread.isRunning():
                self.video_thread.stop()
                print("🛑 ปิดกล้อง")

            # ปิด process ทั้งหมด
            for process in self.running_processes:
                if process.poll() is None:  # ถ้า process ยังทำงานอยู่
                    process.terminate()
                    process.wait()  # รอให้ process ปิดสมบูรณ์
                    print(f"🛑 ปิด process PID: {process.pid}")
            
            # ล้างรายการ process
            self.running_processes.clear()
            
            # เปลี่ยนสถานะปุ่ม
            self.start_button.setText("🚀 เริ่มต้นระบบ")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.status_label.setText("⚡ สถานะระบบ: หยุดทำงาน")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    font-weight: 600;
                    color: #ff9800;
                    padding: 8px;
                    background: rgba(255, 152, 0, 0.2);
                    border-radius: 6px;
                    border: 1px solid #ff9800;
                }
            """)
            
            print("✅ ปิดโปรแกรมทั้งหมดเรียบร้อย")
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการปิดโปรแกรม: {e}")
    
    def open_url(self, url):
        """เปิด URL ในเบราเซอร์"""
        try:
            webbrowser.open(url)
            print(f"🌐 เปิด URL: {url}")
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการเปิด URL: {e}")
    
    def update_text_display(self):
        """อัพเดทข้อมูลจากไฟล์ log.txt"""
        try:
            if os.path.exists('txt_file/log.txt'):
                with open('txt_file/log.txt', 'r', encoding='utf-8') as file:
                    content = file.read()
                    # เพิ่ม timestamp และ formatting
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    formatted_content = f"[{timestamp}] 🔄 อัปเดตบันทึกล่าสุด\n" + "="*40 + "\n" + content
                    self.text_display.setPlainText(formatted_content)
                    # เลื่อนไปยังบรรทัดล่าสุด
                    cursor = self.text_display.textCursor()
                    cursor.movePosition(cursor.End)
                    self.text_display.setTextCursor(cursor)
            else:
                # แสดงข้อความเมื่อไม่พบไฟล์
                self.text_display.setPlainText("📁 Log file not found: txt_file/log.txt\n📝 Waiting for system to create log file...")
        except Exception as e:
            error_msg = f"❌ Error reading log file: {str(e)}\n📁 Expected location: txt_file/log.txt"
            self.text_display.setPlainText(error_msg)
    
    def closeEvent(self, event):
        """จัดการเมื่อปิดหน้าต่าง"""
        # ปิดโปรแกรมทั้งหมด
        self.stop_program()
        with open("txt_file/databases_status.txt", "w") as f:
            f.truncate(0)
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # ตั้งค่าการแสดงผล
    app.setApplicationName("Student Name Announcement System Based on Parent License Plates")
    
    # ตั้งค่าฟอนต์เริ่มต้น
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = SystemGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

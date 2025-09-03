#include <WiFi.h>
#include <WiFiManager.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>
#include "esp_sleep.h"
#include <Preferences.h>

Preferences preferences;

// ============ อ็อบเจกต์ ============
WiFiClient espClient;
PubSubClient client(espClient);
Servo myServo;

// ============ ขาอุปกรณ์ ============
#define BUZZER_PIN 27
#define SENSOR_PIN 33      // ✅ ต้องใช้ GPIO ที่ปลุกได้จาก deep sleep
#define SERVO_PIN 14
#define RESET_BUTTON 4

// ============ ตัวแปร ============
char mqtt_server[40];
int previousSensorValue = HIGH;
unsigned long lastActivityMillis = 0;
const unsigned long IDLE_TIMEOUT_MS = 2 * 60 * 1000UL;  // 2 นาที

int delay_servo = 3000 ;

// ============ ฟังก์ชัน MQTT ============
bool connectMQTT() {
  while (!client.connected()) {
    Serial.println("Connecting to MQTT Broker...");
    if (client.connect("ESP32Client")) {
      Serial.println("MQTT connected");
      client.subscribe("esp8266/feedback");
      return true;
    } else {
      Serial.printf("MQTT connection failed, state: %d\n", client.state());
      delay(2000);
    }
  }
  return false;
}

// ============ ฟังก์ชันควบคุมเซอร์โว ============
void controlServo(const String& command) {
  if (command == "open") {
    Serial.println("เปิดเซอร์โว");
    playSound(1);
    myServo.write(90);

    while (digitalRead(SENSOR_PIN) == LOW) {
      Serial.println("เซ็นเซอร์ยังเจอวัตถุ");
      delay(200);
    }

    delay(delay_servo);
    Serial.println("เซ็นเซอร์ไม่เจอวัตถุแล้ว");
    myServo.write(0);

    if (!client.connected()) {
      Serial.println("MQTT ขาดการเชื่อมต่อ กำลัง reconnect...");
      if (connectMQTT()) {
        Serial.println("Reconnect MQTT สำเร็จ");
      } else {
        Serial.println("Reconnect MQTT ไม่สำเร็จ ไม่สามารถส่งคำสั่งได้");
        return;
      }
    }

    if (client.publish("esp8266/commands", "stop")) {
      Serial.println("ส่งคำสั่ง stop สำเร็จ");
    } else {
      Serial.println("ส่งคำสั่ง stop ไม่สำเร็จ");
    }
  } else if (command == "close") {
    Serial.println("ไม่เปิดเซอร์โว");
  }
}

// ============ Callback MQTT ============
void callback(char* topic, byte* payload, unsigned int length) {
  String message = String((char*)payload).substring(0, length);
  Serial.printf("Received message: %s\n", message.c_str());

  if (message.startsWith("delay=")) {
    int newDelay = message.substring(6).toInt();
    if (newDelay > 0) {
      delay_servo = newDelay;
      preferences.begin("config", false);  // เปิดในโหมดเขียน
      preferences.putInt("delay_servo", delay_servo);
      preferences.end();
      Serial.printf("เปลี่ยน delay_servo เป็น %d ms\n", delay_servo);
    }
  } else {
    controlServo(message);
  }
}

// ============ ฟังก์ชันเสียง ============
void playSound(int mode) {
  if (mode == 1) {
    digitalWrite(BUZZER_PIN, HIGH); delay(300); digitalWrite(BUZZER_PIN, LOW);
  } else if (mode == 2) {
    digitalWrite(BUZZER_PIN, HIGH); delay(100); digitalWrite(BUZZER_PIN, LOW);
    delay(100); digitalWrite(BUZZER_PIN, HIGH); delay(100); digitalWrite(BUZZER_PIN, LOW);
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(SENSOR_PIN, INPUT);
  pinMode(RESET_BUTTON, INPUT_PULLUP);
  digitalWrite(BUZZER_PIN, LOW);
  pinMode(2, OUTPUT);
  digitalWrite(2, LOW);              // ปิดไฟ

  // โหลดค่า MQTT server จาก flash
  preferences.begin("config", true);  // read-only
  String savedServer = preferences.getString("mqtt_server", "192.168.1.100");
  int storedDelay = preferences.getInt("delay_servo", 3000); // default 3000 ms
  delay_servo = storedDelay;
  Serial.printf("โหลด delay_servo จาก flash: %d ms\n", delay_servo);
  preferences.end();
  strncpy(mqtt_server, savedServer.c_str(), sizeof(mqtt_server));
  
  // ============ ปลุกจาก GPIO ถ้าไม่มีวัตถุ ============
  if (esp_sleep_get_wakeup_cause() == ESP_SLEEP_WAKEUP_EXT0) {
    Serial.println("📤 ตื่นจาก Deep Sleep (GPIO Wakeup)");
  } else {
    Serial.println("🔁 เปิดเครื่องปกติ");
  }

// 🔁 รีเซ็ต WiFi ถ้ากดปุ่ม
  if (digitalRead(RESET_BUTTON) == LOW) {
    Serial.println("รีเซ็ตค่า WiFi...");
    WiFiManager wm;
    wm.resetSettings();
    digitalWrite(BUZZER_PIN, HIGH); delay(50); digitalWrite(BUZZER_PIN, LOW);
    delay(1950);
    ESP.restart();
    delay(5000);
  }

  // ============ WiFiManager ============
  WiFiManager wm;
  wm.setTimeout(120);
  WiFiManagerParameter custom_mqtt("server", "MQTT Server", mqtt_server, 40);
  wm.addParameter(&custom_mqtt);

  if (!wm.autoConnect("ESP-Setup")) {
    Serial.println("❌ WiFi connect failed. Restarting...");
    ESP.restart();
  }

  // บันทึกค่า MQTT server ที่กรอกผ่าน WiFiManager
  strcpy(mqtt_server, custom_mqtt.getValue());
  preferences.begin("config", false);  // read-write
  preferences.putString("mqtt_server", mqtt_server);
  preferences.end();

  Serial.println("WiFi connected");
  Serial.print("MQTT Server: ");
  Serial.println(mqtt_server);

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  
  if (!client.connected()) {
    connectMQTT();
  }

  myServo.attach(SERVO_PIN);
  myServo.write(0);

  // ตั้งเวลาเริ่มต้น
  lastActivityMillis = millis();
}

void loop() {
  if (!client.connected() && !connectMQTT()) return;
  client.loop();

  int sensorValue = digitalRead(SENSOR_PIN);
  if (sensorValue != previousSensorValue) {
    const char* message;
    if (sensorValue == LOW) {
      message = "start";
      playSound(2);
    } else {
      message = "stop";
    }
    client.publish("esp8266/commands", message);
    Serial.printf("Published: %s\n", message);
    previousSensorValue = sensorValue;
    
    lastActivityMillis = millis();  // รีเซ็ตเวลา
  }

  // ============ ตรวจจับไม่มีวัตถุ → sleep ============
  if (digitalRead(SENSOR_PIN) == HIGH && millis() - lastActivityMillis >= IDLE_TIMEOUT_MS) {
    Serial.println("😴 ไม่พบวัตถุนานเกิน 2 นาที → เข้าสู่ Deep Sleep");

    // ปลุกเมื่อ SENSOR_PIN เป็น LOW (มีวัตถุ)
    esp_sleep_enable_ext0_wakeup((gpio_num_t)SENSOR_PIN, 0);  // LOW = wakeup
    delay(100);
    esp_deep_sleep_start();
  }

  delay(100);  // ลดโหลด CPU
}

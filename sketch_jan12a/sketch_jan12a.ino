#include <ESP32Servo.h>  // ใช้ไลบรารี ESP32Servo สำหรับ ESP32
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#define WIFI_STA_NAME "SIT-IIoT"
#define WIFI_STA_PASS "Sit1To#Down!9"

#define MQTT_SERVER "mqtt.bookmark.scnd.app"
#define MQTT_PORT 1883
#define MQTT_USERNAME "iothack"
#define MQTT_PASSWORD "iot1234"
#define MQTT_NAME "RANDOMNAME"
WiFiClient client;
PubSubClient mqtt(client);


// ตั้งค่า I2C Address สำหรับหน้าจอ OLED
#define i2c_Address 0x3c

#define SCREEN_WIDTH 128  // ความกว้างหน้าจอ OLED
#define SCREEN_HEIGHT 64  // ความสูงหน้าจอ OLED
#define OLED_RESET -1     // ไม่มีการใช้ขา reset สำหรับหน้าจอ OLED

Adafruit_SH1106G display = Adafruit_SH1106G(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

Servo myServo;
Servo myServo2;
Servo myServo3;

// ฟังก์ชันสำหรับแสดงข้อความบน OLED
void displayMessage(const char* message) {
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SH110X_WHITE);
  display.setCursor(0, 0);
  display.println(message);
  display.display();
  delay(1000);  // แสดงผล 1 วินาที
}

// ฟังก์ชันสำหรับหมุน Servo
void rotateServo(Servo& servo, int angle, const char* message) {
  servo.write(angle);
  // displayMessage(message);
}

void callback(char* topic, byte* payload, unsigned int length) {

   // Convert payload to a string
  char jsonString[length + 1];
  memcpy(jsonString, payload, length);
  jsonString[length] = '\0';

  // Parse JSON payload
  StaticJsonDocument<200> doc;  // Adjust size based on expected payload
  DeserializationError error = deserializeJson(doc, jsonString);

  // Check for errors in parsing
  if (error) {
    Serial.print("Failed to parse JSON: ");
    Serial.println(error.c_str());
    return;
  }

  // Extract data from JSON
  const char* trashType = doc["item"];  // Example: {"trashType": "bottle"}
  const char* code = doc["code"];

  displayMessage("Bottle\nSeparator\nPrepairing...");
  delay(1000);
  displayMessage("Ready");
  Serial.println("Received JSON Payload:");
  Serial.print("code: ");
  Serial.println(code);

  // Act based on the trash type
  if (String(trashType) == "bottle") {
    Serial.println("bottle");
    rotateServo(myServo2, 0, "Servo 2 rotating CW");
    delay(1000);
    rotateServo(myServo2, 90, "Servo 2 stopped");
  } else if (String(trashType) == "can") {
    rotateServo(myServo2, 180, "Servo 2 rotating CW");
    delay(1000);
    rotateServo(myServo2, 90, "Servo 2 stopped");
  }
  displayMessage("finished");
  delay(1000);

  // Display message on OLED
  String displayText = String("Code:") + code;
  displayMessage(displayText.c_str());
  delay(10000);
  displayMessage("Ready");
}

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_STA_NAME, WIFI_STA_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  mqtt.setServer(MQTT_SERVER, MQTT_PORT);
  mqtt.setCallback(callback);

  // กำหนดขา PWM สำหรับ Servo
  myServo2.attach(13);

  // แสดงข้อความต้อนรับบน OLED
  display.begin(i2c_Address, true);
  displayMessage("Welcome\nBottle\nSeparator");
  delay(2000);
  displayMessage("Ready");

  // หยุด Servo
  rotateServo(myServo2, 90, "Servo 2 stopped");
}

void loop() {
    if (mqtt.connected() == false) {
    Serial.print("MQTT connection... ");
    if (mqtt.connect(MQTT_NAME, MQTT_USERNAME, MQTT_PASSWORD)) {
      Serial.println("connected");
      mqtt.subscribe("bottleSeparator/trash"); //change to your topic
    } else {
      Serial.println("failed");
      delay(5000);
    }
  } else {
    mqtt.loop();
  }
    // หมุน Servo ตัวแรกตามเข็มนาฬิกา 360 องศา
    // rotateServo(myServo, 180, "Servo rotating CW");
    // delay(1000);  // ปรับเวลาตามความเร็วของ Servo
    // rotateServo(myServo, 90, "Servo stopped");

    // rotateServo(myServo2, 180, "Servo 2 rotating CW");
    // delay(1000);  // ปรับเวลาตามความเร็วของ Servo
    // rotateServo(myServo2, 90, "Servo 2 stopped");

    // // หมุน Servo ตัวที่สองตามเข็มนาฬิกา 360 องศา
    // rotateServo(myServo3, 180, "Servo 3 rotating CW");
    // delay(1000);  // ปรับเวลาตามความเร็วของ Servo
    // rotateServo(myServo3, 90, "Servo 3 stopped");
}
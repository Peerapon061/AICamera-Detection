#include <WiFi.h>
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

const int pingPin = 5;
int inPin = 18;

void setup() {
  Serial.begin(115200);
  pinMode(19, OUTPUT);
  digitalWrite(19, LOW);

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
}

void loop() {
  if (mqtt.connected() == false) {
    Serial.print("MQTT connection... ");
    if (mqtt.connect(MQTT_NAME, MQTT_USERNAME, MQTT_PASSWORD)) {
      Serial.println("connected");
    } else {
      Serial.println("failed");
      delay(5000);
    }}
    else {
      mqtt.loop();
      long duration, cm;

      pinMode(pingPin, OUTPUT);

      digitalWrite(pingPin, LOW);
      delayMicroseconds(2);
      digitalWrite(pingPin, HIGH);
      delayMicroseconds(5);
      digitalWrite(pingPin, LOW);
      pinMode(inPin, INPUT);
      duration = pulseIn(inPin, HIGH);

      cm = microsecondsToCentimeters(duration);

      Serial.print(cm);
      Serial.print("cm");
      Serial.println();
      delay(100);
      digitalWrite(19, LOW);

      if (cm < 15) {
        digitalWrite(19, HIGH);
        mqtt.publish("bottleSeparator/camera","on camera");
        delay(8000);
      }
      // รอ 1 วินาที
    }
  }

  long microsecondsToCentimeters(long microseconds) {
    // The speed of sound is 340 m/s or 29 microseconds per centimeter.
    // The ping travels out and back, so to find the distance of the
    // object we take half of the distance travelled.
    return microseconds / 29 / 2;
  }

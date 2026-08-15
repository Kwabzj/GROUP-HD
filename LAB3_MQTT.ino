#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// Wi-Fi credentials
const char* ssid = "SmartSense_WiFi";
const char* password = "SmartSense2026";

const char* mqtt_server = "10.232.107.137";
const char* mqtt_topic = "esp32/sensors";

#define DHTPIN 4
#define DHTTYPE DHT11

constexpr int LDR_PIN = 32;
constexpr int TRIG_PIN = 5;
constexpr int ECHO_PIN = 18;
constexpr int LED_PIN = 2;

DHT dht(DHTPIN, DHTTYPE);

const unsigned long PRINT_INTERVAL_MS = 2000;

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long previousMillis = 0;

void setup_wifi() {

  delay(10);

  Serial.println();
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected!");

  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
}

void reconnect_mqtt() {

  while (!client.connected()) {

    Serial.print("Connecting to MQTT broker...");

    String clientId = "SmartSense-";
    clientId += String(random(0xffff), HEX);

    if (client.connect(clientId.c_str())) {

      Serial.println(" connected!");

    } else {

      Serial.print(" failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");

      delay(5000);
    }
  }
}

void setup() {

  Serial.begin(115200);

  analogReadResolution(12);

  dht.begin();

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);

  digitalWrite(TRIG_PIN, LOW);
  digitalWrite(LED_PIN, LOW);

  setup_wifi();

  client.setServer(mqtt_server, 1883);

  Serial.println("DHT11 + LDR + Ultrasonic Sensor Ready");
}

void loop() {

  if (!client.connected()) {
    reconnect_mqtt();
  }

  client.loop();

  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= PRINT_INTERVAL_MS) {

    previousMillis = currentMillis;

    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (isnan(temperature) || isnan(humidity)) {

      Serial.println("DHT11 Read Failed!");

      temperature = 0;
      humidity = 0;
    }

    int ldrRaw = analogRead(LDR_PIN);

    int lightPercent = map(ldrRaw, 0, 4095, 0, 100);
    lightPercent = constrain(lightPercent, 0, 100);

    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);

    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);

    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH, 30000);

    float distance = -1.0;

    if (duration > 0) {
      distance = (duration * 343.0) / 20000.0;
    }

    // LED activates when the temperature is high
    // or when an object is detected within 10 cm
    if (temperature > 35 || (distance > 0 && distance < 10)) {

      digitalWrite(LED_PIN, HIGH);
      Serial.println("DANGER! LED ON");

    } else {

      digitalWrite(LED_PIN, LOW);
    }

    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.print(" °C");

    Serial.print(" | Humidity: ");
    Serial.print(humidity);
    Serial.print("%");

    Serial.print(" | Light: ");
    Serial.print(lightPercent);
    Serial.print("% (Raw: ");
    Serial.print(ldrRaw);
    Serial.print(")");

    Serial.print(" | Distance: ");

    if (distance >= 0) {

      Serial.print(distance, 1);
      Serial.println(" cm");

    } else {

      Serial.println("TIMEOUT");
    }

    char msgBuffer[150];

    snprintf(
      msgBuffer,
      sizeof(msgBuffer),
      "{\"temperature\":%.1f,\"humidity\":%.1f,\"ldr\":%d,\"distance\":%.1f}",
      temperature,
      humidity,
      lightPercent,
      distance >= 0 ? distance : 0.0
    );

    if (client.publish(mqtt_topic, msgBuffer)) {

      Serial.println("MQTT message sent successfully.");

    } else {

      Serial.println("MQTT publish failed!");
    }
  }
}

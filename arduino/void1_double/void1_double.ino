#include <WiFi.h>
#include <WiFiUdp.h>
#include <OSCMessage.h>

//define sound speed in cm/uS
#define SOUND_SPEED 0.034
#define CM_TO_INCH 0.393701

const char* ssid = "Void Network";
const char* password = "**REPLACE ME**";
const char* oscTargetIP = "192.168.0.191";
const int oscTargetPort = 8085;

// CHANGE ME FOR DISTANCE THRESHOLD
const float thresholdInches = 30.0;

const int trigPin = 5;
const int echoPin = 18;

WiFiUDP Udp;


// Sensor 1 pins
const int trigPin1 = 5;
const int echoPin1 = 18;

// Sensor 2 pins
const int trigPin2 = 22;
const int echoPin2 = 23;

void setup() {
    Serial.begin(115200);
    pinMode(trigPin1, OUTPUT);
    pinMode(echoPin1, INPUT);
    pinMode(trigPin2, OUTPUT);
    pinMode(echoPin2, INPUT);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi");

  Udp.begin(oscTargetPort);
}

float getDistance(int trigPin, int echoPin) {
    long duration;
    float distanceCm, distanceInch;
    
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    
    duration = pulseIn(echoPin, HIGH);
    distanceCm = (duration * SOUND_SPEED) / 2;
    distanceInch = distanceCm * CM_TO_INCH;
    
    return distanceInch;
}

void loop() {
    float distance1 = getDistance(trigPin1, echoPin1);
    Serial.print("Sensor 1 Distance (inch): ");
    Serial.print(distance1);
    
    delay(100);
    
    float distance2 = getDistance(trigPin2, echoPin2);
    Serial.print("\tSensor 2 Distance (inch): ");
    Serial.println(distance2);

    OSCMessage msg("/mix");

    if (distance1 <= thresholdInches && distance2 <= thresholdInches) {
      // two people in shared void area
      msg.add(1.0);
    } else if (distance1 <= thresholdInches || distance2 <= thresholdInches) {
      // only 1 person in the shared void area
      msg.add(0.5);
    } else {
      // nobody in void area
      msg.add(0.0);
    }

    Udp.beginPacket(oscTargetIP, oscTargetPort);
    msg.send(Udp);
    Udp.endPacket();
    msg.empty();
    
    delay(500);
}

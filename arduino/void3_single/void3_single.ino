#include <WiFi.h>
#include <WiFiUdp.h>
#include <OSCMessage.h>

//define sound speed in cm/uS
#define SOUND_SPEED 0.034
#define CM_TO_INCH 0.393701

const char* ssid = "Void Network";
const char* password = "**REPLACE ME**";
const char* oscTargetIP = "192.168.0.193";
const int oscTargetPort = 8085;

// CHANGE ME FOR DISTANCE THRESHOLD
const float thresholdInches = 36.0;

const int trigPin = 5;
const int echoPin = 18;

WiFiUDP Udp;

long duration;
float distanceCm;
float distanceInch;

void setup() {
  Serial.begin(115200); // Starts the serial communication
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi");

  Udp.begin(oscTargetPort);
}

void loop() {
  // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  
  // Calculate the distance
  distanceCm = duration * SOUND_SPEED/2;
  
  // Convert to inches
  distanceInch = distanceCm * CM_TO_INCH;
  
  // Prints the distance in the Serial Monitor
  Serial.print("Distance (inch): ");
  Serial.println(distanceInch);

  OSCMessage msg("/mix");

  if (distanceInch <= thresholdInches) {
    msg.add(0.5);
  } else {
    msg.add(0.0);
  }

  Udp.beginPacket(oscTargetIP, oscTargetPort);
  msg.send(Udp);
  Udp.endPacket();
  msg.empty();

  delay(500);
}

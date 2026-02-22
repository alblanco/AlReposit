// Arduino Mega blink test with serial heartbeat
const int LED_PIN = LED_BUILTIN; // Mega built-in LED is pin 13

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(115200);
  delay(1200);
  Serial.println("[blink-test] setup complete");
}

void loop() {
  digitalWrite(LED_PIN, HIGH);
  Serial.println("[blink-test] LED ON");
  delay(500);

  digitalWrite(LED_PIN, LOW);
  Serial.println("[blink-test] LED OFF");
  delay(500);
}

// ESP8266 on-board LED + Serial self-test (no external wiring)
#ifndef LED_BUILTIN
#define LED_BUILTIN 2
#endif

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  delay(300);
  Serial.println("ESP8266 board-only test starting...");
  Serial.print("LED pin: ");
  Serial.println(LED_BUILTIN);
}

void loop() {
  digitalWrite(LED_BUILTIN, LOW);   // ESP8266 onboard LED is usually active-low
  Serial.println("LED ON");
  delay(500);

  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("LED OFF");
  delay(500);
}

// RetroScope - potentiometer reader for Arduino Nano.
//
// Reads up to 7 potentiometers on A0-A6 and streams them over USB
// serial as a comma-separated line, once per loop:
//
//   512,300,1023,0,700,450,200\n
//
// Read on the Raspberry Pi side by inputs/potentiometer_bridge.py.

const int NUM_POTS = 7;
const int PINS[NUM_POTS] = {A0, A1, A2, A3, A4, A5, A6};

void setup() {

  Serial.begin(115200);
}

void loop() {

  for (int i = 0; i < NUM_POTS; i++) {

    Serial.print(analogRead(PINS[i]));

    if (i < NUM_POTS - 1) {
      Serial.print(',');
    }
  }

  Serial.print('\n');

  delay(20); // ~50Hz
}

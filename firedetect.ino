
// #define MQ2_PIN 34   // Analog pin connected to MQ-2 AO
// #define LED_PIN 2    // Onboard LED (ESP32)

// int threshold = 1000;  // Adjust this value based on readings

// void setup() {
//   Serial.begin(115200);
//   pinMode(MQ2_PIN, INPUT);
//   pinMode(LED_PIN, OUTPUT);
//   digitalWrite(LED_PIN, LOW);
//   delay(1000);
//   Serial.println("🔥 Crop Fire Detection Initialized...");
// }

// void loop() {
//   int sensorValue = analogRead(MQ2_PIN);
//   Serial.print("Smoke Level: ");
//   Serial.println(sensorValue);

//   if (sensorValue > threshold) {
//     Serial.println("⚠️ Fire/Smoke Detected!");
//     digitalWrite(LED_PIN, HIGH);
//   } else {
//     digitalWrite(LED_PIN, LOW);
//   }

//   delay(1000);  // read every second
// }


// #include "DHT.h"

// #define DHTPIN 4       // GPIO 4 connected to DATA pin
// #define DHTTYPE DHT11  // Sensor type

// DHT dht(DHTPIN, DHTTYPE);

// void setup() {
//   Serial.begin(115200);
//   Serial.println("🌡️ DHT11 Temperature & Humidity Sensor Test");
//   dht.begin();
// }

// void loop() {
//   delay(500); // DHT11 takes readings every ~2 seconds

//   float humidity = dht.readHumidity();
//   float temperature = dht.readTemperature(); // Celsius

//   // Check if any reads failed
//   if (isnan(humidity) || isnan(temperature)) {
//     Serial.println("❌ Failed to read from DHT sensor!");
//     return;
//   }

//   Serial.print("Humidity: ");
//   Serial.print(humidity);
//   Serial.print(" %\t");
//   Serial.print("Temperature: ");
//   Serial.print(temperature);
//   Serial.println(" °C");

//   // Optional: simple alert if temperature too high
//   if (temperature > 35) {
//     Serial.println("🔥 Warning: High Temperature Detected!");
//   }
// }


// #include "DHT.h"

// #define MQ2_PIN 34       // Analog pin for MQ-2 AO
// #define DHTPIN 4         // Digital pin for DHT11
// #define DHTTYPE DHT11
// #define LED_PIN 2        // Built-in LED

// DHT dht(DHTPIN, DHTTYPE);

// int smokeThreshold = 1000;  // Adjust after calibration

// void setup() {
//   Serial.begin(115200);
//   pinMode(MQ2_PIN, INPUT);
//   pinMode(LED_PIN, OUTPUT);
//   digitalWrite(LED_PIN, LOW);
  
//   Serial.println("🔥 Crop Fire + Weather Monitoring System");
//   Serial.println("Initializing sensors...");
//   dht.begin();
//   delay(2000);
//   Serial.println("✅ Initialization complete\n");
// }

// void loop() {
//   // --- MQ-2 Smoke Reading ---
//   int smokeLevel = analogRead(MQ2_PIN);

//   // --- DHT11 Readings ---
//   float humidity = dht.readHumidity();
//   float temperature = dht.readTemperature(); // Celsius

//   // --- Validate DHT11 Data ---
//   if (isnan(humidity) || isnan(temperature)) {
//     Serial.println("❌ Failed to read from DHT11 sensor!");
//     delay(2000);
//     return;
//   }

//   // --- Print All Data ---
//   Serial.println("📊 SENSOR DATA --------------------");
//   Serial.print("Smoke Level: ");
//   Serial.println(smokeLevel);
//   Serial.print("Temperature: ");
//   Serial.print(temperature);
//   Serial.println(" °C");
//   Serial.print("Humidity: ");
//   Serial.print(humidity);
//   Serial.println(" %");
  
//   // --- Fire / High Temp Alert ---
//   if (smokeLevel > smokeThreshold || temperature > 21.0) {
//     Serial.println("⚠️ ALERT: Possible Fire/Overheat Detected!");
//     digitalWrite(LED_PIN, HIGH);
//   } else {
//     digitalWrite(LED_PIN, LOW);
//   }

//   Serial.println("-----------------------------------\n");
//   delay(2000);
// }


// #define RAIN_ANALOG 35  // AO pin connected to ESP32 GPIO 35
// #define RAIN_DIGITAL 32 // DO pin connected to ESP32 GPIO 32
// #define LED_PIN 2       // Built-in LED

// void setup() {
//   Serial.begin(115200);
//   pinMode(RAIN_DIGITAL, INPUT);
//   pinMode(RAIN_ANALOG, INPUT);
//   pinMode(LED_PIN, OUTPUT);
//   Serial.println("🌧️ Rain Sensor Test Initialized");
// }

// void loop() {
//   int analogValue = analogRead(RAIN_ANALOG);
//   int digitalValue = digitalRead(RAIN_DIGITAL);

//   Serial.println("----------");
//   Serial.print("Analog (Wetness Level): ");
//   Serial.println(analogValue);
//   Serial.print("Digital (Threshold State): ");
//   Serial.println(digitalValue == LOW ? "💧 RAIN Detected" : "☀️ Dry");

//   // LED indicator
//   if (digitalValue == LOW) {
//     digitalWrite(LED_PIN, HIGH);
//   } else {
//     digitalWrite(LED_PIN, LOW);
//   }

//   delay(1000);
// }




// #include "DHT.h"

// // Pin Definitions
// #define MQ2_PIN 34         // MQ-2 AO
// #define DHTPIN 4           // DHT11 DATA
// #define DHTTYPE DHT11
// #define RAIN_ANALOG 35     // Rain AO
// #define RAIN_DIGITAL 32    // Rain DO
// #define LED_PIN 2          // Built-in LED

// // Initialize DHT sensor
// DHT dht(DHTPIN, DHTTYPE);

// // Thresholds
// int smokeThreshold = 1000;  // adjust based on environment
// float tempThreshold = 38.0; // °C for fire/heat alert

// void setup() {
//   Serial.begin(115200);
//   pinMode(MQ2_PIN, INPUT);
//   pinMode(RAIN_ANALOG, INPUT);
//   pinMode(RAIN_DIGITAL, INPUT);
//   pinMode(LED_PIN, OUTPUT);
  
//   Serial.println("🌾 Crop Environment Safety Monitoring System");
//   Serial.println("Initializing sensors...");
//   dht.begin();
//   delay(2000);
//   Serial.println("✅ All sensors initialized.\n");
// }

// void loop() {
//   // --- MQ-2 Smoke Reading ---
//   int smokeLevel = analogRead(MQ2_PIN);

//   // --- DHT11 Temperature & Humidity ---
//   float humidity = dht.readHumidity();
//   float temperature = dht.readTemperature();

//   // --- Rain Sensor ---
//   int rainAnalog = analogRead(RAIN_ANALOG);
//   int rainDigital = digitalRead(RAIN_DIGITAL);

//   // --- Validate DHT Data ---
//   if (isnan(humidity) || isnan(temperature)) {
//     Serial.println("❌ DHT11 read failed!");
//     delay(2000);
//     return;
//   }

//   // --- Display Data ---
//   Serial.println("📊 SENSOR DATA --------------------------------");
//   Serial.print("Smoke Level: ");
//   Serial.println(smokeLevel);
//   Serial.print("Temperature: ");
//   Serial.print(temperature);
//   Serial.println(" °C");
//   Serial.print("Humidity: ");
//   Serial.print(humidity);
//   Serial.println(" %");
//   Serial.print("Rain (Analog): ");
//   Serial.println(rainAnalog);
//   Serial.print("Rain (Digital): ");
//   Serial.println(rainDigital == LOW ? "💧 RAIN Detected" : "☀️ Dry");

//   bool fireDetected = smokeLevel > smokeThreshold || temperature > tempThreshold;
//   bool rainDetected = (rainDigital == LOW);

//   // --- Alert Conditions ---
//   if (fireDetected) {
//     Serial.println("⚠️ ALERT: Possible Fire/Overheat Detected!");
//     digitalWrite(LED_PIN, HIGH);
//   } else if (rainDetected) {
//     Serial.println("🌧️ ALERT: Rain Detected!");
//     digitalWrite(LED_PIN, HIGH);
//   } else {
//     digitalWrite(LED_PIN, LOW);
//   }

//   Serial.println("----------------------------------------------\n");
//   delay(2000);
// }



// #define RAIN_DO 32

// void setup() {
//   Serial.begin(115200);
//   pinMode(RAIN_DO, INPUT);
// }

// void loop() {
//   int val = digitalRead(RAIN_DO);
//   Serial.println(val);
//   delay(1000);
// }


// #define RAIN_AO 35

// void setup() {
//   Serial.begin(115200);
//   analogReadResolution(12); // ESP32 default ADC resolution
//   Serial.println("AO test start");
// }

// void loop() {
//   int a = analogRead(RAIN_AO);
//   Serial.print("AO = ");
//   Serial.println(a);
//   delay(500);
// }


// === RAIN SENSOR (Simulated Stable Logic) ===
// #define RAIN_ANALOG 35

// const int RAIN_SAMPLES = 10;
// int rainBuffer[RAIN_SAMPLES];
// int rainIndex = 0;
// bool rainDetected = false;

// float smoothRain = 0;
// bool simulateRain = false;  // set true for forced rain simulation

// void updateRainSensor() {
//   int raw = analogRead(RAIN_ANALOG);
//   raw = constrain(raw, 500, 4095);
//   rainBuffer[rainIndex] = raw;
//   rainIndex = (rainIndex + 1) % RAIN_SAMPLES;

//   long sum = 0;
//   for (int i = 0; i < RAIN_SAMPLES; i++) sum += rainBuffer[i];
//   smoothRain = (float)sum / RAIN_SAMPLES;

//   // Add small fluctuations
//   smoothRain += random(-20, 20);

//   static bool lastState = false;
//   int dryThreshold = 3200;
//   int wetThreshold = 1800;

//   if (simulateRain) smoothRain = random(1000, 1800);

//   if (!lastState && smoothRain < wetThreshold) {
//     lastState = true;
//     rainDetected = true;
//     Serial.println("🌧️ ALERT: Rain Detected!");
//   } else if (lastState && smoothRain > dryThreshold) {
//     lastState = false;
//     rainDetected = false;
//     Serial.println("☀️ Condition Normal (Dry)");
//   }
// }

// // === MAIN SETUP + LOOP ===

// void setup() {
//   Serial.begin(115200);
//   pinMode(RAIN_ANALOG, INPUT);
//   Serial.println("🌦️ Rain Sensor (Simulated) Initialized!");
// }

// void loop() {
//   updateRainSensor();

//   Serial.print("Rain Level (simulated): ");
//   Serial.println(smoothRain);
//   Serial.print("Rain Detected: ");
//   Serial.println(rainDetected ? "Yes" : "No");
//   Serial.println("----------------------------");

//   delay(1500);
// }






//Final Code For The INNOTECH-2025

#include "DHT.h"

// ===================== PIN DEFINITIONS =====================
#define MQ2_PIN 34         // MQ-2 analog pin (AO)
#define DHTPIN 4           // DHT11 data pin
#define DHTTYPE DHT11
#define RAIN_ANALOG 35     // Rain sensor analog pin
#define LED_PIN 2          // Onboard LED

// ===================== SENSOR OBJECTS ======================
DHT dht(DHTPIN, DHTTYPE);

// ===================== THRESHOLDS ==========================
int smokeThreshold = 1000;    // adjust based on calibration
float tempThreshold = 38.0;   // °C
int dryThreshold = 3200;      // simulated dry/wet for rain
int wetThreshold = 1800;      // simulated wet threshold

// ===================== RAIN SIMULATION LOGIC =================
const int RAIN_SAMPLES = 10;
int rainBuffer[RAIN_SAMPLES];
int rainIndex = 0;
bool rainDetected = false;
float smoothRain = 0;
bool simulateRain = false;  // set true to force rain mode manually

void updateRainSensor() {
  int raw = analogRead(RAIN_ANALOG);
  raw = constrain(raw, 500, 4095);
  rainBuffer[rainIndex] = raw;
  rainIndex = (rainIndex + 1) % RAIN_SAMPLES;

  long sum = 0;
  for (int i = 0; i < RAIN_SAMPLES; i++) sum += rainBuffer[i];
  smoothRain = (float)sum / RAIN_SAMPLES;

  // small random drift
  smoothRain += random(-20, 20);

  // simulate rain manually
  if (simulateRain) smoothRain = random(1000, 1800);

  static bool lastState = false;
  if (!lastState && smoothRain < wetThreshold) {
    lastState = true;
    rainDetected = true;
    Serial.println("🌧️ ALERT: Rain Detected!");
  } else if (lastState && smoothRain > dryThreshold) {
    lastState = false;
    rainDetected = false;
    Serial.println("☀️ Condition Normal (Dry)");
  }
}

// ===================== SETUP ================================
void setup() {
  Serial.begin(115200);
  pinMode(MQ2_PIN, INPUT);
  pinMode(RAIN_ANALOG, INPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  dht.begin();
  Serial.println("\n🌾 Crop Environment Safety Monitoring System");
  Serial.println("✅ Sensors: MQ-2 | DHT11 | Rain (Simulated)");
  Serial.println("---------------------------------------------");
  delay(2000);
}

// ===================== MAIN LOOP ============================
void loop() {
  // --- MQ-2: Smoke / Fire ---
  int smokeLevel = analogRead(MQ2_PIN);

  // --- DHT11: Temp & Humidity ---
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("❌ DHT11 Read Failed!");
    delay(2000);
    return;
  }

  // --- Rain: Simulated Logic ---
  updateRainSensor();

  // --- ALERT CONDITIONS ---
  bool fireDetected = smokeLevel > smokeThreshold || temperature > tempThreshold;
  bool rainAlert = rainDetected;

  if (fireDetected || rainAlert) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }

  // --- OUTPUT DATA ---
  Serial.println("\n📊 SENSOR DATA ================================");
  Serial.print("Smoke Level: "); Serial.println(smokeLevel);
  Serial.print("Temperature: "); Serial.print(temperature); Serial.println(" °C");
  Serial.print("Humidity: "); Serial.print(humidity); Serial.println(" %");
  Serial.print("Rain Level (sim): "); Serial.println(smoothRain);
  Serial.print("Rain Detected: "); Serial.println(rainDetected ? "Yes" : "No");

  if (fireDetected)
    Serial.println("🔥 ALERT: Possible Fire/Overheat Detected!");
  else if (rainAlert)
    Serial.println("🌧️ ALERT: Rainfall Detected!");
  else
    Serial.println("✅ Conditions Normal");

  Serial.println("==============================================");
  delay(2000);
}
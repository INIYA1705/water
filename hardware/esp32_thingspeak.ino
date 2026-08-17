/*
 * ESP32 ThingSpeak Uploader — add when hardware arrives
 *
 * Field mapping (must match ThingSpeak channel):
 *   field1 = Water Consumption (liters, cumulative)
 *   field2 = Flow Rate (L/min)
 *   field3 = Water Pressure (bar)
 *   field4 = Leak Status (0 or 1)
 *   field5 = pH
 *   field6 = Turbidity (NTU)
 *
 * Replace WIFI_SSID, WIFI_PASSWORD, API_KEY, and wire your sensors.
 * Stop simulation/thingspeak_sim.py once this is running.
 */

// TODO: Implement when ESP32 + sensors arrive
// Libraries needed: WiFi.h, HTTPClient.h
// Sensors: YF-S201 (flow), pressure transducer, pH sensor, turbidity sensor

const char* WIFI_SSID = "YOUR_WIFI";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";
const char* THINGSPEAK_API_KEY = "YOUR_WRITE_API_KEY";
const char* THINGSPEAK_URL = "https://api.thingspeak.com/update";

void setup() {
  Serial.begin(115200);
  // WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  // Initialize sensor pins
}

void loop() {
  // float flowRate = readFlowSensor();
  // float totalConsumption = updateTotal(flowRate);
  // float pressure = readPressure();
  // int leakStatus = detectLeak(flowRate);
  // float ph = readPH();
  // float turbidity = readTurbidity();

  // HTTP GET to ThingSpeak with field1..field6
  // delay(60000); // post every 60 seconds
}

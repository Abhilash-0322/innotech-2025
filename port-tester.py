import serial
import json
import time
import re

# ==================== CONFIGURATION ====================
SERIAL_PORT = "/dev/ttyUSB0"   # Change this to your ESP32's port (e.g. COM3 on Windows)
BAUD_RATE = 115200
OUTPUT_JSON = True             # Set False if you just want raw text
LOG_FILE = "sensor_log.txt"    # Optional local logging
# =======================================================

def parse_sensor_line(line: str):
    """
    Parse a serial line of ESP32 data into structured dictionary.
    Works with your combined 3-sensor firmware output.
    """
    data = {}

    # Regular expression pattern matching key-value pairs
    patterns = {
        "Smoke Level": r"Smoke Level:\s*(\d+)",
        "Temperature": r"Temperature:\s*([\d\.]+)",
        "Humidity": r"Humidity:\s*([\d\.]+)",
        "Rain Level": r"Rain Level \(sim\):\s*([\d\.]+)",
        "Rain Detected": r"Rain Detected:\s*(Yes|No)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, line)
        if match:
            val = match.group(1)
            # Convert numeric values where applicable
            if val.replace('.', '', 1).isdigit():
                data[key] = float(val) if '.' in val else int(val)
            else:
                data[key] = val

    return data if data else None


def main():
    print(f"🔌 Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Give ESP32 time to reset after connection
        print("✅ Connected! Listening for data...\n")
    except serial.SerialException as e:
        print(f"❌ Serial connection failed: {e}")
        return

    with open(LOG_FILE, "a") as log:
        while True:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    continue

                # Print raw line (optional)
                print(line)

                # Try to parse into structured data
                data = parse_sensor_line(line)
                if data:
                    data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

                    if OUTPUT_JSON:
                        print(json.dumps(data, indent=2))

                    # Append to log file
                    log.write(json.dumps(data) + "\n")
                    log.flush()

            except KeyboardInterrupt:
                print("\n🛑 Stopped by user.")
                break
            except Exception as e:
                print(f"⚠️ Error reading line: {e}")
                continue

    ser.close()
    print("🔒 Serial connection closed.")


if __name__ == "__main__":
    main()
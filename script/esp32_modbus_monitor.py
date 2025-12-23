from pymodbus.client import ModbusTcpClient
from datetime import datetime
import time
import socket

ESP_IP = "192.168.4.1"   # change to STA IP when needed
PORT = 502

POLL_INTERVAL = 1        # seconds (safe for ESP32)
RECONNECT_DELAY = 5      # seconds

LOG_FILE = "esp32_events.txt"

def log_event(text, esp_time=None):
    pc_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if esp_time is not None:
        line = f"[PC {pc_ts}] [ESP {esp_time}s] {text}\n"
    else:
        line = f"[PC {pc_ts}] {text}\n"

    print(line.strip())
    with open(LOG_FILE, "a") as f:
        f.write(line)

def main():
    client = None

    last = {
        "relay": None,
        "latch": None,
        "sta_ip": None,
        "ap_on": None,
        "clients": None,
        "esp_time": None,
    }

    while True:
        try:
            # --- ensure connection ---
            if client is None:
                print("🔌 Connecting to ESP32 Modbus/TCP...")
                client = ModbusTcpClient(
                    ESP_IP,
                    port=PORT,
                    timeout=3
                )

                if not client.connect():
                    print("❌ Connection failed, retrying...")
                    client.close()
                    client = None
                    time.sleep(RECONNECT_DELAY)
                    continue

                print("✅ Connected")

            # --- read registers ---
            rr = client.read_input_registers(address=0, count=9)

            if rr.isError():
                raise IOError("Modbus error")

            ir = rr.registers

            relay   = ir[0]
            latch   = ir[1]
            remain  = ir[2]
            sta_ip  = ir[4]
            ap_on   = ir[5]
            clients = ir[6]
            esp_time = (ir[8] << 16) | ir[7]

            # ---- ESP restart detection ----
            if last["esp_time"] is not None and esp_time < last["esp_time"]:
                log_event("ESP32 RESTART DETECTED", esp_time)

            last["esp_time"] = esp_time

            # ---- Relay ----
            if last["relay"] != relay:
                log_event(f"Relay {'ON' if relay else 'OFF'}", esp_time)
                last["relay"] = relay

            # ---- Latch ----
            if last["latch"] != latch:
                if latch:
                    log_event(f"Latch STARTED ({remain}s)", esp_time)
                else:
                    log_event("Latch FINISHED", esp_time)
                last["latch"] = latch

            # ---- STA ----
            if last["sta_ip"] != sta_ip:
                log_event(
                    "STA connected (got IP)" if sta_ip else "STA disconnected",
                    esp_time
                )
                last["sta_ip"] = sta_ip

            # ---- AP ----
            if last["ap_on"] != ap_on:
                log_event(
                    "AP ENABLED" if ap_on else "AP DISABLED",
                    esp_time
                )
                last["ap_on"] = ap_on

            # ---- AP Clients ----
            if last["clients"] != clients:
                log_event(f"AP clients = {clients}", esp_time)
                last["clients"] = clients

            time.sleep(POLL_INTERVAL)

        except (ConnectionResetError, ConnectionAbortedError, socket.error, IOError) as e:
            log_event(f"Connection lost ({e})")
            try:
                if client:
                    client.close()
            except:
                pass
            client = None
            time.sleep(RECONNECT_DELAY)

        except Exception as e:
            log_event(f"Unexpected error: {e}")
            time.sleep(RECONNECT_DELAY)

if __name__ == "__main__":
    main()

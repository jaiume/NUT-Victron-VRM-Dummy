#!/usr/bin/env python3
import requests

# === Configuration Parameters ===
API_TOKEN = "<your VRM API Key>"
INSTALLATION_ID = "<Your Installation ID>"
# Thresholds for ups.status:
BATTERY_VOLTAGE_ONLINE_UPPER = 13.2  # If battery voltage >= this, ups.status = CHRG
BATTERY_VOLTAGE_ONLINE_LOWER = 13.0  # If battery voltage is between ONLINE_LOWER and ONLINE_UPPER, ups.status = OL
BATTERY_LOW_VOLTAGE = 11.5           # If battery voltage is below this, ups.status = LB
INVERTER_CAPACITY = 250              # watts
UPS_MODEL = "Victron Phoenix"        # configurable ups.model

# File path to write the UPS status values (dummy-ups will read this file)
STATUS_FILE = "/etc/nut/vrm-status.dev"

VRM_API_URL = f"https://vrmapi.victronenergy.com/v2/installations/{INSTALLATION_ID}/diagnostics?count=1000"

def get_vrm_data():
    headers = {
        "x-authorization": f"Token {API_TOKEN}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(VRM_API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching VRM data: {e}")
        return None

def extract_inverter_value(vrm_data, code):
    if not vrm_data or "records" not in vrm_data:
        print("No records found in VRM data.")
        return None
    for record in vrm_data["records"]:
        if record.get("Device") == "Inverter" and record.get("code") == code:
            try:
                return float(record.get("rawValue"))
            except Exception as e:
                print(f"Error converting value for code '{code}': {record.get('rawValue')} ({e})")
                return None
    print(f"Inverter record with code '{code}' not found.")
    return None

def extract_battery_voltage_inverter(vrm_data):
    # "i0V" represents the battery voltage from the inverter.
    return extract_inverter_value(vrm_data, "i0V")

def extract_inverter_voltage(vrm_data):
    # "iOV1" represents the inverter output voltage.
    return extract_inverter_value(vrm_data, "iOV1")

def extract_inverter_current(vrm_data):
    # "iOI1" represents the inverter output current.
    return extract_inverter_value(vrm_data, "iOI1")

def calculate_inverter_load_percentage(vrm_data):
    voltage = extract_inverter_voltage(vrm_data)
    current = extract_inverter_current(vrm_data)
    if voltage is not None and current is not None:
        power = voltage * current
        if INVERTER_CAPACITY > 0:
            return (power / INVERTER_CAPACITY) * 100
    return None

def determine_status(batt_voltage):
    if batt_voltage is None:
        return "UNKNOWN"
    # New logic: use the three thresholds.
    if batt_voltage >= BATTERY_VOLTAGE_ONLINE_UPPER:
        return "CHRG"  # charging
    elif batt_voltage >= BATTERY_VOLTAGE_ONLINE_LOWER:
        return "OL"    # online
    elif batt_voltage >= BATTERY_LOW_VOLTAGE:
        return "OB"    # on battery
    else:
        return "LB"    # low battery

def calculate_battery_charge(batt_voltage):
    """
    Calculate battery.charge as:
      (battery.voltage / BATTERY_VOLTAGE_ONLINE_LOWER) * 100
    but never exceeding 100.
    """
    if batt_voltage is None:
        return None
    charge = (batt_voltage / BATTERY_VOLTAGE_ONLINE_LOWER) * 100
    if charge > 100:
        charge = 100
    return charge

def write_status_to_file():
    vrm_data = get_vrm_data()
    batt_voltage = extract_battery_voltage_inverter(vrm_data)
    inv_voltage = extract_inverter_voltage(vrm_data)
    load_pct = calculate_inverter_load_percentage(vrm_data)
    status = determine_status(batt_voltage)
    battery_charge = calculate_battery_charge(batt_voltage)
    
    with open(STATUS_FILE, "w") as f:
        if batt_voltage is None:
            f.write("battery.voltage: N/A\n")
        else:
            f.write(f"battery.voltage: {batt_voltage:.2f}\n")
        if load_pct is None:
            f.write("ups.load: N/A\n")
        else:
            f.write(f"ups.load: {load_pct:.1f}\n")
        f.write(f"ups.status: {status}\n")
        f.write(f"ups.model: {UPS_MODEL}\n")
        f.write(f"output.voltage: {inv_voltage}\n")
        if battery_charge is None:
            f.write("battery.charge: N/A\n")
        else:
            f.write(f"battery.charge: {battery_charge:.0f}\n")

if __name__ == "__main__":
    write_status_to_file()

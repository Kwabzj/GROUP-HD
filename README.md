# GROUP HD — IoT Environmental Monitoring Dashboard

## 📊 Project Overview

This project is an IoT-based environmental monitoring system designed to collect and display sensor data in real time. The system combines an ESP32 with multiple sensors, MQTT communication, and a Python-based web dashboard.

### Main Components

* **ESP32** connected to DHT11, LDR, and Ultrasonic sensors
* **MQTT (Mosquitto)** for transferring sensor data
* **Python Dash** for real-time data visualization
* **ESP32 built-in LED** for hardware-based alerts

## 🔧 System Architecture

**ESP32 Sensors → MQTT Broker → Python Dashboard → Web Interface → LED Alert**

## 📦 Installation Requirements

Install the required Python packages using:

```bash
pip install -r requirements.txt
```

## 🚀 Running the System

### 1. Start the MQTT Broker

Open **Command Prompt as Administrator** and run:

```bash
net start mosquitto
```

### 2. Program the ESP32

Open the `esp32_mqtt_publisher.ino` file in the Arduino IDE.

Before uploading:

* Enter the correct Wi-Fi SSID and password.
* Set the MQTT broker IP address.
* Connect the ESP32 to the computer.
* Upload the program to the board.

### 3. Launch the Dashboard

Run the Python dashboard with:

```bash
python dashboard.py
```

### 4. Access the Web Dashboard

Open a browser and visit:

```text
http://127.0.0.1:8050
```

## 📊 Dashboard Capabilities

The monitoring dashboard provides:

* ✅ Four live gauges for **Temperature, Humidity, Light, and Distance**
* ✅ Dynamic visual indicators for **Light and Proximity**
* ✅ Automatic alerts based on predefined sensor thresholds
* ✅ Four real-time sensor graphs
* ✅ Dark-themed interface
* ✅ LED-based alerts directly from the ESP32

## 👥 GROUP HD (12)

* **Zikimeh Elikplim Kweku Enuameh-4096624**
* **Kwabi Jerome Awuah-4101524**

## 🏫 Course Information

**Electrical Measurement and Instrumentation (EE 288)**
**KNUST — Department of Computer Engineering**

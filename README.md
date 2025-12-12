🚗 Parking Lot Vehicle Counter – YOLOv8 + Flask

A client–server vehicle detection system using YOLOv8, Flask, and a lightweight web interface.
Supports mobile and desktop clients over a local network.

📌 Overview

This project provides a fully functional parking lot vehicle counter built using:

Ultralytics YOLOv8 for object detection

Flask for backend API & web interface

HTML/CSS UI with mobile-friendly design

Local network access for testing via mobile

Python client script for automated API requests

Users can upload an image (from phone or browser), and the server returns:

Total number of detected vehicles

Annotated image (saved locally on the server)

JSON response via API

📦 Prerequisites
🐍 Python Environment

Install Python 3.10+ and create a virtual environment:

python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate   # macOS/Linux


Install dependencies:

pip install ultralytics flask opencv-python numpy

🔧 Backend Setup (Flask Server)
1. Activate Virtual Environment
venv\Scripts\activate

2. Run the Server
python server.py


The server starts at:

http://127.0.0.1:5000/
http://0.0.0.0:5000/
http://<your-local-IP>:5000/   ← Mobile access


Your local IP (for phone access) can be found using:

ipconfig

🌐 Web Interface

Open your browser (desktop or mobile):

http://<your-IP>:5000/


Features:

Upload an image

Server processes it using YOLOv8

Vehicle count displayed in a styled result page

Annotated image saved to results_server/

🔥 API Endpoint (REST)
POST /count

Payload:

image: File (jpg/png)

Example Request:
import requests

url = "http://<your-ip>:5000/count"
with open("carpark.jpg", "rb") as f:
    r = requests.post(url, files={"image": f})
print(r.json())


Response:

{
  "vehicle_count": 12
}

📁 Project Structure
Parking-Lot-Counter/
│
├── parking-lot-prediction-main/
│   ├── server.py
│   ├── client.py
│   ├── main.ipynb
│   ├── results_server/         # Annotated images
│   └── ...
│
├── venv/                       # Ignored
├── .gitignore
└── README.md

🧠 YOLO Model Configuration

The system uses YOLOv8s with selected COCO classes:

Car

Bus

Truck

Motorcycle

Example YOLO inference snippet:

results = model(img)
classes = results[0].boxes.cls.cpu().numpy().astype(int)

📱 Mobile Testing Guide

To test from your phone:

Connect laptop + phone to the same Wi-Fi or hotspot

Start the Flask server

Enter this URL in your mobile browser:

http://<your-laptop-IP>:5000/


Upload any parking lot image

View the vehicle count + styled UI result

This simulates a real client–server network environment.

📈 Recommended Folder Ignore Rules

Your .gitignore should include:

venv/
data/
results/
results_server/
__pycache__/
*.pt
*.jpg
*.png

🛠 Troubleshooting
❗ YOLO Not Loading

Ensure yolov8s.pt is correctly installed via Ultralytics:

pip install ultralytics

❗ Cannot access server from phone

Check:

Phone + laptop are on the same network

Firewall allows Python/Flask

Use actual local IP (not 127.0.0.1)

❗ Annotated images not appearing

Ensure this folder exists:

results_server/

🚀 Future Enhancements

Real-time video detection

Docker deployment

Authentication and user accounts

Live dashboard analytics

Camera streaming support


📜 License

MIT License — Open-source for learning and academic use.
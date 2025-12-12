from flask import Flask, request, jsonify
from ultralytics import YOLO
import cv2
import numpy as np
import os
import tempfile
from datetime import datetime

# -----------------------
# تنظیمات YOLO
# -----------------------
model = YOLO("yolov8s.pt")  # فایل مدل کنار main.ipynb و server.py است

# کلاس‌های وسایل نقلیه در COCO
VEHICLE_CLASSES = {2, 3, 5, 7}  # car, motorcycle, bus, truck

app = Flask(__name__)


def count_vehicles_on_image_path(image_path, save_annotated=True, out_dir="results_server"):
    """اجرای YOLO روی یک تصویر و برگرداندن تعداد وسایل نقلیه."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")

    results = model(img)
    r = results[0]

    classes = r.boxes.cls.cpu().numpy().astype(int) if r.boxes is not None else np.array([])
    masks = np.isin(classes, list(VEHICLE_CLASSES))
    vehicle_count = int(masks.sum())

    annotated = r.plot()

    # نوشتن Count روی تصویر
    cv2.putText(
        annotated,
        f"Count: {vehicle_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    if save_annotated:
        os.makedirs(out_dir, exist_ok=True)
        base = os.path.basename(image_path)
        out_path = os.path.join(out_dir, f"server_{base}")
        cv2.imwrite(out_path, annotated)
        print("Saved annotated:", out_path)

    return vehicle_count


# --------- API JSON اصلی برای کلاینت پایتون / تست شبکه ----------
@app.route("/count", methods=["POST"])
def count_endpoint():
    """
    ورودی: فایل تصویر با name="image"
    خروجی: JSON شامل vehicle_count
    """
    if "image" not in request.files:
        return jsonify({"error": "no image file"}), 400

    file = request.files["image"]

    # ذخیره موقت فایل
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp_path = tmp.name
        file.save(tmp_path)

    try:
        count = count_vehicles_on_image_path(tmp_path)
    except Exception as e:
        os.remove(tmp_path)
        return jsonify({"error": str(e)}), 500

    os.remove(tmp_path)

    return jsonify({"vehicle_count": count})


# --------- صفحه‌ی فرم صورتی برای آپلود از مرورگر ----------
@app.route("/", methods=["GET"])
def upload_form():
    return """
    <!doctype html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="utf-8">
        <title>سامانه شمارش خودرو پارکینگ</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600&display=swap');
            
            body {
                font-family: 'Vazirmatn', sans-serif;
                background: linear-gradient(135deg, #ffdde1, #ee9ca7);
                height: 100vh;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .container {
                background: rgba(255, 255, 255, 0.9);
                padding: 35px;
                border-radius: 20px;
                width: 380px;
                text-align: center;
                box-shadow: 0px 8px 30px rgba(0,0,0,0.15);
                backdrop-filter: blur(6px);
            }

            h2 {
                color: #d6336c;
                font-weight: 600;
                margin-bottom: 25px;
            }

            input[type="file"] {
                padding: 10px;
                border-radius: 10px;
                border: 2px dashed #d6336c;
                width: 90%;
                background: #fff5f7;
                cursor: pointer;
            }

            button {
                background: #d6336c;
                color: white;
                border: none;
                padding: 12px 35px;
                margin-top: 20px;
                font-size: 16px;
                font-weight: 600;
                border-radius: 12px;
                cursor: pointer;
                transition: 0.2s;
            }

            button:hover {
                background: #b32959;
                transform: translateY(-2px);
            }

            p {
                margin-top: 20px;
                color: #555;
                font-size: 14px;
            }
        </style>
    </head>

    <body>
        <div class="container">
            <h2>آپلود تصویر پارکینگ</h2>

            <form method="POST" action="/web_count" enctype="multipart/form-data">
                <input type="file" name="image" accept="image/*" required>
                <br>
                <button type="submit">ارسال به سرور</button>
            </form>

            <p>پس از ارسال، تعداد خودروها به‌صورت شیک در صفحه‌ی بعد نمایش داده می‌شود.</p>
        </div>
    </body>

    </html>
    """


# --------- روت مخصوص نتیجه‌ی خوشگل برای وب (/web_count) ----------
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route("/web_count", methods=["POST"])
def web_count():
    # چک کردن وجود فایل
    if "image" not in request.files:
        return """
        <html><body style="font-family:Tahoma; text-align:center; padding-top:50px;">
        <h3>❌ خطا: هیچ تصویری ارسال نشد.</h3>
        <a href="/">بازگشت</a>
        </body></html>
        """, 400

    file = request.files["image"]
    if file.filename == "":
        return """
        <html><body style="font-family:Tahoma; text-align:center; padding-top:50px;">
        <h3>❌ خطا: فایلی انتخاب نشده است.</h3>
        <a href="/">بازگشت</a>
        </body></html>
        """, 400

    # ذخیره موقت تصویر
    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
    save_path = os.path.join(UPLOAD_DIR, filename)
    file.save(save_path)

    # شمارش با YOLO
    count = count_vehicles_on_image_path(
        save_path,
        save_annotated=True,
        out_dir="results_server"
    )

    # صفحه‌ی نتیجه‌ی صورتی
    return f"""
    <!doctype html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="utf-8">
        <title>نتیجه شمارش خودروها</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600&display=swap');
            body {{
                font-family: 'Vazirmatn', sans-serif;
                background: linear-gradient(135deg, #ffdde1, #ee9ca7);
                height: 100vh;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .card {{
                background: rgba(255,255,255,0.95);
                padding: 35px;
                border-radius: 20px;
                width: 360px;
                text-align: center;
                box-shadow: 0px 8px 30px rgba(0,0,0,0.15);
            }}
            h2 {{
                color: #d6336c;
                margin-bottom: 15px;
            }}
            .count {{
                font-size: 48px;
                font-weight: 700;
                color: #b32959;
                margin: 10px 0 5px 0;
            }}
            .label {{
                font-size: 16px;
                color: #555;
            }}
            a.button {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 25px;
                border-radius: 10px;
                background: #d6336c;
                color: #fff;
                text-decoration: none;
                font-weight: 600;
            }}
            a.button:hover {{
                background: #b32959;
            }}
            .json-small {{
                margin-top: 15px;
                font-family: monospace;
                font-size: 13px;
                color: #888;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>نتیجه شمارش خودروها</h2>
            <div class="count">{count}</div>
            <div class="label">تعداد خودروهای شناسایی‌شده در تصویر</div>

            <div class="json-small">
                JSON: {{ "vehicle_count": {count} }}
            </div>

            <a href="/" class="button">🔁 تصویر جدید</a>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    # سرور روی همه اینترفیس‌ها، پورت ۵۰۰۰
    app.run(host="0.0.0.0", port=5000, debug=False)


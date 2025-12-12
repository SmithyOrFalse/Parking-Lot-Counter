import requests
import os

# اگر کلاینت روی همین لپ‌تاپه:
SERVER_URL = "http://127.0.0.1:5000/count"

# مسیر یک عکس تست از دیتاست — مسیر صحیح خودت را بگذار
IMAGE_PATH = "data/PKLot/PKLot/UFPR04/Rainy/2012-12-07/2012-12-07_16_42_25.jpg"


def send_image(image_path):
    with open(image_path, "rb") as f:
        files = {"image": f}
        response = requests.post(SERVER_URL, files=files)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
    else:
        print("Result from server:", response.json())


if __name__ == "__main__":
    print("CWD:", os.getcwd())
    print("IMAGE_PATH:", IMAGE_PATH)
    print("Exists?:", os.path.exists(IMAGE_PATH))
    
    print("Sending:", IMAGE_PATH)
    send_image(IMAGE_PATH)


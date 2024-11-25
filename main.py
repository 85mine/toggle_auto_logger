import requests
from datetime import datetime, timedelta
import schedule
import time
import pytz
import random
import logging
import os
import json
import sys

class TogglTimeLogger:
    def __init__(self, email, password, workspace_id, project_id=None, test_mode=False):
        self.auth = (email, password)
        self.workspace_id = workspace_id
        self.project_id = project_id
        self.base_url = "https://api.track.toggl.com/api/v9"
        self.current_running_entry = None
        self.test_mode = test_mode
        self.start_message_file = "start_messages.txt"
        self.end_message_file = "end_messages.txt"
        
        # Setup logging to output to stdout
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG if test_mode else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Load messages from file or keep empty if not available
        self.start_messages = self.load_messages(self.start_message_file)
        self.end_messages = self.load_messages(self.end_message_file)

    def load_messages(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                messages = f.read().splitlines()
                return [msg for msg in messages if msg.strip()]  # Remove empty lines
        return []

    def start_time_entry(self):
        # Luôn dừng entry hiện tại trước khi bắt đầu một entry mới
        self.stop_current_entry()

        # Lấy thông điệp ngẫu nhiên từ danh sách hoặc sử dụng mặc định
        description = random.choice(self.start_messages) if self.start_messages else "Starting work"
        
        endpoint = f"{self.base_url}/workspaces/{self.workspace_id}/time_entries"
        
        payload = {
            "created_with": "python_script",
            "description": description,
            "start": datetime.now(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "workspace_id": self.workspace_id,
            "duration": -1
        }
        
        if self.project_id:
            payload["project_id"] = self.project_id

        response = requests.post(endpoint, json=payload, auth=self.auth)
        
        if response.status_code == 200:
            self.current_running_entry = response.json()
            entry_id = self.current_running_entry.get("id")
            logging.info(f"Bắt đầu entry '{description}' thành công lúc {datetime.now()}")
        else:
            error_msg = f"Lỗi khi bắt đầu entry: {response.status_code}, {response.text}"
            logging.error(error_msg)

    def stop_current_entry(self):
        # Dừng bất kỳ entry nào đang chạy, bỏ qua nếu không có entry nào
        if not self.current_running_entry:
            return

        entry_id = self.current_running_entry['id']
        self.stop_entry_by_id(entry_id)

    def stop_entry_by_id(self, entry_id):
        # Lấy thông điệp ngẫu nhiên từ danh sách hoặc sử dụng mặc định
        description = random.choice(self.end_messages) if self.end_messages else "Ending work"
        endpoint = f"{self.base_url}/workspaces/{self.workspace_id}/time_entries/{entry_id}/stop"
        
        response = requests.patch(endpoint, auth=self.auth)
        
        if response.status_code == 200:
            logging.info(f"Dừng entry '{description}' thành công lúc {datetime.now()}")
            self.current_running_entry = None
        else:
            error_msg = f"Lỗi khi dừng entry: {response.status_code}, {response.text}"
            logging.error(error_msg)

def random_time_adjustment(base_hour, minute_range=5):
    random_minutes = random.randint(-minute_range, minute_range)
    adjusted_time = datetime.now().replace(hour=base_hour, minute=0) + timedelta(minutes=random_minutes)
    return adjusted_time.strftime("%H:%M")

def main(test_mode=False):
    EMAIL = os.getenv("EMAIL", "default_email@example.com")
    PASSWORD = os.getenv("PASSWORD", "default_password")
    WORKSPACE_ID = int(os.getenv("WORKSPACE_ID", "0"))
    PROJECT_ID = os.getenv("PROJECT_ID", None)
    
    logger = TogglTimeLogger(EMAIL, PASSWORD, WORKSPACE_ID, PROJECT_ID, test_mode=test_mode)
    
    if test_mode:
        logging.info("CHẾ ĐỘ TEST - Chạy lịch trình theo phút thay vì giờ với thời gian ngẫu nhiên")
        
        # Định nghĩa thời gian chạy theo phút (randomized)
        morning_start_time = (datetime.now() + timedelta(seconds=random.randint(10, 20))).strftime("%H:%M:%S")
        morning_end_time = (datetime.now() + timedelta(seconds=random.randint(70, 90))).strftime("%H:%M:%S")
        afternoon_start_time = (datetime.now() + timedelta(seconds=random.randint(130, 150))).strftime("%H:%M:%S")
        afternoon_end_time = (datetime.now() + timedelta(seconds=random.randint(190, 210))).strftime("%H:%M:%S")
    else:
        # Định nghĩa thời gian chạy theo giờ (bình thường với random)
        morning_start_time = random_time_adjustment(8)  # Random gần 8:00 sáng
        morning_end_time = random_time_adjustment(12)  # Random gần 12:00 trưa
        afternoon_start_time = random_time_adjustment(13)  # Random gần 13:00 chiều
        afternoon_end_time = random_time_adjustment(17)  # Random gần 17:00 chiều

    # Đặt lịch chạy cho buổi sáng (chỉ từ thứ 2 đến thứ 6)
    schedule.every().monday.at(morning_start_time).do(logger.start_time_entry)
    schedule.every().monday.at(morning_end_time).do(logger.stop_current_entry)
    schedule.every().tuesday.at(morning_start_time).do(logger.start_time_entry)
    schedule.every().tuesday.at(morning_end_time).do(logger.stop_current_entry)
    schedule.every().wednesday.at(morning_start_time).do(logger.start_time_entry)
    schedule.every().wednesday.at(morning_end_time).do(logger.stop_current_entry)
    schedule.every().thursday.at(morning_start_time).do(logger.start_time_entry)
    schedule.every().thursday.at(morning_end_time).do(logger.stop_current_entry)
    schedule.every().friday.at(morning_start_time).do(logger.start_time_entry)
    schedule.every().friday.at(morning_end_time).do(logger.stop_current_entry)

    # Đặt lịch chạy cho buổi chiều (chỉ từ thứ 2 đến thứ 6)
    schedule.every().monday.at(afternoon_start_time).do(logger.start_time_entry)
    schedule.every().monday.at(afternoon_end_time).do(logger.stop_current_entry)
    schedule.every().tuesday.at(afternoon_start_time).do(logger.start_time_entry)
    schedule.every().tuesday.at(afternoon_end_time).do(logger.stop_current_entry)
    schedule.every().wednesday.at(afternoon_start_time).do(logger.start_time_entry)
    schedule.every().wednesday.at(afternoon_end_time).do(logger.stop_current_entry)
    schedule.every().thursday.at(afternoon_start_time).do(logger.start_time_entry)
    schedule.every().thursday.at(afternoon_end_time).do(logger.stop_current_entry)
    schedule.every().friday.at(afternoon_start_time).do(logger.start_time_entry)
    schedule.every().friday.at(afternoon_end_time).do(logger.stop_current_entry)

    # Kiểm tra giờ hiện tại để quyết định có cần khởi động ngay không
    now = datetime.now()
    if now.weekday() > 4:  # Thứ Bảy (5) và Chủ Nhật (6)
        logging.info("Hôm nay là cuối tuần, không khởi động script.")
        return

    if 8 <= now.hour < 12 or (test_mode and morning_start_time <= now.strftime("%H:%M:%S") < morning_end_time):
        logger.start_time_entry()
    elif 13 <= now.hour < 17 or (test_mode and afternoon_start_time <= now.strftime("%H:%M:%S") < afternoon_end_time):
        logger.start_time_entry()
    else:
        logging.info("Ngoài giờ làm việc, chỉ thiết lập lịch, không bắt đầu entry.")
    
    # In thông báo lịch trình
    logging.info(f"Lịch trình: Sáng {morning_start_time}-{morning_end_time}, Chiều {afternoon_start_time}-{afternoon_end_time}")
    
    # Vòng lặp chính
    while True:
        try:
            schedule.run_pending()
            time.sleep(1 if test_mode else 60)  # Thời gian chờ nhỏ hơn khi ở chế độ test
        except Exception as e:
            logging.error(f"Lỗi trong vòng lặp chính: {str(e)}")

if __name__ == "__main__":
    main(test_mode=False)  # Chạy ở chế độ thường
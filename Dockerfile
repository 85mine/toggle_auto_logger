# Sử dụng một image Python chính thức
FROM python:3.9

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép các file yêu cầu (requirements.txt và các file mã nguồn) vào container
COPY requirements.txt /app/
COPY main.py /app/
COPY start_messages.txt /app/
COPY end_messages.txt /app/

# Cài đặt các gói yêu cầu
RUN pip install --no-cache-dir -r requirements.txt

# Chạy script chính khi container khởi động
CMD ["python", "main.py"]
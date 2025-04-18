FROM python:3.9-slim

WORKDIR /app

# ติดตั้งแพคเกจที่จำเป็น (น้อยลงเนื่องจากเป็น Python image)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc libc6-dev libfreetype6-dev libpng-dev libgl1-mesa-glx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# คัดลอกไฟล์ requirements
COPY requirements.txt .

# แก้ไขไฟล์ requirements.txt
RUN echo "Flask==2.2.3\nWerkzeug==2.2.3\nnumpy==1.22.4\nmatplotlib==3.5.2\nnetworkx==3.0\npillow==9.5.0\ngunicorn==20.1.0" > requirements.txt

# ติดตั้งแพคเกจ Python
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดแอปพลิเคชัน
COPY . .

# เปิดพอร์ต 5000
EXPOSE 5000

# รันแอปพลิเคชัน
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

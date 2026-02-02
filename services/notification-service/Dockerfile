# 1️⃣ Base image
FROM python:3.11-slim

# 2️⃣ Set working directory
WORKDIR /app

# 3️⃣ Environment variables (recommended)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4️⃣ Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5️⃣ Copy requirements first (for caching)
COPY requirements.txt .

# 6️⃣ Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 7️⃣ Copy application code
COPY . .

# 8️⃣ Expose port (same inside container)
EXPOSE 8000

# 9️⃣ Run the service
CMD ["python", "main.py"]

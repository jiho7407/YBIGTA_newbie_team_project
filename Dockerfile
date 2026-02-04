# 1. Base Image
FROM python:3.12-slim

# 2. Set Working Directory
WORKDIR /app

# 3. Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Application Code
COPY ./app ./app
COPY ./database ./database
COPY ./review_analysis ./review_analysis
COPY ./utils ./utils

# 5. Expose Port
EXPOSE 8000

# 6. Run Application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Use an official Python image with system dependencies for face_recognition
FROM python:3.10-slim

# Install required system libraries for OpenCV and dlib (face_recognition dependency)
RUN apt-get update && apt-get install -y \
    cmake \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Create a non-root user (This is a best practice for Hugging Face Spaces)
RUN useradd -m -u 1000 user && chown -R user /app
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Expose the port your app runs on (Required: Hugging Face expects port 7860)
EXPOSE 7860

# Command to run your FastAPI application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
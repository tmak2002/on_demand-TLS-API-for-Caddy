# Use an official Python image as the base
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application code and requirements
COPY src/ /app
COPY requirements.txt /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

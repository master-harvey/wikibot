# Use an official Python runtime as a parent image
FROM python:alpine

# Set the working directory to /app
WORKDIR /app

# Install any necessary dependencies
RUN pip install requests

# Copy the current directory contents into the container at /app
COPY ./ini_populate /app/ini_populate

# Run ini_populate.py when the container launches
CMD ["python", "ini_populate.py"]

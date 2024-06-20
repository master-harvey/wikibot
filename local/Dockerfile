# Use an official Python runtime as a parent image
FROM python:alpine

# Set the working directory to /app
WORKDIR /app

# Install any necessary dependencies
RUN pip install requests pymongo openai beautifulsoup4

# Copy the current directory contents into the container at /app
COPY ./iniPopulate.py /app/iniPopulate.py

# Run ini_populate.py when the container launches
CMD ["python", "iniPopulate.py"]
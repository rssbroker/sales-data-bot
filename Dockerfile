# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Download and install ChromeDriver
RUN apt-get update && apt-get install -y wget unzip
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/120.0.6099.71/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip -d /usr/local/bin/

# Set environment variable for ChromeDriver path
ENV PATH="/usr/local/bin:${PATH}"

# Run app.py when the container launches
CMD ["python", "main.py"]

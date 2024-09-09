# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container at /usr/src/app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY app/ ./app/

# Make port 80 available to the world outside this container
# (You can change this if your app uses a different port)
EXPOSE 8050

# Define environment variable
# (You can add more environment variables if needed)
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app/app.py"]
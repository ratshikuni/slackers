# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn (if not included in requirements.txt)
RUN pip install gunicorn

# Expose the port that Flask runs on (Cloud Run default is 8080)
EXPOSE 8080

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production 
 # Ensure production environment

# Use Gunicorn to run the app (replace python app.py)
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]

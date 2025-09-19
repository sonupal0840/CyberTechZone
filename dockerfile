# Python base image
FROM python:3.11-slim

# System dependencies for ODBC
RUN apt-get update && apt-get install -y curl gnupg apt-transport-https unixodbc-dev
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app

# Expose port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "yourproject.wsgi:application", "--bind", "0.0.0.0:8000"]

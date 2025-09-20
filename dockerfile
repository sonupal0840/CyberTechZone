# Python base image
FROM python:3.11-slim

# System dependencies for ODBC
RUN apt-get update && apt-get install -y curl gnupg apt-transport-https unixodbc-dev

# Add Microsoft package signing key (new method for Debian 12)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg

# Add Microsoft SQL Server repository
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Install ODBC driver
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt



# Copy project files
COPY . /app

# Expose port
EXPOSE 8000

# Start Gunicorn (replace `yourproject` with actual Django project name)
CMD ["gunicorn", "leadgenerationFunnel.wsgi:application", "--bind", "0.0.0.0:8000"]

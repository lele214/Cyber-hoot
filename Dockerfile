FROM python:3.11-alpine
RUN mkdir /app
WORKDIR /app

# Install system dependencies required for Python packages
RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Clean up build dependencies to keep image small
RUN apk del gcc musl-dev linux-headers

COPY . .
CMD [ "python3", "main.py" ]
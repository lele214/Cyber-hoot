FROM python:3.11-alpine
RUN mkdir /app
WORKDIR /app

# Install system dependencies required for Python packages and Node.js
RUN apk add --no-cache gcc musl-dev linux-headers nodejs npm

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies and build Tailwind CSS
COPY package.json package.json
RUN npm install

# Copy source files
COPY . .

# Build Tailwind CSS
RUN npm run build:css

# Clean up build dependencies to keep image small
RUN apk del gcc musl-dev linux-headers

CMD [ "python3", "main.py" ]
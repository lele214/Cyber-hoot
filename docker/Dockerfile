FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev linux-headers nodejs npm netcat-openbsd

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY package.json package-lock.json ./
RUN npm install

COPY app/ ./app/
COPY tailwind.config.js ./
COPY docker/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

RUN mkdir -p app/static && npm run build:css

RUN apk del gcc musl-dev linux-headers

EXPOSE 8000

CMD ["python3", "-m", "app.main"]

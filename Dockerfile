FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev linux-headers nodejs npm netcat-openbsd

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY package.json package-lock.json ./
RUN npm install

COPY app/ ./app/
COPY run.py ./
COPY tailwind.config.js ./

RUN npm run build:css

RUN apk del gcc musl-dev linux-headers

EXPOSE 5000

CMD ["python3", "run.py"]

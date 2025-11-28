FROM python:alpine
RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
CMD [ "python3", "main.py" ]
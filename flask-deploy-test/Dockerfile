FROM python:3.8
RUN mkdir /app
WORKDIR /app/
ADD . /app/
RUN pip3 install -r requirements.txt
CMD ["python3", "/app/main.py"]

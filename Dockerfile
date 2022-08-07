
FROM  python:3.8
WORKDIR /chat-server
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY server.py .
CMD ["python", "./server.py"]

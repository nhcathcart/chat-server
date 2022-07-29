
FROM  python:3.8
ADD server.py .
CMD ["python", "./server.py"]

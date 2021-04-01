FROM python:3.8.8-buster
WORKDIR /app
RUN apt install libffi libheif-dev libde265-dev ffmpeg
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app","--host", "0.0.0.0", "--port", "8000"]

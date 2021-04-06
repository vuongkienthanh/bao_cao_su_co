FROM python:3.8.8-buster
WORKDIR /app
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y ffmpeg
RUN git clone https://github.com/strukturag/libheif.git libheif \
    && cd libheif \
    && ./autogen.sh \
    && ./configure \
    && make -j4 \
    && make install \
    && ldconfig \
    && make clean
RUN pip install git+https://github.com/david-poirier-csn/pyheif.git
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn","-k","uvicorn.workers.UvicornWorker","-w","2","--access-logfile","data/access.log","--log-file","data/error.log","-b","0.0.0.0:8000","main:app"]
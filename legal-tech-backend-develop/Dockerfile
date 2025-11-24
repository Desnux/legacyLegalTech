FROM python:3.11-slim

WORKDIR /app

RUN sed -i 's/Components: main/Components: main contrib non-free/g' /etc/apt/sources.list.d/debian.sources

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl wget vim git nodejs ffmpeg libgmp-dev libmpfr-dev libmpc-dev \
       tesseract-ocr tesseract-ocr-spa ghostscript \
       autoconf autotools-dev automake libtool libleptonica-dev make gcc g++ pkg-config \
       libpng-dev libjpeg-dev libwebp-dev zlib1g-dev pngquant postgresql libpq-dev build-essential \
       libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libxcomposite1 libxdamage1 libatspi2.0-0 \
       libgtk-3-0 libevent-2.1-7 libgstreamer-gl1.0-0 libgstreamer-plugins-bad1.0-0 \
       libharfbuzz-icu0 libenchant-2-2 libsecret-1-0 libmanette-0.2-0 libgles2 \
       xfonts-75dpi xfonts-base \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O /tmp/wkhtmltopdf.deb https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb \
    && dpkg -i /tmp/wkhtmltopdf.deb || true \
    && apt-get -f install -y \
    && rm /tmp/wkhtmltopdf.deb

RUN git clone https://github.com/agl/jbig2enc /tmp/jbig2enc \
    && cd /tmp/jbig2enc \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install \
    && rm -rf /tmp/jbig2enc

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install setuptools --upgrade
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install

COPY . .

RUN ls -lR /app/routers/

EXPOSE 8100

COPY docker/entrypoint.sh /entrypoint.sh
RUN tr -d '\r' < /entrypoint.sh > /entrypoint-unix.sh && mv /entrypoint-unix.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]

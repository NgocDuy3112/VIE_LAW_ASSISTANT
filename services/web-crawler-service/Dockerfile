FROM python:3.11-alpine

WORKDIR /src

# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.22/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.22/community" >> /etc/apk/repositories

ENV CHROME_BIN="/usr/bin/chromium-browser"
ENV CHROMEDRIVER_PATH="/usr/bin/chromedriver"

# install chromedriver
RUN apk update
RUN apk add chromium chromium-chromedriver

# Copy requirements file first to cache dependencies
COPY requirements.txt .

# Install PyTorch separately with correct CPU wheels
RUN pip install --upgrade pip

# Then install the rest of the requirements
RUN pip install -r requirements.txt

# Copy app code
COPY app/ .

# Copy and make entrypoint executable
COPY entrypoint.sh .
RUN chmod +x /src/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/src/entrypoint.sh"]
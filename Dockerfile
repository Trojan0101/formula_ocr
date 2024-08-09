# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

# Initialize working directory
WORKDIR /formula_ocr_docker

# Install build dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install application dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Create path for downloaded images
RUN mkdir downloaded_images

# Assign environment variable for tessdata
ENV TESSDATA_PREFIX=/formula_ocr_docker/data_extractors/tesseract_ocr/tessdata/

# Modify rapid_latex_ocr utils file
RUN rm /usr/local/lib/python3.8/site-packages/rapid_latex_ocr/utils.py
COPY /modified_site_packages/rapid_latex_ocr/utils.py /usr/local/lib/python3.8/site-packages/rapid_latex_ocr/utils.py

# Copy all files to working directory
COPY . .

# Expose port 8080
EXPOSE 8080

# Command to run while docker is ran
# CMD [ "sh", "-c", "nohup uwsgi --http :8080 --module app:app > formula_ocr_main.log 2>&1 &" ]
CMD [ "sh", "-c", "uwsgi --http :8080 --module app:app" ]

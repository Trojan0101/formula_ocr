# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /formula_ocr_docker

COPY requirements.txt requirements.txt
RUN pip install virtualenv
RUN virtualenv formula_ocr_env
RUN source formula_ocr_env/bin/activate
RUN pip3 install -r requirements.txt
RUN sudo rm formula_ocr_env/3.8/site_packages/rapid_latex_ocr/utils.py
RUN cp ./modified_site_packages/rapid_latex_ocr/utils.py formula_ocr_env/3.8/site_packages/rapid_latex_ocr/utils.py
RUN mkdir downloaded_images

COPY . .

CMD [ "nohup", "uwsgi" , "--http", ":8080", "--module", "app:app", ">", "formula_ocr_main.log", "2>&1", "&"]

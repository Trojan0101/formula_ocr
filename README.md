# Formula OCR

**Steps to follow:**

**Using general methodology:**

1) Clone the repo into formula_ocr_main directory:
    ```bash
     git clone https://github.com/Trojan0101/formula_ocr.git
     ```

2) Create a directory for file downloading:
    ```bash
     cd formula_ocr
     mkdir downloaded_images
     ```
 
3) Copy tesseract trained datasets for english, japanese, korean, chinese traditional, and chinese simplified to tessdata path in server:
    ```bash
    cd data_extractors/tesseract_ocr/tessdata
    ```
    ```bash
    mv chi_sim.traineddata chi_tra.traineddata kor.traineddata jpn.traineddata eng.traineddata path/to/tessdata
     ```

4) Install dependencies:
    ```bash
    pip install virtualenv
    ```
    ```bash
    virtualenv formula_ocr_env
    ```
    ```bash
    source formula_ocr_env/bin/activate
    ```
    ```bash
    pip install -r ./requirements.txt
    ```
    ```bash
    pip install uwsgi
     ```

5) Modify minimize_image method [`Substitute size_tuple in the next line`]:
    ```bash
     cd formula_ocr_env/<python_version>/site_packages/rapid_latex_ocr/
    ```
    ```bash
     nano utils.py
     ```
     ```python
     size_tuple = tuple(size.astype(int))
      ```

6) Run:
    ```bash
    nohup uwsgi --http :8080 --module app:app > formula_ocr_main.log 2>&1 &
     ```
    ```bash
    disown
    ```

**Using docker:**

1) Load the Docker Image from the Tar File:
    ```bash
    docker load -i docker_images/formula_ocr_docker_linux.tar
    ```

2) Verify the Image is Loaded:
    ```bash
    docker images
    ```

3) Run a Container from the Image [Create `formula_ocr_log` directory]:
    ```bash
    docker run -p 8080:8080 -v /formula_ocr_log:/formula_ocr_docker --name ocr formula_ocr_docker
    ```

**Notes:**

1) Path to tessdata can be `/usr/local/share/tessdata` or `/usr/share/tessdata`

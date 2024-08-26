# Formula OCR

**Steps to follow:**

**Using general methodology:**

1) Clone the repo into formula_ocr_main directory:
    ```bash
     git clone https://github.com/Trojan0101/formula_ocr.git
     ```

2) Install dependencies:
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

3) Move modified utils.py to rapid_latex_ocr utils.py file:
    ```bash
     mv modified_site_packages/rapid_latex_ocr/utils.py formula_ocr_env/<python_version>/site_packages/rapid_latex_ocr/utils.py
    ```

4) Install missing libraries:
   ```bash
   sudo apt-get install libgl1-mesa-glx
   ```
   
5) Run:
    ```bash
    nohup uwsgi --http :8080 --module app:app > formula_ocr_main.log 2>&1 &
     ```
    ```bash
    disown
    ```

**Using docker:**

1) Create the Docker Image:
    ```bash
    cd formula_ocr
    ```
    ```bash
    docker build -t formula_ocr:latest .
    ```

2) Verify the image:
    ```bash
    docker images
    ```

3) Run a Container from the Image:
    ```bash
    docker run -p 8080:8080 formula_ocr:latest
    ```

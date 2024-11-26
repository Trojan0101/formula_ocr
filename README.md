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

3) Move modified utils.py to `rapid_latex_ocr/` utils.py file:
    ```bash
     mv modified_site_packages/rapid_latex_ocr/utils.py formula_ocr_env/<python_version>/site_packages/rapid_latex_ocr/utils.py
    ```

4) Move modified pooling.py to `torch/nn/modules/` pooling.py file:
    ```bash
     mv modified_site_packages/torch/pooling.py formula_ocr_env/<python_version>/site_packages/torch/nn/modules/pooling.py
    ```

5) Install missing libraries:
   ```bash
   sudo apt-get install libgl1-mesa-glx
   ```
   
6) Run:
    ```bash
    nohup uwsgi --http :8080 --module app:app > formula_ocr_main.log 2>&1 &
     ```
    ```bash
    disown
    ```

# Formula OCR

- Detect and extract text in multiple languages **[English, Chinese traditional, Chinese simplified, Korean, Japanese]**.
- Detect and extract mathematical formulas.
- Detect if diagram is present in the image.
- Detect if text is handwritten or printed.
- Convert data to latex format.

## Steps to follow:

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

3) Move modified pooling.py to `torch/nn/modules/` pooling.py file:
    ```bash
     mv modified_site_packages/torch/nn/modules/pooling.py formula_ocr_env/<python_version>/site_packages/torch/nn/modules/pooling.py
    ```

4) Run:
    ```bash
    nohup uwsgi --http :8080 --module app:app > formula_ocr_main.log 2>&1 &
     ```
    ```bash
    disown
    ```

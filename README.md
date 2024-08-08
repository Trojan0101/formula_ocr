# Formula OCR

**Steps to follow:**

1) Clone the repo into formula_ocr_main directory:
	```bash
 	git clone https://github.com/Trojan0101/formula_ocr_jupyter.git
 	```

2) Copy tesseract trained datasets for english, japanese, korean, chinese traditional, and chinese simplified to tessdata path in server:
	```bash
    git clone https://github.com/tesseract-ocr/tessdata.git
	```
	```bash
    cd tesseract-ocr/tessdata
	```
	```bash
    mv chi_sim.traineddata chi_tra.traineddata kor.traineddata jpn.traineddata eng.traineddata path/to/tessdata
 	```

3) Install dependencies:
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

4) Modify minimize_image method [Substitute size_tuple in the next line]:
	```bash
 	cd formula_ocr_env/<python_version>/site_packages/rapid_latex_ocr/
	```
	```bash
 	nano utils.py
 	```
 	```python
 	size_tuple = tuple(size.astype(int))
  	```

5) Run:
	```bash
	nohup uwsgi --http :8080 --module app:app > formula_ocr_main.log 2>&1 &
 	```

**Notes:**

1) Path to tessdata can be /usr/local/share/tessdata or /usr/share/tessdata


py -m pip install --upgrade pip

py -m pip install -r requirements.txt

 py -m unittest  .\api_test.py

 pyinstaller --onefile --name=jiragit --hidden-import=src --hidden-import=utils main.py

 %JIRAGIT_HOME%

// Ne checkout que sur le branche remote
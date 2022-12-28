# pc-automation-client
PC Automation client

## Build the source code
### Create a virtual invironment and activate it
```bash
python -m venv env
```
```bash
source env/bin/activate
```
### Install requirements
```bash
pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```
### Build
```bash
pyinstaller --noconfirm --onedir --windowed --icon "/home/shangala/Documents/pc-automation-client/pcicon.ico" --name "pc-lambo" --add-data "/home/shangala/Documents/pc-automation-client/pcicon.ico:."  "/home/shangala/Documents/pc-automation-client/client.py"
```
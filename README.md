# SGA

## Requisitos
- Python 3.8 ou superior
- Virtualenv

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # se existir
python manage.py migrate
python manage.py runserver


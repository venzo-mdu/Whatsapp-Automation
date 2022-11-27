from waitress import serve
from main import app
import requests

serve(app, host='127.0.0.1', port=5000, threads=1)
s = requests.get('http://127.0.0.1:5000/schedule')
print(s)
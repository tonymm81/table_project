import eventlet
from eventlet import wsgi
from flaskserverWS import app  # Tuo Flask-sovellus pääkoodista

wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
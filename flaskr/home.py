from NaServer import *

from flask import (
    Blueprint, flash, g, session, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
import time, socket
from flaskr.db import get_db

bp = Blueprint('home', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        IPAddr = request.form['IPAddr']
        password = request.form['password']
        error = None

        if not IPAddr:
            error = 'IP Address is required.'
        if not password:
            error = 'Password is required.'

        # Attempt to check if login works here
	s = NaServer(IPAddr, 1 , 140)
	s.set_server_type("FILER")
	s.set_transport_type("HTTPS")
	s.set_port(443)
	s.set_style("LOGIN")
	s.set_admin_user("admin", password)

	response = s.invoke("system-get-version")
	response.sprintf()
	print("Response after invoke:", response)

        if error is not None:
            flash(error)
        else:
            session.clear()
            session['IPAddr'] = IPAddr
            session['password'] = password
            
            current_app.logger.info(time.ctime() + '\t{} successfully connected to {}'.format(socket.gethostbyname(socket.getfqdn()), IPAddr))
            
            return redirect(url_for('auth.upload'))

    return render_template('home/index.html')




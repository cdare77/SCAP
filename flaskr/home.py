from NaServer import *

from flask import (
    Blueprint, flash, g, session, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
import time, socket, ssl
from flaskr.db import get_db

try:
    _create_unverified_https_context = ssl._create_unverified_context
except:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


bp = Blueprint('home', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        IPAddr = request.form['IPAddr'].encode('ascii', 'ignore')
	user = request.form['user'].encode('ascii','ignore')
        password = request.form['password'].encode('ascii','ignore')
        error = None

        if not IPAddr:
            error = 'IP Address is required.'
	if not user:
	    error = 'User name is required.'
        if not password:
            error = 'Password is required.'

        # Attempt to check if login works
	if not test_login_credentials(IPAddr, user, password):
	    error = 'Invalid login info.'
	    current_app.logger.info(time.ctime() + '\tFailed login request from {}'.format(socket.gethostbyname(socket.getfqdn())))

        if error is not None:
            flash(error)
        else:
	    # update the session
            session.clear()
	    session['user'] = user 
	    session['IPAddr'] = IPAddr
	    session['password']= password	    
            
            current_app.logger.info(time.ctime() + '\t{} successfully connected to {}'.format(socket.gethostbyname(socket.getfqdn()), IPAddr))
            
            return redirect(url_for('auth.upload'))

    return render_template('home/index.html')


def test_login_credentials(IPAddr, user, password):

    s = NaServer(IPAddr, 1 , 140)
    s.set_server_type("FILER")
    s.set_transport_type("HTTPS")
    s.set_port(443)
    s.set_style("LOGIN")
    s.set_admin_user(user, password)

    output = s.invoke("system-get-version")

    if output.results_errno() != 0:
	return False
    else :
	return True


    

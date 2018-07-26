from NaServer import *

from flask import (
    Blueprint, flash, g, session, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
import time, socket, ssl
from flaskr.db import get_db


########################################################
#               GLOBAL VARIABLES                       #
########################################################

# Attempt to turn off SSL verification for HTTPS since Self-Signed
# Certificates will cause authentication to fail
#
# NOTE: This is a Catch-22, in that it violates SCAP procedure. Clearly
#       this needs to be updated in later versions.
try:
    _create_unverified_https_context = ssl._create_unverified_context
except:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


bp = Blueprint('home', __name__)

########################################################
#                    WEBPAGES                          #
########################################################

@bp.route('/', methods=('GET', 'POST'))
def index():
    """ Method which renders our home page. The primary functionality is handling
        form request input from the user. We have the option to connect to a
        remote ontap instance (which is handled by proceed_ontap()) or to 
        use the local machine for our checks (which is handled by proceed_localhost())
        """

    if request.method == 'POST':
        # get user info on which end node to run
        endnode = request.form['endnode']
        
        # handle input
        if endnode == 'localhost':
            return proceed_localhost()
        else:
            return proceed_ontap()
    
    # GET
    return render_template('home/index.html')


########################################################
#                    HELPER METHODS                    #
########################################################

def proceed_localhost():
    """ Method which handles our use case of running checks on
        a local machine. Since must alreay be logged into a 
        user, there is no need to grab IPAddr, user, or password
        info. However, for the sake of clarity, we set the user
        to localhost since that is displayed in the interface """

    # clear all cookies and set new ones
    session.clear() 
    session['user'] = "localhost"
    session['local'] = True
    
    # logging stage
    current_app.logger.info(time.ctime() + '\t continuing as localhost')

    return redirect(url_for('upload.upload'))



def proceed_ontap():
    """ Method which handles our use case of running checks
        on a remote ONTAP instance. This requires two stages
        of gathering user input data and checking the validity
        of such input data. Unlike the proceed_localhost() function,
        this method if prone to errors (i.e. invalid credentials); we
        therefore use the flash module to display errors on the
        client side """

    # grab user input data
    IPAddr = request.form['IPAddr'].encode('ascii', 'ignore')
    user = request.form['user'].encode('ascii','ignore')
    password = request.form['password'].encode('ascii','ignore')
    error = None

    # handle missing information
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
        # display any errors on the user side
        flash(error)
    else:
        # clear all cookies and set new ones
        session.clear()
        session['user'] = user
        session['IPAddr'] = IPAddr
        session['password']= password
        session['local'] = False

        # logging stage
        current_app.logger.info(time.ctime() + '\t{} successfully connected to {}'.format(socket.gethostbyname(socket.getfqdn()), IPAddr))
        current_app.logger.info(time.ctime() + '\t continuing as ONTAP user {}'.format(user))
        
        return redirect(url_for('upload.upload'))


def test_login_credentials(IPAddr, user, password):
    """ Tests the login credentials against a NetApp ONTAP instance by
        invoking a small request and checking if the output returns an error.
        
        NOTE: this is relatively inefficient, as it creates a large amount of
            overhead on top of our originial CustomHTTPSConnection. I didn't 
            have the time to look at all of the prerequisite code in NaServer,
            So I was willing to sacrifice a few thousand clock cycles."""

    # Create a server at our specified address
    s = NaServer(IPAddr, 1 , 140)
    s.set_server_type("FILER")
    s.set_transport_type("HTTPS")
    s.set_port(443)
    s.set_style("LOGIN")
    s.set_admin_user(user, password)

    # send a fake request (i.e. we don't care about the output, 
    # just whether it works)
    output = s.invoke("system-get-version")

    if output.results_errno() != 0:
	return False
    else :
	return True


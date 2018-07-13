import functools

import os

from flask import (
    send_from_directory, current_app, Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import oval


# GLOBAL Array of requests
requests = []

bp = Blueprint('checks', __name__, url_prefix='/checks')

@bp.route('/description', methods=('GET', 'POST'))
def description():
    filenames = g.filenames

    for filename in filenames:
        # create a parser and request for each file
        parser = oval.OVALParser()
        parser.parse(filename)
        request = oval.OVALRequest(parser)
        request.initialize()
        
        requests.append( request )
    
    return render_template('checks/description.html', requests=requests)


@bp.route('/results_overview', methods=('GET', 'POST'))
def results_overview():
    
    drivers = [oval.OVALDriver(request) for request in requests]
    del requests[:]
    
    return render_template('checks/results_overview.html', drivers=drivers)



@bp.before_app_request
def load_filename():
    filenames = session.get('filenames')

    if filenames is None:
        g.filenames = None
    else:
        g.filenames = filenames

@bp.before_app_request
def load_ip_addr():
    IPAddr = session.get('IPAddr')

    if IPAddr is None:
        g.IPAddr = None
    else:
        g.IPAddr = IPAddr

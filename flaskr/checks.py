import functools

import os, time

from flask import (
    send_from_directory, current_app, Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import oval
import jsonpickle

bp = Blueprint('checks', __name__, url_prefix='/checks')

@bp.route('/description', methods=('GET', 'POST'))
def description():

    if request.method == 'POST':
        # the requests stored on the server side must be decrypted and converted back to
        # objects
        session['drivers'] = [jsonpickle.encode(oval.OVALDriver( jsonpickle.decode(ovalrequest) )) for ovalrequest in session['requests']]
        # we have handled the requests so we no longer need them
        current_app.logger.info(time.ctime() + " OVAL drivers initialized")
        
        session.pop('requests', None)
        
        return redirect(url_for('results.results_overview'))

    _requests = []

    # get rid of unnecessary baggage in the session
    filenames = g.filenames
    g.pop('filenames', None)
    session.pop('filenames', None)

    for filename in filenames:
        # create a parser and request for each file
        parser = oval.OVALParser()
        current_app.logger.info(time.ctime() + " OVAL Parser for %s initialized" % filename)
        try:
            parser.parse(filename)
        except OVALParseError:
            current_app.logger.error(time.ctime() + " OVAL Parser could not parse " + filename)
        try:
            ovalrequest = oval.OVALRequest(parser)
            current_app.logger.info(time.ctime() + " OVAL Request forr %s created" % filename)
            ovalrequest.initialize()
            _requests.append( ovalrequest )
        except OVALRequestError:
            current_app.logger.error(time.ctime() + " could not generate OVAL Request for " + filename)

    session['requests'] = [jsonpickle.encode(ovalrequest) for ovalrequest in _requests]

    return render_template('checks/description.html', requests=_requests)




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

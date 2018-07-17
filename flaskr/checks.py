import functools

import os, time

from multiprocessing import Pool

from flask import (
    send_from_directory, current_app, Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import oval

bp = Blueprint('checks', __name__, url_prefix='/checks')


# Global variable -- Attempting to Serialize an OVAL request into a
# JSON object can mess with the regex patterns or paths. Thus,
# session['requests'] will not work 
_requests = []

# Found out that encapsulating multiple drivers is too big for
# the browser cookie size. This led to several 'NoneType' not
# iterable errors
_drivers = []

_pool = None

@bp.route('/description', methods=('GET', 'POST'))
def description():

    global _requests

    if request.method == 'POST':

        global _drivers
        
        _drivers = [oval.OVALDriver( ovalrequest ) for ovalrequest in _requests]
        current_app.logger.info(time.ctime() + "\tOVAL drivers initialized")
        
        # we have handled the requests so we no longer need them
        remove_persist_storage('filenames')
        remove_persist_storage('processType')
        remove_persist_storage('coreFactor')
        del _requests[:] 
        
        return redirect(url_for('checks.results_overview'))


    create_descriptions()
    return render_template('checks/description.html', requests=_requests)



@bp.route('/results_overview', methods=('GET', 'POST'))
def results_overview():
    if request.method == "POST":
        # clean out all unwanted storage
        if _pool:
            _pool.terminate()
        del _drivers[:]
        
        return redirect(url_for('auth.upload'))

    global _drivers

    processType = g.processType
    coreFactor = g.coreFactor

    if processType == 'parallel':
        current_app.logger.info(time.ctime() + "\tProcess pool with %s processes initialized for execution" % coreFactor)
        results = _pool.map(get_result, _drivers)
    else:
        results = [get_result(driver) for driver in _drivers]

    return render_template('checks/results_overview.html', results=results)



def get_result(driver):
    result = oval.OVALResult(driver.request.title, driver.execute_tests())
    return result


def get_description(filename):
        
    # create a parser and request for each file
    parser = oval.OVALParser()
    current_app.logger.info(time.ctime() + "\tOVAL Parser for %s initialized" % filename)
    try:
        parser.parse(filename)
    except OVALParseError:
        current_app.logger.error(time.ctime() + "\tOVAL Parser could not parse " + filename)

    try:
        ovalrequest = oval.OVALRequest(parser)
        current_app.logger.info(time.ctime() + "\tOVAL Request for %s created" % filename)
        ovalrequest.initialize()
        return ovalrequest
    except OVALRequestError:
        current_app.logger.error(time.ctime() + "\tcould not generate OVAL Request for " + filename)



def remove_persist_storage(name):
    g.pop(name, None)
    session.pop(name, None)


def create_descriptions():

    global _requests
    global _pool

    # capture input from form
    filenames = g.filenames
    processType = g.processType
    coreFactor = g.coreFactor

    # ensure no requests persisted from last time
    del _requests[:]

    if processType == 'parallel':
        _pool = Pool(processes=int(coreFactor))
        current_app.logger.info(time.ctime() + "\tProcess pool with %s processes initialized for descriptions" % coreFactor)
        _requests = _pool.map(get_description, filenames)
    
    else:
        for filename in filenames:
            _requests.append(get_description(filename))



@bp.before_app_request
def load_process_type():
    processType = session.get('processType')

    if processType is None:
        g.processType = None
    else:
        g.processType = processType

@bp.before_app_request
def load_core_factor():
    coreFactor = session.get('coreFactor')

    if coreFactor is None:
        g.coreFactor = None
    else:
        g.coreFactor = coreFactor

@bp.before_app_request
def load_filenames():
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

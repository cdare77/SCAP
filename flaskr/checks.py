import functools, os, time, oval
from AES import *
from multiprocessing import Pool, cpu_count

from flask import (
    send_from_directory, current_app, Blueprint, flash, g, redirect, render_template, request, session, url_for
)


########################################################
#               GLOBAL VARIABLES                       #
########################################################

bp = Blueprint('checks', __name__, url_prefix='/checks')

# Global variable -- Attempting to Serialize an OVAL request into a
# JSON object can mess with the regex patterns or paths. Thus,
# session['requests'] will not work 
_requests = []

# Found out that encapsulating multiple drivers is too big for
# the browser cookie size. This led to several 'NoneType' not
# iterable errors
_drivers = []

# Since the overhead of starting up a pool is large, we want
# to only instantiate one
_pool = None


########################################################
#                    WEBPAGES                          #
########################################################

@bp.route('/description', methods=('GET', 'POST'))
def description():
    """ Method which renders our description webpage and adds functionality to
        POST calls. For GET requests, this method essentially creates several
        OVALRequests. For POST requests, this method converts the OVALRequests
        into OVALDrivers, which are used in the following webpage """

    # Captures the global requests variable
    global _requests

    if request.method == 'POST':

        global _drivers
        
        IPAddr = g.IPAddr

        # All sensitive data in the session must be encrypted
        AESKey = [ord(elem) for elem in current_app.config['SECRET_KEY']]
        AES = AESEncryptor(key=AESKey)

        password = AES.decrypt(g.password)
        user = g.user
        
        _drivers = [oval.OVALDriver( ovalrequest, IPAddr=IPAddr, user=user, password=password, verbose=False ) for ovalrequest in _requests]
        current_app.logger.info(time.ctime() + "\tOVAL drivers initialized")
        
        # we have handled the requests so we no longer need them
        _remove_persist_storage('filenames')
        _remove_persist_storage('processType')
        _remove_persist_storage('coreFactor')
        del _requests[:] 
        
        return redirect(url_for('checks.results_overview'))


    # GET
    # Calls all the backend code
    _create_descriptions()
    return render_template('checks/description.html', requests=_requests)



@bp.route('/results_overview', methods=('GET', 'POST'))
def results_overview():
    """ Method which renders our results webpage and adds functionality
        to the POST calls. For GET requests, all the drivers execute their
        tests and pass OVALResults to the HTML. For POST requests, all data
        is cleared and we return to the upload screen """

    if request.method == "POST":
        # clean out all unwanted storage
        if _pool:
            _pool.terminate()
        del _drivers[:]
        
        return redirect(url_for('upload.upload'))

    # GET
    
    # Captures the global drivers variable
    global _drivers

    processType = g.processType
    coreFactor = g.coreFactor

    if processType == 'parallel':
        current_app.logger.info(time.ctime() + "\tProcess pool with %s processes initialized for execution" % coreFactor)
        results = _pool.map(_get_result, _drivers)
    else:
        results = [_get_result(driver) for driver in _drivers]

    return render_template('checks/results_overview.html', results=results)



########################################################
#                    HELPER METHODS                    #
########################################################


def _get_result(driver):
    """ Wrapper function for multiprocessing.Pool.map() function. Creates
        an OVALResult for each test"""
    
    result = oval.OVALResult(driver.request.title, driver.execute_tests())
    current_app.logger.info(time.ctime() + "\tOVAL Result created for %s" % result.title)

    return result


def _get_description(filename):
    """ Wrapper function for multiprocessing.Pool.map() function. Creates a
        OVALParser and OVALRequest for each file """
    
    parser = oval.OVALParser()
    current_app.logger.info(time.ctime() + "\tOVAL Parser for %s initialized" % filename)
    try:
        parser.parse(filename)
    except OVALParseError:
        current_app.logger.error(time.ctime() + "\tOVAL Parser could not parse " + filename)

    try:
        isLocal = g.local
        
        # create an ovalrequest based on our parser and the end node
        ovalrequest = oval.OVALRequest(parser, local=isLocal)
        current_app.logger.info(time.ctime() + "\tOVAL Request for %s created" % filename)
        
        # attempt to initialize the rewuest
        ovalrequest.initialize()
        
        return ovalrequest

    except OVALRequestError:
        current_app.logger.error(time.ctime() + "\tcould not generate OVAL Request for " + filename)



def _remove_persist_storage(name):
    """ Helper function to clear server of cookies tied to %name """
    g.pop(name, None)
    session.pop(name, None)


def _create_descriptions():
    """ Main functionality of checks/description webpage """

    # capture global variables requests and poo
    global _requests
    global _pool

    # extract cookies
    filenames = g.filenames
    processType = g.processType
    coreFactor = g.coreFactor
    
    # ensure no requests persisted from last time
    del _requests[:]

    # determine how program is going to be run
    if processType == 'parallel':
    
        # Multiply core factor by our number of cores
        cores = _get_num_processors()
        num_processes = int(float(coreFactor) * cores)
    
        _pool = Pool(processes=num_processes)
        current_app.logger.info(time.ctime() + "\tProcess pool with %s processes initialized for descriptions" % num_processes)
        _requests = _pool.map(_get_description, filenames)
    
    else:
        for filename in filenames:
            _requests.append(_get_description(filename))

    # We create a pool based off these cookie, so no longer need it
    _remove_persist_storage("processType")
    _remove_persist_storage("coreFactor")


def _get_num_processors():
    """ Does what the name suggests - returns the number
        of cpus """
    cores = 0
    try:
        cores = len(os.sched_getaffinity(0))
    except AttributeError:
        cores = cpu_count()
    return cores



########################################################
#                    COOKIE METHODS                    #
########################################################

@bp.before_app_request
def _load_process_type():
    """ Loads processType data from the cookie to local request storage"""
    processType = session.get('processType')

    if processType is None:
        g.processType = None
    else:
        g.processType = processType

@bp.before_app_request
def _load_core_factor():
    """ Loads coreFactor data from the cookie to local request storage"""
    coreFactor = session.get('coreFactor')

    if coreFactor is None:
        g.coreFactor = None
    else:
        g.coreFactor = coreFactor

@bp.before_app_request
def _load_filenames():
    """ Loads filename data from the cookie to local request storage"""
    filenames = session.get('filenames')

    if filenames is None:
        g.filenames = None
    else:
        g.filenames = filenames

@bp.before_app_request
def _load_ip_addr():
    """ Loads IPAddr data from the cookie to local request storage"""
    IPAddr = session.get('IPAddr')

    if IPAddr is None:
        g.IPAddr = None
    else:
        g.IPAddr = IPAddr

@bp.before_app_request
def _load_user():
    """ Loads user data from the cookie to local request storage"""
    user = session.get('user')

    if user is None:
        g.user = None
    else:
        g.user = user

@bp.before_app_request
def _load_password():
    """ Loads password data from the cookie to local request storage"""
    password = session.get('password')

    if password is None:
        g.password = None
    else:
        g.password = password

@bp.before_app_request
def _load_local():
    """ Loads local (boolean) data from the cookie to local (scope) request storage"""
    local = session.get('local')

    if local is None:
        g.local = None
    else:
        g.local = local

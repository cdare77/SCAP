import functools

import os

from flask import (
    send_from_directory, current_app, Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import oval

from flaskr.db import get_db

bp = Blueprint('checks', __name__, url_prefix='/checks')

@bp.route('/description', methods=('GET', 'POST'))
def description():

    filenames = g.filenames
    requests = []

    for filename in filenames:
    
        parser = oval.OVALParser(filename, False)
        requests.append( oval.OVALRequest(parser) )

    return render_template('checks/description.html', requests=requests)


def dict_to_str(dictionary):
    my_str = ''
    for key, value in dictionary.items():
        my_str += "{}\t:\t{}\n".format(key, value)
    return my_str


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

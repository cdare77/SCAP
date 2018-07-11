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
    
    parser = oval.OVALParser(g.filename, False)
#    dictionary = parser.get_dictionary()
#
#    formatted_dict = {}
#
#    for key, value in dictionary.items():
#        my_str = dict_to_str(value.properties)
#        my_str += "Content  :  {}".format(value.content)
#        formatted_dict[key] = my_str

    request = oval.OVALRequest(parser)

    return render_template('checks/description.html', request=request)


def dict_to_str(dictionary):
    my_str = ''
    for key, value in dictionary.items():
        my_str += "{}\t:\t{}\n".format(key, value)
    return my_str


@bp.before_app_request
def load_filename():
    filename = session.get('filename')

    if filename is None:
        g.filename = None
    else:
        g.filename = filename

@bp.before_app_request
def load_ip_addr():
    IPAddr = session.get('IPAddr')

    if IPAddr is None:
        g.IPAddr = None
    else:
        g.IPAddr = IPAddr

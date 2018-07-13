import functools

import os
import jsonpickle
import oval

from flask import (
    send_from_directory, current_app, Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('results', __name__, url_prefix='/results')

@bp.route('/results_overview', methods=('GET', 'POST'))
def results_overview():
    drivers = [jsonpickle.decode(driver) for driver in g.drivers]
    session.pop('drivers', None)
    return render_template('results/results_overview.html', drivers=drivers)

@bp.before_app_request
def load_drivers():
    drivers = session.get('drivers')

    if drivers is None:
        g.drivers = None
    else:
        g.drivers = drivers

@bp.before_app_request
def load_ip_addr():
    IPAddr = session.get('IPAddr')

    if IPAddr is None:
        g.IPAddr = None
    else:
        g.IPAddr = IPAddr

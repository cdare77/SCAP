import functools

import os

from flask import (
    send_from_directory, current_app, Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('results', __name__, url_prefix='/results')


@bp.route('/results_overview', methods=('GET', 'POST'))
def results_overview():
    

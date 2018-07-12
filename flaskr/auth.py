import functools

import os, time, socket

from flask import (
    send_from_directory, current_app, Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import oval

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

ALLOWED_EXTENSIONS = set(['xml'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=('GET', 'POST'))
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        # get list of files
        files = request.files.getlist("file")
        # if user does not select file, browser also
        # submit an empty part without filename
        if not files or files[0].filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        # create list of valid files
        session['filenames'] = []
        my_addr = socket.gethostbyname(socket.getfqdn())

        for file in files:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                session['filenames'].append(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                current_app.logger.info(time.ctime() + '\t{} successfully uploaded {}'.format(my_addr, filename))
            else:
                current_app.logger.info(time.ctime() + '\t{} attempted to upload {}'.format(my_addr, file.filename))

        if session['filenames']:
            return redirect(url_for('checks.description'))


    return render_template('auth/upload.html')

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],
                               filename)

@bp.before_app_request
def load_ip_addr():
    IPAddr = session.get('IPAddr')

    if IPAddr is None:
        g.IPAddr = None
    else:
        g.IPAddr = IPAddr


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))



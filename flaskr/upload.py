import functools

import os, time, socket, oval

from flask import (
    send_from_directory, current_app, Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


########################################################
#               GLOBAL VARIABLES                       #
########################################################

bp = Blueprint('upload', __name__, url_prefix='/upload')

# Sets are much more efficient for indexing
ALLOWED_EXTENSIONS = set(['xml'])

########################################################
#                    WEBPAGES                          #
########################################################


@bp.route('/upload', methods=('GET', 'POST'))
def upload():
    """ Method which renders our upload webpage. When
        files are uploaded and submitted, we check two forms of
        input: files uploaded and the driver's serialization/parallelization.
        We use this info to proceed to the checks section. """

    if request.method == 'POST':

        # Handle user input regarding files to upload
        handle_file_input()

        # handle user input regarding serialization / parallelization
        processType = request.form['processType']
        session['processType'] = processType

        if processType == 'parallel':
            session['coreFactor'] = request.form['coreFactor']
 
        # if we actually have files that passed the checks,
        # we may proceed
        if session['filenames']:
            return redirect(url_for('checks.description'))

    # GET
    return render_template('upload/upload.html')


########################################################
#                    HELPER METHODS                    #
########################################################

def handle_file_input():
    """ Helper method which handles the user input of multiple files.
        If no files are provided, an error is flashed to the user's screen.
        Any previous files are then cleared from the session. Lastly, we
        iterate over each file uploaded and check whether we want to include
        it based off the extension. """

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
    
    # ensure previous files do not persist
    session.pop('filenames', None)

    # create list of valid files
    session['filenames'] = []

    # gather user info for logging
    my_addr = socket.gethostbyname(socket.getfqdn())

    for file in files:
        if allowed_file(file.filename):
            # modify filename so that it does not have a dangerous pattern
            filename = secure_filename(file.filename)
            # save the file in /uploads
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            # append the file to our valid files
            session['filenames'].append(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            # log out info
            current_app.logger.info(time.ctime() + '\t{} successfully uploaded {}'.format(my_addr, filename))
        else:
            current_app.logger.info(time.ctime() + '\t{} unsuccessfully attempted to upload {}'.format(my_addr, file.filename))


def allowed_file(filename):
    """ Simple inline helper method which allows us to extract
        the file extension and check if it is in our ALLOWED_EXTENSIONS
        set """
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """ Helper method which allows us to look at the content of
        uploaded files """
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],
                               filename)

@bp.route('/logout')
def logout():
    """ Helper method which clears all cookies and takes us back to the
        home page """
    session.clear()
    g.pop('IPAddr', None)
    g.pop('filenames', None)
    return redirect(url_for('index'))

# SCAP for ONTAP

## 1. Overview
The SCAP for ONTAP project is an application meant to be run on <html>*NIX</html> or NetApp systems which checks the state of the specified machine for Security Content Automation Protocol (SCAP) compatibility. The application renders input from OVAL files, which are provided after successfuly connection. For easy usability, the application is executed on a Flask server so that all user interaction can be done via a web browser. Certain scripts can be run independently from the command line - such scripts can distinguish by  
```
if __name__ == "__main__":
```
blocks towards the bottom of the script (which should be fimiliar to any Python developers).

## 2. How to Use
In order to run SCAP for ONTAP, Python must be installed on the machine executing it. In addition, `pip` must be installed to support `Flask`, `flask-bootstrap` and `jsonpickle`. To install the two libraries, simply run
```
pip install Flask
pip install flask-bootstrap
pip install jsonpickle
```
if the reader is further interested in how Flask works, refer to the [Flask Website](http://flask.pocoo.org/). A script `SCAP.sh` is provided to set all the environment variables required for Flask. Refer to standard output to find which port the application is running on - it is typically 5000 for development purposes. The IP address is always `localhost`.

## 3. Considerations
- There is no encryption between `home.py` where the credentials are read and the NetApp API. This is a bit of a catch-22 since it violates SCAP compatibility.
- All actions are logged to the app.log file; however, this log file does not necessarily follow any format besides
```
timestamp message
```

## 4. Future Plans
- Providing an entire SCAP directory at the upload stage complete with XCCDF schemas, CPE files, on top of the current OVAL files.
- Upload files in a concurrent manner instead of iterative

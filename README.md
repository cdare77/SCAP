# SCAP for ONTAP

## 1. Overview
The SCAP for ONTAP project is an application meant to be run on <html>*NIX</html> or NetApp systems which checks the state of the specified machine for Security Content Automation Protocol (SCAP) compatibility. The application renders input from OVAL files, which are provided after successfuly connection. For easy usability, the application is executed on a Flask server so that all user interaction can be done via a web browser. Certain scripts can be run independently from the command line - such scripts can distinguish by  
```
if __name__ == "__main__":
```
blocks towards the bottom of the script (which should be fimiliar to any Python developers).

## 2. How to Use
In order to run SCAP for ONTAP, Python must be installed on the machine executing it. In addition, `pip` must be installed to support `Flask` and  `flask-bootstrap` . To install the two libraries, simply run
```
pip install Flask
pip install flask-bootstrap
```
if the reader is further interested in how Flask works, refer to the [Flask Website](http://flask.pocoo.org/).

A script `SCAP.sh` is provided to set all the environment variables required for Flask. Refer to standard output to find which port the application is running on - it is typically 5000 for development purposes. The IP address is always `localhost`.

## 3. Description of Program
As previously mentioned, the majority of the server-side code is handled via the Flask library. Since Flask also supports Jinja 2.0, all html pages are written in Jinja format. Additionally, since the program utilizes flask-bootstrap, our base.html is actually an extension of  `bootstrap/base.html`. 
At the server level, the program essentially bounces back and forth between POST requests from one page to GET requests for another.  The life-cycle of a typical server-side execution is as follows:

1. home.py (handles login info and connectivity to ONTAP instance)
2. upload.py (uploads any files and takes user settings for serialization/parallelization)
3. checks.py (runs backend code and displays results)

Each script handles both GET and POST requests for the respective front-end documents it is responsible for.
On the backend, there are 4 primary scripts that gather data and check the local system. The lifeline of a typical backend-execution for an OVAL script is the following:

1. OVALParser.py (parses an oval file and creates a dictionary of XMLElements)
2. OVALRequest.py (creates a request ticket which has information on all the tests which need to be run)
(in between steps 2-3 above here)
3. OVALDriver.py (parses the ticket and runs all tests in the ticket)
4. OVALResponse (contains information on whether program passed and, if not, what caused program to fail)
Note that backend steps 1 and 2 run in between server-side steps 2 and 3. However, backend steps 3 and 4 run during backend step 3.

The reason so much code is run on step 3 is because some buffer is needed to transport OVALDrivers to OVALResults. I originally attempted to serialize the classes using `jsonpickle`, but this was an inefficient and non-scalable way of transporting data via cookies. Since a max of 4093 bytes could be sent via cookies, I would have had to cancel any future hopes of uploading an entire SCAP / XCCDF folder. Instead, I have ONE Python script take care of two links in the execution lifeline: OVALDriver and OVALResult. This is also not well-scalable, but I have no better method of buffering OVALDrivers in the server than to store them in a global variable (global to checks.py)

## 4. Considerations
- There is no encryption between `home.py` where the credentials are read and the NetApp API. This is a bit of a catch-22 since it violates SCAP compatibility.
- All actions are logged to the app.log file; however, this log file does not necessarily follow any format besides
```
timestamp message
```
- In order to log into an ONTAP instance, one must turn off SSL authentication so that self-signed certificates work. This also is a bit of a catch-22 since it violates SCAP compatibility
- `checks.py` violates good programming practice of not running any back-end code in the handling of a GET request. GET requests are simple, and should merely render a provide a file - heavy backend work should be prompted by a POST request. This was difficult for me to get around, however, since I wanted the program's timing to be based off user input (clicking a button). 

## 5. Future Plans
- Find efficient way to transport data between Python scripts besides setting cookies in session[] or g.
- Providing an entire SCAP directory at the upload stage complete with XCCDF schemas, CPE files, on top of the current OVAL files.

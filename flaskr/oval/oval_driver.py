"""
Author: Chris Dare
Version: 1.0
"""

import sys, stat, os, re

from oval_request import OVALRequest
from oval_parser import OVALParser, XMLElement
from .. import NaServer
from .. import NaElement

class OVALDriverError(Exception):
    """ Custom exception for the OVAL Driver class """
    pass

class OVALDriver:

    def __init__(self, request, IPAddr = None, user = None, password=None):
        """ Constructor for driver - iteratively executes all tests found in
            a single file """
    
        self.request = request
        
        self.IPAddr = IPAddr
        self.user = user
        self.password = password
        
        self.ontap_server = None
        
        if self.IPAddr and self.user and self.password:
            s = NaServer.NaServer(self.IPAddr, 1, 140)
            s.set_server_type("FILER")
            s.set_transport_type("HTTPS")
            s.set_port(443)
            s.set_style("LOGIN")
            s.set_admin_user(self.user, self.password)
            
            self.ontap_server = s
        
        # Our request must be initialized. This may throw errors;
        # however, we would rather not initialize a driver if there
        # is a faulty request
        if not request.initialized:
            request.initialize()

        # dictionary which matches outputs of requests to functions
        self.test_dictionary = {
            'local_check_file_permissions' : self.local_check_file_permissions(),
            'local_search_for_pattern' : self.local_search_for_pattern(),
            'ontap_ssl_enabled' : self.ontap_ssl_enabled()
        }


    def execute_tests(self):
        """ Executes all tests in an OVAL Request's ticket """
        return [self.test_dictionary[test] for test in self.request.tests]


    def local_search_for_pattern(self):
        """ Given a regex pattern provided in the OVAL
            file, we attempt to use that pattern for matching
            in a destination file """
        
        # This test is specifically for the local machine
        if self.IPAddr is not None:
            return
        
        pattern = self.request.get_body_content('pattern')
        
        # Do not continue if no pattern is provided
        if not pattern:
            return
        
        path = self.request.get_all_files()[0]
        my_file = open(path, 'r').read()
        
        # Check if pattern is a multiline regex
        flags = None
        if pattern[0] is '^' and pattern[-1] is '$':
            flags = re.MULTILINE

        try:
            result = re.match(pattern, my_file, flags)
            if not result:
                return ("Pattern inconsistent or not found in %s" % path, False)
            else:
                return ("%s is consistent" % path, True)
        except:
            # pcre (php) regex will fail in python
            raise OVALDriveError("Regex pattern not compatible with Python RegEx 101. Remember not to use inline flags.")



    def local_check_file_permissions(self):
        """ If file permissions are provided, attempt to check
            the destination file for inconsistencies """

        # This test is specifically meant for the local machine
        if self.IPAddr is not None:
            return

        path = self.request.get_all_files()[0]
        
        st = os.stat(path)
        inconsistent = []   # keep track of inconsistent permissions

        # Check consistency of user permissions
        uexec_str = self.request.get_body_content('uexec')
        if uexec_str and  uexec_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IXUSR):
            inconsistent. append("uexec")
        
        uwrite_str = self.request.get_body_content('uwrite')
        if uwrite_str and  uwrite_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IWUSR):
            inconsistent. append("uwrite")
        
        uread_str = self.request.get_body_content('uread')
        if uread_str and  uread_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IRUSR):
            inconsistent. append("uread")
        
        # Check consistency of group permissions
        gexec_str = self.request.get_body_content('gexec')
        if gexec_str and  gexec_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IXGRP):
            inconsistent. append("gexec")

        gwrite_str = self.request.get_body_content('gwrite')
        if gwrite_str and  gwrite_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IWGRP):
            inconsistent. append("gwrite")

        gread_str = self.request.get_body_content('gread')
        if gread_str and  gread_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IRGRP):
            inconsistent. append("gread")

        # Check consistency of others' permissions
        oexec_str = self.request.get_body_content('oexec')
        if oexec_str and  oexec_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IXOTH):
            inconsistent. append("oexec")

        owrite_str = self.request.get_body_content('owrite')
        if owrite_str and  owrite_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IWOTH):
            inconsistent. append("owrite")

        oread_str = self.request.get_body_content('oread')
        if oread_str and  oread_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IROTH):
            inconsistent. append("oread")

        if not inconsistent:
            return ("File permissions are consistent for %s" % path, True)
        else:
            return ("The following permissions are inconsistent for %s: %s" % (path, str(inconsistent)), False)

    def ontap_ssl_enabled(self):

        if not self.ontap_server:
            raise OVALDriverException("ONTAP driver has not been created.")

        api = NaElement.NaElement("security-ssl-get-iter")
        xi = NaElement.NaElement("desired-attributes")
        api.child_add(xi)

        xi1 = NaElement.NaElement("vserver-ssl-info")
        xi.child_add(xi1)

        xi1.child_add_string("client-authentication-enabled", "<client-authentication-enabled>")
        xi1.child_add_string("server-authentication-enabled", "<server-authentication-enabled>")
        api.child_add_string("max-records", "2")

        xi2 = NaElement.NaElement("query")
        api.child_add(xi2)

        xi3 = NaElement.NaElement("vserver-ssl-info")
        xi2.child_add(xi3)

        xi3.child_add_string("certificate-authority", "*")
        api.child_add_string("tag", "<tag>")

        out = self.ontap_server.invoke_elem(api)
        
        if out.results_status() == "failed":
            pass
        
        print (out.child_get_string("server-authentication-enabled"))

# For testing purposes only
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n\tUsage: python oval_driver.py [file]\n")
        sys.exit()

    print("Num processors:", get_num_processors())

    filename = sys.argv[1]

    parser = OVALParser()
    parser.parse(filename)
    print(parser)

    request = OVALRequest(parser)
    request.initialize()
    print("request:", request)

    driver = OVALDriver(request)
    print(driver.execute_tests())

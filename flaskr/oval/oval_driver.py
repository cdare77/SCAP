"""
Author: Chris Dare
Version: 1.0
"""

import sys, stat, os, re, ssl

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from oval_request import OVALRequest
from oval_parser import OVALParser, XMLElement


########################################################
#               GLOBAL VARIABLES                       #
########################################################

# Attempt to turn off SSL verification for HTTPS since Self-Signed
# Certificates will cause authentication to fail
#
# NOTE: This is a Catch-22, in that it violates SCAP procedure. Clearly
#       this needs to be updated in later versions.
try:
    _create_unverified_https_context = ssl._create_unverified_context
except:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

########################################################
#                     EXCEPTIONS                       #
########################################################

class OVALDriverError(Exception):
    """ Custom exception for the OVAL Driver class """
    pass

########################################################
#                      CLASSES                         #
########################################################

class OVALDriver:

    def __init__(self, request, IPAddr = None, user = None, password=None, verbose=False, version=None):
        """ Constructor for driver - iteratively executes all tests found in
            a single file """
    
        self.request = request
        # ONTAP credentials
        self.IPAddr = IPAddr
        self.user = user
        self.password = password
        
        self.verbose = verbose
        # ONTAP version
        self.version = version
        
        self.ontap_server = None
        
        if self.IPAddr and self.user and self.password:
            # ONTAP server
            s = None
            # Version control
            if self.version == "9.4":
                from NetApp_9_4 import (NaServer, NaElement)
                s = NaServer(self.IPAddr, 1, 140)
            else:
                from NetApp_9_3 import (NaServer, NaElement)
                s = NaServer(self.IPAddr, 1, 130)
                
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
            'local_check_file_permissions' : self._local_check_file_permissions,
            'local_search_for_pattern' : self._local_search_for_pattern,
            'ontap_ssl_enabled' : self._ontap_ssl_enabled,
            'ontap_vols_encrypted' : self._ontap_vols_encrypted,
            'ontap_autosupport_disabled' : self._ontap_autosupport_disabled,
            'ontap_password_authentication' : self._ontap_password_authentication,
            'ontap_sha_hash_enabled' : self._ontap_sha_hash_enabled,
            'ontap_password_policy' : self._ontap_password_policy
        }

        # end constructor ---------


    def execute_tests(self):
        """ Helper method which iterates over the instance's dictionary of
            functions and executes the ones present in the request """
        
        if self.verbose:
            print("Executing the following tests:")
            print(self.request.tests)
        
        """ Executes all tests in an OVAL Request's ticket """
        return [self.test_dictionary[test]() for test in self.request.tests]


    ###########################
    #      LOCAL FUNCTS       #
    ###########################

    def _local_search_for_pattern(self):
        """ Given a regex pattern provided in the OVAL
            file, we attempt to use that pattern for matching
            in a destination file """
        
        if self.verbose:
            print("Executing local_search_for_pattern")
        
        # This test is specifically for the local machine
        if self.ontap_server is not None:
            return
        
        pattern = self.request.get_body_content('pattern')
        raw_pattern = "%r"%pattern
        
        # Do not continue if no pattern is provided
        if not pattern:
            return
        
        path = self.request.get_all_files()[0]
	
        try:
            my_file = open(path, 'r').read()
        except IOError:
            raise OVALDriverError("Could not read %s - check file permissions" % path)


        # Check if pattern is a multiline regex
        flags = None
        if raw_pattern[0] is '^' and raw_pattern[-1] is '$':
            flags = re.MULTILINE

        try: 
            regex = re.compile(raw_pattern, re.MULTILINE)
            result = regex.findall(my_file) 
            
            if not result:
                return (["Pattern inconsistent or not found in %s" % path], False)
            else:
                return (["%s is consistent" % path], True)
        except:
            # pcre (php) regex will fail in python
            raise OVALDriverError("Regex pattern not compatible with Python RegEx 101. Remember not to use inline flags.")



    def _local_check_file_permissions(self):
        """ If file permissions are provided, attempt to check
            the destination file for inconsistencies. We first
            create a list of all files that are inconsistend,
            and then proceed by permission level (user, group,
            other) """
        
        if self.verbose:
            print("Executing local_check_file_permissions")

        # This test is specifically meant for the local machine
        if self.ontap_server is not None:
            return

        path = self.request.get_all_files()[0]
        
        st = os.stat(path)
        inconsistent = []   # keep track of inconsistent permissions

        # Check consistency of user permissions
        uexec_str = self.request.get_body_content('uexec')
        if uexec_str and  uexec_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IXUSR):
            inconsistent.append("uexec")
        
        uwrite_str = self.request.get_body_content('uwrite')
        if uwrite_str and  uwrite_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IWUSR):
            inconsistent.append("uwrite")
        
        uread_str = self.request.get_body_content('uread')
        if uread_str and  uread_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IRUSR):
            inconsistent.append("uread")
        
        # Check consistency of group permissions
        gexec_str = self.request.get_body_content('gexec')
        if gexec_str and  gexec_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IXGRP):
            inconsistent.append("gexec")

        gwrite_str = self.request.get_body_content('gwrite')
        if gwrite_str and  gwrite_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IWGRP):
            inconsistent.append("gwrite")

        gread_str = self.request.get_body_content('gread')
        if gread_str and  gread_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IRGRP):
            inconsistent.append("gread")

        # Check consistency of others' permissions
        oexec_str = self.request.get_body_content('oexec')
        if oexec_str and  oexec_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IXOTH):
            inconsistent.append("oexec")

        owrite_str = self.request.get_body_content('owrite')
        if owrite_str and  owrite_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IWOTH):
            inconsistent.append("owrite")

        oread_str = self.request.get_body_content('oread')
        if oread_str and  oread_str.strip().lower() == 'false' \
            and bool(st.st_mode & stat.S_IROTH):
            inconsistent. append("oread")

        if not inconsistent:
            return (["File permissions are consistent for %s" % path], True)
        else:
	    message = ["The following permission is inconsistent for %s: %s" % (path, incos) for incos in inconsistent]
            return (message, False)


    ###########################
    #      REMOTE FUNCTS      #
    ###########################

    def _ontap_ssl_enabled(self):
        """ Assuming an IP address, username, and password are provided
            to the ONTAP instance, we attempt to retrieve ssl information
            and parse the ZAPI results. We check both server SSL authentication
            and client SSL authentication """
        
        if self.verbose:
            print("Executing ontap_ssl_enabled")

        if not self.ontap_server:
            # We cannot connect if we are not provided IPAddr, user, password
            return

        # send the ZAPI request to the ONTAP node
        out = self.ontap_server.invoke("security-ssl-get-iter")

        if out.results_status() == "failed": 
            # do not attempt to parse results if the request failed
            reason = out.results_reason()
	    raise OVALDriverError("ONTAP driver error " + reason)
        
        # attempt to parse results of request
	attr_list = out.child_get("attributes-list")
	vserver_ssl_info = attr_list.child_get("vserver-ssl-info")
	print (vserver_ssl_info.sprintf())
	
        server_auth_enabled = vserver_ssl_info.child_get_string("server-authentication-enabled")
	client_auth_enabled = vserver_ssl_info.child_get_string("client-authentication-enabled")
 
        # return formatted output to OVALResponse
	if server_auth_enabled != "true" and client_auth_enabled != "true":
	    return (["Server SSL authentication is not enabled", "Client SSL authentication is not enabled"], False)
	if server_auth_enabled != "true":
	    return (["Server SSL authentication is not enabled", "Client SSL authentication passed"], False)
	elif client_auth_enabled != "true":
	    return (["Client SSL authentication is not enabled", "Server SSL authentication passed"], False)
	else:
	    return (["Client SSL authentication passed", "Server SSL authentication passed"], True)



    def _ontap_vols_encrypted(self):
        """ Assuming an IP address, username, and password are provided
            to the ONTAP instance, we attempt to retrieve volume encryption
            status of each active volume. This test only passes if all
            volumes are encrypted """
        
        if self.verbose:
            print("Executing ontap_ssl_enabled")

        if not self.ontap_server:
            # We cannot connect if we are not provided IPAddr, user, password
            return

        out = self.ontap_server.invoke("volume-get-iter")

        if out.results_status == "failed":
            # do not attempt to parse results if request failed
            reason = out.results_reason()
            raise OVALDriverError("ONTAP driver error " + reason)

        # Lists which keep track of each type of volume
        conflicting_vols_list = []
	encrypted_vols_list = []

        attr_list = out.child_get("attributes-list")
        # since there may be more than one child (volume), we
        # collectively request all of them
        vol_attr = attr_list.children_get()

        for vol in vol_attr:
            # Iterate over each volume
            is_encrypted = vol.child_get_string("encrypt")
            vol_id_attr = vol.child_get("volume-id-attributes")
            vol_name = vol_id_attr.child_get_string("name").encode("latin-1")

            if is_encrypted == "false":
                # We have found a bad egg
                conflicting_vols_list.append(vol_name)
	    else:
		encrypted_vols_list.append(vol_name)


        # return the results in the form (message, passed) to OVALResponse
        if not conflicting_vols_list:
            return (["All volumes properly encrypted"], True)
        else:
            return (["The following volumes are encrypted:\t" + str(encrypted_vols_list), "The following volumes are not encrypted:\t" + str(conflicting_vols_list)], False)

    
    def _ontap_autosupport_disabled(self):
        """ Assuming an IP address, username, and password are provided
            to the ONTAP instance, we check every node to make sure
            that autosupport is turned off """

        if self.verbose:
            print("Executing ontap_ssl_enabled")

        if not self.ontap_server:
            # We cannot connect if we are not provided IPAddr, user, password
            return

        out = self.ontap_server.invoke("autosupport-config-get-iter")

        if out.results_status == "failed":
            # do not attempt to parse results if request failed
            reason = out.results_reason()
            raise OVALDriverError("ONTAP driver error " + reason)

        attr_list = out.child_get("attributes-list")
        auto_supp_config_info = attr_list.children_get()
        
        # If there are any nodes with autosupport enabled, we fail the test 
        enabled_list = filter(lambda auto : auto.child_get_string("is-enabled") == "true", auto_supp_config_info)

        if not enabled_list:
            return (["All nodes have autosupport disabled"], True)
        else:
            message = ["The following node still has autosupport enabled: %s" % auto.child_get_string("node-name") for auto in enabled_list]
            return (message, False)


    def _ontap_password_authentication(self):
        """ Assuming an IP address, username, and password are provided
            to the ONTAP instance, we check that every user has password 
            verification enabled """

        if self.verbose:
            print("Executing ontap_ssl_enabled")

        if not self.ontap_server:
            # We cannot connect if we are not provided IPAddr, user, password
            return

        out = self.ontap_server.invoke("security-login-get-iter")
        
        if out.results_status == "failed":
            # do not attempt to parse results if request failed
            reason = out.results_reason()
            raise OVALDriverError("ONTAP driver error " + reason)

        attr_list = out.child_get("attributes-list")
        login_acct_info = attr_list.children_get()

        conflicting_users = filter(lambda acct : acct.child_get_string("authentication-method") != "password", login_acct_info)
        
        if not conflicting_users:
            return (["All users have password authentication enabled"], True)
        else:
            conflicting_user_names = map(lambda acct : acct.child_get_string("user-name").encode("latin-1"), conflicting_users)
            return (["The following users do not have password authentication enabled: %s" % str(conflicting_user_names)], False)


    def _ontap_sha_hash_enabled(self):
        """ Assuming an IP address, username, and password are provided
            to the ONTAP instance, we check that every user has password
            hashing enabled using SHA-512 or another goverment approved
            hash """
        
        if self.verbose:
            print("Executing ontap_ssl_enabled")

        if not self.ontap_server:
            # We cannot connect if we are not provided IPAddr, user, password
            return

        out = self.ontap_server.invoke("security-login-get-iter")
        
        if out.results_status == "failed":
            # do not attempt to parse results if request failed
            reason = out.results_reason()
            raise OVALDriverError("ONTAP driver error " + reason)

        attr_list = out.child_get("attributes-list")
        login_acct_info = attr_list.children_get()
        
        # use set for constant membership time
        approved_hashes = set(["sha512"])

        conflicting_users = filter(lambda acct : acct.child_get_string("password-hash-algorithm") not in approved_hashes, login_acct_info)

        if not conflicting_users:
            return (["All users have approved password hashing"], True)
        else:
            conflicting_user_names = map(lambda acct : acct.child_get_string("user-name").encode("latin-1"), conflicting_users)
            return (["The following users do not have approved password hashing: %s" % str(conflicting_user_names)], False)



    def _ontap_password_policy(self):
        """ Assuming an IP address, username, and password are provided
            to the ONTAP instance, we check that every user role follows
            proper password polocy """
        
        if self.verbose:
            print("Executing ontap_ssl_enabled")

        if not self.ontap_server:
            # We cannot connect if we are not provided IPAddr, user, password
            return

        out = self.ontap_server.invoke("security-login-role-config-get-iter")
        
        if out.results_status == "failed":
            # do not attempt to parse results if request failed
            reason = out.results_reason()
            raise OVALDriverError("ONTAP driver error " + reason)

        attr_list = out.child_get("attributes-list")
        role_config_info = attr_list.children_get()
        
        # Store messages as we check each property of our password
        messages = []
        
        # check delay after failed login
        no_delay_users = filter(lambda acct : acct.child_get_string("delay-after-failed-login") == "0", role_config_info)
        if no_delay_users:
            conflicting_users = map(lambda acct : acct.child_get_string("role-name").encode("latin-1"), no_delay_users)
            messages.append("The following accounts do not have a delay after failed login set: %s" % str(conflicting_users))

        # check whether accounts disallow previous passwords
        no_last_passwd_count = filter(lambda acct : acct.child_get_string("last-passwords-disallowed-count") == "0", role_config_info)
        if no_last_passwd_count:
            conflicting_users = map(lambda acct : acct.child_get_string("role-name").encode("latin-1"), no_last_passwd_count)
            messages.append("The following accounts do not disallow previous passwords: %s" % str(conflicting_users))

        # check whether accounts require password to be updated
        no_change_passwd = filter(lambda acct : acct.child_get_string("change-password-duration-in-days") == "0", role_config_info)
        if no_change_passwd:
            conflicting_users = map(lambda acct : acct.child_get_string("role-name").encode("latin-1"), no_change_passwd)
            messages.append("The following accounts do not require passwords to be updated: %s" % str(conflicting_users))

        # check for a limit on the number of failed login attempts
        no_max_failed_attempts = filter(lambda acct : acct.child_get_string("max-failed-login-attempts") == "0", role_config_info)
        if no_max_failed_attempts:
            conflicting_users = map(lambda acct : acct.child_get_string("role-name").encode("latin-1"), no_max_failed_attempts)
            messages.append("The following accounts do not limit the failed login attempts: %s" % str(conflicting_users))

        # check to make sure special characters are required in password
        no_passwd_special = filter(lambda acct : acct.child_get_string("min-passwd-specialchar") == "0", role_config_info)
        if no_passwd_special:
            conflicting_users = map(lambda acct : acct.child_get_string("role-name").encode("latin-1"), no_passwd_special)
            messages.append("The following accounts do not require special characters in a password: %s" % str(conflicting_users))

        # check to make sure digits are required in password
        no_passwd_digits = filter(lambda acct : acct.child_get_string("passwd-min-digits") == "0", role_config_info)
        if no_passwd_digits:
            conflicting_users = map(lambda acct : acct.child_get_string("role-name").encode("latin-1"), no_passwd_digits)
            messages.append("The following accounts do not require digits in a password: %s" % str(conflicting_users))

        # check to make sure that uppercase characters are required in password
        no_passwd_uppercase = filter(lambda acct : acct.child_get_string("passwd-min-uppercase-chars") == "0", role_config_info)
        if no_passwd_uppercase:
            conflicting_users = map(lambda acct : acct.child_get_string("role-name").encode("latin-1"), no_passwd_uppercase)
            messages.append("The following accounts do not require uppercase characters in a password: %s" % str(conflicting_users))

        if not messages:
            return (["All user roles meet password standards"], True)
        else:
            return (messages, False)



########################################################
#                      TESTING                         #
########################################################

# For testing purposes only
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("\n\tUsage: python oval_driver.py [file] [IPAddr (optional)] [username (optional)] [password (optional)]\n")
        sys.exit()

    filename = sys.argv[1]

    myIPAddr = None
    myUser = None
    myPassword = None
    if len(sys.argv) == 5:
        myIPAddr = sys.argv[2]
        myUser = sys.argv[3]
        myPassword = sys.argv[4]

    parser = OVALParser()
    parser.parse(filename)
#    print(parser)

    request = OVALRequest(parser, local=True, verbose=False)
    request.initialize()
#    print("request:", request)

    driver = OVALDriver(request, IPAddr=myIPAddr, user=myUser, password=myPassword, verbose=True)
    print("Test results:", driver.execute_tests())

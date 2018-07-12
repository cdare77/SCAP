"""
Author: Chris Dare
Version: 1.0
"""

import sys, stat, os, multiprocessing

from oval_request import OVALRequest



class OVALDriverError(Exception):
    pass

class OVALDriver:

    test_dictionary = {
        'check_file_permissions' : self.check_file_permissions(),
        'search_for_pattern' : self.search_for_pattern()
        }

    def __init__(self, request):
        self.request = request
        
        # Our request must be initialized. This may throw errors;
        # however, we would rather not initialize a driver if there
        # is a faulty request
        if not request.initialized:
            request.initialize()


    def execute_tests(self):
        """ Executes all tests in an OVAL Request's ticket """
        
        for test in self.request.tests:
            test_dictionary[test]()


    def search_for_pattern(self, path):
        """ Given a regex pattern provided in the OVAL
            file, we attempt to use that pattern for matching
            in a destination file """
        pattern = self.request.get_body_content('pattern')
        
        # Do not continue if no pattern is provided
        if not pattern:
            return
        
        my_file = open(full_path, 'r').read()
        
        # Check if pattern is a multiline regex
        flags = None
        if pattern[0] is '^' and pattern[-1] is '$':
            flags = re.MULTILINE

        try:
            result = re.match(pattern, my_file, flags)
            return result
        except:
            # pcre (php) regex will fail in python
            raise OVALDriveError("Regex pattern not compatible with Python RegEx 101. Remember not to use inline flags.")


    def check_file_permissions(self, path):
        """ If file permissions are provided, attempt to check
            the destination file for inconsistencies """

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
            return "File permissions are consistent"
        else:
            return "The following permissions are inconsistent: " + str(inconsistent)


def get_num_processors():
    cpu_count = 0
    try:
        cpu_count = len(os.sched_getaffinity(0))
    except AttributeError:
        cpu_count = multiprocessing.cpu_count()
    return cpu_count


print(get_num_processors())

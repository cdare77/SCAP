"""
Author: Chris Dare
Version: 1.0
"""

import sys, stat, os

from oval_request import OVALRequest

def check_file_permissions(self, path):
    """ If file permissions are provided, attempt to check
        the destination file for inconsistencies """

    st = os.stat(path)
    inconsistent = []   # keep track of inconsistent permissions

    # Check consistency of user permissions
    uexec_str = self.get_body_content('uexec')
    if uexec_str and  uexec_str.strip().lower() == 'false' \
        and bool(st.st_mode & stat.S_IXUSR):
        inconsistent. append("uexec")
    
    uwrite_str = self.get_body_content('uwrite')
    if uwrite_str and  uwrite_str.strip().lower() == 'false' \
        and bool(st.st_mode & stat.S_IWUSR):
        inconsistent. append("uwrite")
    
    uread_str = self.get_body_content('uread')
    if uread_str and  uread_str.strip().lower() == 'false' \
        and bool(st.st_mode & stat.S_IRUSR):
        inconsistent. append("uread")
    
    # Check consistency of group permissions
    gexec_str = self.get_body_content('gexec')
    if gexec_str and  gexec_str.strip().lower() == 'false' \
        and bool(st.st_mode & stat.S_IXGRP):
        inconsistent. append("gexec")

    gwrite_str = self.get_body_content('gwrite')
    if gwrite_str and  gwrite_str.strip().lower() == 'false' \
        and bool(st.st_mode & stat.S_IWGRP):
        inconsistent. append("gwrite")

    gread_str = self.get_body_content('gread')
    if gread_str and  gread_str.strip().lower() == 'false' \
        and bool(st.st_mode & stat.S_IRGRP):
        inconsistent. append("gread")

    # Check consistency of others' permissions
    oexec_str = self.get_body_content('oexec')
    if oexec_str and  oexec_str.strip().lower() == 'false' \
        and bool(st.st_mode & stat.S_IXOTH):
        inconsistent. append("oexec")

    owrite_str = self.get_body_content('owrite')
    if owrite_str and  owrite_str.strip().lower() == 'false' \
        and bool(st.st_mode & stat.S_IWOTH):
        inconsistent. append("owrite")

    oread_str = self.get_body_content('oread')
    if oread_str and  oread_str.strip().lower() == 'false' \
        and bool(st.st_mode & stat.S_IROTH):
        inconsistent. append("oread")

    if not inconsistent:
        return "File permissions are consistent"
    else:
        return "The following permissions are inconsistent: " + str(inconsistent)

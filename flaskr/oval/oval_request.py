"""
Author: Chris Dare
Version: 1.0
"""

from oval_parser import OVALParser, XMLElement
import sys, re, os, time
from flask import (current_app, flash)


########################################################
#                     EXCEPTIONS                       #
########################################################

class OVALRequestError(Exception):
    """ Custom exception for this module """
    pass


########################################################
#                      CLASSES                         #
########################################################

class OVALRequest:
    """
    This class essentially cleans the output from the OVAL Parser, determines
    which tests should be executed, and sends a ticket to the oval driver
    """

    def __init__(self, parser, local=True, verbose=False):
        """ Constructor for OVAL request. By default, we want
            to run tests on the local machine and don't want
            output"""

        self.initialized = False
        self.dictionary = parser.get_dictionary()
        self.local = local
        self.verbose = verbose

        if not self.dictionary:
            raise OVALDriveError('Cannot create an OVAL Request from an empty dictionary')


    def __repr__(self):
        if not self.initialized:
            return "Uninitialized request"
        else:
            return "OVALRequest(%s): %s" % (self.title, self.description)


    def initialize(self):
        """ The __init__ function should not call these additional
            methods for debugging purposes. We want to allow an
            OVAL parser to be initialized before setting attributes
            that could potentially throw errors """
        
        if self.verbose:
            print("Initializing request...")

        self.title = self.get_body_content('title')
        self.description = self.get_body_content('description')
        self.tests = self._determine_tests()
        self.initialized = True
        

    def _get_all_elems(self, substring):
        """ Helper function to find all XML tag elements
            whose key contains a given substring """
        return [value for key, value in self.dictionary.items() if substring in key.lower()]

    def get_body_content(self, substring):
        """ helper function to find the first XML tag whose
            name contains the given substring """
        
        array = self._get_all_elems(substring)
        
        if array:
            # return the first occurrence
            primary = array[0].content
            return primary

    def get_all_files(self):
        """ Attempts to search the OVAL file for a filepath
            object, or a path object paired with a filename object.
            If there are multiple filepaths, all are returned. Whenever
            there is a path together with a filename, we assume filename
            is a Regular Expression (RegEx)
        """
    
        files = self._get_all_elems('filepath') # list to return
        paths = self._get_all_elems('path')
        
        if self.verbose:
            print("Cleaning file paths...")

        # Since get_body_content only grabs substrings, paths will
        # also grab all content in filepaths (files)
        if files:
            for f in files:
                if f in paths:
                    # clean paths so that paths and files are disjoint
                    paths.remove(f)
    
        # if there is nothing left to iterate over, we are done
        if not paths:
            return [file.content for file in files]
        
        filenames = self._get_all_elems('filename')
        
        if self.verbose:
            print("Walking over all subdirectories and files for pattern match...")

        ####################################
        #   NEEDS IMPROVEMENT - O(N^4)     #
        ####################################
        for filename in filenames:
            for path in paths:
                if filename.parent == path.parent:
                    # Assume filename only contains RegEx patterns
                    r = re.compile(filename.content)
                    for root, dirs, files_l in os.walk(path.content):
                        matches = [os.path.join(root,x) for x in files_l if r.match(x)]
                        files.extend(matches)

        return files


    def _determine_tests(self):
        """ helper method to examine the xml tags and evaluate
            which tests to run"""
    
        # list of files we will return
        tests = []

        # Get the XMLElements we wish to parse
        file_state = self._get_all_elems('file_state')
        textfilecontent = self._get_all_elems('textfilecontent')
        platform = self._get_all_elems('platform')
        description = self._get_all_elems('description')

        if self.verbose: 
            print("Checking XML body content against known tests...")
        
        if file_state and 'id' in file_state[0].properties and 'file_permissions' in file_state[0].properties['id']:
            if self.local:
                tests.append('local_check_file_permissions')
        if textfilecontent:
            if self.local:
                tests.append('local_search_for_pattern')
        if platform[0].content  == 'ONTAP' and 'SSL' in description[0].content and 'enable' in description[0].content:
            if not self.local:
                tests.append('ontap_ssl_enabled')
        if platform[0].content == 'ONTAP' and 'encrypt' in description[0].content and 'volume' in description[0].content:
            if not self.local:
                tests.append('ontap_vols_encrypted')
        if platform[0].content == 'ONTAP' and 'utosupport' in description[0].content and 'disable' in description[0].content:
            if not self.local:
                tests.append('ontap_autosupport_disabled')


        return tests


########################################################
#                      TESTING                         #
########################################################

# For testing purposes only
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n\tUsage: python oval_parser.py [file]\n")
        sys.exit()

    filename = sys.argv[1]

    parser = OVALParser()
    parser.parse(filename)

    request= OVALRequest(parser, local=True, verbose=True)
    request.initialize()
    print("request:", request)

    print("get_all_files:", request.get_all_files())
    print("request tests:", request.tests)

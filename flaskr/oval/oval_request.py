"""
Author: Chris Dare
Version: 1.0
"""

from oval_parser import OVALParser, XMLElement
import sys, re, os, time
from flask import (current_app, flash)


class OVALRequestError(Exception):
    """ Custom exception for this module """
    pass



class OVALRequest:
    """
    This class essentially cleans the output from the OVAL Parser, determines
    which tests should be executed, and sends a ticket to the oval driver
    """

    def __init__(self, parser):
        """ Constructor for OVAL request """

        self.initialized = False
        self.dictionary = parser.get_dictionary()
        if not self.dictionary:
            current_app.logger.error(time.ctime() + '\tFailed to create OVAL Request: empty dictionary')
            raise OVALDriveError('Cannot create an OVAL Request from an empty dictionary')

        
    def initialize(self):
        """ The __init__ function should not call these additional
            methods for debugging purposes. We want to allow an
            OVAL parser to be initialized before setting attributes
            that could potentially throw errors """
        
        self.title = self.get_body_content('title')
        self.description = self.get_body_content('description')
        self.tests = self.determine_tests()
        self.initialized = True
        

    def get_all_elems(self, substring):
        """ Helper function to find all XML tag elements
            whose key contains a given substring """
        return [value for key, value in self.dictionary.items() if substring in key.lower()]

    def get_body_content(self, substring):
        """ helper function to find the first XML tag whose
            name contains the given substring """
        
        array = self.get_all_elems(substring)
        
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
    
        files = self.get_all_elems('filepath') # list to return
        paths = self.get_all_elems('path')
        
        print(paths)
        
        # Since get_body_content only grabs substrings, paths will
        # also grab all content in filepaths (files)
        if files:
            for f in files:
                if f in paths:
                    # clean paths so that paths and files are disjoint
                    paths.remove(f)
    
        # if there is nothing left to iterate over, we are done
        if not paths:
            return files
        
        filenames = self.get_all_elems('filename')
        
        print(files)
        
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

    def determine_tests(self):
    
        # list of files we will return
        tests = []

        file_state = self.get_body_content('file_state')
        textfilecontent = self.get_body_content('textfilecontent')
        
        if 'id' in file_state.properties and 'file_permissions' in file_state.properties['id']:
            tests.append('check_file_permissions')
        if textfilecontent:
            tests.append('search_for_pattern')

        return tests
    
if len(sys.argv) < 2:
    print("\n\tUsage: python oval_parser.py [file]\n")
    sys.exit()

filename = sys.argv[1]

parser = OVALParser(filename, False)
print(parser)

driver = OVALRequest(parser)
files = driver.get_all_files()

print("get_all_files:", driver.get_all_files())
print("search_for_pattern:", driver.search_for_pattern())
print("grab_file_permissions:", driver.check_file_permissions(files[0]))

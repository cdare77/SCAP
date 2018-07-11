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
    This class takes the input from the OVAL Parser and extracts important
    information. 
    """

    def __init__(self, parser):
        """ Constructor for OVAL request """

        self.dictionary = parser.get_dictionary()
        if not self.dictionary:
            current_app.logger.error(time.ctime() + '\tFailed to create OVAL Request: empty dictionary')
            raise OVALDriveError('Cannot create an OVAL Request from an empty dictionary')

        self.title = self.get_body_content('title')
        self.description = self.get_body_content('description')
        
        

    def get_all_elems(self, substring):
        return [value for key, value in self.dictionary.items() if substring in key.lower()]

    def get_body_content(self, substring):
        """ helper function to find all dictionary elements
            whose key contains a given substring. Only the
            first is returned, however. """
        array = self.get_all_elems(substring)
        
        if array:
            # return the first occurrence
            primary = array[0].content
            return primary

    def get_all_files(self):
    
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
        
        # O(N^4) is good enough LOL
        for filename in filenames:
            for path in paths:
                if filename.parent == path.parent:
                    # Assume filename only contains RegEx patterns
                    r = re.compile(filename.content)
                    for root, dirs, files_l in os.walk(path.content):
                        matches = [os.path.join(root,x) for x in files_l if r.match(x)]
                        files.extend(matches)

        return files



    def search_for_pattern(self):
        """ Given a regex pattern provided in the OVAL
            file, we attempt to use that pattern for matching
            in a destination file """
        pattern = self.get_body_content('pattern')
        
        # Do not continue if no pattern is provided
        if not pattern:
            return
        
        # Get path of destination file to search
        full_path = self.get_all_paths()
        # clean the path
        if type(full_path) is list:
            full_path = full_path[0]
         
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


    
#if len(sys.argv) < 2:
#    print("\n\tUsage: python oval_parser.py [file]\n")
#    sys.exit()
#
#filename = sys.argv[1]
#
#parser = OVALParser(filename, False)
#print(parser)
#
#driver = OVALRequest(parser)
#files = driver.get_all_files()
#
#print("get_all_files:", driver.get_all_files())
#print("search_for_pattern:", driver.search_for_pattern())
#print("grab_file_permissions:", driver.check_file_permissions(files[0]))

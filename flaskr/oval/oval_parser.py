"""
Author: Chris Dare
Version: 1.0
"""

from flask import (current_app, flash)
from collections import deque
import sys, re, time

class XMLElement:
    """
    Class which represents a single XML element.

    Following the natural heirarchy of XML, elements act
    as nodes in a graph and thus have references to their children.
    Other information such as element name, properties, and body 
    content are stored
    """

    def __init__(self, name, content=None, properties=None, parent=None):
        """ Constructor for XMLElement class """

        self.children = []
        self.parent = parent
        self.element_name = name
        self.content = content
        self.properties = properties

    def __repr__(self):
        """ String representation of XMLElement class; prints off all 
        data fields without recursively diving into child's information """

        return "XML Element: %s (properties: %s) (content: %s) (children: %s)" % (self.element_name, str(self.properties), self.content, str([child.element_name for child in self.children]) )

    def get_height(self):
        """ Recursive helper method used to get the height of an XML element
        in the abstract XML tree """

        if not self.children:
            return 0
        else:
            return 1 + max([child.get_height() for child in self.children])

    def print_subtree_r(self, height):
        """ Recursive helper method used in the string representation of
        our OVAL parser. This allows the user to visualize the document
        as a tree """

        my_str = "\t" * (height - 1) + "|-" + self.element_name + "\n"
        for child in self.children:
            my_str += child.print_subtree_r(height + 1)
        return my_str
        


class OVALParseError(Exception):
    """ Custom exception for this module """
    pass
    


class OVALParser:
    """
    This class represents a simplified version of our XML document.
    It effectively strips all necessary informatino from the 
    document, and saves it in a list of individual elements. Following the 
    LIFO structure of a stack, the last element of our list will naturally
    be the root of our XML document.
    """

    def __init__(self, verbose=False):
        """ Constructor for OVAL parser """
        
        self.verbose = verbose
        self.elements_list = []

    
    def __repr__(self):
        """ String representation of our OVAL parser which utilizes
        the recursive print subtree method from our XMLElement """

        if not self.elements_list:
            return "No parsed data"
        else:
            return self.elements_list[-1].print_subtree_r(1)
 

    def parse(self, filename):
        """ A wrapper function for our more private _parse_xml_file """
    
        if not self._is_xml_file(filename):
            if __name__ != "__main__":
                current_app.logger.error(time.ctime() + '\tIncorrect file extension fed to OVAL Parser')
            raise OVALParseError("File extension incorrect - must be .xml")
        
        xml_file = open(filename, 'r')
        self._parse_xml_file(xml_file)
        xml_file.close()


    def get_dictionary(self):
        """ Helper method which converts our elements list into
            a dictionary that is indexed by element names """
        
        d = {}
        for elem in self.elements_list:
            d[elem.element_name] = elem

        return d
    
    
    def set_verbose(self, verbose):
        """ Helper method to adjust whether the parser is verbose or not """
        self.verbose = verbose

    def _is_xml_file(self, filename):
        """ Helper function to check if a given string could be an XML file """

        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() == 'xml'

    def _get_tag_properties(self, line):
        """ Helper function to grab any properties from an XML tag of the form:
                property="value"
            using regular expressions
        """

        d = {}
        for match in re.finditer(r"(([a-z_]+)=\"([\w\/\s]+)\")", line):
            d[match.group(2)] = match.group(3)
        return d


    def _grab_content(self, line):
        """ Helper function to grab body content in between opening and closing
            XML body tags. For example:
        
            <title>Body Content</title>
        """

        regex = re.search(r"<([\w:_-]+)([\ \t]+(([a-z_]+)=\"([\w\/\s]+)\"))*>(.+)<\/\1>", line, re.MULTILINE)
        if regex is not None:
            return regex.group(6)

    def _find_opening_tag(self, line):
        """ Helper function to extract the name of an opening tag using regular
            expressions """

        # regex searching <... key1="value1" etc>
        regex = re.search(r"<([\w:_-]+)([\s]+([a-z_]+)=\"([\w\/\s-]+)\")*[\s]*[/]?>", line, re.MULTILINE)
        if regex is not None:
            return regex.group(1)

    def _find_closing_tag(self, line):
        """ Helper function to notify if a closing tag has been found and possibly return its name """
        
        regex = re.search(r"<\/([\w:_-]+)>", line) # regex searching </...>
        if regex is not None:
            return regex.group(1)
        else:
            regex = re.search(r"\/>", line) # regex searching />
            if regex is not None:
                return "closing"

    def _parse_xml_file(self, this_file):
        """ The primary function behind the OVAL parser. The XML file
            is parsed using a stack to mimic recursion accross elements. 
            Whenever an opening tag for an element is found, a new XML element
            is pushed onto the stack. Whenever a closing tag is found, the
            element is popped from our stack and added to our overall list of
            XML elements. If the stack is not empty by the end of parsing, 
            then there was some error with the input file"""

        # ensure that elements list is cleaned
        del self.elements_list[:]
        # mimic recursive behavior
        tagStack = deque()
    
        for line in this_file:
            opening = self._find_opening_tag(line)
            closing = self._find_closing_tag(line)

            if opening is not None and closing is not None:
                # There is no need to mess with the stack since the entire
                # line is being both opened and closed simultaneously
                elem = XMLElement(opening, content=self._grab_content(line), properties = self._get_tag_properties(line), parent=tagStack[-1])
                try:
                    self.elements_list.append(elem)
                    tagStack[-1].children.append(elem)
                    if self.verbose:
                        print("OPENING AND CLOSING: ", opening, closing, self._grab_content(line), self._get_tag_properties(line))
                except IndexError:
                    raise OVALParseError("Opening brackets < and closing brackets > must exist on the same line")


            elif closing is not None:
                # Theoretically, we should be closing the top element on
                # the stack since that was the most recently added, so pop
                # it off
                try:
                    self.elements_list.append(tagStack.pop())
                    if self.verbose:
                        print("CLOSING: ", closing)
                except IndexError:
                    raise OVALParseError("Opening brackets < and closing brackets > must exist on the same line")
                    
            elif opening is not None:
                # To follow the recursive / stack trend, since we are opening
                # a new element, we want to push this element onto the stack.
                # clearl the parent will be the previous (last) element on the
                # stack
                elem = XMLElement(opening, properties = self._get_tag_properties(line))
                try:
                    # try to add this to the previous elements children
                    tagStack[-1].children.append(elem)
                    elem.parent = tagStack[-1]
                except IndexError:
                    # clearly this will fail for the first element
                    if not self.elements_list:
                        # ignore first element
                        pass
                    else:
                        raise OVALParseError("Opening brackets < and closing brackets > must exist on the same line")
                # push new element onto stack
                tagStack.append(elem)
                if self.verbose:
                    print("OPENING: ", opening)

            elif self.verbose:
                print("INCONCLUSIVE: ", line)
        
        # Too many opening tags
        if len(tagStack) > 0:
            raise OVALParseError("Missing closing tag for " + tagStack[-1].element_name)


# For testing purposes only
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n\tUsage: python oval_parser.py [file]\n")
        sys.exit()

    filename = sys.argv[1]

    parser = OVALParser(True)
    print(parser)
    parser.parse(filename)
    print(parser)

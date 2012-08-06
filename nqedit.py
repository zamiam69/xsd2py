#!/usr/bin/env python

from lxml import etree
import sys
import os.path
from xsd2py.codegen import XSClass, XSParser
import pprint

if __name__ == '__main__':

    xsd_file = sys.argv[1]
    xsd_dir = os.path.dirname(xsd_file)
    xsd = etree.parse(xsd_file, parser=XSParser())
    
    schema = etree.XMLSchema(xsd)
    
    xsdroot = xsd.getroot()
    xsdns = xsdroot.nsmap
        
    S = XSClass(xsdroot)
    
    S._code()

 # vim: sts=4 sw=4 ts=4 et:
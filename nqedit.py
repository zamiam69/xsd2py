#!/usr/bin/env python

from lxml import etree
import sys
import os.path
from xsd2py.codegen import XSClass, XSElement
import pprint

if __name__ == '__main__':

    classes = []

    xsd_file = sys.argv[1]
    xsd = etree.parse(xsd_file)
    schema = etree.XMLSchema(xsd)
    xsdroot = xsd.getroot()
    xsdns = xsdroot.nsmap
    
    include = xsd.xpath("//xs:include[@schemaLocation]", 
                        namespaces=xsdns)
    #for x in include:
    #    inc = etree.parse(x)
    #    print inc.tostring(inc, pretty_print=True)

    # parse simple/complexTypes and elements
    CT = xsd.xpath("./xs:complexType[@name]", namespaces=xsdns)
    ST = xsd.xpath("./xs:simpleType[@name]", namespaces=xsdns)
    E  = xsd.xpath("./xs:element[@name]", namespaces=xsdns)
   
    Names = {}
    for ct in CT:
        ctc = XSClass(ct)
        for n in ctc.name, ctc.className, ctc.methodName:
            if n in Names.keys():
                print """WARNING: name '{0}' already exists""".format(n)
                
        Names[ctc.name] = 1
        Names[ctc.methodName] = 1
        Names[ctc.className] = 1
        print """tag: {0}
-----------------------------------------------------------
methodName: {1}
className: {2}
type: {3}
namespace: {4}
elements: {5}
""".format(ctc.name, ctc.methodName, ctc.className, ctc.xsType,
           ctc.namespaces, ctc.elements)
     
#    for st in ST:
#        print etree.tostring(st, pretty_print=True)

    for e in E:
        ec = XSElement(e)
        
        for n in ec.name, ec.className, ec.methodName:
            if n in Names.keys():
                print """WARNING: name '{0}' already exists""".format(n)
                
        Names[ec.name] = 1
        Names[ec.methodName] = 1
        Names[ec.className] = 1
        print """tag: {0}
-----------------------------------------------------------
methodName: {1}
className: {2}
minOccurs: {3}
maxOccurs: {4}
patterns: {5}
allowed: {6}
""".format(ec.name, ec.methodName, ec.className, ec.minOccurs,
           ec.maxOccurs, ec.patterns, ec.allowed)
    
    #for x in S:
    #   classes.append(XSClass(x))

#    for c in classes: 
#        print c.code("class")
#        for e in c.elements:
#            print e.code("class")

# vim: sts=4 sw=4 ts=4 et:

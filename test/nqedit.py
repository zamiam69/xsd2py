#!/usr/bin/env python

from lxml import etree
import sys

nsXMLSchema = {'xs': 'http://www.w3.org/2001/XMLSchema'}

import pprint

class XSBase(object):

    def __init__(self, tree):
        self._tree = tree
        self._tag = tree.tag
        r = self._tag.rindex("}")
        self._urn = self._tag[1:r]
        self._type = self._tag[r+1:]
        self._name = tree.get("name")
        xstype = tree.get("type")
        self.xsType = xstype
        self._elements = None

        self._doc = "no docstring yet"
        if self._type == "simpleType":
            doc = self._tree.xpath("//xs:documentation", namespaces=self.tree.nsmap)
            self._doc = doc[0].text

        if self._name is None:
            self._className = None
            self._methodName = None
        else:
            methodname = self._name.replace("-", "_")
            self._methodName = methodname
            self.className = methodname[0].upper() + methodname[1:]

        self.minOccurs = tree.get("minOccurs")
        self.maxOccurs = tree.get("maxOccurs")
        if self.minOccurs is None:
            self.minOccurs = 1
        if self.maxOccurs is None:
            self.maxOccurs = 1
        elif self.maxOccurs == "unbounded":
            self.maxOccurs = "\"unbounded\""
        self.data = []

        self._restrictions = XSRestriction(self._tree)
       
    def __repr__(self):
        return etree.tostring(self._tree, pretty_print=True)

    @property
    def tree(self):
        return self._tree

    @property
    def tag(self):
        return self._tag

    @property
    def name(self):
        return self._name

    @property
    def namespaces(self):
        return self._tree.nsmap

    @property
    def methodName(self):
        return self._methodName

    @property
    def classname(self):
        return self._classname

    @property
    def elements(self):
        return self._elements

    @property
    def patterns(self):
        return self._restrictions._patterns

    @property
    def allowed(self):
        return self._restrictions._allowed

    def code(self, code="method"):
        if code == "method":
            return self._methodCode()
        elif code == "class":
            return self._classCode()
        else:
            raise NotImplementedError("This method is not defined.")

    def _methodCode(self):
        if self.xsType is None:
            comment = ""
        else:
            comment = """# {0}: {1}""".format(
                self.name, self.xsType
            )

        code = """
    {0}
    def {1}(self):
        pass
""".format(comment, self.methodName)
        return code

    def _classCode(self):
        code = """
class {0}(object):
\"\"\"{1}\"\"\"
    def __init__(self):
        self._tag = \"{2}\"
        self._urn = \"{3}\"
        self._type = \"{4}\"
        self._xstype = \"{5}\"
        self.data = {6}
        self.minOccurs = {7}
        self.maxOccurs = {8}
        self.patterns = {9}
        self.allowed = {10}
""".format(self.className, self._doc, self.tag, self._urn, self._type, 
    self.xsType, self.data, self.minOccurs, self.maxOccurs,
    self.patterns, self.allowed)
        if self._type == "complexType":
            code += "        self._elements = []\n"
        return code

class XSRestriction(object):
    def __init__(self, tree):
        self._allowed = {}
        self._patterns = []

        for r in tree.xpath("//xs:restriction", namespaces=tree.nsmap):
            for v in r.xpath("xs:enumeration", namespaces=tree.nsmap):
                self._allowed[v.get("value")] = 1
            for v in r.xpath("xs:pattern", namespaces=tree.nsmap):
                self._patterns.append(v.get("value"))

class XSElement(XSBase):
    def __init__(self, tree):
        super(XSElement, self).__init__(tree)
      
class XSClass(XSBase):
    def __init__(self, tree):
        super(XSClass, self).__init__(tree)
        self._elements = []
        for se in self.tree.xpath("xs:sequence/xs:element[@name]", namespaces=self.tree.nsmap):
            E = XSElement(se)
            self._elements.append(E)

    def _classCode(self):
        
        code = super(XSClass, self)._classCode()
        for E in self.elements:
            code += "        self._elements.append(\"{0}\")\n".format(E.methodName)

        for E in self.elements:
            code += E.code("method")
        return code

class XSComplexType(XSClass):
    pass

class XSSimpleType(XSClass):
    pass

if __name__ == '__main__':

    classes = []

    xsd_file = sys.argv[1]
    xsd = etree.parse(xsd_file)
    schema = etree.XMLSchema(xsd)

    t = xsd.xpath("//xs:complexType[@name]", namespaces=nsXMLSchema)
    t.extend(xsd.xpath("//xs:simpleType[@name]", namespaces=nsXMLSchema))

    for x in t:
       classes.append(XSClass(x))

    for c in classes: 
        # print c.code("class")
        for e in c.elements:
            print e.code("class")

# vim: sts=4 sw=4 ts=4 et:

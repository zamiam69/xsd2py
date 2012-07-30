"""
    This space temporarily left blank
"""
from lxml import etree

def _xpath(tree, xpathexp):
    """Short cut for the lxml.etree xpath method"""
    return tree.xpath(xpathexp, namespaces=tree.nsmap)

def _pretty(tree):
    return etree.tostring(tree, pretty_print=True)
 
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

        self._doc = "no docstring yet"
        if self._type == "simpleType":
            doc = _xpath(self.tree, "xs:annotation/xs:documentation")
            self._doc = doc[0].text

        if self._name is None:
            self._className = None
            self._methodName = None
        else:
            methodname = self._name.replace("-", "_")
            self._methodName = methodname
            self._className = methodname[0].upper() + methodname[1:]
            
        self._elements = []
        for e in _xpath(self.tree, "xs:sequence/element"):
            ec = XSElement(e)
            self._elements.append(ev)
      
    def __repr__(self):
        return _pretty(self._tree)

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
    def className(self):
        return self._className

    @property
    def elements(self):
        return self._elements
    
class XSRestriction(object):
    """restriction mix-in"""
    def __init__(self, tree):
        self._allowed = {}
        self._patterns = []

        for r in _xpath(tree, "./xs:restriction"):
            print "### ", _pretty(r)
            for v in _xpath(r, "./xs:enumeration"):
                self._allowed[v.get("value")] = 1
            for v in _xpath(r, "./xs:pattern"):
                self._patterns.append(v.get("value"))
                
    def __repr__(self):
        return {
                "patterns": self._allowed,
                "allowed": self._patterns
        }
                
    @property
    def patterns(self):
        return self._patterns

    @property
    def allowed(self):
        return self._allowed

class XSBaseExt(XSBase):
    def __init__(self, tree):
        super(XSBaseExt, self).__init__(tree)
       
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
""".format(self.className, self._doc, self.tag, self._urn, self._type, 
    self.xsType)
        if self._type == "complexType":
            code += "        self._elements = []\n"
        return code

class XSElement(XSBase, XSRestriction):
    """represents xs:element"""
    def __init__(self, tree):
        XSBase.__init__(self, tree)
        XSRestriction.__init__(self, tree)
        
        self.minOccurs = tree.get("minOccurs")
        self.maxOccurs = tree.get("maxOccurs")
        if self.minOccurs is None:
            self.minOccurs = 1
        if self.maxOccurs is None:
            self.maxOccurs = 1
        elif self.maxOccurs == "unbounded":
            self.maxOccurs = -1
                        
        self.data = []
        self._complexTypes = []
        self._simpleTypes = []
        
        if self.xsType is not None:
            print "################# ", self.xsType
        
        for ct in _xpath(self.tree, "./xs:complexType"):
            ctc = XSClass(ct)
            self._complexTypes.append(ctc)
            
        for st in _xpath(self.tree, "./xs:simpleType"):
            stc = XSClass(st)
            self._simpleTypes.append(stc)
            
    def __repr__(self):
        for c in self._complexTypes, self._simpleTypes:
            return _pretty(c)
                
    def code(self):
        code = """# {3}
class {0}(object):
    def __init__(self):
        self.name = {0}
        self.minOccurs = {1}
        self.maxOccurs = {2}
""".format(self.className, self.minOccurs, self.maxOccurs, self.xsType)
        return code
            

class XSClass(XSBaseExt):
    def __init__(self, tree):
        super(XSClass, self).__init__(tree)
        self._elements = []
        for se in _xpath(self.tree, "./xs:sequence/xs:element[@name]"):
            E = XSElement(se)
            self._elements.append(E)

    def __repr__(self):
        super(XSClass, self).__repr__()
        for e in self._elements:
            return _pretty(e)
        
    def code(self):
        code = """class {0}(object):
    def __init__(self):
        self.name = {0}
""".format(self.className)
        for e in self._elements:
            code += """        self.{0} = {1}()
""".format(e.methodName, e.className)
        code += "\n"
        return code


    def _classCode(self):
        
        code = super(XSClass, self)._classCode()
        for E in self.elements:
            code += """        self._elements.append(\"{0}\")
""".format(E.methodName)

        for E in self.elements:
            code += E.code("method")
        return code
    
    @property
    def elements(self):
        return self._elements

class XSComplexType(XSClass):
    pass

class XSSimpleType(XSClass):
    pass

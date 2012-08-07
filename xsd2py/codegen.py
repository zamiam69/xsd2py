"""
    This space temporarily left blank
"""
from lxml import etree
import re

_NOCODE = ["annotation", "documentation"]

def _xpath(tree, xpathexp):
    """Short cut for the lxml.etree xpath method"""
    return tree.xpath(xpathexp, namespaces=tree.nsmap)

def _pretty(tree):
    return etree.tostring(tree, pretty_print=True)

def _methodName(name):
    if name is not None:
        return name.replace("-", "_")
    return None
    
def _className(name):
    if name is not None:
        methodname = _methodName(name)
        return methodname[0].upper() + methodname[1:]
    return None

def _fNoCode(x):
    return x not in _NOCODE

#def _recContent(method):
#    def recurse(self, *args, **kwargs):
#        for t in self.content:
#            print "=" * 80 
#            print "#", t
#            print "=" * 80 
#            method(self, *args, **kwargs)
#            for c in self.content[t]:
#                print "    ", c.name
#                method(c, *args, **kwargs)
#    return recurse
#        

class XSIncludeResolver(etree.Resolver):
    def resolve(self, url, id, context):
        print "Resolving: ", url, id, context
        return self.resolve_filename(url, context)
    
class XSParser(etree.XMLParser):
    def __init__(self):
        super(XSParser, self).__init__()
        self.resolvers.add(XSIncludeResolver())

class XSBase(object):
    def __init__(self, tree, contains=None):
        self._tree = tree
        self._tag = tree.tag
        r = self._tag.rindex("}")
        self._urn = self._tag[1:r]
        self._type = self._tag[r+1:]
        self._name = tree.get("name")
        self._content = {}

        self._methodName = _methodName(self.name)
        self._className =_className(self.name)
            
        self._contains = contains or []
        for tag in self._contains:
            if tag not in self._content:
                self._content[tag] = []
            sts = _xpath(self._tree, "./xs:" + tag)
            for st in sts:
                C = XSClass(st)
                if C is None:
                    continue
                self._content[tag].append(C)      
                C._process()
                
    def _process(self):
        pass
    
    def _code(self, depth=0, indent="   "):
        code = ""    
        for t in filter(_fNoCode, self.content.keys()):
            for c in self.content[t]:
                code += c._code(depth, indent)
        return code
            
    def  _doc(self):
        doc = ""
        subsections = self.content.keys()
        if "annotation" not in subsections:
            print "... ", self.name
            return ""
        
        for d in self.content["annotation"]:
            doc += d._doc()
        return doc

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
    def xsType(self):
        return self._type

    @property
    def contains(self):
        return self._contains
    
    @property
    def content(self):
        return self._content
    
class XSSchema(XSBase):
    contains = ["annotation", "simpleType", "complexType", "element"]
    
    def __init__(self, tree):
        super(XSSchema, self).__init__(tree, XSSchema.contains)
        #self._includes = [] 
        #included = _xpath(tree, "./xs:include")
        #for inc in included:
        #    loc = inc.get("schemaLocation")
        #    print loc
        
    def _process(self, subtree):
        pass
    
class XSComplexType(XSBase):
    contains = ["annotation", "simpleContent", "complexContent", "sequence"]
    
    def __init__(self, tree):
        super(XSComplexType, self).__init__(tree, XSComplexType.contains)
        
    def _code(self, depth=0, indent="    "):
        code = ""
        if self._className is not None:
            params = {
                      'indent0':  indent * depth,
                      'indent': indent * (depth + 1),
                      'className': self.className,
                      'methodName': self.methodName,
                      'docstring': self._doc(),
            }
            code += """
{indent0}class {className}(object):
{indent0}{indent}\"\"\"{docstring}\"\"\"
{indent0}{indent}def __init__(self):
{indent0}{indent}{indent}pass
""".format(**params)

        for t in filter(_fNoCode, self.content.keys()):
            for c in self.content[t]:
                code += c._code(depth, indent)
        return code
 
class XSSimpleType(XSBase):
    contains = ["annotation", "restriction"]
    
    def __init__(self, tree):
        super(XSSimpleType, self).__init__(tree, XSSimpleType.contains)
    
    def _code(self, depth=0, indent="    "):
        code = ""
        if self._className is not None:
            params = {
                      'indent0':  indent * depth,
                      'indent': indent * (depth + 1),
                      'className': self.className,
                      'methodName': self.methodName,
                      'docstring': self._doc(),
            }
            code += """
{indent0}class {className}(object):
{indent0}{indent}\"\"\"{docstring}\"\"\"
{indent0}{indent}def __init__(self):
{indent0}{indent}{indent}pass
""".format(**params)

        for t in filter(_fNoCode, self.content.keys()):
            for c in self.content[t]:
                code += c._code(depth, indent)
                
        return code
 
class XSSequence(XSBase):
    contains = ["element"]
    
    def __init__(self, tree):
        super(XSSequence, self).__init__(tree, XSSequence.contains)

class XSElement(XSBase):
    contains = ["annotation", "simpleType", "complexType"]
    
    def __init__(self, tree):
        super(XSElement, self).__init__(tree, XSElement.contains)
        self.minOccurs = tree.get("minOccurs")
        self.maxOccurs = tree.get("maxOccurs")
        if self.minOccurs is None:
            self.minOccurs = 1
        if self.maxOccurs is None:
            self.maxOccurs = 1
        elif self.maxOccurs == "unbounded":
            self.maxOccurs = -1

        self.etype = tree.get("type")
        if self.etype is not None:
            xpathexp = "//*[@name = '" + self.etype + "']"
            tdef = self.tree.getroottree().xpath(xpathexp, 
                                                 namespaces=self.tree.nsmap)
            for t in tdef:
                print t.get("name")
                
    def _code(self, depth=0, indent="    "):
        code = ""
        if self._className is not None:
            params = {
                      'indent0':  indent * depth,
                      'indent': indent * (depth + 1),
                      'className': self.className,
                      'methodName': self.methodName,
                      'docstring': self._doc(),
                      'minOccurs': self.minOccurs,
                      'maxOccurs': self.maxOccurs,
                      'superMeth': _methodName(self.etype),
                      'superClass': _className(self.etype),
            }
            code += """
{indent0}class {className}({superClass}):
{indent0}{indent}\"\"\"{docstring}\"\"\"
{indent0}{indent}def __init__(self):
{indent0}{indent}{indent}super({className}, self).__init__()
{indent0}{indent}{indent}self.minOccurs = {minOccurs}
{indent0}{indent}{indent}self.maxOccurs = {maxOccurs}
""".format(**params)
 
        for t in filter(_fNoCode, self.content.keys()):
            for c in self.content[t]:
                code += c._code(depth, indent)
                
        return code
  
class XSDocumentation(XSBase):
    def __init__(self, tree):
        super(XSDocumentation, self).__init__(tree, XSAnnotation.contains)
        
    def __repr__(self):
        return self.tree.text

class XSAnnotation(XSBase):
    contains = ["documentation", "appinfo"]
    
    def __init__(self, tree):
        super(XSAnnotation, self).__init__(tree, XSAnnotation.contains)
            
    def __str__(self):
        return self._doc()
    
    def __repr__(self):
        return _pretty(self._tree)
    
    def _doc(self):
        doc = ""
        for d in self.content["documentation"]:
            doc += repr(d)
        return doc
            
class XSRestriction(XSBase):
    contains = ["enumeration", "pattern"]
    
    def __init__(self, tree):
        super(XSRestriction, self).__init__(tree, XSRestriction.contains)
       
    @property
    def pattern(self):
        return self.content["pattern"]
    
    @property
    def enumeration(self):
        return self.content["enumeration"]
    
    def check(self, extvalue):
        for v in self.enumeration:
            if extvalue == v:
                return true
            
        for p in self.pattern:
            if p.match(extvalue):
                return true
        
        return false
    
class XSClass(object):
    """Factory"""
    def __new__(cls, tree):
        xsobjects = {
            "schema": XSSchema,
            "element": XSElement,
            "complexType": XSComplexType,
            "simpleType": XSSimpleType,
            "annotation": XSAnnotation,
            "restriction": XSRestriction,
            "sequence": XSSequence,
            "documentation": XSDocumentation,
        }        
        tag = tree.tag
        r = tag.rindex("}")
        xstype = tag[r+1:]
        if xstype in xsobjects:
            return xsobjects[xstype](tree)
        else:
            return None
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

# TODO: maybe this can be turned into a decorator
def _recContent(method):
    def recurse(self, *args, **kwargs):
        for t in self.content:
            print "=" * 80 
            print "#", t
            print "=" * 80 
            method(self, *args, **kwargs)
            for c in self.content[t]:
                print "    ", c.name
                method(c, *args, **kwargs)
    return recurse

def initContents(xsinit, *args, **kwargs):
    def initC(xsinit):
        xsinit(self, *args, **kwargs)
        
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
    return initC
 
def initRefs(xsinit, *args, **kwargs):
    def initR(self, *args, **kwargs):
        xsinit(self, *args, **kwargs)
        if ref is not None:
            self._ref = tree.get(ref)
            if self._ref is not None:
                xpathexp = "//*[@name = '" + self._ref + "']"
                tdef = self.tree.getroottree().xpath(xpathexp, 
                                                 namespaces=self.tree.nsmap)
                for t in tdef:
                    print t.get("name")
    return initR

class XSIncludeResolver(etree.Resolver):
    def resolve(self, url, id, context):
        print "Resolving: ", url, id, context
        return self.resolve_filename(url, context)
    
class XSParser(etree.XMLParser):
    def __init__(self):
        super(XSParser, self).__init__()
        self.resolvers.add(XSIncludeResolver())

class XSBase(object):
    
    @initRefs
    @initContents
    def __init__(self, tree, contains=None, ref=None):
        self._tree = tree
        self._tag = tree.tag
        r = self._tag.rindex("}")
        self._urn = self._tag[1:r]
        self._type = self._tag[r+1:]
        self._name = tree.get("name")
        self._value = tree.get("value")
        self._content = {}
        self._ref = None

        self._methodName = _methodName(self.name)
        self._className =_className(self.name)
            
#        self._contains = contains or []
#        for tag in self._contains:
#            if tag not in self._content:
#                self._content[tag] = []
#            sts = _xpath(self._tree, "./xs:" + tag)
#            for st in sts:
#                C = XSClass(st)
#                if C is None:
#                    continue
#                self._content[tag].append(C)      
#                C._process()
#    
#        # Does this class reference another definition?    
#        if ref is not None:
#            self._ref = tree.get(ref)
#            if self._ref is not None:
#                xpathexp = "//*[@name = '" + self._ref + "']"
#                tdef = self.tree.getroottree().xpath(xpathexp, 
#                                                 namespaces=self.tree.nsmap)
#                for t in tdef:
#                    print t.get("name")
#                    # self._ref = t.get("name")
##                    print """
##--------------------------------------------------------------------------------
##ref:  {0}
##tag: {4}
##self._ref: {1}
##name: {2}
##tree: {3}
##--------------------------------------------------------------------------------
##""".format(ref, self._ref, t.get("name"), _pretty(t), self.tag)
#      
    def _process(self):
        pass
    
    def _code(self, depth=0, indent="   ", params=None, template=None):
        code = "" 
        
        if params is not None and template is not None:
            code += template.format(**params)
        
        for t in filter(_fNoCode, self.content.keys()):
            for c in self.content[t]:
                code += c._code(depth, indent, params, template)
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
    def value(self):
        return self._value 
    
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
    
    @property
    def ref(self):
        return self._ref
    
class XSSchema(XSBase):
    contains = ["annotation", "simpleType", "complexType", "element", 
                "attributeGroup"]
    
    def __init__(self, tree):
        super(XSSchema, self).__init__(tree, XSSchema.contains)
        #self._includes = [] 
        #included = _xpath(tree, "./xs:include")
        #for inc in included:
        #    loc = inc.get("schemaLocation")
        #    print loc
        
    def _process(self, subtree):
        pass

class XSComplexContent(XSBase):
    contains = ["annotation", "restriction", "extension"]
    
    def __init__(self, tree):
        super(XSComplexContent, self).__init__(tree, XSComplexContent.contains)
    
    def _code(self, depth=0, indent="    ", params=None, template=None):
        code = ""
        if self._className is not None:
            params = {
                      'indent0':  indent * depth,
                      'indent': indent * (depth + 1),
                      'className': self.className,
                      'methodName': self.methodName,
                      'docstring': self._doc(),
            }
            template = """
{indent0}class {className}(object):
{indent0}{indent}\"\"\"{docstring}\"\"\"
{indent0}{indent}def __init__(self):
"""

        code += super(XSComplexContent, self)._code(depth, indent, params, template)
        return code
    
class XSComplexType(XSBase):
    contains = ["annotation", "simpleContent", "complexContent", "sequence"]
    
    def __init__(self, tree):
        super(XSComplexType, self).__init__(tree, XSComplexType.contains)
        
    def _code(self, depth=0, indent="    ", params=None, template=None):
        code = ""
        if self._className is not None:
            params = {
                      'indent0':  indent * depth,
                      'indent': indent * (depth + 1),
                      'className': self.className,
                      'methodName': self.methodName,
                      'docstring': self._doc(),
            }
            template = """
{indent0}class {className}(object):
{indent0}{indent}\"\"\"{docstring}\"\"\"
{indent0}{indent}def __init__(self):
"""
        code += super(XSComplexType, self)._code(depth, indent, params, template)
        return code

class XSSimpleContent(XSBase):
    contains = ["annotation", "restriction", "extension"]
    
    def __init__(self, tree):
        super(XSSimpleContent, self).__init__(tree, XSSimpleContent.contains)
    
    def _code(self, depth=0, indent="    ", params=None, template=None):
        code = ""
        if self._className is not None:
            params = {
                      'indent0':  indent * depth,
                      'indent': indent * (depth + 1),
                      'className': self.className,
                      'methodName': self.methodName,
                      'docstring': self._doc(),
            }
            template = """
{indent0}class {className}(object):
{indent0}{indent}\"\"\"{docstring}\"\"\"
{indent0}{indent}def __init__(self):
"""

        code += super(XSSimpleContent, self)._code(depth, indent, params, template)
        return code
 
class XSSimpleType(XSBase):
    contains = ["annotation", "restriction"]
    
    def __init__(self, tree):
        super(XSSimpleType, self).__init__(tree, XSSimpleType.contains)
    
    def _code(self, depth=0, indent="    ", params=None, template=None):
        code = ""
        if self._className is not None:
            params = {
                      'indent0':  indent * depth,
                      'indent': indent * (depth + 1),
                      'className': self.className,
                      'methodName': self.methodName,
                      'docstring': self._doc(),
            }
            template = """
{indent0}class {className}(object):
{indent0}{indent}\"\"\"{docstring}\"\"\"
{indent0}{indent}def __init__(self):
"""

        code += super(XSSimpleType, self)._code(depth, indent, params, template)
        return code
 
class XSSequence(XSBase):
    contains = ["element"]
    
    def __init__(self, tree):
        super(XSSequence, self).__init__(tree, XSSequence.contains)

class XSElement(XSBase):
    contains = ["annotation", "simpleType", "complexType"]
    
    def __init__(self, tree):
        super(XSElement, self).__init__(tree, XSElement.contains, "type")
        self.minOccurs = tree.get("minOccurs")
        self.maxOccurs = tree.get("maxOccurs")
        if self.minOccurs is None:
            self.minOccurs = 1
        if self.maxOccurs is None:
            self.maxOccurs = 1
        elif self.maxOccurs == "unbounded":
            self.maxOccurs = -1

    def _code(self, depth=0, indent="    ", params=None, template=None):
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
                      'superMeth': _methodName(self.ref),
                      'superClass': _className(self.ref),
            }
            template = """
{indent0}class {className}({superClass}):
{indent0}{indent}\"\"\"{docstring}\"\"\"
{indent0}{indent}def __init__(self):
{indent0}{indent}{indent}super({className}, self).__init__()
{indent0}{indent}{indent}self.minOccurs = {minOccurs}
{indent0}{indent}{indent}self.maxOccurs = {maxOccurs}
"""
 
        code += super(XSElement, self)._code(depth, indent, params, template)
        return code

class XSExtension(XSBase):
    contains = ["attribute", "attributeGroup"]
    
    def __init__(self, tree):
        super(XSExtension, self).__init__(tree)
        
    def __repr__(self):
        return self.tree.text
    
class XSAttribute(XSBase):
    
    def __init__(self, tree):
        super(XSAttribute, self).__init__(tree)
        
    def __repr__(self):
        return self.tree.text
  
class XSAttributeGroup(XSBase):
    contains = ["attribute"]
    
    def __init__(self, tree):
        super(XSAttributeGroup, self).__init__(tree, XSAttributeGroup.contains, 
                                               "ref")
 
    def __repr__(self):
        return self.tree.text
    
    @property
    def ref(self):
        return self._ref
 
class XSDocumentation(XSBase):
    def __init__(self, tree):
        super(XSDocumentation, self).__init__(tree)
        
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
        super(XSRestriction, self).__init__(tree, XSRestriction.contains, 
                                            "base")
  
    @property
    def pattern(self):
        print self.content["pattern"]
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
    
    def _code(self, depth=0, indent="   ", params=None, template=None):
        code = ""
        params = {
            'indent0':  indent * depth,
            'indent': indent * (depth + 1),
            'values': self.enumeration,
            'patterns': self.pattern
        }
        
        template = """{indent0}{indent}{indent}# allowed values
{indent0}{indent}{indent}self.values = {values}
{indent0}{indent}{indent}self.patterns = {patterns}
"""
            
        code += super(XSRestriction, self)._code(depth, indent, params, template)
        return code

class XSEnumeration(XSBase):
    def __init__(self, tree):
        super(XSEnumeration, self).__init__(tree)
        
    def __repr__(self):
        return '"' + self._value + '"'
    
    def _code(self, depth=0, indent="   ", params=None, template=None):
        return ""
        
class XSPattern(XSEnumeration):
    def __init__(self, tree):
        super(XSPattern, self).__init__(tree)
        
class XSClass(object):
    """Factory"""
    def __new__(cls, tree):
        tag = tree.tag
        r = tag.rindex("}")
        xstype = tag[r+1:]
        xskey = "XS" + xstype[0].upper() + xstype[1:]
        xsclass = globals()[xskey]
        if xsclass is not None:
            return xsclass(tree)
        else:
             return None
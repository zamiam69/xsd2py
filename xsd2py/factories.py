"""
    XML Representation Summaries
    
    from
    
    http://www.w3.org/TR/xmlschema11-1/
"""

from lxml import etree

class XSBase(object):
    """abstract base factory"""
    def __init__(self, name, **kwargs):
        self.name = name
        self._attributes = kwargs["attributes"]
        self._content = kwargs["content"]

    @property
    def attributes(self):
        return self._attributes
    
    @property
    def content(self):
        return self._content

"""XML Representation Summary

<element
  abstract = boolean : false
  block = (#all | List of (extension | restriction | substitution)) 
  default = string
  final = (#all | List of (extension | restriction)) 
  fixed = string
  form = (qualified | unqualified)
  id = ID
  maxOccurs = (nonNegativeInteger | unbounded)  : 1
  minOccurs = nonNegativeInteger : 1
  name = NCName
  nillable = boolean : false
  ref = QName
  substitutionGroup = List of QName
  targetNamespace = anyURI
  type = QName
  {any attributes with non-schema namespace . . .}>
  Content: (annotation?, ((simpleType | complexType)?, alternative*, 
      (unique | key | keyref)*))
</element>
"""
class XSElement(XSBase):

    def __init_(self):
        pass
        
"""
XML Representation Summary

<simpleType
  final = (#all | List of (list | union | restriction | extension)) 
  id = ID
  name = NCName
  {any attributes with non-schema namespace . . .}>
  Content: (annotation?, (restriction | list | union))
</simpleType>
<restriction
  base = QName
  id = ID
  {any attributes with non-schema namespace . . .}>
  Content: (annotation?, (simpleType?, (minExclusive | minInclusive | 
      maxExclusive | maxInclusive | totalDigits | fractionDigits | length | 
      minLength | maxLength | enumeration | whiteSpace | pattern | assertion | 
      explicitTimezone | {any with namespace: ##other})*))
</restriction>
<list
  id = ID
  itemType = QName
  {any attributes with non-schema namespace . . .}>
  Content: (annotation?, simpleType?)
</list>
<union
  id = ID
  memberTypes = List of QName
  {any attributes with non-schema namespace . . .}>
  Content: (annotation?, simpleType*)
</union>
"""
class XSSimpleType(XSBase):
    
    def __init_(self):
        pass

"""
XML Representation Summary

<complexType
  abstract = boolean : false
  block = (#all | List of (extension | restriction)) 
  final = (#all | List of (extension | restriction)) 
  id = ID
  mixed = boolean
  name = NCName
  defaultAttributesApply = boolean : true
  {any attributes with non-schema namespace . . .}>
  Content: (annotation?, (simpleContent | complexContent | 
      (openContent?, (group | all | choice | sequence)?, 
      ((attribute | attributeGroup)*, anyAttribute?), assert*)))
</complexType>
"""
class XSComplexType(XSBase):
    def __init_(self):
        pass

"""
XML Representation Summary

<annotation
  id = ID
  {any attributes with non-schema namespace . . .}>
  Content: (appinfo | documentation)*
</annotation>
<appinfo
  source = anyURI
  {any attributes with non-schema namespace . . .}>
  Content: ({any})*
</appinfo>
<documentation
  source = anyURI
  xml:lang = language
  {any attributes with non-schema namespace . . .}>
  Content: ({any})*
</documentation>
"""
class XSAnnotation(XSBase):
    def __init_(self):
        pass

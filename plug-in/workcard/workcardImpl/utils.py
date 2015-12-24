from SernaApi import *
from PyQt4 import QtXml
from sapiwrap import nodeSet2List
from PyQt4.QtGui import QMessageBox


#############################################################################
class LockPrelreq:
    def __init__(self, node):
        if node:
            self.prelreqNode_ = node
            self.prelreqNode_.setReadOnly(False)
        
    def __del__(self):
        if self.prelreqNode_:
            self.prelreqNode_.setReadOnly(True)
        node = get_node("source-docs", self.prelreqNode_)
        if node:
            node.setReadOnly(False)
    
#############################################################################

class LockNode:
    def __init__(self, node):
        if node:
            self.node_ = node
            self.node_.setReadOnly(False)
        
    def __del__(self):
        if self.node_:
            self.node_.setReadOnly(True)
    
#############################################################################

class StringFunction(XsltExternalFunction):
    def __init__(self, name, nsUri, domain):
        XsltExternalFunction.__init__(self, name, nsUri)
        self.serverDomain = domain
#        self.name = name
 
    def eval(self, valueList):
#        DEBUG document() function
#        if self.name=="document":
#            for it in valueList:
#                print it.getString().__str__()
#            print "-------"
#            return XpathValue(XpathNodeSet())
        return XpathValue(self.serverDomain)
    
#############################################################################

# Creates element with optional attributes and children (recursively)
def build_element(element_name, children, attributes = None):
    element = GroveElement(element_name)

    # Set element attributes
    if attributes:
        for attribute in attributes:
            attr = GroveAttr(attribute[0], attribute[1])
            element.attrs().appendChild(attr)
            
    if isinstance(children, str):
        element.appendChild(GroveText(children))
        
    if isinstance(children, list):
        for child in children:
            child_element = None
            if len(child) > 2:
                child_element = build_element(child[0], child[1], child[2])
            else:
                child_element = build_element(child[0], child[1])
            element.appendChild(child_element)

    if isinstance(children, GroveNode):
        clone = children.cloneNode(True, element)
        element.appendChild(clone)
        
    return element

def build_tree_element(content):
    doc = QtXml.QDomDocument()
    doc.setContent(content)
    return build_sub_element(doc.firstChild())

def build_sub_element(node, parent = None):
    element = None
    while not node.isNull():
        if node.isElement():
            element = GroveElement(node.nodeName().__str__())
            if parent:
                parent.appendChild(element)
            attrs = node.toElement().attributes()
            for i in range(attrs.count()):
                attr = attrs.item(i).toAttr()
                element.attrs().appendChild(GroveAttr(attr.name().__str__(),\
                                                      attr.value().__str__()))
            build_sub_element(node.firstChild(), element)
        if node.isText():
            parent.appendChild(GroveText(node.toText().data().__str__()))
        node = node.nextSibling();
    return element

# Returns element node attribute value
def get_attribute(grove_node, attribute_name):
    attributes = grove_node.asGroveElement().attrs()
    if not attributes.getAttribute(attribute_name):
        return None
    elif not attributes.getAttribute(attribute_name).value():
        return None
    else:
        return str(attributes.getAttribute(attribute_name).value())
    
# Returns list of text data, collected from nodes returned
# by evaluated Xpath expression
def get_data_from_expr(expr, context):
    data = []
    for node in get_nodes(expr, context):
        data.append(get_node_text(node))
    return data
    
# Returns text from the first text node from nodes returned
# by evaluated Xpath expression
def get_datum_from_expr(expr, context):
    node = get_node(expr, context)
    if not node:
        return None
    return get_node_text(node)

def get_datum_from_node(grove_node):
    if grove_node.nodeType() == GroveNode.ATTRIBUTE_NODE:
        return grove_node.asGroveAttr().value().__str__()
    result = "" #SString()
    for child in grove_node.children():
        if child.nodeType() == GroveNode.TEXT_NODE:
            #if child.asGroveText():
            result = result + child.asGroveText().data().__str__()
        elif child.nodeType() == GroveNode.ELEMENT_NODE:
        #elif child.asGroveElement():
            result = result + get_datum_from_node(child)
    return result

# Returns text from the given node
def get_node_text(grove_node):
    if grove_node.nodeType() == GroveNode.ATTRIBUTE_NODE:
        return grove_node.asGroveAttr().value().__str__()
    child = grove_node.getChild(0)
    if not child:
        return str()
    return child.asGroveText().data().__str__()

def get_datum_text_tree(grove_node):
    result = SString()
    for child in grove_node.children():
        if child.asGroveText():
            result = result + child.asGroveText().data()
        elif child.asGroveElement():
            name = str(child.nodeName())
            result = result + SString('<') + name
            attr = child.asGroveElement().attrs().firstChild()
            attrstr = ""
            while attr:
                attrstr = " " + attr.nodeName().__str__() + \
                          "='" +  attr.value().__str__() + "'"
                attr = attr.nextSibling()
            result = result + SString(attrstr) + SString('>')
            result = result + get_datum_text_tree(child)
            result = result + SString("</") + name + SString('>') 
    return result

# Returns first node (from the node-set) of evaluated XPATH expression
def get_node(expr, context):
    if not context:
        return None
    
    nodes = get_nodes(expr, context)
    if nodes and len(nodes) > 0:
        return nodes[0]

    return None
    
def get_nodes(expr, context):
    xpath_value = XpathExpr(expr).eval(context)
    return nodeSet2List(xpath_value.getNodeSet())
    
def get_node_set(expr, context):
    xpath_value = XpathExpr(expr).eval(context)
    if xpath_value:
        return xpath_value.getNodeSet()
    
def print_tree(node):
    if not node.asGroveElement():
        return;
    print(("Node:" + str(node.nodeName())))
    for cur in node.children():
        print_tree(cur)
        
def print_ptree(node):
    if not node:
        return;
    print(("Node:", str(node.name()), "Value:", node.getString().__str__()))
    for cur in node.children():
        print_ptree(cur)
        
# Returns text from the first text node from nodes returned
# by evaluated Xpath expression
def get_first_text_data_from_expr(expr, context):
    node = get_node(expr, context)
    if not node:
        return None
    return get_node_text(node)


def get_dmc_from_avee(node):
    if "avee" == node.nodeName():
        modelic = get_node("/modelic/text()", node).asGroveText().data()
        sdc = get_node("/sdc/text()", node).asGroveText().data()
        chapnum = get_node("/chapnum/text()", node).asGroveText().data()
        section = get_node("/section/text()", node).asGroveText().data()
        subsect = get_node("/subsect/text()", node).asGroveText().data()
        subject = get_node("/subject/text()", node).asGroveText().data()
        discode = get_node("/discode/text()", node).asGroveText().data()
        discodev = get_node("/discodev/text()", node).asGroveText().data()
        incode = get_node("/incode/text()", node).asGroveText().data()
        incodev = get_node("/incodev/text()", node).asGroveText().data()
        itemloc = get_node("/itemloc/text()", node).asGroveText().data()
        return "DMC-" + modelic + "-" + sdc + "-" + chapnum + "-" + section + "-" \
               + subsect + "-" + subject + "-" + subject + "-" + discode + "-" \
               + discodev + "-" + incode + "-" + incodev + "-" + itemloc
    elif "dmCode" == node.nodeName():
        modelic = get_node("@modelIdentCode", node).value()
        sdc = get_node("@systemDiffCode", node).value()
        chapnum = get_node("@systemCode", node).value()
        section = get_node("@subSystemCode", node).value()
        subsect = get_node("@subSubSystemCode", node).value()
        subject = get_node("@assyCode", node).value()
        discode = get_node("@disassyCode", node).value()
        discodev = get_node("@disassyCodeVariant", node).value()
        incode = get_node("@infoCode", node).value()
        incodev = get_node("@infoCodeVariant", node).value()
        itemloc = get_node("@itemLocationCode", node).value()
        return "DMC-" + modelic + "-" + sdc + "-" + chapnum + "-" + section + "-" \
               + subsect + "-" + subject + "-" + subject + "-" + discode + "-" \
               + discodev + "-" + incode + "-" + incodev + "-" + itemloc
               
'''
This function is used to act as a common check against the data return from CMS
'''
def checkReturnResult(self, document, showWarning=True):
    total = getFirstTextDataFromExpr("//resources/count", document)
    if total == "":
        if showWarning:
            QMessageBox.critical(self,"Warning", 
                "The specified criteria would result in a slow search."
                "Please add more search criteria.")
        return False
    else:
        return True
import weakref


def ref(obj):
    return weakref.ref(obj)

def nodeSet2List(nodeset):
    targetList = []

    for onenode in nodeset:
        targetList.append(onenode)

    return targetList

def splitWrap(token, pattern):
    if token is not None and pattern is not None:
        return token.split(pattern)
    else:
        return []
    
def simplifyWhiteSpace(sstr):
    return " ".join(sstr.split())

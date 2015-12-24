from SernaApi import *
from .dialog.LoginCMSDialogBase  import LoginCMSDialogBase
from qt import *
from .utils import *
######################################################################

class LoginCMSDialog(LoginCMSDialogBase):

    def __init__(self,parent,url= None,prj= None,user= None):
        LoginCMSDialogBase.__init__(self, parent.sernaDoc().widget())
        self.url_ = url
        grove = Grove.buildGroveFromFile(url)
        document = grove.document()
        projectNodes = get_nodes("//project", document)
        for node in projectNodes:
            nodevalue = get_datum_from_node(node.asGroveElement())
            self._projectname.insertItem(nodevalue)
        
        if prj!="":
            self._projectname.setCurrentText(prj)
        if user!="":
            self._username.setText(user)

    def getCMS(self):
        return (self._username.text(),self._password.text(),self._projectname.currentText(),self._projectname.currentItem())

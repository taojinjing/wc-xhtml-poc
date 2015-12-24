from qt import *
from .ExecutorBase import *
from .dialog.AboutDialogBase import AboutDialogBase

class AboutPlugin(ExecutorBase):
    def execute(self):
        tmpl_dir = self.sernaDoc_.getDsi().getProperty("template_dir").getString()
        temp_prop = tmpl_dir.__str__() + "/VERSION"
        build_number = ""
        version_number = ""
        plugin_number = ""
        try:
            f = open(temp_prop, 'rb')
            lines = f.readlines()
            f.close()
            for line in lines:
                if line.find('=') < 1:
                    continue
                key, value = line.split('=')
                if key.strip() == "build.number":
                    build_number = value.strip()
                    continue
                if key.strip() == "version.number":
                    version_number = value.strip()
                    continue
                if key.strip() == "plugin.build.number":
                    plugin_number = value.strip()
                    continue
        except:
            pass
        
        ver_ =  version_number+ build_number + " build "+ plugin_number
        dialog = AboutDialogBase(self.qtWidget_)
        dialog.version_.setText(ver_)
        dialog.exec_loop();

from FabricEngine.CreationPlatform.PySide.Widgets import *

class AssetViewerApp(Application):

  def __init__(self, **options):
    
    super(AssetViewerApp, self).__init__(**options)
    
    
    self.constructionCompleted()
    
    
app = AssetViewerApp()
app.exec_()
import os.path
from FabricEngine.CreationPlatform.PySide.Widgets import *

class AssetViewerApp(Application):
  
  __directory = None

  def __init__(self, **options):
    
    super(AssetViewerApp, self).__init__(**options)

    # private member definitions
    self.__directory = os.path.abspath('.')
    
    # access mainwindow and menubar
    mainWindow = self.getMainWindow()
    menuBar = mainWindow.menuBar()
    
    # setup menu actions
    fileMenu = menuBar.addMenu("File")
    browseAction = fileMenu.addAction("Browse")
    fileMenu.addSeparator()
    quitAction = fileMenu.addAction("Quit")
    
    # connect menu action
    browseAction.triggered.connect(self.browseDirectory)
    quitAction.triggered.connect(self.close)
    
    # define the metadata dockwidget class
    class MetaDataDockWidget(DockWidget):
      
      def __init__(self, options):
        
        super(MetaDataDockWidget, self).__init__(options)
        self.setWindowTitle('MetaData')
        self.setMinimumSize(QtCore.QSize(200, 100))
        
        # create new empty widget and set it as central widget
        widget = QtGui.QWidget(self)
        self.setWidget(widget)
        
        # create layout
        widget.setLayout(QtGui.QGridLayout(widget))
        self.__textEdit = QtGui.QPlainTextEdit(widget)
        self.__textEdit.setReadOnly(True)
        widget.layout().addWidget(self.__textEdit, 0, 0)
        
      def setMetaData(self, data):
        self.__textEdit.setPlainText(str(data))
        
      def metaData(self):
        return  self.__textEdit.plainText()
        
    
    # add all dockwidgets
    self.__metaDataDock = MetaDataDockWidget({})
    self.__metaDataDock.setMetaData('Test test test')
    self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.__metaDataDock)
    
    self.constructionCompleted()
    
  def browseDirectory(self, directory = None):
    
    # if this is called from the menubar
    if directory is None:
      qtDir = QtGui.QFileDialog.getExistingDirectory(
        self.getMainWindow(),
        "Choose directory",
        self.__directory)
      if qtDir is None:
        return
      self.__directory = str(qtDir)
    
    print self.__directory
    
    
app = AssetViewerApp()
app.exec_()
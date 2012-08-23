import glob
import os.path
from FabricEngine.CreationPlatform.PySide.Widgets import *
from FabricEngine.CreationPlatform.Nodes.Rendering import *
from FabricEngine.CreationPlatform.Nodes.Manipulation import *
from FabricEngine.CreationPlatform.Nodes.Parsers import *
from FabricEngine.CreationPlatform.Nodes.Kinematics import *
from FabricEngine.CreationPlatform.Nodes.Lights import *

class AssetViewerApp(Application):
  
  __directory = None
  __thumbnails = None

  def __init__(self, **options):
    
    super(AssetViewerApp, self).__init__(**options)

    # private member definitions
    self.__directory = os.path.abspath('.')
    self.__thumbnails = []
    
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
    
    # browse the initial folder
    self.browseDirectory("C:\\Users\\helge\\Documents\\My Dropbox\\Siggraph2012\\AssetBrowser\\Office Objects")
    
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
    else:
      self.__directory = directory

    # gather all files    
    allFiles = []
    allFiles.extend(glob.glob(os.path.join(self.__directory, "*.obj")))
    allFiles.extend(glob.glob(os.path.join(self.__directory, "*.las")))
    allFiles.extend(glob.glob(os.path.join(self.__directory, "*.laz")))
    
    # if we already have a scene, close it
    if len(self._scenes) > 0:
      for thumbnail in self.__thumbnails:
        self.getMainWindow().getCentralWidget().layout().removeWidget(thumbnail)
      self.__thumbnails = []
      self._scenes[0].close()
      self._scenes.remove(self._scenes[0])
      
    # thumbnail widget
    class ThumbnailViewport(Viewport):
      
      def __init__(self, scene, **options):
        super(ThumbnailViewport, self).__init__(scene, **options)
      
        self.setBackgroundColor(Color(0.0, 0.0, 0.0, 1.0))
        self.setMaximumSize(QtCore.QSize(300, 300))
        self.setMinimumSize(self.maximumSize())
      
    # create a new scene
    scene = Scene(self, exts = {'FabricOBJ':'', 'FabricLIDAR': ''}, guarded = True)
    self._scenes.append(scene)
    
    # setup progressbar
    progBar = QtGui.QProgressBar()
    progBar.setWindowModality(QtCore.Qt.ApplicationModal)
    progBar.setMinimum(0)
    progBar.setMaximum(len(allFiles))
    progBar.show()
    
    # loop over all files
    count = 0
    for fileName in allFiles:
      fileNameParts = os.path.split(fileName)
      print fileNameParts[1]
      
      viewport = ThumbnailViewport(
        scene,
        parentWidget = self.getMainWindow(),
        name = fileNameParts[1]
      )
      self.__thumbnails.append(viewport)
      
      # setup the shader
      group = ShaderGroup(scene)
      viewport.addShaderGroupNode(group)
      
      camTarget = Vec3(0.0, 0.0, 0.0)
      camPosition = Vec3(100.0, 100.0, 100.0)
      camNearDistance = 0.1
      camFarDistance = 10.0
      light = None
      
      # get the file extension
      extension = fileName.rpartition('.')[2]
      if extension.lower() == "obj":

        light = PointLight(scene)
        material = Material(scene,
          shaderGroup=group,
          xmlFile='Standard/Phong',
          light=light,
          diffuseColor=Color(0.0,1.0,0.0)
        )

        # create the OBJ parser and the instances
        parser = OBJParser(scene, url = fileName)
        for triangles in parser.getAllTrianglesNodes():
          instance = Instance(scene,
            transform = Transform(scene),
            geometry = triangles,
            material = material
          )
          
          # get the bounding box
          bbox = triangles.getBoundingBox()
          camTarget = bbox['min'].add(bbox['max']).multiplyScalar(0.5)
          camPosition = camTarget.subtract(bbox['max']).multiplyScalar(3.0).add(camTarget)
          camNearDistance = camTarget.subtract(camPosition).length() * 0.01
          camFarDistance = camTarget.subtract(camPosition).length() * 5.0

      # setup the camera + camera manipulation
      camera = TargetCamera(scene,
        target = camTarget,
        position = camPosition,
        nearDistance = camNearDistance,
        farDistance = camFarDistance
      )
      viewport.setCameraNode(camera)
      manipulator = CameraManipulator(scene, autoRegister=False)
      viewport.getManipulatorHostNode().addManipulatorNode(manipulator)
      
      # if we did create a light, connect it to the camera
      light.setTransformNode(camera.getTransformNode())
      
      # for debugging      
      count = count + 1
      if count == 3:
        break
      progBar.setValue(count)
    
    progBar.hide()
      
  def __updateLayout(self):
    centralWidget = self.getMainWindow().getCentralWidget()
    
    col = 0
    row = 0
    for thumbnail in self.__thumbnails:
      centralWidget.layout().addWidget(thumbnail, row, col, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
      col = col + 1
      
      width = col * (thumbnail.maximumSize().width() + 10)
      if width >= centralWidget.size().width():
        col = 0
        row = row + 1
        
  def showMainUI(self):
    super(AssetViewerApp, self).showMainUI()
    self.getMainWindow().setWindowState(QtCore.Qt.WindowMaximized)
    self.__updateLayout()
    
app = AssetViewerApp()
app.exec_()
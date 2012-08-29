from FabricEngine.CreationPlatform.PySide.Widgets import *
from FabricEngine.CreationPlatform.Nodes.Primitives import *
from FabricEngine.CreationPlatform.Nodes.Kinematics import *
from FabricEngine.CreationPlatform.Nodes.Lights import *
from FabricEngine.CreationPlatform.Nodes.Rendering import *
from FabricEngine.CreationPlatform.Nodes.Manipulation import *

class MyApp(Basic3DDemoApplication):
  
  def __init__(self):
    
    # call super class
    super(MyApp, self).__init__()
    
    # set the window title
    self.setWindowTitle("Creation Platform Deformer Tutorial")
    
    # access the scene, viewport and shadergroup
    scene = self.getScene()
    viewport = self.getViewport()
    group = viewport.getShaderGroupNode()
    
    # setup a camera
    camera = TargetCamera(scene)
    viewport.setCameraNode(camera)
    CameraManipulator(scene)
    
    # setup a light
    light = PointLight(scene, transform = camera.getTransformNode())
    
    # construct a torus structured mesh, transform and material
    torus = PolygonMeshTorus(scene, detail = 20)
    transform = Transform(scene)
    material = Material(scene, xmlFile = 'Standard/Phong', shaderGroup = group, light = light)
    
    # construct an instance
    instance = Instance(scene,
      geometry = torus,
      transform = transform,
      material = material
    )
    
    self.constructionCompleted()

app = MyApp()
app.exec_()
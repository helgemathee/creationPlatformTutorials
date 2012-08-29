from FabricEngine.CreationPlatform.PySide.Widgets import *
from FabricEngine.CreationPlatform.Nodes.Primitives import *
from FabricEngine.CreationPlatform.Nodes.Kinematics import *
from FabricEngine.CreationPlatform.Nodes.Lights import *
from FabricEngine.CreationPlatform.Nodes.Rendering import *
from FabricEngine.CreationPlatform.Nodes.Manipulation import *
from FabricEngine.CreationPlatform.Nodes.Geometry.StructuredGeometryComponents.DeformComponentImpl import DeformComponent
from FabricEngine.CreationPlatform.RT.Math import *

class WaveDeformComponent(DeformComponent):
  
  def _setDefaultOptions(self, options):
    super(WaveDeformComponent, self)._setDefaultOptions(options)
    options.setdefault('name', "wave")
    options.setdefault('axis', Vec3(1.0, 0.0, 0.0))
    options.setdefault('center', Vec3(0.0, 0.0, 0.0))
    options.setdefault('amplitude', 1.0)
    options.setdefault('frequency', 1.0)
    
  def apply(self, node):
    
    # ensure that we apply this component to a polygonmesh only
    if not node.isTypeOf('PolygonMesh'):
      raise Exception("Node not of type PolygonMesh!")

    super(WaveDeformComponent, self).apply(node)
    
    # construct a unique name
    name = self._getOption('name') + str(node.getNumComponents()) + '_'
    
    # access the core node
    dgNode = node.getGeometryDGNode()
    
    # add all of the members
    dgNode.addMember(name + 'axis', 'Vec3', self._getOption('axis'))
    dgNode.addMember(name + 'center', 'Vec3', self._getOption('center'))
    dgNode.addMember(name + 'amplitude', 'Scalar', self._getOption('amplitude'))
    dgNode.addMember(name + 'frequency', 'Scalar', self._getOption('frequency'))
    
    # add interfaces
    self._addMemberInterface(dgNode, name+'axis', True)
    self._addMemberInterface(dgNode, name+'center', True)
    self._addMemberInterface(dgNode, name+'amplitude', True)
    self._addMemberInterface(dgNode, name+'frequency', True)
    

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
    
    # apply wave deforms
    deformer = WaveDeformComponent()
    torus.addComponent(deformer)
    
    self.constructionCompleted()

app = MyApp()
app.exec_()
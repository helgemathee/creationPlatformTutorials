from FabricEngine.CreationPlatform.PySide import *
from FabricEngine.CreationPlatform.Nodes.Geometry import *
from FabricEngine.CreationPlatform.Nodes.Primitives import *
from FabricEngine.CreationPlatform.Nodes.Kinematics import *
from FabricEngine.CreationPlatform.Nodes.Lights import *
from FabricEngine.CreationPlatform.Nodes.Rendering import *
from FabricEngine.CreationPlatform.Nodes.Manipulation import *
from FabricEngine.CreationPlatform.Nodes.Animation import *
from FabricEngine.CreationPlatform.Nodes.Geometry.GeometryComponents.DeformComponentImpl import DeformComponent
from FabricEngine.CreationPlatform.RT.Math import *

class WaveDeformComponent(DeformComponent):
  
  def _setDefaultOptions(self, options):
    super(WaveDeformComponent, self)._setDefaultOptions(options)
    options.setdefault('name', "wave")
    options.setdefault('axis', Vec3(1.0, 0.0, 0.0))
    options.setdefault('center', Vec3(0.0, 0.0, 0.0))
    options.setdefault('amplitude', 0.2)
    options.setdefault('frequency', 3.0)
    options.setdefault('speed', 5.0)
    options.setdefault('timeNode', None)
    
  @staticmethod
  def canApplyTo(node):
    return isinstance(node, PolygonMesh)    

  def apply(self, node):
    
    super(WaveDeformComponent, self).apply(node)
    
    # take care of the time reference interface
    self.__node = node
    if node.getInPort('WaveDeformTime') is None:
      node.addReferenceInterface('WaveDeformTime', Time, True, self.__onChangeTime)
      
    # check if we have a timenode setup already
    if not node.hasWaveDeformTimeNode():
      timeNode = self._getOption('timeNode')
      print timeNode
      node.setWaveDeformTimeNode(timeNode)
    
    # construct a unique name
    name = self._getOption('name') + str(node.getNumComponents()) + '_'
    
    # access the core node
    dgNode = node.getGeometryDGNode()
    
    # add all of the members
    dgNode.addMember(name + 'axis', 'Vec3', self._getOption('axis'))
    dgNode.addMember(name + 'center', 'Vec3', self._getOption('center'))
    dgNode.addMember(name + 'amplitude', 'Scalar', self._getOption('amplitude'))
    dgNode.addMember(name + 'frequency', 'Scalar', self._getOption('frequency'))
    dgNode.addMember(name + 'speed', 'Scalar', self._getOption('speed'))
    
    # add interfaces
    self._addMemberInterface(dgNode, name+'axis', True)
    self._addMemberInterface(dgNode, name+'center', True)
    self._addMemberInterface(dgNode, name+'amplitude', True)
    self._addMemberInterface(dgNode, name+'frequency', True)
    self._addMemberInterface(dgNode, name+'speed', True)
    
    # bind the operator
    node.bindDGOperator(
      dgNode.bindings,
      name = "WaveDeformer",
      layout = [
        'self.polygonMesh',
        'self.'+name+'axis',
        'self.'+name+'center',
        'self.'+name+'amplitude',
        'self.'+name+'frequency',
        'self.'+name+'speed',
        'waveDeformTime.time'
      ],
      fileName = FabricEngine.CreationPlatform.buildAbsolutePath('KL', 'WaveDeformer.kl')
    )

  def __onChangeTime(self, data):
    node = data['node']
    self.__node.getGeometryDGNode().setDependency('waveDeformTime', node.getDGNode())


class MyApp(CreationPlatformApplication):
  
  def __init__(self):
    
    # call super class
    super(MyApp, self).__init__(
      setupGlobalTimeNode = True
    )
    
    # set the window title
    self.setWindowTitle("Creation Platform Deformer Tutorial")
    
    # access the scene, viewport and shadergroup
    scene = self.getScene()
    viewport = self.getViewport()
    
    # setup a camera
    camera = TargetCamera(scene)
    viewport.setCameraNode(camera)
    CameraManipulator(scene)
    
    # construct a torus structured mesh, transform and material
    torus = PolygonMeshTorus(scene, detail = 80)
    transform = Transform(scene)
    material = Material(scene, xmlFile='PhongMaterial')
    material.addPreset(name = 'standard')
    
    # construct an instance
    instance = GeometryInstance(scene,
      geometry = torus,   
      transform = transform,
      material = material,
      materialPreset = 'standard'
    )
    
    timeNode = scene.getNode('GlobalTime')
    
    # apply wave deforms
    deformer = WaveDeformComponent(timeNode = timeNode)
    torus.addComponent(deformer)
    deformer = WaveDeformComponent(axis = Vec3(0, 0, 1))
    torus.addComponent(deformer)
    
    self.constructionCompleted()

app = MyApp()
app.exec_()
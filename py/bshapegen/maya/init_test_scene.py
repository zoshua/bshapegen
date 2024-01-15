import random
import maya.cmds as cmds

def create_material(name='material',
                    color_list=[1,1,1]):
  # create lambert material
  lambert = cmds.shadingNode('lambert', asShader=True)
  # rename lambert material
  lambert = cmds.rename(lambert, name)

  # set lambert color
  cmds.setAttr(lambert + '.color', color_list[0], color_list[1], color_list[2], type='double3')

  return lambert

def creat_neutral_and_pose(top_node='shapes',
                           base_name='shape',
                           num=0,
                           move_mult=5):
  # create top node
  if not cmds.objExists(top_node):
    cmds.group(em=1,n=top_node)
  
  # create base group
  base_grp = cmds.group(em=1,
                      n=f'{base_name}_{num}_grp',
                      p=top_node)

  # create neutral base group
  neutral_base_grp = cmds.group(em=1,
                                n=f'{base_name}_{num}_neutral_grp',
                                p=base_grp)

  # create a mesh plane
  neutral_name = f'{base_name}_{num}_neutral'
  cmds.polyPlane(sx=1, sy=1, w=1, h=1, name=neutral_name)

  # parent to base group
  cmds.parent(neutral_name, neutral_base_grp)

  # rotate the plane on x axis
  cmds.xform(neutral_name, ro=(90, 0, 0))

  # extrude the plane
  edge_list = [2,6]
  for edge in edge_list:
    cmds.polyExtrudeEdge(f'{neutral_name}.e[{edge}]', 
                         kft=True, 
                         lty=1, 
                         ls=(1, 1, 1))

  # modify neutral
  edge_list = [1,2,6,9]
  for edge in edge_list:
    rand_z = random.uniform(0.9, 1.5)
    # scale edge in z
    cmds.scale(1, 1, rand_z,
               f'{neutral_name}.e[{edge}]', 
               pivot=(0, 0, 0), r=True)

  # delete neutral history
  cmds.delete(neutral_name, constructionHistory=True)

  # create pose group
  pose_grp = cmds.group(em=1,
                        n=f'{base_name}_{num}_pose_grp',
                        p=base_grp)

  # duplicate neutral to create pose
  pose_name = f'{base_name}_{num}_pose'
  cmds.duplicate(neutral_name, name=pose_name)
  cmds.parent(pose_name, pose_grp)

  # modify pose with bend deformer
  cmds.select(cl=True)
  deformer_name = f'{pose_name}_{num}_bend'
  deformer_handle = f'{deformer_name}Handle'
  cmds.nonLinear(pose_name,name=deformer_name, type='bend')
  cmds.setAttr(f'{deformer_name}.lowBound', 0)
  cmds.setAttr(f'{deformer_name}.curvature', 100)

  cmds.setAttr(f'{deformer_handle}.rotateX',180)

  rand_ry = random.uniform(25, 50)
  cmds.setAttr(f'{deformer_handle}.rotateY',rand_ry)

  cmds.setAttr(f'{deformer_handle}.rotateZ',90)

  # delete pose history
  cmds.delete(pose_name, constructionHistory=True)

  # freeze transform on neutral
  cmds.makeIdentity(neutral_name, apply=True, t=1, r=1, s=1, n=0)

  # freeze transform on pose
  cmds.makeIdentity(pose_name, apply=True, t=1, r=1, s=1, n=0)

  # move pose group up
  cmds.xform(pose_grp, t=(0, 3, 0))

  # move base group into place based on num
  cmds.xform(base_grp, t=(num*move_mult, 0, 0))


def create_scene(num_train_shapes = 10,
                 num_predict_shapes = 2):
  # clear scene
  cmds.select(all=True)
  cmds.delete()

  # create model build data
  for i in range(num_train_shapes):
    creat_neutral_and_pose(top_node='train_shapes',
                           base_name='train_shape',
                           num=i)
  
  # create and assign material to train neutral shapes
  train_shapes_mtl = create_material(name='train_neutral_material',
                                    color_list=[0.9,0.9,0])
  cmds.select('train_shape_*_neutral')
  cmds.hyperShade(assign=train_shapes_mtl)

  # create and assign material to train pose shapes
  train_shapes_mtl = create_material(name='train_pose_material',
                                    color_list=[0.9,0.45,0])
  cmds.select('train_shape_*_pose')
  cmds.hyperShade(assign=train_shapes_mtl)

  # create model predict data
  for i in range(num_predict_shapes):
    creat_neutral_and_pose(top_node='predict_shapes',
                          base_name='predict_shape',
                          num=i)
  
  # move predict shape top node forward in z
  cmds.xform('predict_shapes', t=(0, 0, 5))

  # create and assign material to predict neutral shapes
  predict_shapes_neutral_mtl = create_material(name='predict_neutral_material',
                                              color_list=[0,0.9,0.9])
  cmds.select('predict_shape_*_neutral')
  cmds.hyperShade(assign=predict_shapes_neutral_mtl)

  # create and assign material to predict pose shapes
  predict_shapes_pose_mtl = create_material(name='predict_pose_material',
                                            color_list=[0.1,0.1,0.9])
  cmds.select('predict_shape_*_pose')
  cmds.hyperShade(assign=predict_shapes_pose_mtl)
    
  # clear selection
  cmds.select('predict_shapes',r=True)

  # view fit
  cmds.viewFit(animate=True)

  # return top nodes
  return 'train_shapes', 'predict_shapes'


##########################
if __name__ == '__main__':
  create_scene()
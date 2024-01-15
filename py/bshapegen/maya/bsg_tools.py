import os
import maya.cmds as cmds

def create_material(name='material',
                    color_list=[1,1,1]):
  '''create material'''
  if not cmds.objExists(name):
    # create lambert material
    lambert = cmds.shadingNode('lambert', asShader=True)
    # rename lambert material
    lambert = cmds.rename(lambert, name)
  else:
    lambert = name

  # set lambert color
  cmds.setAttr(lambert + '.color', color_list[0], color_list[1], color_list[2], type='double3')

  return lambert


def get_model_input_data(mesh_list=[],end_str=''):
  '''X shapes'''
  X_shape_list = []
  for mesh in mesh_list:
    if end_str != '':
      if not mesh.endswith(end_str):
        continue
    #
    flat_vrt_list = []
    vtx_index_list = cmds.getAttr( mesh+".vrts", multiIndices=True )
    for vrt in vtx_index_list:
      pos=cmds.xform( (mesh+'.vtx[%s]'%vrt),t=1,q=1)

      pos[0]=str(pos[0])
      pos[1]=str(pos[1])
      pos[2]=str(pos[2])

      flat_vrt_list.extend(pos)
    X_shape_list.append(flat_vrt_list)

  #
  return X_shape_list


def get_model_output_data(mesh_list=[],end_str=''):
  '''Y shapes'''
  Y_shape_list = []
  #
  for mesh in mesh_list:
    if end_str != '':
      if not mesh.endswith(end_str):
        continue
    #
    flat_vrt_list = []
    vtx_index_list = cmds.getAttr( mesh+".vrts", multiIndices=True )
    for vrt in vtx_index_list:
      pos=cmds.xform( (mesh+'.vtx[%s]'%vrt),t=1,q=1)

      pos[0]=str(pos[0])
      pos[1]=str(pos[1])
      pos[2]=str(pos[2])

      flat_vrt_list.extend(pos)
    #
    Y_shape_list.append(flat_vrt_list)

  #
  return Y_shape_list


def write_vtx_m(m_path='',data=[]):
  f = open(m_path,'w')

  for line in data:
    f.write(' '.join(line)+'\n')

  f.close()

  # hide user
  m_path = m_path.replace(os.getlogin(),'~')

  print('Saved:',m_path)


def read_vtx_m(m_path='',tgt_mesh='',shape_num=0):
  '''
  read vtx pos data
  return in usable array
  '''
  data = []

  f = open(m_path,'r')

  line_list = f.readlines()
  for line in line_list:
    if line != '\n':
      data.append(line)

  f.close()

  #prep data 
  data = data[0].replace('\n','').split(' ')

  shape_data_list = []

  tgt_mesh_vtx_num = cmds.polyEvaluate(tgt_mesh, vertex=True )

  for i in range(0,tgt_mesh_vtx_num*3*shape_num,tgt_mesh_vtx_num*3):
      shape_data_list.append( data[i:i+tgt_mesh_vtx_num*3] )

  return shape_data_list


def create_shapes(tgt_mesh='',
                  shape_name_list=[],
                  shape_data_list=[]):
  '''
  dup tgt_mesh 
  read vtx pos data
  apply to new dup verts
  '''

  new_mesh_list = []

  tgt_mesh_vtx_num = cmds.polyEvaluate(tgt_mesh, vertex=True )
  
  for i in range(len(shape_name_list)):
    new_shape_mesh = tgt_mesh.replace('_neutral','_'+shape_name_list[i]+'_predict')
    if not cmds.objExists(new_shape_mesh):
      new_shape_mesh = cmds.duplicate(tgt_mesh,n=new_shape_mesh)[0]

    print('New Shape:',new_shape_mesh)

    cmds.select(cl=1)

    i_vtx = 0
    for j in range(0,tgt_mesh_vtx_num*3,3):
      #print(shape_data_list[i][j:j+3])
      pos = shape_data_list[i][j:j+3]

      cmds.xform(new_shape_mesh+'.vtx['+str(i_vtx)+']',
               t=[float(pos[0]),float(pos[1]),float(pos[2])])

      i_vtx += 1

    new_mesh_list.append(new_shape_mesh)

  return new_mesh_list


def get_pose_predict_shapes_diff(top_node=''):
  '''
  Return:
    1. A list of the difference between the pose and predict shapes
    2. A total sum of the differences found
  '''
  diff_list = []
  diff_sum = 0

  # get all children of top_node
  ad_list = cmds.listRelatives(top_node, ad=True)
  
  # get all *_pose_grp nodes
  pose_grp_list = []

  for ad in ad_list:
    if ad.endswith('_pose_grp'):
      pose_grp_list.append(ad)

  # get diff data for each pose_grp
  for pose_grp in pose_grp_list:
    pose = pose_grp.replace('_pose_grp','_pose')
    pose_predict = pose_grp.replace('_pose_grp','_pose_predict')
    # for each vertex measure the difference between the pose and pose_predict mesh by vector magnitude
    pose_vtx_list = cmds.ls(pose+'.vtx[*]',fl=True)
    pose_predict_vtx_list = cmds.ls(pose_predict+'.vtx[*]',fl=True)
    pose_diff = 0
    for i in range(len(pose_vtx_list)):
      pose_vtx_pos = cmds.xform(pose_vtx_list[i], q=True, t=True, ws=True)
      pose_predict_vtx_pos = cmds.xform(pose_predict_vtx_list[i], q=True, t=True, ws=True)
      diff = [pose_vtx_pos[0]-pose_predict_vtx_pos[0],
              pose_vtx_pos[1]-pose_predict_vtx_pos[1],
              pose_vtx_pos[2]-pose_predict_vtx_pos[2]]
      # get magnitude of diff
      diff_mag = (diff[0]**2 + diff[1]**2 + diff[2]**2)**0.5
      # add to pose_diff
      pose_diff += diff_mag
    #
    diff_list.append([pose_grp, pose_diff])
    diff_sum += pose_diff

  return diff_list, diff_sum


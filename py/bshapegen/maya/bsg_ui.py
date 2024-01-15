import os
import sys
from pathlib import Path

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import * 

from shiboken2 import wrapInstance 

import maya.OpenMayaUI as omui
import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import bshapegen.utils as utils
import bshapegen.maya.bsg_tools as bsg_t
import bshapegen.maya.init_test_scene as its

abs_file = os.path.abspath(__file__)
parent_dir = Path(abs_file).parents[1].as_posix()

sep='/'

def get_env_path():
  if os.name == 'nt':
    user = os.getlogin()
    _path=f'C:/Users/{user}/.conda/envs/vast_venv;C:/Users/{user}/.conda/envs/vast_venv/Library/mingw-w64/bin;C:/Users/{user}/.conda/envs/vast_venv/Library/usr/bin;C:/Users/{user}/.conda/envs/vast_venv/Library/bin;C:/Users/{user}/.conda/envs/vast_venv/Scripts;C:/Users/{user}/.conda/envs/vast_venv/bin;C:/Program Files/Microsoft/jdk-11.0.12.7-hotspot/bin;C:/Windows/system32;C:/Windows;C:/Windows/System32/Wbem;C:/Windows/System32/WindowsPowerShell/v1.0;C:/Windows/System32/OpenSSH;C:/Program Files/Microsoft VS Code/bin;C:/Program Files/Microsoft SQL Server/150/Tools/Binn;C:/Program Files/Microsoft SQL Server/Client SDK/ODBC/170/Tools/Binn;C:/Program Files/dotnet;C:/ProgramData/Anaconda3;C:/ProgramData/Anaconda3/Library/mingw-w64/bin;C:/ProgramData/Anaconda3/Library/usr/bin;C:/ProgramData/Anaconda3/Library/bin;C:/ProgramData/Anaconda3/Scripts;C:/ProgramData/Anaconda3/bin;C:/ProgramData/Anaconda3/condabin;C:/Program Files/Git/cmd;C:/Users/{user}/AppData/Local/Microsoft/WindowsApps;C:/Users/{user}/.dotnet/tools'
  elif os.name == 'posix':
    _path='/opt/anaconda3/envs/bshapegen_venv/bin:/opt/anaconda3/condabin:/usr/local/bin:/usr/bin:/bin:/usr/sbin'
  else:
    print('OS Not Supported:', os.name)
    _path=''
  #
  return _path


class NodePath(QWidget):
  def __init__(self,
              my_parent=None,
              label='',
              default_value='',
              placeholder_text=''):
    #
    QWidget.__init__(self, parent=my_parent)
    self.my_parent = my_parent

    # widgets
    self.label = QLabel(label, self)
    self.lineedit = QLineEdit(self)
    self.lineedit.setPlaceholderText(placeholder_text)
    self.pushButton = QPushButton('<<', self)
    self.pushButton.setMaximumHeight(18)

    # layout
    self.main_layout = QHBoxLayout()
    self.main_layout.setMargin(1)
    self.main_layout.addWidget(self.label)
    self.main_layout.addWidget(self.lineedit)
    self.main_layout.addWidget(self.pushButton)
    self.setLayout(self.main_layout)

    # connections
    self.pushButton.clicked.connect(self.set_from_selection)


  def set_from_selection(self):
    val = cmds.ls(sl=1)
    if val:
      val = val[0]
      self.lineedit.setText(val)


  def getText(self):
    return self.lineedit.text()


class FileInput(QWidget):
  def __init__(self,
              my_parent=None,
              label='',
              start_dir='',
              default_value='~/bshapegen/data',
              placeholder_text='',
              directory_mode=False):
    #
    QWidget.__init__(self, parent=my_parent)
    self.my_parent = my_parent
    self.start_dir = start_dir
    self.directory_mode = directory_mode

    # widgets
    self.work_dir_label = QLabel(label, self)
    self.work_dir_lineedit = QLineEdit(self)
    self.work_dir_lineedit.setPlaceholderText(placeholder_text)
    if default_value:
        self.work_dir_lineedit.setText(default_value)

    self.pushButton = QPushButton(' ... ', self)
    self.pushButton.setMaximumHeight(18)

    # layout
    self.main_layout = QHBoxLayout()
    self.main_layout.setMargin(1)
    self.main_layout.addWidget(self.work_dir_label)
    self.main_layout.addWidget(self.work_dir_lineedit)
    self.main_layout.addWidget(self.pushButton)
    self.setLayout(self.main_layout)

    # connections
    self.pushButton.clicked.connect(self._select)


  def _select(self):
    if self.directory_mode:
      val = QFileDialog.getExistingDirectory(self, 'Select Directory', self.start_dir)
    else:
      val = QFileDialog.getOpenFileName(self, 'Select File', self.start_dir)
    self.start_dir = val
    if len(val):
      self.work_dir_lineedit.setText(val)


  def getText(self):
    work_dir = os.path.expanduser(self.work_dir_lineedit.text())

    # make dir if not exists
    if not os.path.exists(work_dir):
      os.makedirs(work_dir)

    return work_dir


class NumInput(QFrame):
  def __init__(self,
               parent=None,
               name='',
               value=0.0,
               toolTip=''):
    super(NumInput, self).__init__()

    self.my_parent = parent

    #label
    self.label = QLabel(name)
    #line input
    self.input_LineEdit = QLineEdit()
    self.input_LineEdit.setMinimumWidth(50)
    self.input_LineEdit.setText(str(value))
    self.input_LineEdit.setToolTip(toolTip)

    #layout
    self.main_layout = QHBoxLayout()
    self.main_layout.setMargin(1)
    self.main_layout.setSpacing(1)
    self.setLayout(self.main_layout)

    #add widgets
    self.main_layout.addWidget(self.label)
    self.main_layout.addWidget(self.input_LineEdit)


  def getText(self):
    return self.input_LineEdit.text()


class IntInput(NumInput):
  def __init__(self,
               parent=None,
               name='',
               value=0.0,
               toolTip=''):
    #
    NumInput.__init__(self,
                       parent=parent,
                       name=name,
                       value=value,
                       toolTip=toolTip)

    self.onlyInt = QIntValidator()
    self.input_LineEdit.setValidator(self.onlyInt)


class DblInput(NumInput):
  def __init__(self,
               parent=None,
               name='',
               value=0.0,
               toolTip=''):
    #
    NumInput.__init__(self,
                       parent=parent,
                       name=name,
                       value=value,
                       toolTip=toolTip)

    self.onlyDouble = QDoubleValidator()
    self.input_LineEdit.setValidator(self.onlyDouble)


class BSG_UI(MayaQWidgetDockableMixin,QMainWindow):
  def __init__(self,
               parent=None,
               start_dir='~/bshapegen/data'):
    super(BSG_UI, self).__init__(parent)

    MayaQWidgetDockableMixin.show(self, dockable=True)

    # window init attrs
    self.setWindowTitle('BlendShapeGen')
    
    #
    self.main_VBoxLayout=QVBoxLayout()
    self.main_VBoxLayout.setMargin(3)
    self.main_VBoxLayout.setSpacing(3)

    self.main_Frame = QFrame()
    self.main_Frame.setLayout(self.main_VBoxLayout)

    # working directory
    self.wrk_dir_FileInput = FileInput(my_parent=self,
                                      label='Work Dir:',
                                      start_dir=start_dir,
                                      default_value=start_dir,
                                      directory_mode=True)

    self.wrk_dir_FileInput.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    # init test scene
    self.its_GroupBox = QGroupBox('Init Test Scene')
    self.its_GroupBox.setStyleSheet("QGroupBox { border: 1px solid gray; \
                                                   border-radius: 3px; margin-top: 0.5em;} \
                                      QGroupBox::title { subcontrol-origin: margin; \
                                                          left: 10px; padding: 0 3px 0 3px;}")
    self.its_VBoxLayout=QVBoxLayout()
    self.its_VBoxLayout.setMargin(3)
    self.its_VBoxLayout.setSpacing(10)
    self.its_GroupBox.setLayout(self.its_VBoxLayout)

    self.num_train_shapes_IntInput = IntInput(parent=parent,
                                        name='train shapes',
                                        value=100,
                                        toolTip='Integer Values Only')

    self.num_predict_shapes_IntInput = IntInput(parent=parent,
                                    name='predict shapes',
                                    value=5,
                                    toolTip='Integer Values Only')
    
    self.its_params_HBoxLayout=QHBoxLayout()
    self.its_params_HBoxLayout.addWidget(self.num_train_shapes_IntInput)
    self.its_params_HBoxLayout.addWidget(self.num_predict_shapes_IntInput)
    self.its_VBoxLayout.addLayout(self.its_params_HBoxLayout)

    self.build_its_PushButton = QPushButton('Build Test Scene')
    self.its_VBoxLayout.addWidget(self.build_its_PushButton)

    # train data
    self.export_GroupBox = QGroupBox('Train Data')
    self.export_GroupBox.setStyleSheet("QGroupBox { border: 1px solid gray; \
                                                   border-radius: 3px; margin-top: 0.5em;} \
                                      QGroupBox::title { subcontrol-origin: margin; \
                                                          left: 10px; padding: 0 3px 0 3px;}")
    self.export_VBoxLayout=QVBoxLayout()
    self.export_VBoxLayout.setMargin(3)
    self.export_VBoxLayout.setSpacing(10)
    self.export_GroupBox.setLayout(self.export_VBoxLayout)

    self.export_group_NodePath = NodePath(my_parent=self,
                                          label='train group:',
                                          placeholder_text='select build data group')

    self.export_group_NodePath.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    self.export_VBoxLayout.addWidget(self.export_group_NodePath)

    self.export_model_data_PushButton = QPushButton('Export Training Data')
    self.export_VBoxLayout.addWidget(self.export_model_data_PushButton)

    # build
    self.train_GroupBox = QGroupBox('Build')
    self.train_GroupBox.setStyleSheet("QGroupBox { border: 1px solid gray; \
                                                   border-radius: 3px; margin-top: 0.5em;} \
                                      QGroupBox::title { subcontrol-origin: margin; \
                                                          left: 10px; padding: 0 3px 0 3px;}")
    self.train_VBoxLayout=QVBoxLayout()
    self.train_VBoxLayout.setMargin(3)
    self.train_VBoxLayout.setSpacing(10)
    self.train_GroupBox.setLayout(self.train_VBoxLayout)

    self.neuron_num_IntInput = IntInput(parent=parent,
                                        name='neurons',
                                        value=512,
                                        toolTip='Integer Values Only')

    self.epochs_IntInput = IntInput(parent=parent,
                                    name='epochs',
                                    value=150,
                                    toolTip='Integer Values Only')

    self.learning_rate_DblInput = DblInput(parent=parent,
                                            name='learning rate',
                                            value=0.001,
                                            toolTip='Float Values Only')

    self.model_params_HBoxLayout=QHBoxLayout()
    self.model_params_HBoxLayout.addWidget(self.neuron_num_IntInput)
    self.model_params_HBoxLayout.addWidget(self.epochs_IntInput)
    self.model_params_HBoxLayout.addWidget(self.learning_rate_DblInput)
    self.train_VBoxLayout.addLayout(self.model_params_HBoxLayout)

    self.build_model_PushButton = QPushButton('Build Model')
    self.train_VBoxLayout.addWidget(self.build_model_PushButton)

    # predict
    self.predict_GroupBox = QGroupBox('Predict')
    self.predict_GroupBox.setStyleSheet("QGroupBox { border: 1px solid gray; \
                                                    border-radius: 3px; margin-top: 0.5em;} \
                                        QGroupBox::title { subcontrol-origin: margin; \
                                                          left: 10px; padding: 0 3px 0 3px;}")
    self.predict_VBoxLayout=QVBoxLayout()
    self.predict_VBoxLayout.setMargin(3)
    self.predict_VBoxLayout.setSpacing(10)
    self.predict_GroupBox.setLayout(self.predict_VBoxLayout)

    self.predict_NodePath = NodePath(my_parent=self,
                                      label='predict group:',
                                      placeholder_text='select predict data group')

    self.predict_NodePath.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    self.predict_VBoxLayout.addWidget(self.predict_NodePath)
    
    self.write_predict_import_data_PushButton = QPushButton('Export > Predict > Import Data')
    self.predict_VBoxLayout.addWidget(self.write_predict_import_data_PushButton)

    # add widgets to main layout
    self.main_VBoxLayout.addWidget(self.wrk_dir_FileInput)
    self.main_VBoxLayout.addWidget(self.its_GroupBox)
    self.main_VBoxLayout.addWidget(self.export_GroupBox)
    self.main_VBoxLayout.addWidget(self.train_GroupBox)
    self.main_VBoxLayout.addWidget(self.predict_GroupBox)
    self.main_VBoxLayout.addStretch(1)

    # main layout
    self.m_frame = QFrame()
    self.m_frame.setLayout(self.main_VBoxLayout)
    self.setCentralWidget(self.m_frame)

    # connections
    self.build_its_PushButton.clicked.connect(self.build_test_scene_cmd)
    self.export_model_data_PushButton.clicked.connect(self.export_model_data_cmd)
    self.build_model_PushButton.clicked.connect(self.build_model_cmd)
    self.write_predict_import_data_PushButton.clicked.connect(self.write_predict_import_data_cmd)

  
  def build_test_scene_cmd(self):
    print('Build Test Scene')

    num_train_shapes = int(self.num_train_shapes_IntInput.getText())
    num_predict_shapes = int(self.num_predict_shapes_IntInput.getText())

    _train, _predict = its.create_scene(num_train_shapes=num_train_shapes,
                                        num_predict_shapes=num_predict_shapes)
    
    self.export_group_NodePath.lineedit.setText(_train)
    self.predict_NodePath.lineedit.setText(_predict)


  def export_model_data_cmd(self):
    print('Export PyTorch Model Training & Testing [X,Y] Data')

    wrk_dir = self.wrk_dir_FileInput.getText()

    # get childen of group
    group_node = self.export_group_NodePath.getText()
    mesh_list = cmds.listRelatives(group_node,ad=1)

    if not mesh_list:
      print(f'Nodes Not Found Under: {group_node}')
      return

    # write X data
    bsl=bsg_t.get_model_input_data(mesh_list=mesh_list,
                                   end_str='_neutral')
    i_data_path=sep.join([wrk_dir,'model_input_data.m'])
    bsg_t.write_vtx_m(m_path=i_data_path,
                       data=bsl)

    # write Y data
    asl=bsg_t.get_model_output_data(mesh_list=mesh_list,
                                   end_str='_pose')
    o_data_path=sep.join([wrk_dir,'model_output_data.m'])
    bsg_t.write_vtx_m(m_path=o_data_path,
                       data=asl)


  def build_model_cmd(self):
    print('Build PyTorch Seq Model')

    wrk_dir = self.wrk_dir_FileInput.getText()

    _path = get_env_path()
    env = os.environ
    env['PATH']=_path

    commands = []
    # base cmd
    commands.append('python')
    commands.append(f'{parent_dir}/build_model.py')
    # and args
    commands.append('--neuron_num')
    commands.append(self.neuron_num_IntInput.getText())
    commands.append('--learning_rate')
    commands.append(self.learning_rate_DblInput.getText())
    commands.append('--epochs')
    commands.append(self.epochs_IntInput.getText())
    commands.append(sep.join([wrk_dir,'model_input_data.m']))
    commands.append(sep.join([wrk_dir,'model_output_data.m']))
    commands.append(sep.join([wrk_dir,'model.pt']))
    commands.append(sep.join([wrk_dir,'in_mean.m']))
    commands.append(sep.join([wrk_dir,'in_std.m']))
    commands.append(sep.join([wrk_dir,'out_mean.m']))
    commands.append(sep.join([wrk_dir,'out_std.m']))

    command_str = ' '.join(commands)  

    results = utils.subprocess_cmd([command_str],
                                    env=env,
                                    wait=1,
                                    shell=1,
                                    v=1)
    
    if results == 0:
      print('Build Model Success!')
    else:
      print('Build Model Failed!')


  def write_predict_import_data_cmd(self):
    print('Run Prediction and Import Results!')

    wrk_dir = self.wrk_dir_FileInput.getText()

    _path = get_env_path()
    env = os.environ
    env['PATH']=_path

    # delete predicted data if exists
    predict_mesh = cmds.ls('predict_shape_*_predict')
    if predict_mesh:
      cmds.delete(predict_mesh)

    # get _neutral mesh nodes
    group_node = self.predict_NodePath.getText()
    node_list = cmds.listRelatives(group_node,ad=1)
    mesh_list = []
    for node in node_list:
      if node.endswith('_neutral'):
        mesh_list.append(node)
    
    # predict and import data
    for i,mesh in enumerate(mesh_list):
      
      # input data file name
      i_data_name=f'{mesh}_input_data.m'

      # output data file name
      o_data_name=f'{mesh}_output_data.m'

      # write predict X data
      psl=bsg_t.get_model_input_data(mesh_list=[mesh],
                                    end_str='_neutral')
      p_data_path=sep.join([wrk_dir,i_data_name])
      bsg_t.write_vtx_m(m_path=p_data_path,
                        data=psl)

      # run prediction
      commands = []
      # base cmd
      commands.append('python')
      commands.append(f'{parent_dir}/infer_model.py')
      # and args
      commands.append(sep.join([wrk_dir,'model.pt']))
      commands.append(sep.join([wrk_dir,i_data_name]))
      commands.append(sep.join([wrk_dir,'in_mean.m']))
      commands.append(sep.join([wrk_dir,'in_std.m']))
      commands.append(sep.join([wrk_dir,'out_mean.m']))
      commands.append(sep.join([wrk_dir,'out_std.m']))
      commands.append(sep.join([wrk_dir,o_data_name]))

      command_str = ' '.join(commands)  

      results = utils.subprocess_cmd([command_str],
                                      env=env,
                                      wait=1,
                                      shell=1,
                                      v=1)
      
      if results == 0:
        print(f'Predict {mesh} Success!')
      else:
        print(f'Predict {mesh} Failed!')
      
      # read predict Y data
      p_shape_data_path=sep.join([wrk_dir,o_data_name])
      p_shape_data = bsg_t.read_vtx_m(m_path=p_shape_data_path,
                                      tgt_mesh=mesh,
                                      shape_num=1)

      # create predicted shapes
      new_mesh_list = bsg_t.create_shapes(tgt_mesh=mesh,
                                          shape_name_list=['pose'],
                                          shape_data_list=p_shape_data)
      
      pose_parent = f'predict_shape_{i}_pose_grp'
      cmds.parent(new_mesh_list,pose_parent,relative=1)
    
    # create and assign material to predict Y data
    predict_shapes_mtl = bsg_t.create_material(name='predict_Y_material',
                                              color_list=[0.9,0,0.9])
    cmds.select('predict_shape_*_predict')
    cmds.hyperShade(assign=predict_shapes_mtl)

    # run diff report
    diff_list, diff_sum = bsg_t.get_pose_predict_shapes_diff('predict_shapes')
    for mesh_data in diff_list:
        print(f'Mesh: {mesh_data[0]} - Diff: {mesh_data[1]}')

    print(f'Pose Predict Shapes Total Diff Sum: {diff_sum}')



  def closeEvent(self,QCloseEvent):
    self.close()
    self.deleteLater()


  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
        self.close()
        self.deleteLater()
import os
import traceback
import subprocess

def subprocess_cmd(cmd=[],env=os.environ,wait=0,shell=None,v=0):
  if v:
    print('subprocess_cmd():')
    cmd_str = ' '.join(cmd)
    # replace user name with ~
    cmd_str = cmd_str.replace(os.getlogin(),'~')
    print(cmd_str)

  si=None
  if os.name == 'nt':
    si=subprocess.STARTUPINFO()
    si.dwFlags=subprocess.STARTF_USESHOWWINDOW
    if not shell:
      shell = 1

  if os.name == 'posix':
    if not shell:
      shell = 0
  
  try:
    output=subprocess.Popen(cmd,
                            env=env,
                            startupinfo=si,
                            shell=shell)
    
    if wait:
      exit_codes = output.wait()
      return exit_codes
  except Exception as e:
    print('###################')
    print(traceback.format_exc())
    print('###################')






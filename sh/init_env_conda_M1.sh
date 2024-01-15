# get the real working directory of the script
called_path=${0%/*}
stripped=${called_path#[^/]*}

if [ "$called_path" = "$stripped" ]; then
  init_env_dir=$called_path
else
  init_env_dir=`pwd`$stripped
fi

#get list of conda environments
find_in_conda_env(){
  conda env list | grep "${@}" >/dev/null 2>/dev/null
}

if find_in_conda_env ".*bshapegen_venv.*" ; then
  #activate virtual environment
  conda activate bshapegen_venv
else 
  #create virtual environment
  conda create --yes --name bshapegen_venv python=3.8
  #activate virtual environment
  conda activate bshapegen_venv
fi

# install requirements
pip install -r $init_env_dir/../py/requirements_conda_M1.txt

export PYTHONPATH=$init_env_dir/../py:$PYTHONPATH

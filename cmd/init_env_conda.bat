@echo off
::check virtual environment exists
call conda env list | findstr /rc:".*bshapegen_venv.*" > %TEMP%\tmpfile.txt
set /p VENV_EXISTS=<%TEMP%\tmpfile.txt
del %TEMP%\tmpfile.txt

::create virtual environment if it doesn't exist
if "%VENV_EXISTS%"=="" call conda create --yes --name bshapegen_venv python=3.8

::activate virtual environment
call conda activate bshapegen_venv

::install requirements
pip install -r %~dp0..\py\requirements_conda.txt

::update PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%~dp0..\py
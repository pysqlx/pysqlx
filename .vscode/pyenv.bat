@echo off

:: get the project root directory
set PROJECT_ROOT_DIR=%~dp0\..\

pushd .
cd %PROJECT_ROOT_DIR%
set PROJECT_ROOT_DIR=%CD%
popd

:: make sure python 3.10.4 is installed in the default location
set PROJECT_PYTHON_BASE_EXE=C:\Python\3.10.4_x64\python.exe

if not exist "%PROJECT_PYTHON_BASE_EXE%" (
    echo BUILD ERROR: Cannot find python installation: "%PROJECT_PYTHON_BASE_EXE%"
    exit /B 1
)

:: create/activate python virtual env for development
set PROJECT_PY_VER_ENV_DIR=%PROJECT_ROOT_DIR%\.venv\
set PROJECT_PY_VER_ENV_ACTIVATE=%PROJECT_PY_VER_ENV_DIR%Scripts\activate.bat

echo Using python dev env "%PROJECT_PY_VER_ENV_DIR%"

if exist "%PROJECT_PY_VER_ENV_ACTIVATE%" (
    call "%PROJECT_PY_VER_ENV_ACTIVATE%"
    exit /B 0
)

"%PROJECT_PYTHON_BASE_EXE%" -m pip install -U pip setuptools wheel
"%PROJECT_PYTHON_BASE_EXE%" -m venv %PROJECT_PY_VER_ENV_DIR%

call "%PROJECT_PY_VER_ENV_ACTIVATE%"

python -m pip install -U pip setuptools wheel --no-warn-script-location

pushd .
cd %PROJECT_ROOT_DIR%
python -m pip install -U -r "dev_requirements.txt" --no-warn-script-location
popd

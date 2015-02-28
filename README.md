MS Visual Studio Project Generator
=========

## What it does
This utility generates projects for several C++ IDEs at once. 
It is designed to make projects that can be opened out-of-the-box with either **Microsoft's _Visual Studio_** and/or **JetBrain's _CLion_**.\*


## Building
### Windows
1. Download and install python2.7
2. Download and install py2exe
3. In cmd.exe: 
	 `cd "[directory containing this package's setup.py file]"`
	 `[python interpreter path] setup.py py2exe`

### Unix-like
1. Download and install python2.7
2. Download and install PyInstaller
3. In a terminal:
	 `cd "[directory containing this package's setup.py file]"`
	 `[python interpreter path] ./setup.py`

## Usage
Simply provide a directory filepath as the final argument to the script or compiled exe, and the generator will do its magic!


>  \*This project is not affiliated with or endorsed by any of the IDEs, companies, etc. mentioned.

# dsa110-controlscripts

scripts/executables to control DSA110 using Etcd. 

## Purpose
Scripts and executables to control the DSA110 array using Etcd which can be scheduled to run via the WebUI.

## Workflow
The WebUI can be instructed to load scripts from this repo. Only scripts on the master branch can be uploaded. The tip of master should always have a semantic version tag of the form: vX.Y.Z Development should be on named branches of the form: <user>/feature. Initials are best for <user>. Place source code for compiled executables under the src/<executableName> directory. Do not use spaces in any path or name.

## Python
Python scripts will be interpreted using version 3.6.

## Issues
Please file any bugs/enhancements under DSA110-issues.

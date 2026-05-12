@echo off
setlocal

set "NODE_EXE=C:\Program Files\nodejs\node.exe"
if not exist "%NODE_EXE%" set "NODE_EXE=node"

"%NODE_EXE%" "%~dp0..\..\node_modules\@playwright\test\cli.js" %*

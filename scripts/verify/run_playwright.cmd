@echo off
setlocal

set "NODE_EXE=%ProgramFiles%\nodejs\node.exe"
if not exist "%NODE_EXE%" set "NODE_EXE=%ProgramFiles(x86)%\nodejs\node.exe"
if not exist "%NODE_EXE%" set "NODE_EXE=node.exe"

set "PW_CLI=%~dp0..\..\node_modules\@playwright\test\cli.js"
if not exist "%PW_CLI%" (
	echo Playwright test CLI not found at "%PW_CLI%" 1>&2
	exit /b 1
)

"%NODE_EXE%" "%PW_CLI%" %*
exit /b %ERRORLEVEL%

@echo off
rmdir /s /q server_release
md server_release
echo f | xcopy /y /i server_startup.py server_release\server_startup.py
echo f | xcopy /y /i utils.py server_release\utils.py
echo f | xcopy /y /i cipher.py server_release\cipher.py
echo f | xcopy /y /i constants.py server_release\constants.py
set/p option=need users.yaml?(y/n):
if "%option%"=="y" (
  echo f | xcopy /y /i users.yaml server_release\users.yaml
)
xcopy /y /i server\*.* server_release\server\*.*
pause
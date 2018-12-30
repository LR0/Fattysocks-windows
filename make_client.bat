@echo off
pyinstaller -F -i res\icon.ico -n Fattysocks -p res --windowed --onefile client_window.pyw
xcopy /y res\*.* dist\res\*.*
rmdir /s /q client_release
ren dist client_release
pause
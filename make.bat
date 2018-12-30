@echo off
pyinstaller -F -i res\icon.ico -n Fattysocks -p res --windowed --onefile client_window.pyw
xcopy /y res\*.* dist\res\*.*
pause
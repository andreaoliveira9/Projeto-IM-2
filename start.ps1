Set-Location -Path .\IM
Start-Process -FilePath .\start.bat

Set-Location -Path ..\FusionEngine
Start-Process -FilePath .\start.bat

Set-Location -Path ..\GenericGesturesModality-2023
Start-Process -FilePath .\GenericGesturesModality.exe

Set-Location -Path ..\WebAppAssistantV2
Start-Process -FilePath .\start_web_app.bat

Set-Location -Path ..
Start-Sleep -Seconds 3
Start-Process "msedge.exe" "https://127.0.0.1:8082/index.htm"

Set-Location -Path .\app
.\venv\Scripts\activate
python.exe .\main.py
@echo off
set /p "user=Enter username to delete: "
curl -X DELETE https://localhost:5000/delete/%user% --ssl-no-revoke
pause
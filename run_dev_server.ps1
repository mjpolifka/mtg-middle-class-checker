param(
    [int]$Port = 5001
)

$ErrorActionPreference = "Stop"

Write-Host "Starting Flask dev server on http://127.0.0.1:$Port"
pipenv run python -m flask --app app run --port $Port --no-reload

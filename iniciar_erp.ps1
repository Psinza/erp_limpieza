$ProjectRoot = "C:\Users\Administrator\Documents\Proyecto\ERPSIMPLE\erp_limpieza"
Set-Location $ProjectRoot
$env:PYTHONPATH = $ProjectRoot
Write-Host "--- ERP Limpieza ---" -ForegroundColor Green
Write-Host "Activando entorno virtual..." -ForegroundColor Cyan
& ".\env\Scripts\Activate.ps1"
Write-Host "Aplicando migraciones..." -ForegroundColor Magenta
python manage.py migrate
Write-Host "Recolectando archivos estaticos..." -ForegroundColor Magenta
python manage.py collectstatic --noinput
Write-Host "Iniciando servidor..." -ForegroundColor Yellow
python manage.py runserver
# Script para reinstalar PostgreSQL no Windows
# Execute como Administrador

Write-Host "Script de reinstalacao do PostgreSQL" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# 1. Parar serviços PostgreSQL
Write-Host "1. Parando servicos PostgreSQL..." -ForegroundColor Yellow
try {
    Stop-Service -Name "postgresql-x64-17" -Force -ErrorAction Stop
    Write-Host "Servico PostgreSQL parado" -ForegroundColor Green
}
catch {
    Write-Host "Nao foi possivel parar o servico: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 2. Desinstalar PostgreSQL via Windows Installer
Write-Host "2. Desinstalando PostgreSQL..." -ForegroundColor Yellow
try {
    $uninstallString = Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like "*PostgreSQL*" }
    if ($uninstallString) {
        Write-Host "Encontrado: $($uninstallString.Name)" -ForegroundColor Cyan
        $uninstallString.Uninstall()
        Write-Host "PostgreSQL desinstalado" -ForegroundColor Green
    }
    else {
        Write-Host "PostgreSQL nao encontrado no Windows Installer" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Erro na desinstalacao: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 3. Remover diretórios residuais
Write-Host "3. Removendo diretorios residuais..." -ForegroundColor Yellow
$directories = @(
    "C:\Program Files\PostgreSQL",
    "C:\Program Files (x86)\PostgreSQL",
    "$env:APPDATA\postgresql",
    "$env:LOCALAPPDATA\postgresql"
)

foreach ($dir in $directories) {
    if (Test-Path $dir) {
        try {
            Remove-Item -Path $dir -Recurse -Force -ErrorAction Stop
            Write-Host "Removido: $dir" -ForegroundColor Green
        }
        catch {
            Write-Host "Nao foi possivel remover: $dir" -ForegroundColor Yellow
        }
    }
}

# 4. Limpar variáveis de ambiente
Write-Host "4. Limpando variaveis de ambiente..." -ForegroundColor Yellow
$envVars = @("POSTGRES_HOME", "PGDATA", "PGUSER")
foreach ($var in $envVars) {
    if ([Environment]::GetEnvironmentVariable($var, "Machine")) {
        [Environment]::SetEnvironmentVariable($var, $null, "Machine")
        Write-Host "Variavel removida: $var" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Desinstalacao concluida!" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "   1. Reinicie o computador" -ForegroundColor White
Write-Host "   2. Baixe PostgreSQL 17 em: https://www.postgresql.org/download/windows/" -ForegroundColor White
Write-Host "   3. Instale com as seguintes opcoes:" -ForegroundColor White
Write-Host "      - Porta: 5432" -ForegroundColor White
Write-Host "      - Senha do usuario postgres: postgres" -ForegroundColor White
Write-Host "      - Nao marcar 'Stack Builder'" -ForegroundColor White
Write-Host "   4. Execute: python setup_postgres_local.py" -ForegroundColor White
Write-Host ""
Write-Host "Dica: Durante a instalacao, anote a senha do usuario postgres!" -ForegroundColor Yellow


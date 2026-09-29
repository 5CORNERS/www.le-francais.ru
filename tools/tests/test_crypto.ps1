<#
.SYNOPSIS
    Unit and integration tests for tools/encrypt_env.ps1 and tools/decrypt_env.ps1.
.DESCRIPTION
    Validates AES-256 encryption, PBKDF2 SHA-256 derivation, decryption roundtrip,
    DATABASE_URL enforcement (port 5433), and incorrect password rejection.
#>

$RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$EncryptScript = Join-Path $RepoRoot "tools\encrypt_env.ps1"
$DecryptScript = Join-Path $RepoRoot "tools\decrypt_env.ps1"

$PassedTests = 0
$FailedTests = 0

function Assert-Condition {
    param(
        [bool]$Condition,
        [string]$TestName,
        [string]$FailureMessage = ""
    )
    if ($Condition) {
        Write-Host "  [PASS] $TestName" -ForegroundColor Green
        $script:PassedTests++
    } else {
        Write-Host "  [FAIL] $TestName" -ForegroundColor Red
        if ($FailureMessage) {
            Write-Host "         Reason: $FailureMessage" -ForegroundColor Yellow
        }
        $script:FailedTests++
    }
}

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Running Crypto & Env Tooling Tests" -ForegroundColor Cyan
Write-Host " Repo Root: $RepoRoot" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# Prepare temporary paths
$TestEnvFile = Join-Path $RepoRoot "tools\tests\.env.test"
$TestEncFile = Join-Path $RepoRoot "tools\tests\.env.test.enc"
$TestDecFile = Join-Path $RepoRoot "tools\tests\.env.test.dec"

$TestEnvNoDbFile = Join-Path $RepoRoot "tools\tests\.env.nodb.test"
$TestEncNoDbFile = Join-Path $RepoRoot "tools\tests\.env.nodb.test.enc"
$TestDecNoDbFile = Join-Path $RepoRoot "tools\tests\.env.nodb.test.dec"

$TestWrongDecFile = Join-Path $RepoRoot "tools\tests\.env.wrong.dec"

try {
    # -------------------------------------------------------------
    # Test 1: Scripts Exist
    # -------------------------------------------------------------
    Write-Host "`nTest Suite 1: Tool scripts existence" -ForegroundColor Cyan
    Assert-Condition (Test-Path $EncryptScript) "encrypt_env.ps1 exists" "Missing $EncryptScript"
    Assert-Condition (Test-Path $DecryptScript) "decrypt_env.ps1 exists" "Missing $DecryptScript"

    if (-not (Test-Path $EncryptScript) -or -not (Test-Path $DecryptScript)) {
        Write-Host "Cannot proceed with functional tests until scripts exist." -ForegroundColor Yellow
        exit 1
    }

    # -------------------------------------------------------------
    # Test 2: Standard Roundtrip with DATABASE_URL rewrite
    # -------------------------------------------------------------
    Write-Host "`nTest Suite 2: Encryption and Decryption Roundtrip with DATABASE_URL rewrite" -ForegroundColor Cyan
    $InitialContent = @"
SECRET_KEY=unit-test-secret-key-xyz-123
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://remote_user:remote_pass@db.production.net:5432/remote_db
CUSTOM_CONFIG_VALUE="french language portal"
"@
    [System.IO.File]::WriteAllText($TestEnvFile, $InitialContent, [System.Text.Encoding]::UTF8)

    $TestPassword = "TestSecretPassword!987"

    # Encrypt
    & "$EncryptScript" -InputFile $TestEnvFile -OutputFile $TestEncFile -Password $TestPassword
    $encExit = $LASTEXITCODE
    Assert-Condition ($encExit -eq 0) "encrypt_env.ps1 returns exit code 0" "Exit code was $encExit"
    Assert-Condition (Test-Path $TestEncFile) "Encrypted output file created" "File not found: $TestEncFile"

    if (Test-Path $TestEncFile) {
        $encBytes = [System.IO.File]::ReadAllBytes($TestEncFile)
        # Payload must be at least 32 bytes (16 salt + 16 IV) + at least 1 AES block (16 bytes)
        Assert-Condition ($encBytes.Length -ge 48) "Encrypted payload contains Salt (16B) + IV (16B) + Ciphertext" "Length was $($encBytes.Length)"

        # Verify plaintext is not leaked in encrypted file
        $encRawString = [System.Text.Encoding]::ASCII.GetString($encBytes)
        Assert-Condition (-not $encRawString.Contains("unit-test-secret-key")) "Ciphertext does not contain plaintext secrets" "Plaintext leaked in ciphertext"
    }

    # Decrypt
    & "$DecryptScript" -InputFile $TestEncFile -OutputFile $TestDecFile -Password $TestPassword
    $decExit = $LASTEXITCODE
    Assert-Condition ($decExit -eq 0) "decrypt_env.ps1 returns exit code 0" "Exit code was $decExit"
    Assert-Condition (Test-Path $TestDecFile) "Decrypted file created" "File not found: $TestDecFile"

    if (Test-Path $TestDecFile) {
        $decContent = [System.IO.File]::ReadAllText($TestDecFile, [System.Text.Encoding]::UTF8)

        Assert-Condition ($decContent.Contains("SECRET_KEY=unit-test-secret-key-xyz-123")) "Decrypted content preserves SECRET_KEY"
        Assert-Condition ($decContent.Contains("DEBUG=True")) "Decrypted content preserves DEBUG"
        Assert-Condition ($decContent.Contains("ALLOWED_HOSTS=localhost,127.0.0.1")) "Decrypted content preserves ALLOWED_HOSTS"
        Assert-Condition ($decContent.Contains('CUSTOM_CONFIG_VALUE="french language portal"')) "Decrypted content preserves CUSTOM_CONFIG_VALUE"
        Assert-Condition ($decContent.Contains("DATABASE_URL=postgres://postgres@127.0.0.1:5433/le_francais")) "DATABASE_URL replaced with 127.0.0.1:5433" "Actual content: $decContent"
        Assert-Condition (-not $decContent.Contains("db.production.net")) "Old DATABASE_URL is not present"
    }

    # -------------------------------------------------------------
    # Test 3: DATABASE_URL appended when missing
    # -------------------------------------------------------------
    Write-Host "`nTest Suite 3: DATABASE_URL appended when missing" -ForegroundColor Cyan
    $NoDbContent = @"
APP_NAME=LeFrancais
API_KEY=dummy-token-abc
"@
    [System.IO.File]::WriteAllText($TestEnvNoDbFile, $NoDbContent, [System.Text.Encoding]::UTF8)

    & "$EncryptScript" -InputFile $TestEnvNoDbFile -OutputFile $TestEncNoDbFile -Password $TestPassword
    & "$DecryptScript" -InputFile $TestEncNoDbFile -OutputFile $TestDecNoDbFile -Password $TestPassword

    if (Test-Path $TestDecNoDbFile) {
        $decNoDbContent = [System.IO.File]::ReadAllText($TestDecNoDbFile, [System.Text.Encoding]::UTF8)
        Assert-Condition ($decNoDbContent.Contains("APP_NAME=LeFrancais")) "Decrypted content preserves APP_NAME"
        Assert-Condition ($decNoDbContent.Contains("API_KEY=dummy-token-abc")) "Decrypted content preserves API_KEY"
        Assert-Condition ($decNoDbContent.Contains("DATABASE_URL=postgres://postgres@127.0.0.1:5433/le_francais")) "DATABASE_URL appended to env file"
    } else {
        Assert-Condition $false "Decrypted nodb file created" "File missing: $TestDecNoDbFile"
    }

    # -------------------------------------------------------------
    # Test 4: Incorrect Password Rejection
    # -------------------------------------------------------------
    Write-Host "`nTest Suite 4: Incorrect password rejection" -ForegroundColor Cyan
    if (Test-Path $TestWrongDecFile) {
        Remove-Item -Path $TestWrongDecFile -Force
    }

    & "$DecryptScript" -InputFile $TestEncFile -OutputFile $TestWrongDecFile -Password "TotallyWrongPassword!000" 2>$null
    $wrongPassExit = $LASTEXITCODE

    Assert-Condition ($wrongPassExit -ne 0) "decrypt_env.ps1 rejects incorrect password with non-zero exit code" "Exit code was $wrongPassExit"
    Assert-Condition (-not (Test-Path $TestWrongDecFile)) "Decrypted file not written on wrong password" "File should not exist"

    # -------------------------------------------------------------
    # Test 5: Corrupted file rejection
    # -------------------------------------------------------------
    Write-Host "`nTest Suite 5: Corrupted payload rejection" -ForegroundColor Cyan
    $CorruptedFile = Join-Path $RepoRoot "tools\tests\.env.corrupt.enc"
    [System.IO.File]::WriteAllBytes($CorruptedFile, (New-Object byte[] 10)) # less than 32 bytes

    & "$DecryptScript" -InputFile $CorruptedFile -OutputFile $TestWrongDecFile -Password $TestPassword 2>$null
    $corruptExit = $LASTEXITCODE

    Assert-Condition ($corruptExit -ne 0) "decrypt_env.ps1 rejects truncated payload (<32 bytes)" "Exit code was $corruptExit"
    if (Test-Path $CorruptedFile) {
        Remove-Item -Path $CorruptedFile -Force
    }

} finally {
    # Teardown temporary test files
    $filesToClean = @(
        $TestEnvFile,
        $TestEncFile,
        $TestDecFile,
        $TestEnvNoDbFile,
        $TestEncNoDbFile,
        $TestDecNoDbFile,
        $TestWrongDecFile
    )
    foreach ($file in $filesToClean) {
        if (Test-Path $file) {
            Remove-Item -Path $file -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "`n====================================================" -ForegroundColor Cyan
$summaryColor = if ($FailedTests -eq 0) { 'Green' } else { 'Red' }
Write-Host " Test Summary: $PassedTests Passed, $FailedTests Failed" -ForegroundColor $summaryColor
Write-Host "====================================================" -ForegroundColor Cyan

if ($FailedTests -gt 0) {
    exit 1
} else {
    exit 0
}

<#
.SYNOPSIS
    Decrypts an AES-256 encrypted payload (.env.dev.enc) to a local .env file.
.DESCRIPTION
    Derives key via PBKDF2 (100,000 iterations), decrypts AES-256-CBC with PKCS7,
    and enforces DATABASE_URL=postgres://postgres@127.0.0.1:5433/le_francais.
#>
param(
    [string]$InputFile,
    [string]$OutputFile,
    [string]$Password
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path $PSScriptRoot -Parent
if (-not $InputFile) {
    $InputFile = Join-Path $RepoRoot ".env.dev.enc"
}
if (-not $OutputFile) {
    $OutputFile = Join-Path $RepoRoot ".env"
}

if (-not (Test-Path $InputFile)) {
    [Console]::Error.WriteLine("Encrypted environment file not found: $InputFile")
    exit 1
}

$allBytes = [System.IO.File]::ReadAllBytes($InputFile)
if ($allBytes.Length -lt 48) {
    [Console]::Error.WriteLine("Encrypted file is corrupted or too short ($($allBytes.Length) bytes).")
    exit 1
}

if (-not $Password) {
    $secure = Read-Host "Enter project secrets decryption password" -AsSecureString
    $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

if ([string]::IsNullOrEmpty($Password)) {
    [Console]::Error.WriteLine("Password cannot be empty.")
    exit 1
}

try {
    # Extract Salt (16B) and IV (16B)
    $salt = New-Object byte[] 16
    $iv = New-Object byte[] 16
    [System.Array]::Copy($allBytes, 0, $salt, 0, 16)
    [System.Array]::Copy($allBytes, 16, $iv, 0, 16)

    $cipherLen = $allBytes.Length - 32
    $cipherBytes = New-Object byte[] $cipherLen
    [System.Array]::Copy($allBytes, 32, $cipherBytes, 0, $cipherLen)

    # Derive 256-bit AES key via PBKDF2 with SHA-256
    $hashName = [System.Security.Cryptography.HashAlgorithmName]::SHA256
    $kdf = New-Object System.Security.Cryptography.Rfc2898DeriveBytes($Password, $salt, 100000, $hashName)
    $key = $kdf.GetBytes(32)

    # Decrypt
    $aes = [System.Security.Cryptography.Aes]::Create()
    $aes.KeySize = 256
    $aes.Mode = [System.Security.Cryptography.CipherMode]::CBC
    $aes.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7
    $aes.Key = $key
    $aes.IV = $iv

    $decryptor = $aes.CreateDecryptor()
    $plainBytes = $decryptor.TransformFinalBlock($cipherBytes, 0, $cipherBytes.Length)
    $plainText = [System.Text.Encoding]::UTF8.GetString($plainBytes)

    # Enforce local portable PostgreSQL port 5433
    $targetDbUrl = "DATABASE_URL=postgres://postgres@127.0.0.1:5433/le_francais"
    if ($plainText -match "(?m)^DATABASE_URL=.*$") {
        $plainText = [System.Text.RegularExpressions.Regex]::Replace($plainText, "(?m)^DATABASE_URL=.*$", $targetDbUrl)
    } else {
        $plainText = $plainText.TrimEnd() + "`r`n" + $targetDbUrl + "`r`n"
    }

    $outDir = Split-Path $OutputFile -Parent
    if ($outDir -and -not (Test-Path $outDir)) {
        New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    }

    [System.IO.File]::WriteAllText($OutputFile, $plainText, [System.Text.Encoding]::UTF8)

    Write-Host "Successfully decrypted $InputFile -> $OutputFile (DATABASE_URL mapped to port 5433)" -ForegroundColor Green
    exit 0
} catch [System.Security.Cryptography.CryptographicException] {
    [Console]::Error.WriteLine("Decryption failed: Incorrect password or corrupted payload.")
    exit 1
} catch {
    [Console]::Error.WriteLine("Decryption error: $_")
    exit 1
}

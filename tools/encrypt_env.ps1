<#
.SYNOPSIS
    Encrypts a .env file to an AES-256 encrypted payload (.env.dev.enc).
.DESCRIPTION
    Uses PBKDF2 key derivation (SHA-256, 100,000 iterations, random salt)
    and AES-256-CBC with PKCS7 padding. Compatible with PowerShell 5.1 and 7+.
#>
param(
    [string]$InputFile,
    [string]$OutputFile,
    [string]$Password
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path $PSScriptRoot -Parent
if (-not $InputFile) {
    $InputFile = Join-Path $RepoRoot ".env"
}
if (-not $OutputFile) {
    $OutputFile = Join-Path $RepoRoot ".env.dev.enc"
}

if (-not (Test-Path $InputFile)) {
    [Console]::Error.WriteLine("Input file not found: $InputFile")
    exit 1
}

if (-not $Password) {
    $secure = Read-Host "Enter encryption password" -AsSecureString
    $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

if ([string]::IsNullOrEmpty($Password)) {
    [Console]::Error.WriteLine("Password cannot be empty.")
    exit 1
}

try {
    # Generate 16-byte random salt and 16-byte random IV
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $salt = New-Object byte[] 16
    $iv = New-Object byte[] 16
    $rng.GetBytes($salt)
    $rng.GetBytes($iv)

    # Derive 256-bit AES key via PBKDF2 (SHA-256, 100,000 iterations)
    $hashName = [System.Security.Cryptography.HashAlgorithmName]::SHA256
    $kdf = New-Object System.Security.Cryptography.Rfc2898DeriveBytes($Password, $salt, 100000, $hashName)
    $key = $kdf.GetBytes(32)

    # Encrypt
    $aes = [System.Security.Cryptography.Aes]::Create()
    $aes.KeySize = 256
    $aes.Mode = [System.Security.Cryptography.CipherMode]::CBC
    $aes.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7
    $aes.Key = $key
    $aes.IV = $iv

    $plainBytes = [System.IO.File]::ReadAllBytes($InputFile)
    $encryptor = $aes.CreateEncryptor()
    $cipherBytes = $encryptor.TransformFinalBlock($plainBytes, 0, $plainBytes.Length)

    # Write output: Salt (16B) + IV (16B) + Ciphertext
    $outDir = Split-Path $OutputFile -Parent
    if ($outDir -and -not (Test-Path $outDir)) {
        New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    }

    $outStream = [System.IO.File]::Create($OutputFile)
    $outStream.Write($salt, 0, $salt.Length)
    $outStream.Write($iv, 0, $iv.Length)
    $outStream.Write($cipherBytes, 0, $cipherBytes.Length)
    $outStream.Close()

    Write-Host "Successfully encrypted $InputFile -> $OutputFile" -ForegroundColor Green
    exit 0
} catch {
    [Console]::Error.WriteLine("Encryption failed: $_")
    exit 1
}

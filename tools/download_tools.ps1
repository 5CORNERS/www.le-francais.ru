<#
.SYNOPSIS
    Downloads and extracts all required runtime binaries, tools, and database backups.
.DESCRIPTION
    Ensures micromamba, portable PostgreSQL 15, ffmpeg, geoip, and database backups
    are prepared and flattened in their expected local directory structures.
#>
param()

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " [Tools Setup] Initializing Windows Dev Dependencies" -ForegroundColor Cyan
Write-Host " Repo Root: $RepoRoot" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Micromamba
$mambaExe = Join-Path $RepoRoot "tools\bin\micromamba.exe"
if (-not (Test-Path $mambaExe)) {
    Write-Host "`n[1/5] Downloading Micromamba..." -ForegroundColor Yellow
    $binDir = Join-Path $RepoRoot "tools\bin"
    New-Item -ItemType Directory -Force -Path $binDir | Out-Null

    $tempMamba = Join-Path $RepoRoot "tools\temp_mamba"
    New-Item -ItemType Directory -Force -Path $tempMamba | Out-Null

    $mambaArchive = Join-Path $tempMamba "micromamba.tar.bz2"
    $mambaUrl = "https://micro.mamba.pm/api/micromamba/win-64/latest"
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $mambaUrl -OutFile $mambaArchive -UseBasicParsing

    Write-Host "Extracting Micromamba..." -ForegroundColor Yellow
    tar.exe -xf "$mambaArchive" -C "$tempMamba"

    # Search for micromamba.exe inside temp folder
    $foundMamba = Get-ChildItem -Path $tempMamba -Filter "micromamba.exe" -Recurse | Select-Object -First 1
    if ($foundMamba) {
        Move-Item -Path $foundMamba.FullName -Destination $mambaExe -Force
        Write-Host "Micromamba installed at: $mambaExe" -ForegroundColor Green
    } else {
        [Console]::Error.WriteLine("Failed to find micromamba.exe after extraction.")
        exit 1
    }

    Remove-Item -Recurse -Force -Path $tempMamba -ErrorAction SilentlyContinue
} else {
    Write-Host "`n[1/5] Micromamba already present." -ForegroundColor Green
}

# 2. PostgreSQL 15 Portable Binaries
$pgCtl = Join-Path $RepoRoot "tools\pgsql\bin\pg_ctl.exe"
if (-not (Test-Path $pgCtl)) {
    Write-Host "`n[2/5] Downloading PostgreSQL 15 portable binaries..." -ForegroundColor Yellow
    $toolsDir = Join-Path $RepoRoot "tools"
    New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null

    $tempPg = Join-Path $RepoRoot "tools\temp_pg"
    New-Item -ItemType Directory -Force -Path $tempPg | Out-Null

    $pgZip = Join-Path $toolsDir "postgres16.zip"
    $pgUrl = "https://get.enterprisedb.com/postgresql/postgresql-16.4-1-windows-x64-binaries.zip"
    if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
        & curl.exe -L -o "$pgZip" "$pgUrl"
    } else {
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($pgUrl, $pgZip)
    }

    Write-Host "Extracting PostgreSQL 15 binaries..." -ForegroundColor Yellow
    tar.exe -xf "$pgZip" -C "$tempPg"

    $innerPg = Join-Path $tempPg "pgsql"
    $targetPg = Join-Path $RepoRoot "tools\pgsql"
    if (Test-Path $innerPg) {
        New-Item -ItemType Directory -Force -Path $targetPg | Out-Null
        Copy-Item -Path "$innerPg\*" -Destination $targetPg -Recurse -Force
        # Remove unused bulky pgAdmin 4 (50,000 files / 500MB)
        $unneededPgAdmin = Join-Path $targetPg "pgAdmin 4"
        if (Test-Path $unneededPgAdmin) {
            Remove-Item -Recurse -Force -Path $unneededPgAdmin -ErrorAction SilentlyContinue
        }
        Write-Host "PostgreSQL 16 flattened to: $targetPg" -ForegroundColor Green
    } else {
        [Console]::Error.WriteLine("Unexpected archive structure for PostgreSQL binaries.")
        exit 1
    }

    Remove-Item -Recurse -Force -Path $tempPg -ErrorAction SilentlyContinue
    Remove-Item -Force -Path $pgZip -ErrorAction SilentlyContinue
} else {
    Write-Host "`n[2/5] PostgreSQL 15 binaries already present." -ForegroundColor Green
}

# 3. FFmpeg
$ffmpegExe = Join-Path $RepoRoot "ffmpeg\ffmpeg.exe"
if (-not (Test-Path $ffmpegExe)) {
    Write-Host "`n[3/5] Setting up FFmpeg..." -ForegroundColor Yellow
    $ffmpegDir = Join-Path $RepoRoot "ffmpeg"
    New-Item -ItemType Directory -Force -Path $ffmpegDir | Out-Null

    # Check if system ffmpeg exists
    $sysFfmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
    if ($sysFfmpeg -and (Test-Path $sysFfmpeg.Source)) {
        Copy-Item -Path $sysFfmpeg.Source -Destination $ffmpegExe -Force
        Write-Host "Copied FFmpeg from system PATH: $($sysFfmpeg.Source)" -ForegroundColor Green
    } else {
        Write-Host "Downloading portable FFmpeg..." -ForegroundColor Yellow
        $tempFf = Join-Path $RepoRoot "tools\temp_ff"
        New-Item -ItemType Directory -Force -Path $tempFf | Out-Null
        $ffZip = Join-Path $tempFf "ffmpeg.zip"
        $ffUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
            & curl.exe -L -o "$ffZip" "$ffUrl"
        } else {
            Invoke-WebRequest -Uri $ffUrl -OutFile $ffZip -UseBasicParsing
        }
        tar.exe -xf "$ffZip" -C "$tempFf"
        $foundFf = Get-ChildItem -Path $tempFf -Filter "ffmpeg.exe" -Recurse | Select-Object -First 1
        if ($foundFf) {
            Move-Item -Path $foundFf.FullName -Destination $ffmpegExe -Force
            Write-Host "FFmpeg installed at: $ffmpegExe" -ForegroundColor Green
        }
        Remove-Item -Recurse -Force -Path $tempFf -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "`n[3/5] FFmpeg already present." -ForegroundColor Green
}

# 4. GeoIP Databases
$geoipDir = Join-Path $RepoRoot "geoip"
$cityMmdb = Join-Path $geoipDir "GeoLite2-City.mmdb"
$countryMmdb = Join-Path $geoipDir "GeoLite2-Country.mmdb"
New-Item -ItemType Directory -Force -Path $geoipDir | Out-Null

if ((Test-Path $cityMmdb) -and (Test-Path $countryMmdb)) {
    Write-Host "`n[4/5] GeoIP databases already present in $geoipDir." -ForegroundColor Green
} else {
    Write-Host "`n[4/5] Checking GeoIP databases..." -ForegroundColor Yellow
    # If present elsewhere on the system, copy them
    $knownGeoipPaths = @(
        (Join-Path $RepoRoot "geoip"),
        (Join-Path $env:USERPROFILE "workspace\postgres-setup\geoip"),
        (Join-Path $env:USERPROFILE "PycharmProjects\le-francais\geoip")
    )
    foreach ($kg in $knownGeoipPaths) {
        if (Test-Path (Join-Path $kg "GeoLite2-City.mmdb")) {
            Copy-Item -Path (Join-Path $kg "GeoLite2-City.mmdb") -Destination $cityMmdb -Force
        }
        if (Test-Path (Join-Path $kg "GeoLite2-Country.mmdb")) {
            Copy-Item -Path (Join-Path $kg "GeoLite2-Country.mmdb") -Destination $countryMmdb -Force
        }
    }
    if ((Test-Path $cityMmdb) -and (Test-Path $countryMmdb)) {
        Write-Host "GeoIP databases verified." -ForegroundColor Green
    } else {
        Write-Host "Notice: GeoLite2-City.mmdb and GeoLite2-Country.mmdb should be placed in $geoipDir" -ForegroundColor Yellow
    }
}

# 5. Database Backups: Extract .dir.tar.gz archives in tools\backups
$backupsDir = Join-Path $RepoRoot "tools\backups"
New-Item -ItemType Directory -Force -Path $backupsDir | Out-Null

Write-Host "`n[5/5] Checking and extracting database backups..." -ForegroundColor Yellow

$archives = Get-ChildItem -Path $backupsDir -Filter "*.dir.tar.gz" -File
if ($archives) {
    foreach ($arc in $archives) {
        Write-Host "Extracting $($arc.Name)..." -ForegroundColor Yellow
        tar.exe -xf $arc.FullName -C $backupsDir
    }
    Write-Host "Database backup archives extracted successfully." -ForegroundColor Green
} else {
    Write-Host "Notice: No .dir.tar.gz files found in $backupsDir." -ForegroundColor Yellow
}

Write-Host "`nAll tools setup tasks finished successfully." -ForegroundColor Green
exit 0

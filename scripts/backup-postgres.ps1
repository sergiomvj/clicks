param(
  [string]$Timestamp = (Get-Date -Format 'yyyyMMdd-HHmmss'),
  [string]$OutputDir = '.\backups',
  [string]$Bucket = ''
)

if (-not $env:PGHOST) { throw 'PGHOST is required.' }
if (-not $env:PGPORT) { $env:PGPORT = '5432' }
if (-not $env:PGDATABASE) { throw 'PGDATABASE is required.' }
if (-not $env:PGUSER) { throw 'PGUSER is required.' }
if (-not $env:PGPASSWORD) { throw 'PGPASSWORD is required.' }

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$backupFile = Join-Path $OutputDir ("fbr-click-$Timestamp.sql.gz")

$pgDump = Get-Command pg_dump -ErrorAction SilentlyContinue
if ($null -eq $pgDump) {
  throw 'pg_dump not found in PATH.'
}

$gzip = Get-Command gzip -ErrorAction SilentlyContinue
if ($null -eq $gzip) {
  throw 'gzip not found in PATH.'
}

$dumpProcess = Start-Process -FilePath $pgDump.Source -ArgumentList @('-h', $env:PGHOST, '-p', $env:PGPORT, '-U', $env:PGUSER, '-d', $env:PGDATABASE, '--no-owner', '--no-privileges') -NoNewWindow -RedirectStandardOutput "$backupFile.raw" -PassThru -Wait
if ($dumpProcess.ExitCode -ne 0) {
  throw "pg_dump failed with exit code $($dumpProcess.ExitCode)."
}

$gzipProcess = Start-Process -FilePath $gzip.Source -ArgumentList @('-f', "$backupFile.raw") -NoNewWindow -PassThru -Wait
if ($gzipProcess.ExitCode -ne 0) {
  throw "gzip failed with exit code $($gzipProcess.ExitCode)."
}

Move-Item "$backupFile.raw.gz" $backupFile -Force

if ($Bucket) {
  $aws = Get-Command aws -ErrorAction SilentlyContinue
  if ($null -eq $aws) {
    throw 'AWS CLI not found in PATH.'
  }
  aws s3 cp $backupFile "$Bucket/$(Split-Path $backupFile -Leaf)"
}

Write-Output "BACKUP_CREATED=$backupFile"

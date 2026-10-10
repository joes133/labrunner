# labrunner installer (Windows / PowerShell)
#
# Note: all output strings are intentionally ASCII-only.
# Windows PowerShell 5.1 reads BOM-less .ps1 files using the system
# ANSI codepage, which turns non-ASCII characters into mojibake on
# Chinese Windows. Keeping this file pure ASCII avoids that entirely.

$ErrorActionPreference = 'Stop'

$src = Split-Path -Parent $MyInvocation.MyCommand.Definition
$dst = Join-Path $HOME '.workbuddy\skills\labrunner'

Write-Host 'Installing labrunner ...'
Write-Host "  from : $src"
Write-Host "  to   : $dst"

if (Test-Path $dst) {
    Write-Host '  target exists, will be overwritten' -ForegroundColor Yellow
}

New-Item -ItemType Directory -Force -Path $dst | Out-Null

Copy-Item (Join-Path $src 'SKILL.md')   -Destination $dst -Force
Copy-Item (Join-Path $src 'README.md')  -Destination $dst -Force
Copy-Item (Join-Path $src 'LICENSE')    -Destination $dst -Force
Copy-Item (Join-Path $src 'scripts')    -Destination (Join-Path $dst 'scripts')    -Recurse -Force
Copy-Item (Join-Path $src 'references') -Destination (Join-Path $dst 'references') -Recurse -Force

# .local holds personal config and must never be overwritten blindly
$localDst = Join-Path $dst '.local'
if (-not (Test-Path $localDst)) {
    New-Item -ItemType Directory -Force -Path $localDst | Out-Null
    $example = Join-Path $src '.local\profile.example.json'
    if (Test-Path $example) {
        Copy-Item $example -Destination $localDst -Force
    }
}

Write-Host ''
Write-Host "Installed to: $dst" -ForegroundColor Green
Write-Host ''
Write-Host 'Next step - install dependencies:'
Write-Host '  pip install pillow python-docx chardet'
Write-Host '  pip install pywin32          (needed for window capture)'
Write-Host ''
Write-Host 'Done. Trigger it with: "help me do this lab" / "write the lab report"'

# labrunner installer (Windows / PowerShell)
#
# Note: all output strings are intentionally ASCII-only.
# Windows PowerShell 5.1 reads BOM-less .ps1 files using the system
# ANSI codepage, which turns non-ASCII characters into mojibake on
# Chinese Windows. Keeping this file pure ASCII avoids that entirely.
#
# Usage:
#   .\install.ps1                    # install to workbuddy (default)
#   .\install.ps1 -Client claude     # install to a specific client
#   .\install.ps1 -List              # show known clients and their paths

param(
    [string]$Client = 'auto',
    [switch]$List
)

$ErrorActionPreference = 'Stop'

$src = Split-Path -Parent $MyInvocation.MyCommand.Definition

# ---------------------------------------------------------------------------
# Client registry.
# SKILL.md is an open standard (Anthropic Agent Skills), so the same files
# work everywhere - only the install location differs.
# ---------------------------------------------------------------------------
$clients = [ordered]@{
    'workbuddy' = Join-Path $HOME '.workbuddy\skills\labrunner'
    'claude'    = Join-Path $HOME '.claude\skills\labrunner'
    'cursor'    = Join-Path $HOME '.cursor\skills\labrunner'
    'codex'     = Join-Path $HOME '.codex\skills\labrunner'
    'agents'    = Join-Path $HOME '.agents\skills\labrunner'
    'kiro'      = Join-Path $HOME '.kiro\agents\labrunner'
}

# A client counts as "detected" when its parent config dir exists.
$detectRoot = @{
    'workbuddy' = Join-Path $HOME '.workbuddy'
    'claude'    = Join-Path $HOME '.claude'
    'cursor'    = Join-Path $HOME '.cursor'
    'codex'     = Join-Path $HOME '.codex'
    'agents'    = Join-Path $HOME '.agents'
    'kiro'      = Join-Path $HOME '.kiro'
}

function Show-ClientList {
    Write-Output 'Known clients:'
    foreach ($k in $clients.Keys) {
        $mark = ' '
        if (Test-Path $detectRoot[$k]) { $mark = '*' }
        Write-Output ("  {0} {1,-10} {2}" -f $mark, $k, $clients[$k])
    }
    Write-Output ''
    Write-Output '  * = detected on this machine'
}

function Install-To {
    param([string]$Name, [string]$Dst)

    Write-Output ''
    Write-Output "[$Name]"
    Write-Output "  -> $Dst"

    New-Item -ItemType Directory -Force -Path $Dst | Out-Null

    foreach ($f in @('SKILL.md', 'README.md', 'LICENSE')) {
        $p = Join-Path $src $f
        if (Test-Path $p) { Copy-Item $p -Destination $Dst -Force }
    }

    # Replace directories wholesale. Copy-Item into an existing directory
    # nests a copy inside it (dst\references\references), so remove first.
    foreach ($d in @('scripts', 'references')) {
        $p = Join-Path $src $d
        $q = Join-Path $Dst $d
        if (Test-Path $p) {
            if (Test-Path $q) { Remove-Item $q -Recurse -Force }
            Copy-Item $p -Destination $q -Recurse -Force
        }
    }

    # .local holds personal config: profile.json is NEVER touched, but
    # profile.example.json is just a template and is always refreshed.
    $localDst = Join-Path $Dst '.local'
    if (-not (Test-Path $localDst)) {
        New-Item -ItemType Directory -Force -Path $localDst | Out-Null
    }
    $example = Join-Path $src '.local\profile.example.json'
    if (Test-Path $example) {
        Copy-Item $example -Destination $localDst -Force
    }

    Write-Output '  installed'
}

Write-Output 'Installing labrunner ...'
Write-Output "  from : $src"

if ($List) {
    Show-ClientList
    Write-Output ''
    Write-Output 'Next step - install dependencies:'
    Write-Output '  pip install pillow python-docx chardet'
    Write-Output '  pip install pywin32          (Windows only, window capture)'
} else {
    $targets = @()

    if ($Client -eq 'auto') {
        # Auto mode installs to workbuddy only. Every other client must be
        # named explicitly with -Client, so labrunner never writes into a
        # directory you did not ask for.
        $targets = @('workbuddy')
        Write-Output '  auto mode: workbuddy only'
        Write-Output '  run -List to see every supported client'
    } else {
        if (-not $clients.Contains($Client)) {
            Write-Output ''
            Write-Output "Unknown client: $Client"
            Show-ClientList
            $targets = @()
        } else {
            $targets = @($Client)
        }
    }

    foreach ($t in $targets) {
        Install-To -Name $t -Dst $clients[$t]
    }

    Write-Output ''
    Write-Output 'Next step - install dependencies:'
    Write-Output '  pip install pillow python-docx chardet'
    Write-Output '  pip install pywin32          (Windows only, window capture)'
    Write-Output ''
    Write-Output 'Done. Trigger with: /labrunner  or  "help me run this lab"'
}

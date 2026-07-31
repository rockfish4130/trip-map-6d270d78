<#
.SYNOPSIS
  Stamp the build time, commit, and push -- which triggers a GitHub Pages rebuild.

.EXAMPLE
  pwsh tools/publish.ps1 -Message "Update Day 6 birding notes"

.NOTES
  * Run from the repo root (or anywhere; paths are resolved relative to this script).
  * Requires: git, python (for the build stamp).
  * GitHub Pages redeploys automatically ~15-60s after the push. The live URL and
    repo settings are documented in README.md.
#>
param(
  [Parameter(Mandatory = $true)][string]$Message
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot   # repo root = parent of tools/

Write-Host "1/4  Stamping build time..."
python (Join-Path $PSScriptRoot "stamp_build.py")

Write-Host "2/4  git add..."
git -C $repo add -A

Write-Host "3/4  git commit..."
git -C $repo commit -m $Message

Write-Host "4/4  git push..."
git -C $repo push origin main

Write-Host "Done. GitHub Pages will rebuild shortly; see README.md for the live URL."

function Get-ScriptDirectory { Split-Path $MyInvocation.ScriptName }
$source = Join-Path (Get-ScriptDirectory) 'output'
$destination = Join-Path (Get-ScriptDirectory) 'save'
Copy-Item $source -Destination $destination -Recurse

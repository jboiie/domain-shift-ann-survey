# Windows only, needs Microsoft Word. Refreshes the table of contents page numbers in the report.
param([string]$Docx = "Domain_Shift_Survey_Report.docx")
$path = Join-Path $PSScriptRoot $Docx
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $d = $w.Documents.Open($path, $false, $false)
    foreach ($t in $d.TablesOfContents) { $t.Update() }
    $d.Save()
    Write-Output ("pages: " + $d.ComputeStatistics(2))
    $d.Close($false)
} finally { $w.Quit() }

param([string]$Docx = "Domain_Shift_Survey_Report.docx", [string]$Pdf = "Domain_Shift_Survey_Report.pdf", [string]$Step = "pdf")
$root = (Get-Location).Path
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
Write-Output ("word pid " + (Get-Process WINWORD | Sort-Object StartTime | Select-Object -Last 1).Id)
try {
    $d = $w.Documents.Open((Join-Path $root $Docx), $false, $false)
    foreach ($t in $d.TablesOfContents) { $t.Update() }
    Write-Output "toc updated"
    if ($Step -eq "pdf") {
        $d.SaveAs2((Join-Path $root $Pdf), 17)
        Write-Output "pdf saved"
    } else {
        $d.Save()
        Write-Output "docx saved"
    }
    Write-Output ("pages: " + $d.ComputeStatistics(2))
    $d.Close($false)
} finally { $w.Quit() }

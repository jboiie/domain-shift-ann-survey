param([string]$Docx = "Domain_Shift_Survey_Report.docx", [string]$Out = "ref\pages")
$root = (Get-Location).Path
New-Item -ItemType Directory -Force (Join-Path $root $Out) | Out-Null
Get-ChildItem (Join-Path $root $Out) -Filter *.emf | Remove-Item -Force
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $d = $w.Documents.Open((Join-Path $root $Docx), $false, $true)
    $n = $d.ComputeStatistics(2)
    $pg = $d.ActiveWindow.ActivePane.Pages
    foreach ($i in 1..$n) {
        $b = $pg.Item($i).EnhMetaFileBits
        [IO.File]::WriteAllBytes((Join-Path $root ("$Out\p{0:D2}.emf" -f $i)), $b)
    }
    Write-Output "rendered $n pages"
    $d.Close($false)
} finally { $w.Quit() }

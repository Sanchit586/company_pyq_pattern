param(
    [Parameter(Mandatory=$true)][string]$PdfUrl,
    [string]$Pages = '1,2,3',
    [int]$TextLimit = 6000,
    [switch]$IndexCompanies
)
$ErrorActionPreference = 'Stop'
if ($PdfUrl -notmatch '^https://drive\.google\.com/uc\?export=download&id=[A-Za-z0-9_-]+$') {
    throw 'Expected an ordinary public Google Drive download URL.'
}
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Storage.Streams.InMemoryRandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime] > $null
[Windows.Storage.Streams.DataWriter,Windows.Storage.Streams,ContentType=WindowsRuntime] > $null
[Windows.Data.Pdf.PdfDocument,Windows.Data.Pdf,ContentType=WindowsRuntime] > $null
[Windows.Data.Pdf.PdfPageRenderOptions,Windows.Data.Pdf,ContentType=WindowsRuntime] > $null
[Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics.Imaging,ContentType=WindowsRuntime] > $null
[Windows.Graphics.Imaging.SoftwareBitmap,Windows.Graphics.Imaging,ContentType=WindowsRuntime] > $null
[Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime] > $null
[Windows.Media.Ocr.OcrResult,Windows.Foundation,ContentType=WindowsRuntime] > $null
$script:OperationAdapter = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.IsGenericMethodDefinition -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
} | Select-Object -First 1
$script:ActionAdapter = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and -not $_.IsGenericMethodDefinition -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction'
} | Select-Object -First 1
function Wait-WinRt($Operation, [Type]$ResultType) {
    $task = $script:OperationAdapter.MakeGenericMethod($ResultType).Invoke($null, @($Operation))
    $task.GetAwaiter().GetResult()
}
$client = New-Object System.Net.WebClient
$bytes = $client.DownloadData($PdfUrl)
$client.Dispose()
if ($bytes.Length -lt 5 -or [System.Text.Encoding]::ASCII.GetString($bytes,0,4) -ne '%PDF') {
    throw 'Public download did not return a PDF.'
}
$pdfStream = [Windows.Storage.Streams.InMemoryRandomAccessStream]::new()
$writer = [Windows.Storage.Streams.DataWriter]::new($pdfStream)
$writer.WriteBytes($bytes)
$null = Wait-WinRt ($writer.StoreAsync()) ([uint32])
$null = $writer.DetachStream()
$writer.Dispose()
$pdfStream.Seek(0)
$pdf = Wait-WinRt ([Windows.Data.Pdf.PdfDocument]::LoadFromStreamAsync($pdfStream)) ([Windows.Data.Pdf.PdfDocument])
Write-Output ('PDF pages: ' + $pdf.PageCount)
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if ($null -eq $engine) { throw 'Windows OCR language is unavailable.' }
$pageNumbers = if ($Pages -match '^(\d+)-(\d+)$') { [int]$Matches[1]..[int]$Matches[2] } else { $Pages.Split(',') }
foreach ($pageNumber in $pageNumbers) {
    $page = $pdf.GetPage([uint32]([int]$pageNumber - 1))
    $raster = [Windows.Storage.Streams.InMemoryRandomAccessStream]::new()
    $options = [Windows.Data.Pdf.PdfPageRenderOptions]::new()
    $options.DestinationWidth = 1900
    $task = $script:ActionAdapter.Invoke($null, @($page.RenderToStreamAsync($raster, $options)))
    $null = $task.GetAwaiter().GetResult()
    $raster.Seek(0)
    $decoder = Wait-WinRt ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($raster)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bitmap = Wait-WinRt ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $result = Wait-WinRt ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
    $body = $result.Text
    $show = $true
    if ($IndexCompanies) {
        $header = $body.Substring(0,[Math]::Min(450,$body.Length))
        $show = $header -match '(?i)Google|Microsoft|Amazon|Goldman|Qualcomm|Flipkart|Adobe|Oracle|Nvidia|Accenture|Uber|Apple|DE\s*Shaw|Infosys|\bTCS\b|\bIBM\b|Wipro|Cisco|Morgan|American Express|Wells Fargo|Walmart|Samsung|Intel|Cognizant|Barclays|\bHCL\b|Databricks|Facebook|Jane Street|Graviton|Squarepoint|\bIMC\b|Rubrik|Salesforce|\bDell\b|Tech Mahindra|Sprinklr|Arista|Arcesium|Mastercard|Deutsche|BlackRock|Capital One|Meesho|Zomato|Optiver|Tower Research|Bank of America|\bCiti\b|Mindtree'
    }
    if ($show) { Write-Output ('PDF PAGE ' + $pageNumber + ': ' + $body.Substring(0,[Math]::Min($TextLimit,$body.Length))) }
    $bitmap.Dispose()
    $raster.Dispose()
    $page.Dispose()
    if ([int]$pageNumber % 20 -eq 0) { Write-Output ('PROGRESS: page ' + $pageNumber) }
}
$pdfStream.Dispose()

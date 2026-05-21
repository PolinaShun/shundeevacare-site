$user = "git"
$pass = "Shundeeva112358"
$server = "185.127.24.17"
$base_path = "/www/shundeevacare.ru"

# Работаем в текущей директории скрипта
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptPath

$files = @(
    @{ local = "index.html"; remote = "/index.html" },
    @{ local = "assets/img/edu14.webp"; remote = "/assets/img/edu14.webp" }
)

foreach ($file in $files) {
    Write-Host "Uploading $($file.local) to $($file.remote)..."
    try {
        $request = [System.Net.FtpWebRequest]::Create("ftp://$server$base_path$($file.remote)")
        $request.Credentials = New-Object System.Net.NetworkCredential($user, $pass)
        $request.Method = [System.Net.WebRequestMethods+Ftp]::UploadFile
        $request.UsePassive = $true
        
        $localPath = Join-Path $scriptPath $file.local
        $fileBytes = [System.IO.File]::ReadAllBytes($localPath)
        $request.ContentLength = $fileBytes.Length
        
        $requestStream = $request.GetRequestStream()
        $requestStream.Write($fileBytes, 0, $fileBytes.Length)
        $requestStream.Close()
        
        $response = $request.GetResponse()
        Write-Host "Success: $($response.StatusDescription)"
        $response.Close()
    } catch {
        Write-Host "Failed: $($_.Exception.Message)"
    }
}

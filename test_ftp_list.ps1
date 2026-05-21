$user = "git"
$pass = "Shundeeva112358"
$server = "185.127.24.17"
$path = "/www/shundeevacare.ru/"

$request = [System.Net.FtpWebRequest]::Create("ftp://$server$path")
$request.Credentials = New-Object System.Net.NetworkCredential($user, $pass)
$request.Method = [System.Net.WebRequestMethods+Ftp]::ListDirectory
$request.UsePassive = $true

try {
    $response = $request.GetResponse()
    $reader = New-Object System.IO.StreamReader($response.GetResponseStream())
    $reader.ReadToEnd()
    $reader.Close()
    $response.Close()
} catch {
    Write-Host "Failed: $($_.Exception.Message)"
}

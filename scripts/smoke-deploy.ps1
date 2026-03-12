param(
  [string]$FrontendUrl = 'https://click.fbrapps.com',
  [string]$ApiHealthUrl = 'https://api.click.fbrapps.com/health',
  [string]$GrafanaUrl = 'https://click.fbrapps.com/grafana/'
)

$results = @()

function Test-Endpoint {
  param(
    [string]$Name,
    [string]$Url
  )

  try {
    $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 15
    $results += [pscustomobject]@{
      name = $Name
      url = $Url
      status_code = [int]$response.StatusCode
      ok = $response.StatusCode -ge 200 -and $response.StatusCode -lt 400
    }
  } catch {
    $statusCode = -1
    if ($_.Exception.Response) {
      $statusCode = [int]$_.Exception.Response.StatusCode
    }
    $results += [pscustomobject]@{
      name = $Name
      url = $Url
      status_code = $statusCode
      ok = $false
    }
  }
}

Test-Endpoint -Name 'frontend' -Url $FrontendUrl
Test-Endpoint -Name 'api_health' -Url $ApiHealthUrl
Test-Endpoint -Name 'grafana' -Url $GrafanaUrl

$results | ConvertTo-Json -Depth 10
if ($results.Where({ -not $_.ok }).Count -gt 0) {
  exit 1
}

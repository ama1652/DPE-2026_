# Team 2 - alle Tests lokal ausfuehren (DMN-Test, Endzustand-Test, Code-Build)
# Verantwortlich: Saifudin Mohammadi
# Start: Doppelklick auf tests_starten.cmd (gleicher Ordner). Braucht kein Git, Java oder Maven.

$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ErrorActionPreference = "Stop"
$repo  = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$tools = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "DPE-Werkzeuge"
$ergebnis = Join-Path ([Environment]::GetFolderPath("Desktop")) "testergebnis.txt"
Start-Transcript -Path $ergebnis -Force | Out-Null

try {
    New-Item -ItemType Directory -Force $tools | Out-Null

    # 1. Java 21 (portabel, ohne Installation)
    $jdk = Get-ChildItem $tools -Directory -Filter "jdk-21*" -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $jdk) {
        Write-Host "Lade Java 21 ... (ca. 200 MB, bitte warten)"
        Invoke-WebRequest -UseBasicParsing "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse" -OutFile "$tools\jdk.zip"
        Expand-Archive "$tools\jdk.zip" $tools -Force
        Remove-Item "$tools\jdk.zip"
        $jdk = Get-ChildItem $tools -Directory -Filter "jdk-21*" | Select-Object -First 1
    }

    # 2. Maven (portabel)
    $mvnDir = Join-Path $tools "apache-maven-3.9.11"
    if (-not (Test-Path $mvnDir)) {
        Write-Host "Lade Maven ..."
        Invoke-WebRequest -UseBasicParsing "https://archive.apache.org/dist/maven/maven-3/3.9.11/binaries/apache-maven-3.9.11-bin.zip" -OutFile "$tools\maven.zip"
        Expand-Archive "$tools\maven.zip" $tools -Force
        Remove-Item "$tools\maven.zip"
    }
    $env:JAVA_HOME = $jdk.FullName
    $env:Path = "$($jdk.FullName)\bin;$mvnDir\bin;$env:Path"
    $mvn = "$mvnDir\bin\mvn.cmd"

    # 3. Die drei Pruefungen im Repo-Ordner
    $schritte = @(
        @("werkzeuge\dmn-test",        "test"),
        @("werkzeuge\endzustand-test", "test"),
        @("code\team2",                "package")
    )
    $ErrorActionPreference = "Continue"
    & java -version
    & $mvn -v
    foreach ($s in $schritte) {
        Write-Host ""
        Write-Host "=== $($s[0]): mvn $($s[1]) ===" -ForegroundColor Cyan
        Push-Location (Join-Path $repo $s[0])
        $log = Join-Path $tools ("log_" + ($s[0] -replace '[\\/]', '_') + ".txt")
        & $mvn -B $s[1] *> $log
        Get-Content $log | Select-String -CaseSensitive -Pattern "Tests run:|OK  End|FAIL|\[ERROR\]|BUILD" | ForEach-Object { $_.Line }
        Pop-Location
    }
}
catch {
    Write-Host ""
    Write-Host "FEHLER: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Stop-Transcript | Out-Null
    Write-Host ""
    Write-Host "Fertig. Ergebnis auf dem Desktop: testergebnis.txt" -ForegroundColor Green
    Write-Host "Vollstaendige Logs: $tools\log_*.txt"
    Read-Host "Enter druecken zum Schliessen"
}

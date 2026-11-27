# Team 2 - CIB seven Run (ohne Docker) starten, Modelle deployen, Instanz PH-0001:TP-M starten (Schritt 3)
# Verantwortlich: Saifudin Mohammadi
# Start: Doppelklick auf cib_starten.cmd (gleicher Ordner)

$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ErrorActionPreference = "Stop"
$doku  = [Environment]::GetFolderPath("MyDocuments")
$desk  = [Environment]::GetFolderPath("Desktop")
$tools = Join-Path $doku "DPE-Werkzeuge"
$repo  = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$rest  = "http://localhost:8080/engine-rest"
Start-Transcript -Path (Join-Path $desk "cib_ergebnis.txt") -Force | Out-Null

try {
    New-Item -ItemType Directory -Force $tools | Out-Null

    # 1. Java 21 (wie bei den Tests, portabel)
    $jdk = Get-ChildItem $tools -Directory -Filter "jdk-21*" -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $jdk) {
        Write-Host "Lade Java 21 ..."
        Invoke-WebRequest -UseBasicParsing "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse" -OutFile "$tools\jdk.zip"
        Expand-Archive "$tools\jdk.zip" $tools -Force; Remove-Item "$tools\jdk.zip"
        $jdk = Get-ChildItem $tools -Directory -Filter "jdk-21*" | Select-Object -First 1
    }
    $env:JAVA_HOME = $jdk.FullName
    $env:Path = "$($jdk.FullName)\bin;$env:Path"

    # 2. CIB seven Run 3.0.0 laden (nur beim ersten Mal)
    $cibDir = Join-Path $tools "cibseven-run"
    if (-not (Test-Path $cibDir)) {
        Write-Host "Lade CIB seven Run 3.0.0 ... (bitte warten)"
        Invoke-WebRequest -UseBasicParsing "https://artifacts.cibseven.org/repository/public/org/cibseven/bpm/run/cibseven-bpm-run/3.0.0/cibseven-bpm-run-3.0.0.zip" -OutFile "$tools\cib.zip"
        Expand-Archive "$tools\cib.zip" $cibDir -Force; Remove-Item "$tools\cib.zip"
    }
    $startBat = Get-ChildItem $cibDir -Recurse -Filter "start.bat" | Select-Object -First 1
    if (-not $startBat) { throw "start.bat in $cibDir nicht gefunden" }

    # 3. Engine starten, falls sie noch nicht laeuft (eigenes Fenster, offen lassen!)
    $laeuft = $false
    try { Invoke-RestMethod "$rest/engine" | Out-Null; $laeuft = $true } catch {}
    if (-not $laeuft) {
        Write-Host "Starte CIB seven in eigenem Fenster (offen lassen) ..."
        Start-Process cmd.exe -ArgumentList "/k", "`"$($startBat.FullName)`"" -WorkingDirectory $startBat.DirectoryName
        Write-Host "Warte auf die Engine (bis 3 Minuten) ..."
        for ($i = 0; $i -lt 60; $i++) {
            Start-Sleep 3
            try { Invoke-RestMethod "$rest/engine" | Out-Null; $laeuft = $true; break } catch {}
        }
        if (-not $laeuft) { throw "CIB seven antwortet nicht auf $rest" }
    }
    Write-Host "CIB seven laeuft, Version:" (Invoke-RestMethod "$rest/version").version -ForegroundColor Green

    # 4. Modelle aus diesem Repo-Ordner
    $modelle = Join-Path $repo "prozesse\team2"

    # 5. Alle 5 BPMN und 2 DMN in einem Deployment
    Push-Location $modelle
    $curlArgs = @("-s", "-X", "POST", "$rest/deployment/create",
                  "-F", "deployment-name=team2", "-F", "enable-duplicate-filtering=true")
    Get-ChildItem *.bpmn, *.dmn | ForEach-Object { $curlArgs += @("-F", "$($_.Name)=@$($_.Name)") }
    $antwort = curl.exe @curlArgs
    Pop-Location
    $prozesse = (Invoke-RestMethod "$rest/process-definition/count?latestVersion=true").count
    $dmn      = (Invoke-RestMethod "$rest/decision-definition/count?latestVersion=true").count
    Write-Host "Deployt: $prozesse Prozesse (erwartet mind. 5), $dmn DMN (erwartet mind. 2)"
    if ($prozesse -lt 5 -or $dmn -lt 2) { Write-Host "Antwort der Engine: $antwort" -ForegroundColor Yellow }

    # 6. Instanz ueber "Bestand manuell gemeldet" starten
    $body = @{
        messageName      = "PflegeApp_Bestandsmeldung_Team2"
        businessKey      = "PH-0001:TP-M"
        processVariables = @{
            pflegehaushaltId = @{ value = "PH-0001"; type = "String" }
            produktId        = @{ value = "TP-M";    type = "String" }
        }
        resultEnabled    = $true
    } | ConvertTo-Json -Depth 5
    $r = Invoke-RestMethod -Method Post "$rest/message" -ContentType "application/json" -Body $body
    $pi = $r[0].processInstance.id
    Write-Host "Instanz gestartet: $pi (Business Key PH-0001:TP-M)" -ForegroundColor Green

    # 7. Wo steht die Instanz? Ohne Worker wartet sie an der ersten External Task.
    Invoke-RestMethod "$rest/external-task?processInstanceId=$pi" |
        ForEach-Object { Write-Host "Wartet an External Task: $($_.activityId)  (Topic $($_.topicName))" }
    Write-Host "Cockpit: http://localhost:8080"
}
catch {
    Write-Host ""
    Write-Host "FEHLER: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Stop-Transcript | Out-Null
    Write-Host ""
    Write-Host "Ergebnis auf dem Desktop: cib_ergebnis.txt" -ForegroundColor Green
    Read-Host "Enter druecken zum Schliessen (das CIB-seven-Fenster offen lassen)"
}

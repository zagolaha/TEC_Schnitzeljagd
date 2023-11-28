Write-Host "[[ TEC-SCHNITZELJAGD BEARBEITUNGSTOOL ]]"
Write-Host "(1) Leaderboard-Eintrag löschen"
Write-Host "(2) Frage bearbeiten"
Write-Host "(3) Quiz-Dauer bearbeiten"

$number = Read-Host "Gewünschte Operation (als Zahl) eingeben"
$address = "https://127.0.0.1:5000"

<#
    TODO:
    - [X] Add ID column to questions (and leaderboard while you're at it)
    - [X] Daten zuverlässig anzeigen
    - [X] Fragen "bearbeit-bar" machen
#>

switch ([int]$number) {
    1 {
        $res = Invoke-WebRequest -Uri "$($address)/getLeaderboardAsJson"
        $res | ConvertFrom-Json | Out-Host
        $id = Read-Host "Den Eintrag mit welcher ID willst Du löschen?"
        $res = Invoke-WebRequest -Uri "$($address)/delete/$([int]$id)" -Method Delete
        if ($res.StatusCode -eq 200) {
            Write-Host "Löschen erfolgreich" -ForegroundColor Green
        } else {
            Write-Warning "Fehler beim Löschen"
        }
    }
    2 {
        $res = Invoke-WebRequest -Uri "$($address)/frage"
        $content = $res.Content | ConvertFrom-Json
        for ($i = 0; $i -lt $content.Count; $i++) {
            $content[$i] | Add-Member -MemberType NoteProperty -Name "ID" -Value $i
        }
        $content | Out-Host
        Write-Host "(1) Eintrag hinzufügen"
        Write-Host "(2) Eintrag löschen"
        Write-Host "(3) Eintrag bearbeiten"
        $number = Read-Host "Was soll ausgeführt werden?"
        switch ([int]$number) {
            1 {
                # Erstellen
                $question = Read-Host "Gib die Frage ein"
                $0 = Read-Host "Antwortmöglichkeit 1"
                $1 = Read-Host "Antwortmöglichkeit 2"
                $2 = Read-Host "Antwortmöglichkeit 3"
                $3 = Read-Host "Antwortmöglichkeit 4"
                $solution = Read-Host "Welche ist die Richtige (1-4)?"
                $obj = @{
                    "question" = $question
                    "answers" = @($0, $1, $2, $3)
                    "solution" = [int]$solution - 1
                }
                $obj | Out-Host
                $confirm = Read-Host "Darf die Frage so gespeichert werden (0: nein, 1: ja)?"
                if ([int]$confirm -eq 1) {
                    $res = Invoke-WebRequest -Uri "$($address)/frage" -Method Put -Body ($obj | ConvertTo-Json) -ContentType "application/json"
                    if ($res.StatusCode -eq 200) {
                        Write-Host "Erstellen erfolgreich" -ForegroundColor Green
                    } else {
                        Write-Warning "Fehler beim Erstellen"
                    }
                } else {
                    Write-Warning "Vorgang wird abgebrochen..."
                }
            }
            2 {
                # Löschen
                $id = Read-Host "Die Frage mit welcher ID soll gelöscht werden?"
                $body = @{value=[int]$id} | ConvertTo-Json
                $res = Invoke-WebRequest -Uri "$($address)/frage" -Method Delete -Body $body -ContentType "application/json"
                if ($res.StatusCode -eq 200) {
                    Write-Host "Löschen erfolgreich" -ForegroundColor Green
                } else {
                    Write-Warning "Fehler beim Löschen"
                }
            }
            3 {
                # Ändern
                $id = Read-Host "Der Eintrag mit welcher ID soll geändert werden?"
                Write-Host "(1) Frage ändern"
                Write-Host "(2) Antwort #1 ändern"
                Write-Host "(3) Antwort #2 ändern"
                Write-Host "(4) Antwort #3 ändern"
                Write-Host "(5) Antwort #4 ändern"
                Write-Host "(6) Lösung ändern"
                $number = Read-Host "Was soll ausgeführt werden?"
                switch ([int]$number) {
                    1 {
                        Write-Host "Bisher: $($content[[int]$id].question)"
                        $new = Read-Host "Wie soll die neue Frage lauten?"
                        $body = @{type="question";index=[int]$id;content=$new} | ConvertTo-Json
                        $res = Invoke-WebRequest -Uri "$($address)/frage" -Method Patch -Body $body -ContentType "application/json"
                        if ($res.StatusCode -eq 200) {
                            Write-Host "Änderung erfolgreich" -ForegroundColor Green
                        } else {
                            Write-Warning "Fehler beim Ändern der Frage"
                        }
                    }
                    {$_ -in 2,3,4,5} {
                        # Antwort ändern
                        Write-Host "Bisher: $($content[[int]$id].answers[[int]$_])" # FIXME
                        $new = Read-Host "Wie soll die neue Antwort lauten?"
                        $body = @{type="answer";index=[int]$id;number=([int]$_-2);content=$new} | ConvertTo-Json
                        $res = Invoke-WebRequest -Uri "$($address)/frage" -Method Patch -Body $body -ContentType "application/json"
                        if ($res.StatusCode -eq 200) {
                            Write-Host "Änderung erfolgreich" -ForegroundColor Green
                        } else {
                            Write-Warning "Fehler beim Ändern der Antwort"
                        }
                    }
                    6 {
                        # Lösung ändern
                        Write-Host "Bisher: $($content[[int]$id].solution)"
                        # TODO: Vllt alle Antworten anzeigen?
                        $new = Read-Host "Welche Antwort (0-3) ist die Richtige?"
                        $body = @{type="solution";index=[int]$id;content=[int]$new} | ConvertTo-Json
                        $res = Invoke-WebRequest -Uri "$($address)/frage" -Method Patch -Body $body -ContentType "application/json"
                        if ($res.StatusCode -eq 200) {
                            Write-Host "Änderung erfolgreich" -ForegroundColor Green
                        } else {
                            Write-Warning "Fehler beim Ändern der Lösung"
                        }
                    }
                    Default {
                        Write-Warning "Invalider Input."
                    }
                }
            }
            default {
                Write-Warning "Invalider Input."
            }
        }
    }
    3 {
        $currentTime = Invoke-WebRequest -Uri "$($address)/time"
        Write-Host "Derzeitige Dauer beträgt $($currentTime.Content.Trim()) Minuten"
        $newTime = Read-Host "Neue Zeit (in min)"
        $requestBody = @{value=[int]$newTime} | ConvertTo-Json
        $res = Invoke-WebRequest -Uri "$($address)/time" -Method Patch -Body $requestBody -ContentType "application/json"
        if ($res.StatusCode -eq 200) {
            Write-Host "Änderung erfolgreich" -ForegroundColor Green
        } else {
            Write-Warning "Fehler beim Ändern der Dauer"
        }
    }
    default {
        Write-Warning "Invalider Input."
    }
}

Write-Host "Skript wird beendet..."
CMD /c PAUSE

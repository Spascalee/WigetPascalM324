# Tagebbbuch

[![CI](https://github.com/Spascalee/WigetPascalM324/actions/workflows/ci.yml/badge.svg)](https://github.com/Spascalee/WigetPascalM324/actions/workflows/ci.yml)

Eine kleine Tagebuch-Webapplikation (Flask). Das Projekt zeigt einen vollständigen
DevOps-Ablauf für Modul 324: Anforderungen als Issues, GitHub Flow, automatische
Prüfungen vor Commit und Push, CI bei jedem Pull Request sowie automatische Releases
und Auslieferung auf Azure.

**Laufende Applikation:** https://tagebbbuch-m324-wiget-bcf8fshcaqd6fhee.austriaeast-01.azurewebsites.net

## Entwicklungsumgebung einrichten

Voraussetzungen: Python 3.12 oder neuer, Git, Visual Studio Code (empfohlen).

Einmalig nach dem Klonen (PowerShell, im Projektordner):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pre-commit install
```

`pre-commit install` richtet drei Git-Hooks ein (festgelegt in
`default_install_hook_types` in `.pre-commit-config.yaml`):

| Hook | Wann | Was passiert |
| --- | --- | --- |
| `pre-commit` | bei `git commit` | Dateien prüfen, Code mit **black** formatieren, mit **flake8** prüfen, Commits auf `main` verhindern |
| `commit-msg` | bei `git commit` | Commit-Message muss eine Issue nennen, z. B. `(#3)` |
| `pre-push` | bei `git push` | alle Tests mit **pytest** ausführen; schlägt ein Test fehl, wird nicht gepusht |

Formatiert black beim Commit eine Datei um, bricht der Commit ab. Die Datei mit
`git add` erneut hinzufügen und den Commit wiederholen.

Lokale Konfiguration: Datei `.env` im Projektordner anlegen (wird nicht eingecheckt):

```
PASSWORD="einLokalesTestpasswort"
```

App starten: `flask run` → http://127.0.0.1:5000

### Visual Studio Code

Der Ordner `.vscode` enthält die Projekteinstellungen:

- `extensions.json`: empfohlene Erweiterungen (Python, black, flake8, EditorConfig,
  GitHub Pull Requests, GitHub Actions). VS Code schlägt sie beim Öffnen vor.
- `settings.json`: nutzt automatisch `.venv`, formatiert beim Speichern mit black,
  aktiviert pytest im Test-Explorer.
- `tasks.json`: Aufgaben „App lokal starten", „Tests mit Coverage",
  „Alle pre-commit-Prüfungen" (Terminal → Aufgabe ausführen).
- `launch.json`: Konfiguration „Tagebbbuch debuggen" mit Haltepunkten (F5).

`.editorconfig` legt Zeichensatz, Zeilenenden und Einrückung für alle Editoren fest.

Manuelle Prüfungen:

```powershell
pre-commit run --all-files                  # alle Commit-Prüfungen
pytest --cov --cov-report=term-missing      # Tests mit Testabdeckung
```

## Arbeitsablauf (GitHub Flow)

1. Jede Änderung beginnt mit einer **Issue** (Vorlage „Anforderung" oder
   „Fehlermeldung"), mit Typ-Etikette, Meilenstein und Eintrag im Projekt-Board.
2. Von `main` einen Branch `feature/<issue>-<kurzname>` erstellen.
3. Zuerst den Testfall, dann die Umsetzung committen. Jede Commit-Message nennt
   die Issue (`#<nummer>`).
4. Branch pushen, Pull Request auf `main` mit `Closes #<nummer>` eröffnen.
5. Mergen, sobald die Checks grün sind. Die Issue wird dabei automatisch geschlossen.

`main` ist durch ein Ruleset geschützt: Änderungen nur per Pull Request, und die
Checks `lint` und `test` müssen grün sein. Direktes Pushen oder Löschen ist gesperrt.

## Tests und Continuous Integration

Der Workflow `.github/workflows/ci.yml` läuft bei jedem Pull Request auf `main`,
bei jedem Push auf `main` und als erster Schritt jedes Releases.

| Job | Prüfung |
| --- | --- |
| `lint` | Formatierung mit `black --check`, Code-Qualität mit `flake8` |
| `test` | alle Tests mit `pytest`, Testabdeckung mit `pytest-cov` (mindestens 90 %, sonst schlägt der Job fehl) |

Der Job `test` speichert `coverage.xml` und `test-results.xml` als Artefakt
„testberichte" (30 Tage) und zeigt die Testabdeckung in der Zusammenfassung des Laufs.

Lokal dieselbe Prüfung: `pytest --cov --cov-report=term-missing`

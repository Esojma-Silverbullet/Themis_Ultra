# aiobookoo-ultra

Unterstützt: **Bookoo Themis Ultra**

Dieses Repository stellt das asynchrone BLE-Protokoll der Themis Ultra bereit
und definiert genau ein Service-/Characteristic-Set (Ultra). Kompatible Wrapper
(`aiobookoo`) existieren nur für Altimporte; der einzig empfohlene Pfad ist
`aiobookoo_ultra`.

## Empfohlener Importpfad

```python
from aiobookoo_ultra import BookooScale
```

Ein Legacy-Kompatibilitätswrapper (`aiobookoo`) existiert nur, damit bestehende
Altimporte weiterlaufen. Neue Integrationen sollen ausschließlich
`aiobookoo_ultra` verwenden; Mini-/Legacy-Protokolle gehören nicht zu diesem
Paket.

## Installation

* Veröffentlichung (PyPI): `pip install aiobookoo-ultra`
* Aus Git-Tag (z. B. 0.2.0):\
  `pip install git+https://github.com/Esojma-Silverbullet/aiobookoo-Ultra.git@0.2.0`

Nach der Installation steht das Modul ohne weitere Anpassungen zur Verfügung;
weitere Framework-spezifische Logik ist bewusst nicht enthalten.

## Firmware-Kompatibilität

Version 0.2.0 unterstützt das von Bookoo am 12. August 2026 veröffentlichte
Protokoll für die Release-Firmware 4.0.0. Zusätzlich zu den laufenden Daten für
Gewicht, Timer, Flow und Batterie werden folgende Firmware-4-Funktionen
unterstützt:

* Pulvergewicht lesen und einstellen (`0.1` bis `999.0 g`)
* Ereignis- und Abschlussdaten des Automatikmodus lesen
* Waage ausschalten (nicht während des Ladens)

Die laufenden Gewichtswerte werden laut Herstellerprotokoll immer in Gramm
übertragen. Das Einheit-Byte beschreibt lediglich die Anzeigeeinheit der Waage.
Kalibrierung und automatische Stop-Bedingung werden nicht als
Home-Assistant-Bedienelemente vorgesehen.

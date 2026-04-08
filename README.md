# Bookoo Themis Ultra – Home Assistant Integration

This is a Home Assistant custom integration for the **Bookoo Themis Ultra** Bluetooth scale.

The integration provides:
- Weight sensor
- Flow rate sensor
- Timer duration sensor
- Battery level
- Control buttons (tare, start timer, stop timer, tare & start)

The integration is optimized for the **Ultra BLE protocol** and uses the
`aiobookoo-ultra` Python library, bundled in this repository.

---

## Installation (via HACS)

1. Open **HACS**
2. Go to **Integrations**
3. Add this repository as a **Custom Repository**
4. Install **Bookoo Themis Ultra**
5. Restart Home Assistant

The required Python dependency (`aiobookoo-ultra`) is included in this repository.

---

## Requirements

- Home Assistant with Bluetooth support
- Bluetooth Proxy (ESPHome recommended)
- Bookoo Themis Ultra scale

---

## Dokumentation (Deutsch)

### Installation (HACS)

1. **HACS** öffnen
2. **Integrationen** auswählen
3. Dieses Repository als **Custom Repository** hinzufügen
4. **Bookoo Themis Ultra** installieren
5. Home Assistant neu starten

Die Python-Bibliothek **aiobookoo-ultra** ist im Repository enthalten und wird
automatisch genutzt.

### Voraussetzungen

- Home Assistant mit Bluetooth-Unterstützung
- Bluetooth Proxy (ESPHome empfohlen)
- Bookoo Themis Ultra Waage

---

## Credits & Attribution

This project is based on earlier work by:
- **makerwolf** and contributors (original Bookoo integration)
- The Home Assistant community

All original work remains under its respective license.

---

## License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for details.

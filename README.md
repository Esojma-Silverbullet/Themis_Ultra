# Bookoo Themis Ultra – Home Assistant Integration

This is a Home Assistant custom integration for the **Bookoo Themis Ultra** Bluetooth scale.

The integration provides:
- Weight sensor
- Flow rate sensor
- Timer duration sensor
- Battery level
- Control buttons (tare, start timer, stop timer, tare & start)

The integration is optimized for the **Ultra BLE protocol** and uses the
`aiobookoo-ultra` Python library.

---

## Installation (via HACS)

1. Open **HACS**
2. Go to **Integrations**
3. Add this repository as a **Custom Repository**
4. Install **Bookoo Themis Ultra**
5. Restart Home Assistant

The required Python dependency (`aiobookoo-ultra`) is installed automatically.

---

## Requirements

- Home Assistant with Bluetooth support
- Bluetooth Proxy (ESPHome recommended)
- Bookoo Themis Ultra scale

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

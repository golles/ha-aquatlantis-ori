# Aquatlantis Ori Integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Repo stars][stars-shield]][stars]
[![License][license-shield]](LICENSE)
[![GitHub Activity][commits-shield]][commits]
[![Code coverage][codecov-shield]][codecov]
[![hacs][hacs-shield]][hacs]
[![installs][hacs-installs-shield]][ha-active-installation-badges]
[![Project Maintenance][maintenance-shield]][maintainer]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

A Home Assistant custom integration for controlling Aquatlantis Ori smart controllers. Monitor sensors, and control lighting.

> [!CAUTION]
> This project is a personal, unofficial effort and is not affiliated with Aquatlantis. It was created to learn and experiment with controlling my own aquarium.
> The Ori API was reverse-engineered for this purpose, and functionality may break at any time if Aquatlantis changes their API.
> I'm not responsible for any damage or issues that may arise from using this client. Use at your own risk!

## Supported Devices

This integration supports the **Aquatlantis Ori smart controller** and its compatible accessories.

### Light Compatibility

| Light Type | Status              | Notes                            |
| ---------- | ------------------- | -------------------------------- |
| RGBW Ultra | ✅ Fully Supported  | Complete RGBW control            |
| Easy LED   | ⚠️ Likely Supported | Should work but not fully tested |
| UV Ultra   | ❌ Not Supported    | Currently not compatible         |

### Sensor Compatibility

| Sensor Type              | Status           | Notes                        |
| ------------------------ | ---------------- | ---------------------------- |
| No sensor                | ✅ Supported     | Basic light control          |
| Temperature sensor       | ✅ Supported     | Water temperature monitoring |
| Air temperature/humidity | ❌ Not Supported | Currently not compatible     |

> [!TIP]
> If you own a device that isn't fully supported, please [open an issue](https://github.com/golles/ha-aquatlantis-ori/issues) and let me know. With your help, I will try to add support for it.

## Installation

### Method 1: HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the "+" button
4. Search for "Aquatlantis Ori"
5. Click "Download" and restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from [GitHub releases](https://github.com/golles/ha-aquatlantis-ori/releases)
2. Extract the files to your Home Assistant `custom_components` directory:
   ```
   config/
   └── custom_components/
       └── ori/
           ├── __init__.py
           ├── manifest.json
           └── ... (all other files)
   ```
3. Restart Home Assistant

## Configuration

Configuration is done entirely through the Home Assistant UI - no YAML editing required!

### Quick Start

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for **"Aquatlantis Ori"**
4. Follow the setup wizard to connect your device

The integration will automatically discover and configure all available entities based on your Ori device's capabilities.

![Demo dashboard](/img/demo_dashboard.png)

## Available Entities

Once configured, the integration provides various entities to monitor and control your aquarium:

### Light Entity

The main light control entity with full RGBW support and brightness control.

- **Effects**: Manual, automatic, and dynamic mode
- **Features**: On/off, brightness (0-100%), RGBW colors (0-255 each)
- **Modes**:
  - On/off only when automatic or dynamic mode is enabled
  - RGBW when manual mode is selected

### Button Entities

**Preset Buttons (1-4)**

Quick-access buttons for your saved color presets from the Ori app.

- Only active in manual mode with dynamic mode disabled
- Each button contains RGBW values in attributes
- Instantly applies the preset when pressed

### Control Entities

**Manual Controls** - Individual intensity and RGBW number entities (disabled by default)

### Sensor Entities

#### Core Sensors

- **Device Status** (binary) - Online/offline detection (~5 min delay)
- **Water Temperature** - Current temperature reading (5-min updates)
- **Water Temperature Problem** (binary) - Temperature threshold alerts

#### Diagnostic Sensors (disabled by default)

- **Bluetooth MAC Address** - Device identifier
- **IP Address** - Network location with port in attributes
- **WiFi Signal Strength** - Connection quality
- **SSID** - Connected network name
- **Uptime** - Device runtime

### Update Entity

**Firmware Update**

- Automatic firmware update detection
- Download URL and filename in attributes
- Update through Ori app (not directly through HA)

## Available services

The integration provides a custom service to set complex light schedules.

## Usage Examples

### Basic Light Control

Control your light like any other Home Assistant light:

```yaml
# Change the light mode (effect)
action: light.turn_on
target:
  entity_id: light.aquarium_light
data:
  effect: manual # automatic or dynamic

# Turn on with warm white at 80% brightness
action: light.turn_on
target:
  entity_id: light.aquarium_light
data:
  brightness_pct: 80
  rgbw_color: [0, 0, 0, 255]  # Pure white

# Set custom color (purple)
action: light.turn_on
target:
  entity_id: light.aquarium_light
data:
  brightness_pct: 60
  rgbw_color: [128, 0, 128, 0]  # Purple

# Turn off the light
action: light.turn_off
target:
  entity_id: light.aquarium_light
```

### Automation Examples

```yaml
# Turn on aquarium light at sunrise
automation:
  - alias: Aquarium Morning Light
    trigger:
      platform: sun
      event: sunrise
    action:
      - alias: Make sure the light is in manual mode
        action: light.turn_on
        data:
          effect: manual
        target:
          entity_id: light.aquarium_light

      - alias: Set light to warm sunrise colors
        action: light.turn_on
        target:
          entity_id: light.aquarium_light
        data:
          brightness_pct: 30
          rgbw_color: [255, 100, 50, 100]

# Alert when water temperature is too high
automation:
  - alias: Aquarium Temperature Alert
    trigger:
      platform: state
      entity_id: binary_sensor.aquarium_water_temperature_problem
      to: "on"
    action:
      - action: notify.mobile_app_your_phone
        data:
          title: Aquarium Alert
          message: Water temperature is outside normal range!
```

### Service example: Set schedule

You can set a complex light schedule using the `ori.set_schedule` service. The schedule consists of as many entries you like, each defined by a start time, intensity and values for different channels.
The format for a schedule entry is as follows: `hour,minute,intensity,red,green,blue,white`

```yaml
action: ori.set_schedule
data:
  device_id: b12345c1dca0996b9619e7df53a42ad3
  schedule:
    - 8,59,0,0,0,0,0 # time: 08:59, intensity: 0, red: 0, green: 0, blue: 0, white: 0
    - 9,0,15,20,20,25,30 # time: 09:00, intensity: 15, red: 20, green: 20, blue: 25, white: 30
    - 10,0,40,30,30,35,50 # time: 10:00, intensity: 40, red: 30, green: 30, blue: 35, white: 50
    - 12,0,80,35,35,45,80 # time: 12:00, intensity: 80, red: 35, green: 35, blue: 45, white: 80
    - 15,0,70,30,30,40,70 # time: 15:00, intensity: 70, red: 30, green: 30, blue: 40, white: 70
    - 17,0,40,20,20,25,40 # time: 17:00, intensity: 40, red: 20, green: 20, blue: 25, white: 40
    - 18,0,0,0,0,0,0 # time: 18:00, intensity: 0, red: 0, green: 0, blue: 0, white: 0
```

## Troubleshooting

### Debug Logging

To collect detailed logs for troubleshooting:

#### Method 1: Integration Debug (Recommended)

1. Go to **Settings** → **Devices & Services** → **Aquatlantis Ori**
2. Click the 3 dots menu in the top right corner
3. Click **"Enable debug logging"**
4. Reproduce the issue
5. Click **"Stop debug logging"** to download the log file

#### Method 2: Logger Configuration

Add this to your `configuration.yaml`:

```yaml
logger:
  default: warn
  logs:
    aquatlantis_ori: debug
    custom_components.ori: debug
```

More information: [Home Assistant Logger Integration](https://www.home-assistant.io/integrations/logger)

### Getting Help

1. Check the [existing issues](https://github.com/golles/ha-aquatlantis-ori/issues) first
2. If you find a new issue, [create a detailed bug report](https://github.com/golles/ha-aquatlantis-ori/issues/new)
3. Include debug logs and your device model information

## Contributing

Contributions are welcome! This project is open source and benefits from community involvement.

### How to Contribute

1. **Report Issues**: Found a bug or have a feature request? [Open an issue](https://github.com/golles/ha-aquatlantis-ori/issues)
2. **Code Contributions**: Check the [Contribution Guidelines](CONTRIBUTING.md) for development setup
3. **Device Support**: Help expand device compatibility by testing with your hardware

### Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development setup instructions.

[buymecoffee]: https://www.buymeacoffee.com/golles
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[codecov]: https://app.codecov.io/gh/golles/ha-aquatlantis-ori
[codecov-shield]: https://img.shields.io/codecov/c/github/golles/ha-aquatlantis-ori?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/golles/ha-aquatlantis-ori.svg?style=for-the-badge
[commits]: https://github.com/golles/ha-aquatlantis-ori/commits/main
[hacs]: https://github.com/custom-components/hacs
[hacs-shield]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[ha-active-installation-badges]: https://github.com/golles/ha-active-installation-badges
[hacs-installs-shield]: https://raw.githubusercontent.com/golles/ha-active-installation-badges/main/badges/ori.svg
[license-shield]: https://img.shields.io/github/license/golles/ha-aquatlantis-ori.svg?style=for-the-badge
[maintainer]: https://github.com/golles
[maintenance-shield]: https://img.shields.io/badge/maintainer-golles-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/golles/ha-aquatlantis-ori.svg?style=for-the-badge
[releases]: https://github.com/golles/ha-aquatlantis-ori/releases
[stars-shield]: https://img.shields.io/github/stars/golles/ha-aquatlantis-ori?style=for-the-badge
[stars]: https://github.com/golles/ha-aquatlantis-ori/stargazers

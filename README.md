# Aquatlantis Ori

[![GitHub Release][releases-shield]][releases]
[![GitHub Repo stars][stars-shield]][stars]
[![License][license-shield]](LICENSE)
[![GitHub Activity][commits-shield]][commits]
[![Code coverage][codecov-shield]][codecov]
[![hacs][hacs-shield]][hacs]
[![installs][hacs-installs-shield]][ha-active-installation-badges]
[![Project Maintenance][maintenance-shield]][maintainer]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

Aquatlantis Ori custom component for Home Assistant.

> [!CAUTION]
> This project is a personal, unofficial effort and is not affiliated with Aquatlantis. It was created to learn and experiment with controlling my own aquarium.
> The Ori API was reverse-engineered for this purpose, and functionality may break at any time if Aquatlantis changes their API.
> I'm not responsible for any damage or issues that may arise from using this client. Use at your own risk!

## Installation

### HACS installation

The most convenient method for installing this custom component is via HACS. Simply search for the name, and you should be able to locate and install it seamlessly.

### Manual installation guide:

1. Utilize your preferred tool to access the directory in your Home Assistant (HA) configuration, where you can locate the `configuration.yaml` file.
2. Should there be no existing `custom_components` directory, you must create one.
3. Inside the newly created `custom_components` directory, generate a new directory named `ori`.
4. Retrieve and download all files from the `custom_components/ori/` directory in this repository.
5. Place the downloaded files into the newly created `ori` directory.
6. Restart Home Assistant.

## Configuration is done in the UI

Within the HA user interface, navigate to "Configuration" -> "Integrations", click the "+" button, and search for "Aquatlantis Ori" to add the integration.

## Sensors

![Demo dashboard](/img/demo_dashboard.png)

### Binary Sensors

**Status**

The status sensor indicates whether the device is online or offline, it takes around 5 minutes before it is detected as offline.

**Water temperature**

The water temperature sensor (problem) is based on the water temperature thresholds set in the Aquatlantis Ori app. If the water temperature exceeds the maximum or falls below the minimum threshold, it will be marked as a problem sensor. The attributes of this sensor include the current water temperature, the minimum and maximum values, and whether Ori app notifications are enabled. Note that this sensor is only available when a temperature sensor is connected to the Ori device.

### Buttons

These are the presets that can be set in the Aquatlantis Ori app. They can be used to quickly set the light to a specific color.

**Preset [1-4]**

These buttons allow you to set the aquarium light to predefined color presets. Each preset corresponds to a specific RGBW color configuration, which can be customized in the Aquatlantis Ori app. The attributes of each preset include the red, green, blue, and white values of the preset.

Note that these buttons will only change the light when the light mode is set to manual and when dynamic mode is disabled. You can use these buttons to change the values and they will be applied when the light mode is set to manual.

### Light

The light entity represents the aquarium light and can be controlled through Home Assistant. It supports brightness and RGBW color settings.

The light entity can be controlled using the below action, like any light in Home Assistant. The RGBW values are represented as a list of four integers, where each integer corresponds to the red, green, blue, and white colors (0-255). The intensity can be set as brightness percentage (0-100).

```yaml
action: light.turn_on
target:
  entity_id: light.aquarium_light
data:
  brightness_pct: 80
  rgbw_color:
    - 0
    - 0
    - 0
    - 255
```

Note that the light entity will only support on/off when automatic mode or dynamic mode is enabled. When manual mode is enabled and dynamic mode is disabled, the light entity will support brightness and RGBW color settings.

### Numbers

**Intensity/Red/Green/Blue/White**

These numbers represent the intensity and RGBW values of the light. They can be used to set the color of the light in Home Assistant.
Since it is suggested to control the light through the light entity, these numbers are disabled by default.

Note that these numbers will only be available when the light mode is set to manual and when dynamic mode is disabled.

### Selects

**Dynamic mode**

This controls the dynamic mode. The dynamic mode is also known as the lightning effect, which can be turned on or off.

**Light mode**

This controls the light mode. The light mode can be set to manual or automatic. In manual mode, you can control the light using the light entity (or the numbers), while in automatic mode, the light will follow the settings defined in the Aquatlantis Ori app.

### Sensors

**Bluetooth mac address**

Diagnostic sensor that provides the Bluetooth MAC address of the Ori device, disabled by default.

**IP address**

Diagnostic sensor that provides the IP address and port (attribute) of the Ori device, disabled by default.

**Wifi signal**

Diagnostic sensor that provides the Wifi signal strength of the Ori device, disabled by default.

**SSID**

Diagnostic sensor that provides the SSID of the Wifi network the Ori device is connected to, disabled by default.

**Uptime**

Diagnostic sensor that provides the uptime of the Ori device, disabled by default.

**Water temperature**

Sensor that provides the current temperature reading from the Ori device. The temperature is updated every 5 minutes. Note that this sensor is only available when a temperature sensor is connected to the Ori device.

### Update

**Firmware**

The integration will automatically check for firmware updates and notify you if a new version is available. You can then update the firmware in the Aquatlantis app. Latest firmware filename and download URL are available in the attributes.

## Collect logs

To activate the debug log necessary for issue reporting, follow these steps:

1. Go to "Configuration" -> "Integrations" -> "Aquatlantis Ori" within the Home Assistant interface.
2. On the left side, locate the "Enable debug logging" button and click on it.
3. Once you collected enough information, Stop debug logging, this will download the log file as well.
4. Share the log file in an issue.

Additionally, logging for this component can be enabled by configuring the logger in Home Assistant with the following steps:

```yaml
logger:
  default: warn
  logs:
    aquatlantis_ori: debug
    custom_components.ori: debug
```

More info can be found on the [Home Assistant logger integration page](https://www.home-assistant.io/integrations/logger)

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

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

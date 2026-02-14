# Clouding.io Integration for Home Assistant

[![Maintenair : bastgau](https://img.shields.io/badge/maintener-bastgau-orange?logo=github&logoColor=%23959da5&labelColor=%232d333a)](https://github.com/bastgau)
[![Made with Python](https://img.shields.io/badge/Made_with-Python-blue?style=flat&logo=python&logoColor=%23959da5&labelColor=%232d333a)](https://www.python.org/)
[![Made for Home Assistant](https://img.shields.io/badge/Made_for-Homeassistant-blue?style=flat&logo=homeassistant&logoColor=%23959da5&labelColor=%232d333a)](https://www.home-assistant.io/)
[![GitHub Release](https://img.shields.io/github/v/release/bastgau/ha-clouding?logo=github&logoColor=%23959da5&labelColor=%232d333a&color=%230e80c0)](https://github.com/bastgau/ha-clouding/releases)
[![HACS validation](https://github.com/bastgau/ha-clouding/actions/workflows/validate-for-hacs.yml/badge.svg)](https://github.com/bastgau/ha-clouding/actions/workflows/validate-for-hacs.yml)
[![HASSFEST validation](https://github.com/bastgau/ha-clouding/actions/workflows/validate-with-hassfest.yml/badge.svg)](https://github.com/bastgau/ha-clouding/actions/workflows/validate-with-hassfest.yml)

<p align="center" width="100%">
    <img src="https://brands.home-assistant.io/_/clouding/logo.png">
</p>

## Description

This integration lets you monitor and control your [Clouding.io](https://www.clouding.io) cloud instances directly from **Home Assistant**. Automate server management, get real-time status updates, and trigger actions based on your cloud infrastructure, all from your Home Assistant interface.

## Features

### Services

Manage your [Clouding.io](https://www.clouding.io)  servers with these services:

- **Start Server**: Power on your instance.
- **Stop Server**: Shut down your instance gracefully.
- **Hard Reboot Server**: Forcefully reboot your instance.
- **Reboot Server**: Reboot your instance gracefully.
- **Archive Server**: Archive your instance to save resources.
- **Unarchive Server**: Restore an archived instance to active status.

### Sensors

Track your Clouding.io instances with these real-time sensors:

- **Creation Date**: When the instance was created.
- **DNS Address**: The DNS address assigned to the instance.
- **Flavor**: The instance type (CPU, RAM, and storage configuration).
- **Hostname**: The hostname of the instance.
- **Name**: The custom name of the instance.
- **Power State**: Current power status (running, stopped, etc.).
- **Public IP**: The public IP address of the instance.
- **RAM**: Amount of RAM allocated to the instance.
- **SSD**: Amount of SSD storage allocated.
- **Status**: Overall status of the instance (active, archived, etc.).
- **VCores**: Number of virtual CPU cores allocated.

## Translation

The integration is currently translated in few langages :

- English

## Installation

### Installation via HACS

1. Add this repository as a custom repository to HACS:

[![Add Repository](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=bastgau&repository=ha-clouding&category=Integration)

2. Use HACS to install the integration.
3. Restart Home Assistant.
4. Set up the integration using the UI:

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=clouding)


### Manual Installation

1. Download the integration files from the GitHub repository.
2. Place the integration folder in the custom_components directory of Home Assistant.
3. Restart Home Assistant.
4. Set up the integration using the UI:

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=clouding)

## Debugging

It is possible to show the info and debug logs for the Clouding integration, to do this you need to enable logging in the configuration.yaml, example below:

```
logger:
  default: warning
  logs:
    custom_components.clouding: debug
```

Logs do not remove sensitive information so careful what you share, check what you are about to share and blank identifying information.

## Frequently Asked Questions

### How do I configure the refresh frequency?

By default, the data is updated every 5 minutes. You can configure a different frequency as explained on the following [page](docs/guide-configuring-refresh.md).

## Support & Contributions

If you encounter any issues or wish to contribute to improving this integration, feel free to open an issue or a pull request on the GitHub repository.

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/bastgau)

Enjoy!

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=bastgau/ha-clouding&type=Date)](https://www.star-history.com/#bastgau/ha-clouding&Date)

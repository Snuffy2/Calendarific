# Calendarific
[![GitHub Release](https://img.shields.io/github/release/Snuffy2/Calendarific.svg?style=for-the-badge)](https://github.com/Snuffy2/Calendarific/releases)
[![GitHub Release Date](https://img.shields.io/github/release-date/Snuffy2/Calendarific?label=Last%20Release&style=for-the-badge)](#places)
[![GitHub Commit Activity](https://img.shields.io/github/commit-activity/y/Snuffy2/Calendarific.svg?style=for-the-badge)](https://github.com/Snuffy2/Calendarific/commits/master)
[![GitHub last commit](https://img.shields.io/github/last-commit/Snuffy2/Calendarific?style=for-the-badge)](#places)
[![License](https://img.shields.io/github/license/Snuffy2/Calendarific?color=blue&style=for-the-badge)](LICENSE)<br/>
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/Snuffy2/Calendarific/hacs_validate.yml?branch=main&style=for-the-badge)](#calendarific)<br/>


The 'Calendarific' component is a Home Assistant custom sensor which counts down to public holidays and observances, by querying the Calendarific api

State Returned:
* The number of days remaining to the next occurance.

Attributes (both are provided by the Calendarific api):
* date:  The next date of the holiday (formatted by date_format configuration option if set)
* description: The description of the holiday.

## Table of Contents

* [Installation](#installation)
  + [Manual Installation](#manual-installation)
  + [Installation via HACS](#installation-via-hacs)
* [Platform Configuration](#platform-configuration)
  + [Platform Configuration Parameters](#platform-configuration-parameters)
* [Sensor Configuration](#sensor-configuration)
  + [Sensor Configuration Parameters](#sensor-configuration-parameters)

## Installation

### MANUAL INSTALLATION

1. Download the `calendarific.zip` file from the 
   [latest release](https://github.com/Snuffy2/calendarific/releases/latest).
2. Unpack the release and copy the `custom_components/calendarific` directory
   into the `custom_components` directory of your Home Assistant
   installation.
3. Configure the `calendarific` platform
4. Restart Home Assistant.
5. Configure sensors either in the configuration.yaml or by using the integrations page

### INSTALLATION VIA HACS

1. Ensure that [HACS](https://custom-components.github.io/hacs/) is installed.
2. Search for and install the "calendarific" integration.
3. Configure the `calendarific` platform.
4. Restart Home Assistant.
5. Configure sensors either in the configuration.yaml or by using the integrations page

## Platform Configuration

You will need an API key from Calendarific.com Go to the [sign up page](https://calendarific.com/signup) and open a new account.  A free tier account is limited to 1000 api calls per month.  This integration will make two calls per day (and two on home assistant start)

### The Calendarific platform MUST be configured in the configuration.yaml file.

```yaml
# Example configuration.yaml platform entry
calendarific:
  api_key: YOUR_API_KEY
  country: GB
  state: GB-WLS
```
### Platform configuration parameters
|Attribute |Optional|Description
|:----------|----------|------------
| `api_key` | No | your api key from calendarific.com
| `country` | No | your country code [here is a list of supported countries](https://calendarific.com/supported-countries)
| `state` | Yes | your state code (ISO 3166-2 subdivision code) [[USA](https://en.wikipedia.org/wiki/ISO_3166-2:US)] [[UK](https://en.wikipedia.org/wiki/ISO_3166-2:GB)] _note the state code is for the country in the uk (counties not supported) or the state in the us._   If omitted, only national holidays will be displayed

## Sensor Configuration

Individual sensors can be configured using Config flow or in configuration.yaml:


### Config Flow

In Configuration/Integrations click on the + button, select Calendarific and configure the options on the form (The available holidays will automatically appear on the list if the platform was configured correctly in the above step).
### configuration.yaml

Add `calendarific` sensor in your `configuration.yaml`. The following example adds two sensors - New Year's Day and Christmas Day _(Note that these must be entered EXACTLY as they are on the Calendarific server)_
```yaml
# Example configuration.yaml sensor entry
sensor:
  - platform: calendarific
    holiday: New Year's Day
  - platform: calendarific
    holiday: Christmas Day
```

### Sensor Configuration Parameters
|Attribute |Optional|Description
|:----------|----------|------------
| `holiday` | No | Name of holiday provided by calendarific api
| `name` | Yes | Friendly name **Default**: Holiday name
| `icon_normal` | Yes | Default icon **Default**:  `mdi:calendar-blank`
| `icon_today` | Yes | Icon if the holiday is today **Default**: `mdi:calendar-star`
| `days_as_soon` | Yes | Days in advance to display the icon defined in `icon_soon` **Default**: 1
| `icon_soon` | Yes | Icon if the holiday is 'soon' **Default**: `mdi:calendar`
| `date_format` | Yes | formats the returned date **Default**: '%Y-%m-%d' _for reference, see [http://strftime.org/](http://strftime.org/)_

# Calendarific
[![GitHub Release](https://img.shields.io/github/release/Snuffy2/Calendarific.svg?style=for-the-badge)](https://github.com/Snuffy2/Calendarific/releases)
[![GitHub Release Date](https://img.shields.io/github/release-date/Snuffy2/Calendarific?label=Last%20Release&style=for-the-badge)](#places)
[![GitHub Commit Activity](https://img.shields.io/github/commit-activity/y/Snuffy2/Calendarific.svg?style=for-the-badge)](https://github.com/Snuffy2/Calendarific/commits/master)
[![GitHub last commit](https://img.shields.io/github/last-commit/Snuffy2/Calendarific?style=for-the-badge)](#places)
[![License](https://img.shields.io/github/license/Snuffy2/Calendarific?color=blue&style=for-the-badge)](LICENSE)<br/>
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/Snuffy2/Calendarific/hacs_validate.yml?branch=main&style=for-the-badge)](#calendarific)<br/>


The `Calendarific` component is a Home Assistant custom sensor which counts down to public holidays and observances, by querying the Calendarific api

#### State Returned
* The number of days remaining to the next occurance.

#### Attributes (both are provided by the Calendarific api):
* date:  The next date of the holiday (formatted by date_format configuration option if set)
* description: The description of the holiday.

## Table of Contents

* [Installation](#installation)
  + [Installation via HACS](#hacs-recommended)
  + [Manual Installation](#manual)
* [Platfor Configuration](#platform-configuration)
  + [Platform Configuration Parameters](#platform-configuration-parameters)
* [Sensor Configuration](#sensor-configuration)
  + [Sensor Configuration Parameters](#sensor-configuration-parameters)

## Installation
### HACS *(recommended)*
1. Ensure that [HACS](https://hacs.xyz/) is installed
1. [Click Here](https://my.home-assistant.io/redirect/hacs_repository/?owner=custom-components&repository=places) to directly open `Calendarific` in HACS **or**<br/>
  a. Navigate to HACS<br/>
  b. Click `+ Explore & Download Repositories`<br/>
  c. Find the `Calendarific` integration <br/>
1. Click `Download`
1. Restart Home Assistant
1. See [Configuration](#configuration) below

<details>
<summary><h3>Manual</h3></summary>

You probably <u>do not</u> want to do this! Use the HACS method above unless you know what you are doing and have a good reason as to why you are installing manually

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`)
1. If you do not have a `custom_components` directory there, you need to create it
1. In the `custom_components` directory create a new folder called `calendarific`
1. Download the `calendarific.zip` file from the [latest release](https://github.com/Snuffy2/calendarific/releases/latest).
1. Unpack the release
1. Place _all_ the files from the `custom_components/places/` directory in this repository into the new directory you created
1. Restart Home Assistant
1. See [Configuration](#configuration) below

</details>

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
### Configuration Parameters
|Attribute |Required|Description
|:----------|----------|------------
| `api_key` | Yes | your api key from calendarific.com
| `country` | Yes | your country code [here is a list of supported countries](https://calendarific.com/supported-countries)
| `state` | No | your state code (ISO 3166-2 subdivision code) [[USA](https://en.wikipedia.org/wiki/ISO_3166-2:US)] [[UK](https://en.wikipedia.org/wiki/ISO_3166-2:GB)] _note the state code is for the country in the uk (counties not supported) or the state in the us._   If omitted, only national holidays will be displayed

## Sensor Configuration

In Configuration/Integrations click on the + button, select Calendarific and configure the options on the form (The available holidays will automatically appear on the list if the platform was configured correctly in the above step).

### Sensor Configuration Parameters
|Attribute |Required|Description
|:----------|----------|------------
| `holiday` | Yes | Name of holiday provided by calendarific api
| `name` | No | Friendly name **Default**: Holiday name
| `icon_normal` | No | Default icon **Default**:  `mdi:calendar-blank`
| `icon_today` | No | Icon if the holiday is today **Default**: `mdi:calendar-star`
| `days_as_soon` | No | Days in advance to display the icon defined in `icon_soon` **Default**: 1
| `icon_soon` | No | Icon if the holiday is 'soon' **Default**: `mdi:calendar`
| `date_format` | No | Format the returned date **Default**: `%x` (Locale’s appropriate date representation) _for reference, see [http://strftime.org/](http://strftime.org/)_


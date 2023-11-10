# Calendarific
[![GitHub Release](https://img.shields.io/github/release/Snuffy2/Calendarific.svg?style=for-the-badge)](https://github.com/Snuffy2/Calendarific/releases)
[![GitHub Release Date](https://img.shields.io/github/release-date/Snuffy2/Calendarific?label=Last%20Release&style=for-the-badge)](#places)
[![GitHub Commit Activity](https://img.shields.io/github/commit-activity/y/Snuffy2/Calendarific.svg?style=for-the-badge)](https://github.com/Snuffy2/Calendarific/commits/master)
[![GitHub last commit](https://img.shields.io/github/last-commit/Snuffy2/Calendarific?style=for-the-badge)](#places)
[![License](https://img.shields.io/github/license/Snuffy2/Calendarific?color=blue&style=for-the-badge)](LICENSE)<br/>
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/Snuffy2/Calendarific/hacs_validate.yml?branch=main&style=for-the-badge)](#calendarific)<br/>

#### Building on the excellent work by @pinkywafer

The `Calendarific` component is a Home Assistant custom sensor which counts down to public holidays and observances, by querying the Calendarific api. The holidays also appear in the Home Assistant Calendar.

#### State Returned
* The number of days remaining to the next occurance.

#### Attributes:
* date:  The next date of the holiday _(formatted by the date_format configuration option)_
* description: The description of the holiday.

## Table of Contents

* [Installation](#installation)
  + [Installation via HACS](#hacs-recommended)
  + [Manual Installation](#manual)
* [Platform Configuration](#platform-configuration)
  + [Platform Configuration Parameters](#platform-configuration-parameters)
* [Sensor Configuration](#sensor-configuration)
  + [Sensor Configuration Parameters](#sensor-configuration-parameters)

## Installation
### HACS *(recommended)*
1. Ensure that [HACS](https://hacs.xyz/) is installed
1. Navigate to HACS
2. Click the <img width="25" alt="2023-11-10_15-31-28" src="https://github.com/Snuffy2/Calendarific/assets/6526076/80fb7906-0b60-4002-b119-614c5ac03024"> in the top right of the screen and select <img width="21" alt="2023-11-10_15-28-402" src="https://github.com/Snuffy2/Calendarific/assets/6526076/a79c3a37-91fa-4039-9f2f-bb86d169bb00"> Custom Repositories<br/>
    a. Repository: `https://github.com/Snuffy2/Calendarific`<br/>
    b. Category: `Integration`<br/>
    c. Click `Add` then close the popup<br/>
&nbsp;&nbsp;&nbsp;&nbsp;<img width="402" alt="2023-11-10_15-12-26" src="https://github.com/Snuffy2/Calendarific/assets/6526076/97f76676-ba63-4198-a2ea-9ed785c49575"><br/>
1. [Click Here](https://my.home-assistant.io/redirect/hacs_repository/?owner=Snuffy2&repository=Calendarific) to directly open `Calendarific` in HACS **or**<br/>
  a. Navigate to HACS<br/>
  b. Search for `Calendarific`<br/>
  c. Find the `Calendarific` integration with the description of: "Calendarific holiday sensor for Home Assistant (updated by Snuffy2)"<br/>
1. Click `Download`
1. Restart Home Assistant
1. See [Platform Configuration](#platform-configuration) below

<details>
<summary><h3>Manual</h3></summary>

You probably <u>do not</u> want to do this! Use the HACS method above unless you know what you are doing and have a good reason as to why you are installing manually

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`)
1. If you do not have a `custom_components` directory there, you need to create it
1. In the `custom_components` directory create a new folder called `calendarific`
1. Download the `calendarific.zip` file from the [latest release](https://github.com/Snuffy2/calendarific/releases/latest).
1. Unpack the release
1. Place _all_ the files from the `custom_components/calendarific/` directory in this repository into the new directory you created
1. Restart Home Assistant
1. See [Platform Configuration](#platform-configuration) below

</details>

## Platform Configuration

### The Calendarific platform MUST be configured in the configuration.yaml file.

You will need an API key from Calendarific.com Go to the [sign up page](https://calendarific.com/signup) and open a new account.  A free tier account is limited to 1000 api calls per month.  This integration will make two calls per day (and two on home assistant start)

```yaml
# Example configuration.yaml platform entry
calendarific:
  api_key: YOUR_API_KEY
  country: GB
  state: GB-WLS
```

### Platform Configuration Parameters

|Attribute |Required|Description
| -- | -- | --
| `api_key` | Yes | your api key from calendarific.com
| `country` | Yes | your country code [here is a list of supported countries](https://calendarific.com/supported-countries)
| `state` | No | your state code (ISO 3166-2 subdivision code) [[USA](https://en.wikipedia.org/wiki/ISO_3166-2:US)] [[UK](https://en.wikipedia.org/wiki/ISO_3166-2:GB)] _note the state code is for the country in the uk (counties not supported) or the state in the us._   If omitted, only national holidays will be displayed

## Sensor Configuration

In Configuration/Integrations click on the + button, select Calendarific and configure the options on the form (The available holidays will automatically appear on the list if the platform was configured correctly in the above step).

1. [Click Here](https://my.home-assistant.io/redirect/config_flow_start/?domain=calendarific) to directly add a `Calendarific` sensor **or**<br/>
    a. In Home Assistant, go to Settings -> [Integrations](https://my.home-assistant.io/redirect/integrations/)<br/>
    b. Click `+ Add Integrations` and select `Calendarific`<br/>
2. Add your configuration ([see Sensor Configuration Parameters](#sensor-configuration-parameters))
4. Click `Submit`

* Repeat as needed to create additional `Calendarific` sensors
* Options can be changed for existing `Calendarific` sensors in Home Assistant Integrations by selecting `Configure` under the desired `Calendarific` sensor.

### Sensor Configuration Parameters

|Attribute |Required|Default|Description
| -- | -- | -- | --
| `holiday` | Yes || Name of the holiday provided by calendarific api
| `name` | No | \<Holiday Name\> | Friendly name
| `icon_normal` | No | `mdi:calendar-blank` | Default icon
| `icon_today` | No | `mdi:calendar-star` | Icon if the holiday is today
| `days_as_soon` | No | 1 | Days in advance to display the icon defined in `icon_soon`
| `icon_soon` | No | `mdi:calendar` | Icon if the holiday is 'soon'
| `date_format` | No | `%x` _(Locale’s appropriate date representation)_ | Format the returned date. _for reference, see [http://strftime.org/](http://strftime.org/)_


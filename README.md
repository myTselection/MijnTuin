[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/myTselection/MijnTuin.svg)](https://github.com/myTselection/MijnTuin/releases)
![GitHub repo size](https://img.shields.io/github/repo-size/myTselection/MijnTuin.svg)

[![GitHub issues](https://img.shields.io/github/issues/myTselection/MijnTuin.svg)](https://github.com/myTselection/MijnTuin/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/myTselection/MijnTuin.svg)](https://github.com/myTselection/MijnTuin/commits/master)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/myTselection/MijnTuin.svg)](https://github.com/myTselection/MijnTuin/graphs/commit-activity)

# MijnTuin (ALPHA) - NOT WORKING YET! NOT TESTED YET!
[MijnTuin.org](https://www.mijntuin.org/) Home Assistant custom component. This custom component has been built from the ground up to bring your Mijn Tuin garden planning details into Home Assistant to help you towards a better follow upon your garden. This integration is built against the public website provided by MijnTuin.org.

This integration is in no way affiliated with MijnTuin.org.


<p align="center"><img src="https://raw.githubusercontent.com/myTselection/MijnTuin/master/icon.png"/></p>


## Installation
- [HACS](https://hacs.xyz/): add url https://github.com/myTselection/MijnTuin as custom repository (HACS > Integration > option: Custom Repositories)
- Restart Home Assistant
- Add 'MijnTuin' integration via HA Settings > 'Devices and Services' > 'Integrations'
- Provide MijnTuin username and password
- Sensor `mijntuin` should become available with the number of action to take this month.

## Status
Still some optimisations are planned, see [Issues](https://github.com/myTselection/MijnTuin/issues) section in GitHub.

## Technical pointers
The main logic and API connection related code can be found within source code youfone.be/custom_components/youfone.be:
- [sensor.py](https://github.com/myTselection/MijnTuin/blob/master/custom_components/MijnTuin/sensor.py)
- [utils.py](https://github.com/myTselection/MijnTuin/blob/master/custom_components/MijnTuin/utils.py) -> mainly ComponentSession class

All other files just contain boilerplat code for the integration to work wtihin HA or to have some constants/strings/translations.

## Example usage: 
### Markdown
<p align="center"><img src="https://raw.githubusercontent.com/myTselection/MijnTuin/master/Markdown%20Card%20example.png"/></p>

```
type: vertical-stack
cards:
  - type: markdown
    content: >-
		TODO
```

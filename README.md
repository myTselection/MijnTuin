[![HACS Default](https://img.shields.io/badge/HACS-Default-blue.svg)](https://github.com/hacs/default)
[![GitHub release](https://img.shields.io/github/release/myTselection/MijnTuin.svg)](https://github.com/myTselection/MijnTuin/releases)
![GitHub repo size](https://img.shields.io/github/repo-size/myTselection/MijnTuin.svg)

[![GitHub issues](https://img.shields.io/github/issues/myTselection/MijnTuin.svg)](https://github.com/myTselection/MijnTuin/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/myTselection/MijnTuin.svg)](https://github.com/myTselection/MijnTuin/commits/master)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/myTselection/MijnTuin.svg)](https://github.com/myTselection/MijnTuin/graphs/commit-activity)

# MijnTuin Home Assistant integration
[MijnTuin.org](https://www.mijntuin.org/) Home Assistant custom component. This custom component has been built from the ground up to bring your Mijn Tuin garden planning details into Home Assistant to help you towards a better follow upon your garden. This integration is built against the public website provided by MijnTuin.org.

This integration is in no way affiliated with MijnTuin.org. At least a free account of the website MijnTuin.org is required. The management of your garden and plants in your garden needs to be setup on the website MijnTuin.org.


<p align="center"><img src="https://raw.githubusercontent.com/myTselection/MijnTuin/master/icon.png"/></p>


## Installation
- [HACS](https://hacs.xyz/): search for the integration in the list of HACS
- Restart Home Assistant
- Add 'MijnTuin' integration via HA Settings > 'Devices and Services' > 'Integrations'
- Provide MijnTuin username and password
- Sensor `mijntuin` should become available with the number of action to take this month. The attributes provide further details on the type of activities in your garden, the plants and the number of activities per month.
- For each type of activity a sensor should become available with the number of action for this activity to take this month. The attributes provide further details per month.

Since the sensors of this Mijn Tuin integration may contain much data in the attributes, it might be desired to disable full detailed history logging in the recorder of Home Assistant. You may disable it by adding below in `configuration.yaml`:
```
recorder:
  exclude:
    entity_globs:
      - sensor.mijn_tuin*
```

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

<details><summary><b>Markdown card example code</b></summary>

```
type: markdown
content: >-
  ## Activiteiten deze maand: {{states('sensor.mijn_tuin')}}


  {% set activities = states | rejectattr("entity_id","eq","sensor.mijn_tuin") |
  selectattr("entity_id", "match","^sensor.mijn_tuin_*") | list %}

  {% for activity_device in activities %}

  {% set activity = activity_device.entity_id %}

  {% if state_attr(activity,"actionsThisMonth") > 0 %}

  {% set this_month = now().strftime("%B") %}

  {% set currplants = state_attr(activity,this_month) | list %}

  {% set currplantstodo = currplants | selectattr('buttons','defined') | list %}

  {% set currplantsdone = currplants | rejectattr('buttons','defined') | list %}


    <details>
    <summary>
    <b>{{state_attr(activity,'activityType') }}: </b> ({{state_attr(activity,this_month)|length }})</summary>
    
    {% if (currplantstodo | length) > 0 %}
    -  <details>
       <summary>Te doen</summary>
       {% for plant in currplantstodo  %}
         - <details>
           <summary> 
           <img src="{{ plant.get('photo').get('src') }} " width="30"></img> <b><a href="{{ plant.get('plant_link') }}" target="_blank" title="{{ plant.get('latin_name') }}">{{ plant.get('name') }}</a></b>: {{ plant.get('description') }}</summary>
            {% if plant.get('details','')|length  > 0 %}
            - {{ plant.get('details') }}
            {% endif %}
            
            - <a href="{{ plant.get('link') }}" target="_blank">link</a>
            {% if plant.get('buttons','')|length  > 0 %}- <a href="{{ plant.get('buttons')}}" target="_blank">Markeer als gedaan</a>{% endif %}
            
            </details> 
        {% endfor %}
        </details>
    {% endif %}
    {% if (currplantsdone | length) > 0 %}
    -  <details>
       <summary>Gedaan</summary>
       {% for plant in currplantsdone  %}
         - <details>
           <summary> 
           <img src="{{ plant.get('photo').get('src') }} " width="30"></img> <b><a href="{{ plant.get('plant_link') }}" target="_blank" title="{{ plant.get('latin_name') }}">{{ plant.get('name') }}</a></b>: {{ plant.get('description') }}</summary>
            {% if plant.get('details','')|length  > 0 %}
            - {{ plant.get('details') }}
            {% endif %}
            
            - <a href="{{ plant.get('link') }}" target="_blank">link</a>
            {% if plant.get('buttons','')|length  > 0 %}- <a href="{{ plant.get('buttons')}}" target="_blank">markeer als gedaan</a>{% endif %}
            
            </details> 
            {% endfor %}
        </details>
    {% endif %}


    </details></br>

  {% endif %}

  {% endfor %}


  ### Planten: 

  {% for plant in state_attr('sensor.mijn_tuin','Plants')
  %}[{{plant.get('name')}}]({{plant.get('link')}}
  "{{plant.get('latin_name')}}"), {% endfor %}

```

</details>

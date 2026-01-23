#!/usr/bin/env python3
"""Scan for all marriage/engagement events in the API."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'gramps_ha'))

from grampsweb_api import GrampsWebAPI
import json

# Initialize API
api = GrampsWebAPI(
    url="http://homeassistant:5000",
    username="erdal",
    password="1_Linux?"
)

try:
    # Get all people
    all_people = api.get_people()
    print(f"Total people: {len(all_people)}\n")
    
    marriage_count = 0
    marriage_events_found = []
    
    # Check every person's events
    for person_idx, person in enumerate(all_people):
        person_name = api._get_person_name(person)
        
        # Check person-level events
        event_ref_list = person.get("event_ref_list", [])
        for event_ref in event_ref_list:
            if not isinstance(event_ref, dict):
                continue
            
            event_handle = event_ref.get("ref") or event_ref.get("handle") or event_ref.get("hlink")
            if not event_handle:
                continue
            
            event = api._get_event(event_handle)
            if not event:
                continue
            
            event_type = event.get("type", {})
            type_string = (
                event_type.get("string", "")
                if isinstance(event_type, dict)
                else str(event_type)
            )
            
            if "marriage" in type_string.lower() or "engagement" in type_string.lower():
                marriage_count += 1
                dateval = event.get("date", {})
                date_str = "?"
                if isinstance(dateval, dict):
                    raw = dateval.get("dateval") or dateval.get("val") or dateval.get("start")
                    date_str = str(raw) if raw else "?"
                
                marriage_events_found.append({
                    "person": person_name,
                    "event_type": type_string,
                    "date": date_str
                })
        
        # Check family events
        families = person.get("family_list", [])
        for family_handle_or_ref in families:
            family_handle = family_handle_or_ref if isinstance(family_handle_or_ref, str) else (
                family_handle_or_ref.get("ref") or family_handle_or_ref.get("handle") or family_handle_or_ref.get("hlink")
            )
            
            if not family_handle:
                continue
            
            family = api._get_family(family_handle)
            if not family:
                continue
            
            for event_ref in family.get("event_ref_list", []):
                ev_handle = event_ref.get("ref") or event_ref.get("handle") or event_ref.get("hlink")
                if not ev_handle:
                    continue
                
                event = api._get_event(ev_handle)
                if not event:
                    continue
                
                event_type = event.get("type", {})
                type_string = (
                    event_type.get("string", "")
                    if isinstance(event_type, dict)
                    else str(event_type)
                )
                
                if "marriage" in type_string.lower() or "engagement" in type_string.lower():
                    marriage_count += 1
                    dateval = event.get("date", {})
                    date_str = "?"
                    if isinstance(dateval, dict):
                        raw = dateval.get("dateval") or dateval.get("val") or dateval.get("start")
                        date_str = str(raw) if raw else "?"
                    
                    marriage_events_found.append({
                        "person": person_name,
                        "event_type": type_string,
                        "date": date_str,
                        "family": family_handle
                    })
    
    print(f"Total marriage/engagement events found: {marriage_count}\n")
    print("Events:")
    for idx, event in enumerate(marriage_events_found[:20]):
        print(f"{idx+1}. {event['person']}: {event['event_type']} - {event['date']}")
    
    if len(marriage_events_found) > 20:
        print(f"... and {len(marriage_events_found) - 20} more")
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()

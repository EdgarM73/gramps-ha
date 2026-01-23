#!/usr/bin/env python3
"""Debug _get_marriage_dates for specific people."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'gramps_ha'))

from grampsweb_api import GrampsWebAPI
import json
import logging

logging.basicConfig(level=logging.DEBUG)

# Initialize API
api = GrampsWebAPI(
    url="http://homeassistant:5000",
    username="erdal",
    password="1_Linux?"
)

try:
    # Get all people
    all_people = api.get_people()
    
    # Find Erdal Akkaya and debug
    target_names = ["Erdal Akkaya", "Esat Akkaya", "Fadila Ahic"]
    
    for person in all_people:
        person_name = api._get_person_name(person)
        if person_name in target_names:
            print(f"\n{'='*80}")
            print(f"Debugging: {person_name}")
            print(f"{'='*80}")
            
            # Manually call _get_marriage_dates with debugging
            marriages = api._get_marriage_dates(person)
            print(f"Result: {len(marriages)} marriages found")
            for spouse, date in marriages:
                print(f"  - {spouse}: {date}")
            
            # Debug person structure
            print(f"\nPerson structure:")
            print(f"  event_ref_list length: {len(person.get('event_ref_list', []))}")
            print(f"  family_list: {person.get('family_list', [])}")
            
            # Check if we can fetch the person with full details
            handle = person.get("handle")
            if handle:
                detailed = api._get(f"people/{handle}")
                print(f"\nDetailed fetch:")
                print(f"  event_ref_list length: {len(detailed.get('event_ref_list', []))}")
                print(f"  event_ref_list: {json.dumps(detailed.get('event_ref_list', [])[:3], indent=2)}")

except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()

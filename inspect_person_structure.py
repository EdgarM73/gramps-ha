#!/usr/bin/env python3
"""Inspect raw person/event structure."""

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
    print(f"Total people: {len(all_people)}")
    
    # Check first 3 people's structures
    for idx, person in enumerate(all_people[:3]):
        person_name = api._get_person_name(person)
        print(f"\n{'='*80}")
        print(f"Person {idx+1}: {person_name}")
        print(f"{'='*80}")
        
        # Print event_ref_list structure
        event_ref_list = person.get("event_ref_list", [])
        print(f"event_ref_list type: {type(event_ref_list)}")
        print(f"event_ref_list length: {len(event_ref_list)}")
        if event_ref_list:
            print(f"event_ref_list[0] type: {type(event_ref_list[0])}")
            print(f"event_ref_list[0] = {json.dumps(event_ref_list[0], indent=2, default=str)}")
            print(f"event_ref_list[:3] = {json.dumps(event_ref_list[:3], indent=2, default=str)}")
        
        # Print family_list structure
        family_list = person.get("family_list", [])
        print(f"\nfamily_list type: {type(family_list)}")
        print(f"family_list length: {len(family_list)}")
        if family_list:
            print(f"family_list[0] type: {type(family_list[0])}")
            print(f"family_list[0] = {json.dumps(family_list[0], indent=2, default=str)}")
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()

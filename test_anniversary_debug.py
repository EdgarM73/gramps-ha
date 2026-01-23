#!/usr/bin/env python3
"""Debug script to test anniversary extraction directly."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'gramps_ha'))

from grampsweb_api import GrampsWebAPI
import logging

# Setup logging to see what's happening
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

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
    
    # Try to get anniversaries
    _LOGGER.info("=" * 80)
    _LOGGER.info("CALLING get_anniversaries()")
    _LOGGER.info("=" * 80)
    anniversaries = api.get_anniversaries(limit=50)
    
    print(f"\n\nAnniversaries found: {len(anniversaries)}")
    for idx, ann in enumerate(anniversaries[:10]):
        print(f"  {idx+1}. {ann}")
    
    # Now manually debug _get_marriage_dates for a few people
    print("\n\n" + "=" * 80)
    print("MANUAL DEBUG: _get_marriage_dates for first 10 people")
    print("=" * 80)
    
    for idx, person in enumerate(all_people[:10]):
        person_name = api._get_person_name(person)
        marriages = api._get_marriage_dates(person)
        print(f"\nPerson {idx+1}: {person_name}")
        print(f"  Marriages found: {len(marriages)}")
        print(f"  Family list: {len(person.get('family_list', []))}")
        print(f"  Event ref list: {len(person.get('event_ref_list', []))}")
        for spouse, date in marriages:
            print(f"    - {spouse}: {date}")
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()

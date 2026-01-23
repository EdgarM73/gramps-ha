#!/usr/bin/env python3
"""Test anniversaries with full output."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components', 'gramps_ha'))

from grampsweb_api import GrampsWebAPI

# Initialize API
api = GrampsWebAPI(
    url="http://homeassistant:5000",
    username="erdal",
    password="1_Linux?"
)

try:
    # Get anniversaries
    anniversaries = api.get_anniversaries(limit=100)
    
    print(f"Total anniversaries found: {len(anniversaries)}\n")
    
    for idx, ann in enumerate(anniversaries):
        print(f"{idx+1}. {ann['person_name']}")
        print(f"   Marriage date: {ann['marriage_date']}")
        print(f"   Next anniversary: {ann['next_anniversary']}")
        print(f"   Years together: {ann['years_together']}")
        print(f"   Days until: {ann['days_until']}\n")

except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()

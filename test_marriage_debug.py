"""Debug marriage/engagement detection in Gramps API."""
import requests

URL = "http://homeassistant:5000"
USERNAME = "erdal"
PASSWORD = "1_Linux?"


def main():
    tok = requests.post(
        f"{URL}/api/token/",
        json={"username": USERNAME, "password": PASSWORD},
        timeout=10,
    )
    tok.raise_for_status()
    token = tok.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    people = requests.get(f"{URL}/api/people/", headers=headers, timeout=30).json()
    print(f"Total people: {len(people)}\n")

    # Sample first 5 people with families
    sample_count = 0
    for person in people:
        families = person.get("family_list", []) or []
        if not families:
            continue
        
        sample_count += 1
        if sample_count > 5:
            break

        name = person.get("primary_name", {})
        first = name.get("first_name", "")
        surns = name.get("surname_list", [])
        surname = surns[0].get("surname", "") if surns else ""
        full_name = f"{first} {surname}".strip()

        print(f"Person: {full_name}")
        print(f"  Handle: {person.get('handle')}")
        print(f"  Families: {len(families)}")
        
        for idx, family_ref in enumerate(families):
            print(f"  Family {idx + 1}:")
            print(f"    family_ref type: {type(family_ref)}")
            print(f"    family_ref value: {family_ref}")
            
            # Extract handle
            if isinstance(family_ref, str):
                fam_handle = family_ref
            elif isinstance(family_ref, dict):
                fam_handle = family_ref.get("ref") or family_ref.get("handle") or family_ref.get("hlink")
            else:
                print(f"    ERROR: Unknown family_ref type")
                continue
            
            if "/" in fam_handle:
                fam_handle = fam_handle.rstrip("/").split("/")[-1]
            
            print(f"    Extracted handle: {fam_handle}")
            
            # Fetch family
            try:
                family = requests.get(f"{URL}/api/families/{fam_handle}", headers=headers, timeout=10).json()
                print(f"    Family fetched successfully")
                print(f"    parent_rel_list: {family.get('parent_rel_list', [])}")
                print(f"    event_ref_list length: {len(family.get('event_ref_list', []) or [])}")
                
                # Check events
                for ev_idx, event_ref in enumerate(family.get("event_ref_list", []) or []):
                    print(f"      Event {ev_idx + 1}:")
                    print(f"        event_ref: {event_ref}")
                    
                    if isinstance(event_ref, str):
                        ev_handle = event_ref
                    elif isinstance(event_ref, dict):
                        ev_handle = event_ref.get("ref") or event_ref.get("handle") or event_ref.get("hlink")
                    else:
                        print(f"        ERROR: Unknown event_ref type")
                        continue
                    
                    if "/" in ev_handle:
                        ev_handle = ev_handle.rstrip("/").split("/")[-1]
                    
                    try:
                        event = requests.get(f"{URL}/api/events/{ev_handle}", headers=headers, timeout=10).json()
                        etype = event.get("type", {})
                        tstr = etype.get("string", "") if isinstance(etype, dict) else str(etype)
                        print(f"        Event type: {tstr}")
                        print(f"        Date: {event.get('date', {})}")
                    except Exception as e:
                        print(f"        ERROR fetching event: {e}")
            except Exception as e:
                print(f"    ERROR fetching family: {e}")
        print()


if __name__ == "__main__":
    main()

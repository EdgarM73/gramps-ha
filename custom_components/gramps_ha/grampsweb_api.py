"""API client for Gramps Web."""
import logging
from datetime import datetime, date
import requests

_LOGGER = logging.getLogger(__name__)


class GrampsWebAPI:
    """Class to interact with Gramps Web API."""

    def __init__(self, url: str, username: str = None, password: str = None, surname_filter: str = ""):
        """Initialize the API client."""
        self.url = url.rstrip("/")
        self.username = username
        self.password = password
        self.surname_filter = surname_filter.strip() if surname_filter else ""
        self.token = None
        self._session = requests.Session()
        
        if self.surname_filter:
            _LOGGER.info("Surname filter active: %s", self.surname_filter)

    def _authenticate(self):
        """Authenticate with the Gramps Web API."""
        if not self.username or not self.password:
            return True
        
        try:
            response = self._session.post(
                f"{self.url}/api/token/",
                json={
                    "username": self.username,
                    "password": self.password,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            self.token = data.get("access_token")
            
            if self.token:
                self._session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
            return True
        except Exception as err:
            _LOGGER.warning("Failed to authenticate with Gramps Web: %s", err)
            return False

    def _get(self, endpoint: str, params: dict = None):
        """Make a GET request to the API."""
        if not self.token and self.username:
            self._authenticate()
        
        try:
            url = f"{self.url}/api/{endpoint}"
            _LOGGER.debug("GET request to: %s", url)
            
            response = self._session.get(
                url,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            
            _LOGGER.debug("Response status: %s", response.status_code)
            return response.json()
        except Exception as err:
            _LOGGER.error("API request to %s failed: %s", endpoint, err, exc_info=True)
            raise

    def _resolve_event_handle(self, event_ref: dict) -> str | None:
        """Resolve an event handle from different possible keys."""
        if not event_ref:
            return None

        # Gramps may provide the event reference under different keys
        handle = None
        for key in ("ref", "handle", "hlink"):
            candidate = event_ref.get(key)
            if candidate:
                handle = candidate
                break

        if not handle or not isinstance(handle, str):
            return None

        # If the handle looks like a URL/path, keep only the last segment
        if "/" in handle:
            handle = handle.rstrip("/").split("/")[-1]

        return handle

    def _parse_dateval(self, dateval):
        """Convert Gramps dateval list into a Python date using safe heuristics."""
        try:
            if not isinstance(dateval, (list, tuple)):
                return None

            # We only need the first three entries for day/month/year
            vals = list(dateval[:3])
            if len(vals) < 3:
                return None

            # Ensure all are integers
            try:
                vals = [int(v) for v in vals]
            except Exception:
                return None

            # Try combinations with a plausible year (>= 100)
            combinations = [
                (2, 1, 0),  # dateval = [day, month, year]
                (0, 1, 2),  # dateval = [year, month, day]
                (0, 2, 1),  # dateval = [year, day, month]
            ]

            for y_idx, m_idx, d_idx in combinations:
                year, month, day = vals[y_idx], vals[m_idx], vals[d_idx]
                if year < 100:
                    continue
                if not (1 <= month <= 12 and 1 <= day <= 31):
                    continue
                return date(year, month, day)

            return None
        except Exception:
            return None

    def get_people(self):
        """Get all people from Gramps Web."""
        _LOGGER.debug("Fetching people from %s", self.url)
        try:
            result = self._get("people/")
            _LOGGER.debug("API response type: %s", type(result))
            return result
        except Exception as err:
            _LOGGER.error("Failed to get people: %s", err, exc_info=True)
            raise

    def get_birthdays(self, limit: int = 50):
        """Get upcoming birthdays from Gramps Web."""
        try:
            _LOGGER.info("Fetching birthdays from Gramps Web API")
            
            # Get all people
            try:
                all_people = self.get_people()
                _LOGGER.info("Fetched %s people from Gramps Web", len(all_people) if isinstance(all_people, list) else "unknown")
            except Exception as people_err:
                _LOGGER.error("Failed to fetch people: %s", people_err, exc_info=True)
                return []
            
            if not all_people:
                _LOGGER.warning("No people data returned from Gramps Web")
                return []

            # Diagnostics: check how many have event lists or valid birth refs
            birth_ref_valid = 0
            with_events = 0
            sampled_event_type = None
            for person in all_people:
                event_ref_list = person.get("event_ref_list", []) or []
                if event_ref_list:
                    with_events += 1
                    if sampled_event_type is None:
                        handle = self._resolve_event_handle(event_ref_list[0])
                        if handle:
                            try:
                                evt = self._get(f"events/{handle}")
                                etype = evt.get("type", {})
                                type_string = etype.get("string", "") if isinstance(etype, dict) else str(etype)
                                sampled_event_type = f"handle={handle}, type={type_string}"
                            except Exception as diag_err:
                                sampled_event_type = f"handle={handle}, error={diag_err}"
                bri = person.get("birth_ref_index", -1)
                if bri >= 0 and bri < len(event_ref_list):
                    birth_ref_valid += 1
            _LOGGER.info("Diagnostics: %s/%s have event_ref_list, %s/%s have valid birth_ref_index", with_events, len(all_people), birth_ref_valid, len(all_people))
            if sampled_event_type:
                _LOGGER.info("Diagnostics sample event: %s", sampled_event_type)
            
            # Filter to only include people with a birth date
            people_data = [
                person for person in all_people 
                if self._has_birth_date(person)
            ]
            _LOGGER.info("Filtered to %s people with birth dates (from %s total)", 
                        len(people_data), len(all_people))
            
            if not people_data:
                _LOGGER.warning("No people with birth dates found")
                return []
            
            birthdays = []
            people_with_birth = 0
            living_people = 0
            deceased_people = 0
            
            today = date.today()
            current_year = today.year
            
            # Sample first person for debugging
            if people_data:
                sample = people_data[0]
                _LOGGER.debug("Sample person data: %s", sample)
                _LOGGER.debug("Sample birth_ref_index: %s", sample.get("birth_ref_index"))
                _LOGGER.debug("Sample event_ref_list length: %s", len(sample.get("event_ref_list", [])))
                if sample.get("event_ref_list"):
                    _LOGGER.debug("Sample first event: %s", sample.get("event_ref_list")[0])
            
            # Search for specific person: Erdal Akkaya
            for p in people_data:
                pname = self._get_person_name(p)
                if "erdal" in pname.lower() and "akkaya" in pname.lower():
                    _LOGGER.info("Found Erdal Akkaya:")
                    _LOGGER.info("  Full data: %s", p)
                    _LOGGER.info("  birth_ref_index: %s", p.get("birth_ref_index"))
                    _LOGGER.info("  death_ref_index: %s", p.get("death_ref_index"))
                    _LOGGER.info("  event_ref_list: %s", p.get("event_ref_list"))
                    break
            
            for person in people_data:
                # Get name
                name = self._get_person_name(person)
                
                # Apply surname filter if configured
                if self.surname_filter:
                    if self.surname_filter.lower() not in name.lower():
                        continue
                
                # Get birth event
                birth_date = self._extract_birth_date(person)
                if not birth_date:
                    # Should not happen since we pre-filtered, but handle it
                    continue
                
                people_with_birth += 1
                
                # Check if person is still alive
                is_alive = self._is_person_alive(person)
                
                if is_alive:
                    living_people += 1
                else:
                    deceased_people += 1
                    _LOGGER.debug("Skipping deceased person: %s", name)
                    continue
                
                # Calculate next birthday
                next_birthday_info = self._calculate_next_birthday(birth_date, name)
                
                if next_birthday_info:
                    birthdays.append(next_birthday_info)
            
            _LOGGER.info("Summary - Total with birth date: %s, Living: %s, Deceased: %s", 
                        people_with_birth, living_people, deceased_people)
            _LOGGER.info("Found %s birthdays from living people", len(birthdays))
            
            # Sort by days until birthday
            birthdays.sort(key=lambda x: x["days_until"])
            
            return birthdays[:limit]
            
        except Exception as err:
            _LOGGER.error("Failed to fetch birthdays: %s", err, exc_info=True)
            return []

    def _has_birth_date(self, person: dict) -> bool:
        """Check if person has a birth date set."""
        try:
            # Check birth_ref_index
            birth_ref_index = person.get("birth_ref_index", -1)
            event_ref_list = person.get("event_ref_list", [])
            
            # If birth_ref_index is valid, we have a birth date
            if birth_ref_index >= 0 and birth_ref_index < len(event_ref_list):
                event_handle = self._resolve_event_handle(event_ref_list[birth_ref_index])
                if event_handle:
                    parsed = self._fetch_event_date(event_handle)
                    if parsed:
                        return True
            
            # Otherwise, check if there's a birth event in the list
            for event_ref in event_ref_list:
                event_handle = self._resolve_event_handle(event_ref)
                if not event_handle:
                    continue
                try:
                    parsed = self._fetch_event_date(event_handle)
                    if parsed:
                        return True
                except Exception:
                    continue
            
            return False
            
        except Exception as err:
            _LOGGER.debug("Error checking birth date: %s", err)
            return False

    def _extract_birth_date(self, person: dict):
        """Extract birth date from person data."""
        try:
            birth_ref_index = person.get("birth_ref_index", -1)
            event_ref_list = person.get("event_ref_list", [])

            # If birth_ref_index is valid, try that reference first
            if birth_ref_index >= 0 and birth_ref_index < len(event_ref_list):
                event_handle = self._resolve_event_handle(event_ref_list[birth_ref_index])
                if event_handle:
                    parsed = self._fetch_event_date(event_handle, require_birth=True)
                    if parsed:
                        return parsed

            # Otherwise, scan all events for a birth event
            for event_ref in event_ref_list:
                event_handle = self._resolve_event_handle(event_ref)
                if not event_handle:
                    continue
                try:
                    parsed = self._fetch_event_date(event_handle, require_birth=True)
                    if parsed:
                        return parsed
                except Exception as event_err:
                    _LOGGER.debug("Could not fetch event %s: %s", event_handle, event_err)
                    continue

            return None

        except Exception as err:
            _LOGGER.debug("Could not extract birth date: %s", err)
            return None

    def _fetch_event_date(self, event_handle: str, require_birth: bool = False):
        """Fetch and parse an event date, optionally requiring a birth event."""
        try:
            if not event_handle:
                return None

            # Clean up handle if it's a path-like string
            handle = event_handle
            if "/" in handle:
                handle = handle.rstrip("/").split("/")[-1]

            event_data = self._get(f"events/{handle}")

            if require_birth:
                event_type = event_data.get("type", {})
                type_string = event_type.get("string", "") if isinstance(event_type, dict) else str(event_type)
                if "birth" not in type_string.lower():
                    return None

            date_info = event_data.get("date", {})
            parsed = self._parse_dateval(date_info.get("dateval", []))
            if parsed:
                _LOGGER.debug("Parsed event date: %s", parsed)
                return parsed

            return None
        except Exception as err:
            _LOGGER.debug("Could not fetch event date: %s", err)
            return None

    def _is_person_alive(self, person: dict) -> bool:
        """Check if person is still alive (no death date)."""
        try:
            # Check death_ref_index
            death_ref_index = person.get("death_ref_index", -1)
            
            if death_ref_index == -1:
                # No death event, person is alive
                return True
            
            # Person has a death event, they are deceased
            _LOGGER.debug("Person has death_ref_index: %s", death_ref_index)
            return False
            
        except Exception as err:
            _LOGGER.debug("Could not determine if person is alive: %s", err)
            # If we can't determine, assume person is alive
            return True

    def _parse_gramps_date(self, date_str: str):
        """Parse Gramps date format to Python date."""
        try:
            # Gramps can have various date formats
            # Common format: "1990-01-15" or "15 Jan 1990"
            if "-" in date_str and len(date_str) == 10:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            # Add more parsing logic as needed
            return None
        except Exception:
            return None

    def _get_person_name(self, person: dict):
        """Get person's display name."""
        try:
            primary_name = person.get("primary_name", {})
            first_name = primary_name.get("first_name", "")
            
            # Get surname from surname_list
            surname_list = primary_name.get("surname_list", [])
            surname = ""
            if surname_list:
                surname = surname_list[0].get("surname", "")
            
            full_name = f"{first_name} {surname}".strip()
            return full_name if full_name else "Unknown"
        except Exception:
            return "Unknown"

    def _calculate_next_birthday(self, birth_date: date, name: str):
        """Calculate next birthday occurrence."""
        try:
            today = date.today()
            current_year = today.year
            
            # Calculate this year's birthday
            this_year_birthday = birth_date.replace(year=current_year)
            
            # If birthday already passed this year, use next year
            if this_year_birthday < today:
                next_birthday = birth_date.replace(year=current_year + 1)
            else:
                next_birthday = this_year_birthday
            
            days_until = (next_birthday - today).days
            age = next_birthday.year - birth_date.year
            
            return {
                "person_name": name,
                "birth_date": birth_date.isoformat(),
                "next_birthday": next_birthday.isoformat(),
                "age": age,
                "days_until": days_until,
            }
            
        except Exception as err:
            _LOGGER.debug("Could not calculate birthday for %s: %s", name, err)
            return None

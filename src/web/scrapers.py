import json
import re
from datetime import datetime
from typing import Any, Protocol, TypeVar

import pytz
import requests
from bs4 import BeautifulSoup, Tag

from django.utils import timezone

from web import models

ST = TypeVar("ST", covariant=True)


class Scraper(Protocol[ST]):
    """Scrape the URL and return a typed object."""

    def scrape(self, url: str) -> ST:
        ...


class MeetupHomepageScraper(Scraper[list[models.Event]]):
    """Scrape a list of upcoming events from a Meetup group's home page."""

    def __init__(self) -> None:
        self.event_scraper = MeetupEventScraper()

        naive_now = datetime.now()
        self._now = timezone.localtime()
        # See https://gist.github.com/ajosephau/2a22698faaf6206ce195c7aa78e48247
        self._timezones_by_abbreviation = {pytz.timezone(tz).tzname(naive_now): tz for tz in pytz.all_timezones}
    
    def scrape(self, url: str) -> list[str]:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        upcoming_section = soup.find_all(id="upcoming-section")[0]
        events = upcoming_section.find_all_next(id=re.compile(r"event-card-"))
        filtered_event_containers = [event for event in events if self._filter_event(event)]
        event_urls = [event_container["href"] for event_container in filtered_event_containers]
        # events = [self.event_scraper.scrape(url) for url in event_urls]  # TODO: parallelize (with async?)
        return event_urls

    def _filter_event(self, event: Tag) -> bool:
        time: str = event.find_all("time")[0].text
        time, tz_abbrv = time.rsplit(maxsplit=1)
        tz = self._timezones_by_abbreviation[tz_abbrv]
        tz = pytz.timezone(tz)
        event_datetime = datetime.strptime(time, "%a, %b %d, %Y, %I:%M %p").astimezone(tz)
        return event_datetime > self._now


class MeetupEventScraper(Scraper[models.Event]):
    """Scrape an Event from a Meetup details page."""

    TIME_RANGE_PATTERN = re.compile(r"(\d{1,}:\d{2} [AP]M) to \d{1,}:\d{2} [AP]M")

    def scrape(self, url: str) -> models.Event:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        try:
            apollo_state = self._parse_apollo_state(soup)
            event_json = self._parse_event_json(apollo_state)
        except LookupError:
            event_json = {}
            
        if event_json:
            name = event_json["title"]
            description = event_json["description"]
            date_time = datetime.fromisoformat(event_json["dateTime"])
            location_data = apollo_state[event_json["venue"]["__ref"]]
            location = f"{location_data['address']}, {location_data['city']}, {location_data['state']}"
        else:
            name = self._parse_name(soup)
            description = self._parse_description(soup)
            date_time = self._parse_date_time(soup)
            location = self._parse_location(soup)

        return models.Event(
            name=name,
            description=description,
            date_time=date_time,
            location=location,
        )

    def _parse_apollo_state(self, soup: BeautifulSoup) -> dict:
        next_data = soup.find_all(attrs={"id": "__NEXT_DATA__"})[0].text
        next_data = json.loads(next_data)
        apollo_state: dict[str, Any] = next_data["props"]["pageProps"]["__APOLLO_STATE__"]
        return apollo_state

    def _parse_event_json(self, apollo_state: dict) -> dict:
        event_key = [key for key in apollo_state.keys() if key.split(":")[0] == "Event"][0]
        event_value = apollo_state[event_key]
        return event_value

    def _parse_name(self, soup: BeautifulSoup) -> str:
        name: str = soup.find_all("h1")[0].text
        name = " ".join(name.split())
        return name

    def _parse_description(self, soup: BeautifulSoup) -> str:
        description: str = soup.find_all(attrs={"id": "event-details"})[0].text
        description = description.lstrip()
        if description.startswith("Details"):
            description = description[len("Details"):].lstrip()
        return description
    
    def _parse_date_time(self, soup: BeautifulSoup) -> datetime:
        return datetime.fromisoformat(soup.find_all("time")[0]["datetime"])

    def _parse_location(self, soup: BeautifulSoup) -> str:
        location: str = soup.find_all(attrs={"data-testid": "location-info"})[0].text
        location = " ".join((line.strip() for line in location.splitlines()))
        location = location.replace(" · ", ", ")
        return location

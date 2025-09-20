"""Static BBC station metadata for the BBC UK provider.

This module defines the initial STATIONS mapping. Dynamic discovery
(via `discovery.py`) can merge new/updated entries at runtime.
"""

from __future__ import annotations

from typing import TypedDict


class StationEntry(TypedDict, total=False):
    """Typed dict for a station entry."""

    name: str
    slug: str
    isml: str
    icon: str
    group: str


# Minimal seed list for nationals (you can add more if you want).
# Dynamic discovery will merge/augment this at startup.
STATIONS: dict[str, dict[str, str]] = {
    "bbc_radio_1": {
        "name": "BBC Radio 1",
        "slug": "bbc_radio_one",
        "isml": "bbc_radio_one.isml",
        "group": "national",
        "icon": "icons/radio1.png",
    },
    "bbc_radio_2": {
        "name": "BBC Radio 2",
        "slug": "bbc_radio_two",
        "isml": "bbc_radio_two.isml",
        "group": "national",
        "icon": "icons/radio2.png",
    },
    "bbc_radio_3": {
        "name": "BBC Radio 3",
        "slug": "bbc_radio_three",
        "isml": "bbc_radio_three.isml",
        "group": "national",
        "icon": "icons/radio3.png",
    },
    "bbc_radio_4": {
        "name": "BBC Radio 4",
        "slug": "bbc_radio_four",
        "isml": "bbc_radio_fourfm.isml",  # exception: "fourfm"
        "group": "national",
        "icon": "icons/radio4.png",
    },
    "bbc_radio_4extra": {
        "name": "BBC Radio 4 Extra",
        "slug": "bbc_radio_four_extra",
        "isml": "bbc_radio_four_extra.isml",
        "group": "national",
        "icon": "icons/radio4extra.png",
    },
    "bbc_radio_5live": {
        "name": "BBC Radio 5 Live",
        "slug": "bbc_radio_five_live",
        "isml": "bbc_radio_five_live.isml",
        "group": "national",
        "icon": "icons/fivelive.png",
    },
    "bbc_6music": {
        "name": "BBC 6 Music",
        "slug": "bbc_6music",
        "isml": "bbc_6music.isml",
        "group": "national",
        "icon": "icons/6music.png",
    },
    "bbc_world_service": {
        "name": "BBC World Service",
        "slug": "bbc_world_service",
        "isml": "bbc_world_service.isml",
        "group": "national",
        "icon": "icons/worldservice.png",
    },
}


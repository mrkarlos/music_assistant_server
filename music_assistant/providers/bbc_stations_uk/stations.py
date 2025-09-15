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
STATIONS: dict[str, StationEntry] = {
    "bbc_radio_1": {
        "name": "BBC Radio 1",
        "slug": "bbc_radio_one",
        "isml": "bbc_radio_one.isml",
        "icon": "bbc1.png",
        "group": "national",
    },
    "bbc_radio_2": {
        "name": "BBC Radio 2",
        "slug": "bbc_radio_two",
        "isml": "bbc_radio_two.isml",
        "icon": "bbc2.png",
        "group": "national",
    },
    "bbc_radio_3": {
        "name": "BBC Radio 3",
        "slug": "bbc_radio_three",
        "isml": "bbc_radio_three.isml",
        "icon": "bbc3.png",
        "group": "national",
    },
    "bbc_radio_4": {
        "name": "BBC Radio 4 (FM)",
        "slug": "bbc_radio_four",
        "isml": "bbc_radio_fourfm.isml",
        "icon": "bbc4.png",
        "group": "national",
    },
    "bbc_radio_5live": {
        "name": "BBC Radio 5 Live",
        "slug": "bbc_radio_5live",
        "isml": "bbc_radio_five_live.isml",
        "icon": "bbc5.png",
        "group": "national",
    },
    "bbc_6music": {
        "name": "BBC Radio 6 Music",
        "slug": "bbc_6music",
        "isml": "bbc_6music.isml",
        "icon": "bbc6.png",
        "group": "national",
    },
}

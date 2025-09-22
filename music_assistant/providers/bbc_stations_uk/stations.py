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
        "icon": "radio_1.png",
    },
    "bbc_radio_one_anthems": {
        "name": "BBC Radio 1 Anthems",
        "slug": "bbc_radio_one_anthems",
        "isml": "bbc_radio_one_anthems.isml",
        "group": "national",
        "icon": "radio1_anthems.png",
    },
    "bbc_radio_one_dance": {
        "name": "BBC Radio 1 Dance",
        "slug": "bbc_radio_one_dance",
        "isml": "bbc_radio_one_dance.isml",
        "group": "national",
        "icon": "radio1_dance.png",
    },
    "bbc_1xtra": {
        "name": "BBC Radio 1Xtra",
        "slug": "bbc_1xtra",
        "isml": "bbc_1xtra.isml",
        "group": "national",
        "icon": "radio_1_xtra.png",
    },
    "bbc_radio_2": {
        "name": "BBC Radio 2",
        "slug": "bbc_radio_two",
        "isml": "bbc_radio_two.isml",
        "group": "national",
        "icon": "radio_2.png",
    },
    "bbc_radio_3": {
        "name": "BBC Radio 3",
        "slug": "bbc_radio_three",
        "isml": "bbc_radio_three.isml",
        "group": "national",
        "icon": "radio3.png",
    },
    "bbc_radio_three_unwind": {
        "name": "BBC Radio 3 Unwind",
        "slug": "bbc_radio_three_unwind",
        "isml": "bbc_radio_three_unwind.isml",
        "group": "national",
        "icon": "radio3_unwind.png",
    },
    "bbc_radio_fourfm": {
        "name": "BBC Radio 4",
        "slug": "bbc_radio_fourfm",
        "isml": "bbc_radio_fourfm.isml",  # exception: "fourfm"
        "group": "national",
        "icon": "radio4.png",
    },
    "bbc_radio_four_extra": {
        "name": "BBC Radio 4 Extra",
        "slug": "bbc_radio_four_extra",
        "isml": "bbc_radio_four_extra.isml",
        "group": "national",
        "icon": "radio4extra.png",
    },
    "bbc_radio_five_live": {
        "name": "BBC Radio 5 Live",
        "slug": "bbc_radio_five_live",
        "isml": "bbc_radio_five_live.isml",
        "group": "national",
        "icon": "fivelive.png",
    },
    "bbc_radio_five_live_sports_extra": {
        "name": "BBC Radio 5 Sports Extra",
        "slug": "bbc_radio_five_live_sports_extra",
        "isml": "bbc_radio_five_live_sports_extra.isml",
        "group": "national",
        "icon": "radio5_live_sports_extra.png",
    },
    "bbc_radio_five_sports_extra_2": {
        "name": "BBC Radio 5 Sports Extra 2",
        "slug": "bbc_radio_five_sports_extra_2",
        "isml": "bbc_radio_five_sports_extra_2.isml",
        "group": "national",
        "icon": "radio5_live_sports_extra_2.png",
    },
    "bbc_radio_five_sports_extra_3": {
        "name": "BBC Radio 5 Sports Extra 3",
        "slug": "bbc_radio_five_sports_extra_3",
        "isml": "bbc_radio_five_sports_extra_3.isml",
        "group": "national",
        "icon": "radio5_live_sports_extra_3.png",
    },
    "bbc_radio_6_music": {
        "name": "BBC Radio 6 Music",
        "slug": "bbc_6music",
        "isml": "bbc_6music.isml",
        "group": "national",
        "icon": "radio6_music.png",
    },
    "bbc_world_service": {
        "name": "BBC World Service",
        "slug": "bbc_world_service",
        "isml": "bbc_world_service.isml",
        "group": "national",
        "icon": "radio_worldservice.png",
    },
    "bbc_asian_network": {
        "name": "BBC Asian Network",
        "slug": "bbc_asian_network",
        "isml": "bbc_asian_network.isml",
        "group": "national",
        "icon": "radio_asian_network.png",
    },
    "bbc_sounds_news": {
        "name": "BBC News",
        "slug": "bbc_sounds_news",
        "isml": "bbc_sounds_news.isml",
        "group": "national",
        "icon": "radio_sounds_news.png",
    },
    "bbc_radio_scotland_fm": {
        "name": "BBC Radio Scotland",
        "slug": "bbc_radio_scotland_fm",
        "isml": "bbc_radio_scotland_fm.isml",
        "group": "national",
        "icon": "radio_scotland.png",
    },
    "bbc_radio_scotland_mw": {
        "name": "BBC Radio Scotland Extra",
        "slug": "bbc_radio_scotland_mw",
        "isml": "bbc_radio_scotland_mw.isml",
        "group": "national",
        "icon": "radio_scotland_extra.png",
    },
    "bbc_radio_orkney": {
        "name": "BBC Radio Orkney",
        "slug": "bbc_radio_orkney",
        "isml": "bbc_radio_orkney.isml",
        "group": "national",
        "icon": "radio_orkney.png",
    },
    "bbc_radio_shetland": {
        "name": "BBC Radio Shetland",
        "slug": "bbc_radio_shetland",
        "isml": "bbc_radio_shetland.isml",
        "group": "national",
        "icon": "radio_shetland.png",
    },
    "bbc_radio_nan_gaidheal": {
        "name": "BBC Radio nan Gàidheal",
        "slug": "bbc_radio_nan_gaidheal",
        "isml": "bbc_radio_nan_gaidheal.isml",
        "group": "national",
        "icon": "radio_nan_gaidheal.png",
    },
    "bbc_radio_ulster": {
        "name": "BBC Radio Ulster",
        "slug": "bbc_radio_ulster",
        "isml": "bbc_radio_ulster.isml",
        "group": "national",
        "icon": "radio_ulster.png",
    },
    "bbc_radio_foyle": {
        "name": "BBC Radio Foyle",
        "slug": "bbc_radio_foyle",
        "isml": "bbc_radio_foyle.isml",
        "group": "national",
        "icon": "radio_foyle.png",
    },
    "bbc_radio_wales_fm": {
        "name": "BBC Radio Wales",
        "slug": "bbc_radio_wales_fm",
        "isml": "bbc_radio_wales_fm.isml",
        "group": "national",
        "icon": "radio_wales_fm.png",
    },
    "bbc_radio_wales_am": {
        "name": "BBC Radio Wales Extra",
        "slug": "bbc_radio_wales_am",
        "isml": "bbc_radio_wales_am.isml",
        "group": "national",
        "icon": "radio_wales_am.png",
    },
    "bbc_radio_cymru": {
        "name": "BBC Radio Cymru",
        "slug": "bbc_radio_cymru",
        "isml": "bbc_radio_cymru.isml",
        "group": "national",
        "icon": "radio_cymru.png",
    },
    "bbc_radio_cymru_2": {
        "name": "BBC Radio Cymru 2",
        "slug": "bbc_radio_cymru_2",
        "isml": "bbc_radio_cymru_2.isml",
        "group": "national",
        "icon": "radio_cymru_2.png",
    },
    "cbeebies_radio": {
        "name": "CBeebies Radio",
        "slug": "cbeebies_radio",
        "isml": "cbeebies_radio.isml",
        "group": "national",
        "icon": "radio_cbeebies.png",
    },
    "bbc_radio_wiltshire": {
        "name": "BBC Radio Wiltshire",
        "slug": "bbc_radio_wiltshire",
        "isml": "bbc_radio_wiltshire.isml",
        "group": "local",
        "icon": "",
    },
}

# Build a reverse index: slug -> provider_id, derived from STATIONS
_SLUG_TO_PID: dict[str, str] = {meta["slug"]: pid for pid, meta in STATIONS.items()}


def slug_to_provider_id(slug: str) -> str:
    """Return provider_id for a BBC slug using STATIONS as the source of truth."""
    return _SLUG_TO_PID.get(slug, slug)


def rebuild_slug_index() -> None:
    """Recompute the slug->provider_id index after STATIONS changes."""
    _SLUG_TO_PID.clear()
    _SLUG_TO_PID.update({meta["slug"]: pid for pid, meta in STATIONS.items()})

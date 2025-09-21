"""Dynamic discovery of BBC stations from the BBC Sounds Stations page.

This module fetches https://www.bbc.co.uk/sounds/stations, extracts
station slugs and labels from the National/Regional and Local sections,
derives `.isml` names, and merges the results into the provider's
static STATIONS mapping.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

import aiohttp

BBC_STATIONS_URL = "https://www.bbc.co.uk/sounds/stations"

# Exceptions where `.isml` is not simply f"{slug}.isml".
ISML_EXCEPTIONS = {
    "bbc_radio_four": "bbc_radio_fourfm.isml",
    "bbc_radio_5live": "bbc_radio_five_live.isml",
}

# Optional: override display names for a few slugs.
NAME_OVERRIDES = {
    "bbc_radio_four": "BBC Radio 4 (FM)",
}


def normalise_station_name(raw: str) -> str:
    """Normalise scraped BBC station names (minimal rules)."""
    # Strip leading/trailing spaces
    station_name = raw.strip()
    # Always uppercase "BBC"
    return re.sub(r"\bbbc\b", "BBC", station_name, flags=re.IGNORECASE)


def slug_to_isml(slug: str) -> str:
    """Map a BBC station slug to its `.isml` filename.

    Args:
        slug: BBC slug (e.g. "bbc_radio_one").

    Returns:
        The `.isml` filename for the live HLS presentation.
    """
    return ISML_EXCEPTIONS.get(slug, f"{slug}.isml")


def slug_to_provider_id(slug: str) -> str:
    """Map a BBC slug to the provider's `item_id` scheme.

    Args:
        slug: BBC slug (e.g. "bbc_radio_one").

    Returns:
        Provider item id (e.g. "bbc_radio_1"). Falls back to slug if unknown.
    """
    mapping = {
        "bbc_radio_one": "bbc_radio_1",
        "bbc_radio_two": "bbc_radio_2",
        "bbc_radio_three": "bbc_radio_3",
        "bbc_radio_four": "bbc_radio_4",
        "bbc_radio_5live": "bbc_radio_5live",
        "bbc_6music": "bbc_6music",
    }
    return mapping.get(slug, slug)


def _extract_section(html: str, section_id: str) -> str:
    """Return the inner HTML of a `<section id="..."> ... </section>`.

    Args:
        html: Full HTML document as a string.
        section_id: The value of the section's id attribute.

    Returns:
        The inner HTML string of the section, or an empty string if not found.
    """
    start = re.search(rf'<section[^>]+id=["\']{section_id}["\']', html, re.IGNORECASE)
    if not start:
        return ""
    tail = html[start.end() :]
    end = re.search(r"</section>", tail, re.IGNORECASE)
    return tail[: end.start()] if end else tail


# Anchor pattern: href="/sounds/play/live/<slug>" with optional aria-label.
_STATION_ANCHOR = re.compile(
    r'<a[^>]+href="/sounds/play/live/([a-z0-9_]+)"[^>]*?(?:aria-label="([^"]+)")?',
    re.IGNORECASE,
)


def _parse_stations(section_html: str) -> list[tuple[str, str]]:
    """Parse a section's HTML into a list of (slug, label).

    Args:
        section_html: Inner HTML of a stations section.

    Returns:
        A list of (slug, name) tuples.
    """
    results: list[tuple[str, str]] = []
    for match in _STATION_ANCHOR.finditer(section_html):
        slug = match.group(1)
        label = (match.group(2) or slug.replace("_", " ").title()).strip()
        results.append((slug, label))
    return results


async def scrape_bbc_sounds_stations(
    session: aiohttp.ClientSession,
) -> dict[str, dict[str, dict[str, Any]]]:
    """Fetch and parse the BBC Sounds Stations page.

    Args:
        session: An aiohttp ClientSession to use for the HTTP request.

    Returns:
        A dict with two groups, "national" and "local", each mapping
        provider ids to station metadata:
        {
          "national": { provider_id: {"name": str, "slug": str, "isml": str} },
          "local":    { provider_id: {"name": str, "slug": str, "isml": str} }
        }
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.bbc.co.uk/",
    }
    timeout = aiohttp.ClientTimeout(total=20)
    async with session.get(BBC_STATIONS_URL, headers=headers, timeout=timeout) as resp:
        resp.raise_for_status()
        html = await resp.text()

    nat_html = _extract_section(html, "national_and_regional_stations")
    loc_html = _extract_section(html, "local-stations")

    national_pairs = _parse_stations(nat_html)
    local_pairs = _parse_stations(loc_html)

    def build_map(pairs: Iterable[tuple[str, str]]) -> dict[str, dict[str, Any]]:
        data: dict[str, dict[str, Any]] = {}
        for slug, name in pairs:
            pid = slug_to_provider_id(slug)
            display = NAME_OVERRIDES.get(slug, normalise_station_name(name))
            data[pid] = {"name": display, "slug": slug, "isml": slug_to_isml(slug)}
        return data

    return {
        "national": build_map(national_pairs),
        "local": build_map(local_pairs),
    }


def merge_discovered_stations(
    discovered: dict[str, dict[str, dict[str, Any]]],
    stations: dict[str, dict[str, Any]],
    logger: Any,
) -> None:
    """Merge discovered station metadata into an existing mapping in-place.

    Args:
        discovered: Output of `scrape_bbc_sounds_stations`.
        stations: The provider's STATIONS dict to update.

    Notes:
        This merge is non-destructive for existing keys; it only fills missing fields.
    """
    for group in ("national", "local"):
        for provider_id, meta in discovered.get(group, {}).items():
            name = normalise_station_name(meta["name"])
            slug = meta["slug"]
            isml = meta["isml"]

            if provider_id not in stations:
                logger.debug(f"Adding radio {name} {slug} to stored radios")

                stations[provider_id] = {
                    "name": name,
                    "slug": slug,
                    "isml": isml,
                    "group": group,
                }
            else:
                stations[provider_id].setdefault("name", name)
                stations[provider_id].setdefault("slug", slug)
                stations[provider_id].setdefault("isml", isml)
                stations[provider_id].setdefault("group", group)

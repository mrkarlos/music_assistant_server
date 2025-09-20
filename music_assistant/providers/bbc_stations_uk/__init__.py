"""
DEMO/TEMPLATE Music Provider for Music Assistant.

This is an empty music provider with no actual implementation.
Its meant to get started developing a new music provider for Music Assistant.

"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path
from typing import TYPE_CHECKING, cast
from urllib.parse import urljoin, urlparse

import aiohttp
from music_assistant_models.config_entries import ConfigEntry, ConfigValueType, ProviderConfig
from music_assistant_models.enums import (
    ConfigEntryType,
    ContentType,
    ImageType,
    MediaType,
    ProviderFeature,
    StreamType,
)
from music_assistant_models.errors import MediaNotFoundError, UnplayableMediaError
from music_assistant_models.media_items import (
    AudioFormat,
    BrowseFolder,
    ItemMapping,
    MediaItemImage,
    MediaItemType,
    ProviderMapping,
    Radio,
    SearchResults,
)
from music_assistant_models.streamdetails import StreamDetails

from music_assistant.models.music_provider import MusicProvider

from .discovery import merge_discovered_stations, scrape_bbc_sounds_stations
from .stations import STATIONS

SUPPORTED_FEATURES = {
    ProviderFeature.SEARCH,
    ProviderFeature.BROWSE,
    # RadioBrowser doesn't support a library feature at all
    # but MA users like to favorite their radio stations and
    # have that included in backups so we store it in the config.
    ProviderFeature.LIBRARY_RADIOS,
    ProviderFeature.LIBRARY_RADIOS_EDIT,
}

CONF_STORED_RADIOS = "stored_uk_bbc_radios"

BBC_STATIONS_URL = "https://www.bbc.co.uk/sounds/stations"

ROOT_NATIONAL = "bbc:national"
ROOT_LOCAL = "bbc:local"

# Known exceptions where .isml != slug + ".isml"
ISML_EXCEPTIONS = {
    "bbc_radio_four": "bbc_radio_fourfm.isml",  # Radio 4 main feed
    "bbc_radio_5live": "bbc_radio_five_live.isml",  # five_live spelling
}

A_FILES_TPL = (
    "https://a.files.bbci.co.uk/ms6/live/3441A116-B12E-4D2F-ACA8-C1984642FA4B/"
    "audio/simulcast/hls/{region}/pc_hd_abr_v2/aks/{slug}.m3u8"  # codespell:ignore aks
)

# --- Config ------------------------------------------------------------------

# Keep this minimal: UK region only; change to "ww" if you want worldwide.
BBC_REGION = "uk"

# Default bitrate preference (can be 96000 or 320000).
DEFAULT_BITRATE = 320000

# Optional: icon paths (replace with your own assets if preferred).
STATION_ICONS_BASE_URL = (
    "https://raw.githubusercontent.com/music-assistant/music-assistant.io/main/docs/assets/icons"
)


if TYPE_CHECKING:
    from music_assistant_models.provider import ProviderManifest

    from music_assistant.mass import MusicAssistant


# provider/__init__.py (or your module file that defines setup)


async def setup(
    mass: MusicAssistant,
    manifest: ProviderManifest,
    config: ProviderConfig,
) -> UkBbcRadioStationsProvider:
    """Initialize provider(instance) with given configuration."""
    prov = UkBbcRadioStationsProvider(mass, manifest, config)

    try:
        discovered = await scrape_bbc_sounds_stations(mass.http_session)
        merge_discovered_stations(discovered, STATIONS)
    except Exception as err:
        prov.logger.warning("BBC station discovery failed at setup: %s", err)
    return prov


async def get_config_entries(
    mass: MusicAssistant,
    instance_id: str | None = None,
    action: str | None = None,
    values: dict[str, ConfigValueType] | None = None,
) -> tuple[ConfigEntry, ...]:
    """
    Return Config entries to setup this provider.
    instance_id: id of an existing provider instance (None if new instance setup).
    action: [optional] action key called from config entries UI.
    values: the (intermediate) raw values for config entries sent with the action.
    """
    # ruff: noqa: ARG001 D205
    return (
        ConfigEntry(
            # RadioBrowser doesn't support a library feature at all
            # but MA users like to favorite their radio stations and
            # have that included in backups so we store it in the config.
            key=CONF_STORED_RADIOS,
            type=ConfigEntryType.STRING,
            multi_value=True,
            label=CONF_STORED_RADIOS,
            default_value=[],
            required=False,
            hidden=True,
        ),
    )


class UkBbcRadioStationsProvider(MusicProvider):
    """
    UK BBC Radio Station  Music provider.

    Music provider for UK streams of BBC Radio Stations.


    Just like with any other subclass, make sure that if you override
    any of the default methods (such as __init__), you call the super() method.
    In most cases its not needed to override any of the builtin methods and you only
    implement the abc methods with your actual implementation.
    """

    def __init__(
        self, mass: MusicAssistant, manifest: ProviderManifest, config: ProviderConfig
    ) -> None:
        """Initialize the BBC UK Radio provider.

        Args:
            mass: The Music Assistant core instance.
            manifest: The provider manifest describing this provider.
            config: Configuration values for this provider instance.
        """
        super().__init__(mass, manifest, config)
        # Default bitrate for HLS streams (AAC). Options typically 96000 or 320000.
        self.preferred_bitrate: int = 320000

    @property
    def supported_features(self) -> set[ProviderFeature]:
        """Return the features supported by this Provider."""
        return SUPPORTED_FEATURES

    async def loaded_in_mass(self) -> None:
        """Call after the provider has been loaded."""
        # OPTIONAL
        # this is an optional method that you can implement if
        # relevant or leave out completely if not needed.
        # In most cases this can be omitted for music providers.

    async def unload(self, is_removed: bool = False) -> None:
        """
        Handle unload/close of the provider.

        Called when provider is deregistered (e.g. MA exiting or config reloading).
        is_removed will be set to True when the provider is removed from the configuration.
        """
        # OPTIONAL
        # This is an optional method that you can implement if
        # relevant or leave out completely if not needed.
        # It will be called when the provider is unloaded from Music Assistant.
        # for example to disconnect from a service or clean up resources.

    @property
    def is_streaming_provider(self) -> bool:
        """
        Return True if the provider is a streaming provider.

        This literally means that the catalog is not the same as the library contents.
        For local based providers (files, plex), the catalog is the same as the library content.
        It also means that data is if this provider is NOT a streaming provider,
        data cross instances is unique, the catalog and library differs per instance.

        Setting this to True will only query one instance of the provider for search and lookups.
        Setting this to False will query all instances of this provider for search and lookups.
        """
        # For streaming providers return True here but for local file based providers return False.
        return True

    async def search(
        self,
        search_query: str,
        media_types: list[MediaType],  # must be a list, not set|None
        limit: int = 25,
    ) -> SearchResults:
        """Search stations by name/id/slug (radios only)."""
        # Defensive: treat empty list as radios
        types = media_types or [MediaType.RADIO]

        results = SearchResults()
        if MediaType.RADIO in types:
            q = (search_query or "").strip().lower()
            radios: list[Radio] = []
            for pid, meta in STATIONS.items():
                name = (meta.get("name") or "").lower()
                slug = (meta.get("slug") or "").lower()
                if not q or q in name or q in pid.lower() or q in slug:
                    radios.append(self._parse_radio(pid))
                    if len(radios) >= limit:
                        break
            results.radio = radios
        return results

    # --- Library / Browse ----------------------------------------------------

    async def get_library_radios(self) -> AsyncGenerator[Radio, None]:
        """Yield all available BBC Radio stations from the provider."""
        for prov_id in STATIONS:
            yield self._parse_radio(prov_id)

    async def get_radio(self, prov_radio_id: str) -> Radio:
        """Return details for a single BBC Radio station by its provider id."""
        if prov_radio_id not in STATIONS:
            raise MediaNotFoundError("Station not found")
        return self._parse_radio(prov_radio_id)

    async def browse(self, path: str) -> list[MediaItemType | ItemMapping | BrowseFolder]:
        """Two-level browser: root → (national|local) → station items."""
        scheme = self.instance_id or self.domain or "bbc_stations_uk"
        prefix = f"{scheme}://"

        def canon(p: str | None) -> str:
            """Normalize a browse path: strip provider prefix + slashes."""
            s = (p or "").strip()
            # strip leading repeats of "<scheme>://"
            while s.startswith(prefix):
                s = s[len(prefix) :]
            # normalize slashes
            return s.lstrip("/").removesuffix("/")

        cp = canon(path)

        # Root: empty, "root", or provider prefix
        if cp in ("", "root"):
            return [
                BrowseFolder(item_id="national", provider=self.lookup_key, name="BBC — National"),
                BrowseFolder(item_id="local", provider=self.lookup_key, name="BBC — Local"),
            ]

        if cp == "national":
            prov_ids = sorted(
                pid for pid, meta in STATIONS.items() if meta.get("group") == "national"
            )
            return [self._parse_radio(pid) for pid in prov_ids]

        if cp == "local":
            prov_ids = sorted(pid for pid, meta in STATIONS.items() if meta.get("group") == "local")
            return [self._parse_radio(pid) for pid in prov_ids]

        # Direct station id (e.g. when MA passes a concrete item_id)
        if cp in STATIONS:
            return [self._parse_radio(cp)]

        # Fallback: everything
        return [self._parse_radio(pid) for pid in sorted(STATIONS)]

    # -- Library Add/Remove functions

    async def library_add(self, item: MediaItemType) -> bool:
        """Add item to provider's library. Return true on success."""
        stored_radios = self.config.get_value(CONF_STORED_RADIOS)
        if TYPE_CHECKING:
            stored_radios = cast("list[str]", stored_radios)
        if item.item_id in stored_radios:
            return False
        self.logger.debug("Adding radio %s to stored radios", item.item_id)
        stored_radios = [*stored_radios, item.item_id]
        self.update_config_value(CONF_STORED_RADIOS, stored_radios)
        return True

    async def library_remove(self, prov_item_id: str, media_type: MediaType) -> bool:
        """Remove item from provider's library. Return true on success."""
        stored_radios = self.config.get_value(CONF_STORED_RADIOS)
        if TYPE_CHECKING:
            stored_radios = cast("list[str]", stored_radios)
        if prov_item_id not in stored_radios:
            return False
        self.logger.debug("Removing radio %s from stored radios", prov_item_id)
        stored_radios = [x for x in stored_radios if x != prov_item_id]
        self.update_config_value(CONF_STORED_RADIOS, stored_radios)
        return True

    # --- Playback ------------------------------------------------------------

    async def get_stream_details(self, item_id: str, media_type: MediaType) -> StreamDetails:
        """Get streamdetails for a BBC radio station."""
        if media_type != MediaType.RADIO:
            raise UnplayableMediaError(f"Unsupported media type: {media_type}")
        if item_id not in STATIONS:
            raise MediaNotFoundError(f"Unknown station: {item_id}")

        station = STATIONS[item_id]
        # 1) Discover current Akamai pool via a.files manifest
        variant_url = await self._discover_variant_url(station["slug"])
        # 2) Convert to stable (non-token) UK no-rewind URL at preferred bitrate
        stable_url = self._to_static_url(variant_url, station["isml"], self.preferred_bitrate)

        return StreamDetails(
            item_id=item_id,
            provider=self.lookup_key,
            audio_format=AudioFormat(
                content_type=ContentType.AAC,  # BBC HLS = AAC-LC
                channels=2,
            ),
            media_type=MediaType.RADIO,
            stream_type=StreamType.HLS,
            path=stable_url,
            allow_seek=False,
            can_seek=False,
            duration=0,
        )

    async def on_streamed(self, streamdetails: StreamDetails) -> None:
        """Call when a stream finished playing."""
        # Nothing to clean up in this minimal provider.
        self.logger.debug(
            f"BBC station {streamdetails.item_id} streamed for {streamdetails.seconds_streamed} s"
        )

    # --- Helpers -------------------------------------------------------------

    def _root_uri(self) -> str:
        """Return the root URI for this provider (e.g. 'bbc_stations_uk://')."""
        # prefer instance_id (unique per install); fallback to domain
        scheme = self.instance_id or self.domain or "bbc_stations_uk"
        return f"{scheme}://"

    async def resolve_image(self, path: str) -> str | bytes:
        """
        Resolve an image reference for this provider.

        Args:
            path: Input path or URL. May be a full URL, a local provider-prefixed path
                like "/providers/<domain>/icons/foo.png", or a plain "icons/foo.png".

        Returns:
            Either raw bytes (for local icon files) or the original string (for remote URLs).

        Notes:
            - Strips the "/providers/<domain>/" prefix if present.
            - Looks in the provider's local "icons/" folder for matching files.
            - If found, returns the file contents as bytes so MA can serve it.
            - Otherwise, the path is returned unchanged (e.g. http/https URL).
        """
        # normalize any stray /providers/<domain>/ prefix back to local path
        prefix = f"/providers/{self.domain}/"
        path = path.removeprefix(prefix)  # -> "icons/fivelive.png"

        if path.startswith("icons/"):
            local_path = Path(__file__).parent / path
            if local_path.exists():
                return local_path.read_bytes()
        return path  # pass through http(s) URLs unchanged

    def _parse_radio(self, prov_id: str) -> Radio:
        st = STATIONS[prov_id]
        radio = Radio(
            provider=self.lookup_key,
            item_id=prov_id,
            name=st["name"],
            provider_mappings={
                ProviderMapping(
                    provider_domain=self.domain,
                    provider_instance=self.instance_id,
                    item_id=prov_id,
                    available=True,
                )
            },
        )
        # Optional icon (replace with your own assets as needed)
        icon_file = st.get("icon")
        if icon_file:
            radio.metadata.add_image(
                MediaItemImage(
                    provider=self.lookup_key,
                    type=ImageType.THUMB,
                    path=f"icons/{st['icon']}",
                    remotely_accessible=False,  # important: triggers resolve_image()
                )
            )
        return radio

    async def _discover_variant_url(self, slug: str, region: str = BBC_REGION) -> str:
        """Resolve BBC entry manifest to the Akamai .isml playlist for a station.

        Args:
            slug: Station slug (e.g. "bbc_radio_one").
            region: BBC region code ("uk" or "ww").

        Returns:
            Final playlist URL containing `.isml` in its path.

        Raises:
            UnplayableMediaError: If the expected child playlist or .isml URL
                cannot be resolved.
        """
        entry = A_FILES_TPL.format(region=region, slug=slug)
        timeout = aiohttp.ClientTimeout(total=10)

        # Fetch the entry manifest
        async with self.mass.http_session.get(entry, timeout=timeout, allow_redirects=True) as r:
            r.raise_for_status()
            body = await r.text()

        # Extract first child m3u8 from manifest body
        child = next(
            (
                line
                for line in (ln.strip() for ln in body.splitlines())
                if line and not line.startswith("#") and line.endswith(".m3u8")
            ),
            None,
        )
        if child is None:
            raise UnplayableMediaError(f"No child playlist found in {entry}")

        if not child.startswith("http"):
            child = urljoin(entry, child)

        # Follow redirects on the child URL
        async with self.mass.http_session.get(child, timeout=timeout, allow_redirects=True) as r2:
            r2.raise_for_status()
            final_url = str(r2.url)

        # Guard: ensure final URL contains `.isml`
        if ".isml" not in final_url:
            raise UnplayableMediaError(f"Resolved URL did not contain .isml: {final_url}")

        return final_url

    def _to_static_url(self, any_m3u8_url: str, isml: str, bitrate: int) -> str:
        """Trim to the .isml directory and append a non-rewind variant at the chosen bitrate."""
        # We avoid urlparse joins to keep it robust across Akamai variants.
        # Example in → https://as-hls-uk-live.akamaized.net/pool_x/live/uk/<slug>/<isml>/playlist.m3u8?...
        #  → out: .../<isml>/<slug>-audio=<bitrate>.norewind.m3u8
        # Extract scheme://netloc and path:

        p = urlparse(any_m3u8_url)
        parts = [seg for seg in p.path.split("/") if seg]
        try:
            idx = parts.index(isml)
        except ValueError as exc:
            raise UnplayableMediaError(f"Expected {isml} in path: {any_m3u8_url}") from exc

        base = "/" + "/".join(parts[: idx + 1])
        slug_no_ext = isml.replace(".isml", "")
        return f"{p.scheme}://{p.netloc}{base}/{slug_no_ext}-audio={bitrate}.norewind.m3u8"

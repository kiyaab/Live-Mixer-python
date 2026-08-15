"""Routing matrix for flexible signal paths."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class RouteDestination(Enum):
    MAIN = auto()
    MONITOR = auto()
    FX = auto()
    RECORD = auto()
    NONE = auto()


@dataclass
class ChannelRoute:
    """Routing configuration for a single channel."""

    input_index: int
    destinations: set[RouteDestination] = field(
        default_factory=lambda: {RouteDestination.MAIN}
    )
    pre_fader: bool = False


class RoutingEngine:
    """
    Manages input-to-channel and channel-to-bus routing.

    Phase 1 uses direct 1:1 input mapping; matrix routing expands in Phase 4.
    """

    def __init__(self, num_channels: int) -> None:
        self._routes: list[ChannelRoute] = [
            ChannelRoute(input_index=i) for i in range(num_channels)
        ]

    @property
    def num_channels(self) -> int:
        return len(self._routes)

    def get_input_for_channel(self, channel_index: int) -> int:
        return self._routes[channel_index].input_index

    def set_input_for_channel(self, channel_index: int, input_index: int) -> None:
        self._routes[channel_index].input_index = input_index

    def get_destinations(self, channel_index: int) -> set[RouteDestination]:
        return set(self._routes[channel_index].destinations)

    def set_destinations(
        self, channel_index: int, destinations: set[RouteDestination]
    ) -> None:
        self._routes[channel_index].destinations = destinations

    def add_destination(
        self, channel_index: int, destination: RouteDestination
    ) -> None:
        self._routes[channel_index].destinations.add(destination)

    def remove_destination(
        self, channel_index: int, destination: RouteDestination
    ) -> None:
        self._routes[channel_index].destinations.discard(destination)

    def is_routed_to(self, channel_index: int, destination: RouteDestination) -> bool:
        return destination in self._routes[channel_index].destinations

    def to_dict(self) -> list[dict]:
        return [
            {
                "input_index": r.input_index,
                "destinations": [d.name for d in r.destinations],
                "pre_fader": r.pre_fader,
            }
            for r in self._routes
        ]

    def from_dict(self, data: list[dict]) -> None:
        for i, route_data in enumerate(data):
            if i >= len(self._routes):
                break
            self._routes[i].input_index = route_data.get("input_index", i)
            dest_names = route_data.get("destinations", ["MAIN"])
            self._routes[i].destinations = {
                RouteDestination[name] for name in dest_names
            }
            self._routes[i].pre_fader = route_data.get("pre_fader", False)

"""Tests for routing engine."""

import pytest

from audio.routing import RouteDestination, RoutingEngine


class TestRoutingEngine:
    def test_default_1_to_1_mapping(self):
        router = RoutingEngine(4)
        for i in range(4):
            assert router.get_input_for_channel(i) == i

    def test_reassign_input(self):
        router = RoutingEngine(4)
        router.set_input_for_channel(0, 3)
        assert router.get_input_for_channel(0) == 3

    def test_default_main_destination(self):
        router = RoutingEngine(2)
        assert router.is_routed_to(0, RouteDestination.MAIN)
        assert router.is_routed_to(1, RouteDestination.MAIN)

    def test_add_monitor_destination(self):
        router = RoutingEngine(2)
        router.add_destination(1, RouteDestination.MONITOR)
        assert router.is_routed_to(1, RouteDestination.MAIN)
        assert router.is_routed_to(1, RouteDestination.MONITOR)

    def test_serialization_roundtrip(self):
        router = RoutingEngine(2)
        router.set_input_for_channel(1, 0)
        router.add_destination(0, RouteDestination.FX)
        data = router.to_dict()
        router2 = RoutingEngine(2)
        router2.from_dict(data)
        assert router2.get_input_for_channel(1) == 0
        assert router2.is_routed_to(0, RouteDestination.FX)

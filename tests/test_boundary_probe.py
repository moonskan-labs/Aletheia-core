"""The optional stage probe cannot spend past its declared cap or alter pilot inputs."""

import importlib
from pathlib import Path

import httpx
import pytest

from aletheia.providers.errors import ErrorCode, ProviderError


@pytest.fixture
def probe(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    return importlib.import_module("probe_phase_one_boundaries")


def test_probe_uses_six_historical_claims_and_four_method_controls(probe):
    selected, _ = probe.cases()
    assert len(selected) == 10 and len({id for id, _ in selected}) == 10
    assert sum(probe.frozen_source(id) is not None for id in probe.CASE_IDS) == 5
    venus = probe.frozen_source("b0002")
    assert "58 million km" in venus.original_text and "108 million km" in venus.original_text
    assert "Stage diagnostic" in venus.limitations[0]


async def test_attempt_cap_rejects_before_any_network_call(probe):
    attempts = [{} for _ in range(probe.CAP)]
    transport = probe.CappedTransport("nebius", attempts)
    try:
        with pytest.raises(ProviderError) as error:
            await transport.handle_async_request(httpx.Request("POST", "https://model.invalid"))
        assert error.value.code == ErrorCode.BUDGET
        assert len(attempts) == probe.CAP
    finally:
        await transport.aclose()

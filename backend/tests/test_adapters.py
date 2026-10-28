import pytest
from app.services.adapters.registry import adapter_registry
from app.services.adapters.mock import MockAdapter
from app.core.exceptions import UnsupportedPlatformError

@pytest.mark.asyncio
async def test_mock_adapter_analysis():
    adapter = adapter_registry.find_adapter("mock-media.anydown.local", "https://mock-media.anydown.local/test-video")
    assert isinstance(adapter, MockAdapter)

    res = await adapter.analyze("https://mock-media.anydown.local/test-video")
    assert res.platform == "mock"
    assert len(res.formats) >= 3
    assert any(f.format_id == "mock-1080p" for f in res.formats)
    assert any(f.format_id == "mock-mp3" for f in res.formats)
    assert any(f.format_id == "mock-jpg" for f in res.formats)

def test_adapter_registry_lookup():
    # YouTube
    yt = adapter_registry.find_adapter("www.youtube.com", "https://www.youtube.com/watch?v=123")
    assert yt.id == "youtube"

    # Instagram
    insta = adapter_registry.find_adapter("instagram.com", "https://instagram.com/reel/123")
    assert insta.id == "instagram"

    # Unsupported domain
    with pytest.raises(UnsupportedPlatformError):
        adapter_registry.find_adapter("unknown-domain.invalid", "https://unknown-domain.invalid/video")

def test_capabilities_export():
    caps = adapter_registry.get_all_capabilities()
    assert len(caps) >= 8
    # Ensure all caps have policies
    for c in caps:
        assert c.name
        assert c.policy_notice
        assert len(c.supported_formats) > 0

def test_ytdlp_base_opts_has_player_clients():
    from app.services.adapters.ytdlp_base import get_base_ydl_opts
    opts = get_base_ydl_opts()
    assert 'extractor_args' in opts
    yt_args = opts['extractor_args'].get('youtube', {})
    assert 'android' in yt_args.get('player_client', [])
    assert 'webpage' in yt_args.get('player_skip', [])
    assert 'User-Agent' in opts.get('http_headers', {})


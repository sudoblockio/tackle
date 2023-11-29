
from tackle import tackle

def test_native_hook_lock(base_hooks_dir):
    output = tackle(raw_input={'data->': 'provider_cache_data'})

    assert 'hook_type' in output['data'][0]
    assert len(output['data']) > 100

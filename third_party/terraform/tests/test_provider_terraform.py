# import os
# import pytest
#
# from tackle import tackle
# from tackle.utils.paths import rmtree
#
#
# # TODO: Need to be able test pyinquirer
# def test_provider_terraform():
#     """Verify the hook call works successfully."""
#     output = tackle(no_input=True)
#
#     assert not output['cloudflare_enable']
#
#
# def test_provider_terraform_remote():
#     """Verify the hook call works successfully."""
#     output = tackle("https://github.com/insight-w3f/terraform-polkadot-k8s-config",
#                     no_input=True)
#     assert output
#
#
# @pytest.fixture()
# def clean_up_tf():
#     yield
#     output_files = ["terraform0.13.6", "testing-path"]
#     for o in output_files:
#         if os.path.isfile(o):
#             os.remove(o)
#         if os.path.isdir(o):
#             rmtree(o)
#
#
# def test_provider_terraform_install(clean_up_tf):
#     """Verify the hook call works successfully."""
#     output = tackle('install.yaml', no_input=True)
#
#     assert '0.12.29' not in output['version_13']
#     assert len(output['version']) > 30
#     assert "You can update" in output['check_basic']
#     assert "You can update" in output['check_path']
#
#
# @pytest.mark.slow
# def test_provider_terraform_terragrunt_install(clean_up_tf):
#     """Verify the hook call works successfully."""
#     output = tackle('install.yaml', no_input=True)
#
#     assert output

"""Tool portability stays local; these tests never start a provider process."""
from pathlib import Path
import pytest
import save_provider_acceptance as acceptance


def test_windows_cli_uses_derived_checkout_and_narrow_tool_settings(monkeypatch,tmp_path):
    calls=[]
    monkeypatch.setattr(acceptance,'WINDOWS',True)
    monkeypatch.setattr(acceptance,'ROOT',tmp_path)
    monkeypatch.setattr(acceptance,'WSL',['wsl','-d','fixture-linux'])
    monkeypatch.setenv('SAVE_TEST_CLI_PATH','/opt/test-tools/supabase')
    def output(args,**kwargs):
        calls.append(args)
        return '/mnt/fixture/checkout\n'
    monkeypatch.setattr(acceptance.subprocess,'check_output',output)
    command=acceptance.cli_command()
    assert calls==[['wsl','-d','fixture-linux','-e','wslpath','-a',str(tmp_path)]]
    assert command==['wsl','-d','fixture-linux','--cd','/mnt/fixture/checkout','-e','env',
                     'DOCKER_HOST='+acceptance.DOCKER_SOCKET,'/opt/test-tools/supabase']


def test_native_cli_tool_override_has_no_hosted_target(monkeypatch):
    monkeypatch.setattr(acceptance,'WINDOWS',False)
    monkeypatch.setenv('SAVE_TEST_CLI_PATH','/opt/test-tools/supabase')
    assert acceptance.cli_command()==['env','DOCKER_HOST='+acceptance.DOCKER_SOCKET,'/opt/test-tools/supabase']


@pytest.mark.parametrize('url', ['https://hosted.supabase.co','http://10.0.0.4:54421',
                              'http://localhost:54321','http://user:secret@localhost:54421'])
def test_acceptance_refuses_hosted_remote_or_wrong_project_api(url):
    with pytest.raises(AssertionError): acceptance.local_api_url({'API_URL':url})


def test_local_container_identity_is_exact(monkeypatch):
    monkeypatch.setattr(acceptance.subprocess,'check_output',lambda *args,**kwargs:acceptance.DB_CONTAINER+'-other\n')
    with pytest.raises(AssertionError): acceptance.assert_local_stack()
    monkeypatch.setattr(acceptance.subprocess,'check_output',lambda *args,**kwargs:acceptance.DB_CONTAINER+'\n')
    acceptance.assert_local_stack()


def test_local_url_uses_validated_wsl_interface_and_fixed_port(monkeypatch):
    monkeypatch.setattr(acceptance,'WINDOWS',True)
    monkeypatch.setattr(acceptance.subprocess,'check_output',lambda *args,**kwargs:'172.24.1.2\n')
    assert acceptance.local_api_url({'API_URL':'http://127.0.0.1:54421'})=='http://172.24.1.2:54421'

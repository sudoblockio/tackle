from tackle import BaseHook, Field
import paramiko


class SshInteractiveQuery(BaseHook):
    """Interactive shell session hook."""

    hook_type = "ssh_interactive"

    # fmt: off
    host: str = Field(None, description="Host address.")
    username: str = Field(..., description="User name used to authenticate.")
    port: int = Field(22, description="Connection port number.")
    password: str = Field(None, description="Optional password used to authenticate.")
    key_filename: str = Field(None, description="Private key file path.")

    # fmt: on

    def interactive(self):
        pass

    def exec(self):
        try:
            import interactive
        except ImportError:
            from . import interactive

        client = paramiko.SSHClient()

        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(
            self.host, username=self.username, key_filename=self.key_filename
        )
        channel = client.get_transport().open_session()
        channel.get_pty()
        channel.invoke_shell()

        interactive.interactive_shell(channel)
        client.close()

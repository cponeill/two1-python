"""Open your 21.co profile in a web browser."""
# standard python imports
import logging
import webbrowser
import json as jsonlib

# 3rd party importss
import click

# two1 imports
import two1
import two1.commands.status
from two1 import TWO1_WWW_HOST
from two1.wallet import Wallet
from two1.server import rest_client
from two1.server.machine_auth_wallet import MachineAuthWallet
from two1.commands.util import decorators
from two1.commands.config import Config

# Creates a ClickLogger
logger = logging.getLogger(__name__)

# Captures username
wallet = Wallet()
username = Config().username
client = rest_client.TwentyOneRestClient(two1.TWO1_HOST, MachineAuthWallet(wallet), username)

@click.command()
@click.option('--json', default=False, is_flag=True, help='Uses JSON Output')
@click.pass_context
@decorators.catch_all
@decorators.check_notifications
@decorators.capture_usage
def profile(ctx, json):
    """Open your 21.co profile in a web browser."""
    #_profile(ctx.obj['config'].username)
    if json:
        _search_profile(ctx.obj['config'].username, "%s/%s" % (TWO1_WWW_HOST, ctx.obj['config'].username)
    else:
        _profile(ctx.obj['config'].username)

def _profile(username):
    url = "%s/%s" % (TWO1_WWW_HOST, username)
    webbrowser.open(url)

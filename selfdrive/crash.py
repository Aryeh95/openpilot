"""Install exception handler for process crash."""
import os
import sys
from selfdrive.version import version, dirty

from selfdrive.swaglog import cloudlog

if os.getenv("NOLOG") or os.getenv("NOCRASH"):
  def capture_exception(*exc_info):
    pass
  def bind_user(**kwargs):
    pass
  def bind_extra(**kwargs):
    pass
  def install():
    pass
else:
  from raven import Client
  from raven.transport.http import HTTPTransport
  client = Client('https://69bc2e046a1e43df9759bbcfb4b84bc8:095b70312c16499fbc14bf44bde7a4ed@sentry.io/1406472',
                  install_sys_hook=False, transport=HTTPTransport, release=version, tags={'dirty': dirty})

  def capture_exception(*args, **kwargs):
    client.captureException(*args, **kwargs)
    cloudlog.error("crash", exc_info=kwargs.get('exc_info', 1))

  def bind_user(**kwargs):
    client.user_context(kwargs)

  def bind_extra(**kwargs):
    client.extra_context(kwargs)

  def install():
    # installs a sys.excepthook
    __excepthook__ = sys.excepthook
    def handle_exception(*exc_info):
      if exc_info[0] not in (KeyboardInterrupt, SystemExit):
        capture_exception(exc_info=exc_info)
      __excepthook__(*exc_info)
    sys.excepthook = handle_exception

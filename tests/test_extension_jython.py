# -*- coding: utf-8 -*-

import os
import sys
import unittest


PROJECT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_DIRECTORY not in sys.path:
    sys.path.insert(0, PROJECT_DIRECTORY)

try:
    from burp import IContextMenuInvocation
    BURP_API_AVAILABLE = True
except ImportError:
    BURP_API_AVAILABLE = False


class _FakeResponseInfo(object):
    def __init__(self, headers):
        self._headers = headers

    def getHeaders(self):
        return self._headers


class _FakeHelpers(object):
    def __init__(self, headers):
        self._headers = headers

    def analyzeResponse(self, response):
        return _FakeResponseInfo(self._headers)


class _FakeCallbacks(object):
    def __init__(self, headers):
        self.helpers = _FakeHelpers(headers)
        self.output = []
        self.errors = []
        self.alerts = []
        self.extension_name = None
        self.menu_factory = None

    def getHelpers(self):
        return self.helpers

    def getExtensionFilename(self):
        return os.path.join(PROJECT_DIRECTORY, "SetCookieToCookie.py")

    def setExtensionName(self, name):
        self.extension_name = name

    def registerContextMenuFactory(self, factory):
        self.menu_factory = factory

    def printOutput(self, message):
        self.output.append(message)

    def printError(self, message):
        self.errors.append(message)

    def issueAlert(self, message):
        self.alerts.append(message)


class _FakeMessage(object):
    def __init__(self, response):
        self._response = response

    def getResponse(self):
        return self._response


class _FakeInvocation(object):
    def __init__(self, context, response):
        self._context = context
        self._response = response

    def getInvocationContext(self):
        return self._context

    def getSelectedMessages(self):
        return [_FakeMessage(self._response)]


@unittest.skipUnless(BURP_API_AVAILABLE, "requires Jython and the Burp API")
class ExtensionJythonTests(unittest.TestCase):
    def _extension(self, headers):
        from SetCookieToCookie import BurpExtender

        callbacks = _FakeCallbacks(headers)
        extension = BurpExtender()
        extension.registerExtenderCallbacks(callbacks)
        return extension, callbacks

    def test_registers_name_and_context_menu_factory(self):
        extension, callbacks = self._extension([])

        self.assertEqual("Set-Cookie to Cookie", callbacks.extension_name)
        self.assertIs(extension, callbacks.menu_factory)

    def test_burp_style_execfile_without_dunder_file_loads(self):
        extension_path = os.path.join(PROJECT_DIRECTORY, "SetCookieToCookie.py")
        namespace = {"__name__": "burp_execfile_extension"}

        execfile(extension_path, namespace)
        callbacks = _FakeCallbacks([])
        extension = namespace["BurpExtender"]()
        extension.registerExtenderCallbacks(callbacks)

        self.assertEqual("Set-Cookie to Cookie", callbacks.extension_name)
        self.assertIs(extension, callbacks.menu_factory)

    def test_response_menu_action_copies_complete_cookie_header(self):
        import SetCookieToCookie
        from java.awt.datatransfer import Clipboard, DataFlavor

        headers = [
            "HTTP/1.1 200 OK",
            "Set-Cookie: sid=abc; Path=/",
            "Set-Cookie: theme=dark; SameSite=Lax",
        ]
        extension, callbacks = self._extension(headers)
        clipboard = Clipboard("synthetic test clipboard")

        class TestToolkit(object):
            @staticmethod
            def getDefaultToolkit():
                return TestToolkit()

            def getSystemClipboard(self):
                return clipboard

        invocation = _FakeInvocation(
            IContextMenuInvocation.CONTEXT_MESSAGE_VIEWER_RESPONSE,
            bytearray(b"response"),
        )

        menu_items = extension.createMenuItems(invocation)
        self.assertEqual(1, len(menu_items))
        listeners = menu_items[0].getActionListeners()
        toolkit = SetCookieToCookie.Toolkit
        try:
            SetCookieToCookie.Toolkit = TestToolkit
            listeners[0].actionPerformed(None)
        finally:
            SetCookieToCookie.Toolkit = toolkit
        self.assertEqual(
            "Cookie: sid=abc; theme=dark",
            clipboard.getData(DataFlavor.stringFlavor),
        )
        self.assertEqual(["Copied 2 cookies to the clipboard."], callbacks.alerts)
        self.assertEqual([], callbacks.errors)

    def test_request_context_has_no_menu_item(self):
        extension, callbacks = self._extension(["Set-Cookie: sid=abc"])
        invocation = _FakeInvocation(
            IContextMenuInvocation.CONTEXT_MESSAGE_VIEWER_REQUEST,
            bytearray(b"request"),
        )

        self.assertIsNone(extension.createMenuItems(invocation))

    def test_cookieless_response_has_no_menu_item(self):
        extension, callbacks = self._extension(["HTTP/1.1 204 No Content"])
        invocation = _FakeInvocation(
            IContextMenuInvocation.CONTEXT_MESSAGE_EDITOR_RESPONSE,
            bytearray(b"response"),
        )

        self.assertIsNone(extension.createMenuItems(invocation))

    def test_java_parser_error_does_not_log_response_data(self):
        from java.lang import IllegalArgumentException

        def fail(response):
            raise IllegalArgumentException("synthetic-cookie-value")

        extension, callbacks = self._extension([])
        callbacks.helpers.analyzeResponse = fail
        invocation = _FakeInvocation(
            IContextMenuInvocation.CONTEXT_MESSAGE_EDITOR_RESPONSE,
            bytearray(b"response"),
        )

        self.assertIsNone(extension.createMenuItems(invocation))
        self.assertEqual(["Could not inspect the selected response."], callbacks.errors)
        self.assertEqual([], callbacks.alerts)


if __name__ == "__main__":
    unittest.main()

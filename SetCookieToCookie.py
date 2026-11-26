# -*- coding: utf-8 -*-
"""Burp/Jython extension: copy response Set-Cookie headers as one Cookie header."""

import os

from burp import IBurpExtender
from burp import IContextMenuFactory
from burp import IContextMenuInvocation
from java.awt import Toolkit
from java.awt.datatransfer import StringSelection
from java.awt.event import ActionListener
from java.lang import Exception as JavaException
from javax.swing import JMenuItem


class _CopyCookieHeaderAction(ActionListener):
    def __init__(self, extension, message):
        self._extension = extension
        self._message = message

    def actionPerformed(self, event):
        self._extension.copy_response_cookies(self._message)


class BurpExtender(IBurpExtender, IContextMenuFactory):
    EXTENSION_NAME = "Set-Cookie to Cookie"
    MENU_LABEL = "Copy Set-Cookie as Cookie header"

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self._load_cookie_helpers(callbacks)

        callbacks.setExtensionName(self.EXTENSION_NAME)
        callbacks.registerContextMenuFactory(self)
        callbacks.printOutput(
            "%s loaded. Right-click a response containing Set-Cookie."
            % self.EXTENSION_NAME
        )

    def createMenuItems(self, invocation):
        try:
            if invocation is None or not self._is_response_context(invocation):
                return None

            messages = invocation.getSelectedMessages()
            if messages is None or len(messages) == 0:
                return None

            message = messages[0]
            if not self._response_cookie_pairs(message):
                return None

            menu_item = JMenuItem(self.MENU_LABEL)
            menu_item.addActionListener(_CopyCookieHeaderAction(self, message))
            return [menu_item]
        except (Exception, JavaException):
            self._callbacks.printError("Could not inspect the selected response.")
            return None

    def _load_cookie_helpers(self, callbacks):
        # Burp loads Jython extensions with execfile() and does not define
        # __file__. The callbacks API is therefore the reliable way to locate
        # modules shipped next to the extension.
        extension_filename = callbacks.getExtensionFilename()
        extension_directory = os.path.dirname(os.path.abspath(extension_filename))
        namespace = {"__name__": "set_cookie_to_cookie_helpers"}
        execfile(os.path.join(extension_directory, "cookie_header.py"), namespace)
        self._extract_cookie_pairs = namespace["extract_cookie_pairs"]
        self._format_cookie_header = namespace["format_cookie_header"]

    def _response_cookie_pairs(self, message):
        response = message.getResponse()
        if not response:
            return []
        headers = self._helpers.analyzeResponse(response).getHeaders()
        return self._extract_cookie_pairs(headers)

    def copy_response_cookies(self, message):
        try:
            pairs = self._response_cookie_pairs(message)
        except (Exception, JavaException):
            self._report_error("Could not inspect the selected response.")
            return
        if not pairs:
            self._callbacks.issueAlert("The selected response has no valid Set-Cookie headers.")
            return
        self.copy_to_clipboard(self._format_cookie_header(pairs), len(pairs))

    def _is_response_context(self, invocation):
        context = invocation.getInvocationContext()
        return context in (
            IContextMenuInvocation.CONTEXT_MESSAGE_EDITOR_RESPONSE,
            IContextMenuInvocation.CONTEXT_MESSAGE_VIEWER_RESPONSE,
        )

    def copy_to_clipboard(self, cookie_header, cookie_count):
        try:
            clipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
            clipboard.setContents(StringSelection(cookie_header), None)
        except (Exception, JavaException):
            self._report_error("Could not write to the system clipboard.")
            return

        self._callbacks.issueAlert(
            "Copied %d cookie%s to the clipboard."
            % (cookie_count, "" if cookie_count == 1 else "s")
        )

    def _report_error(self, message):
        self._callbacks.printError(message)
        self._callbacks.issueAlert(message)

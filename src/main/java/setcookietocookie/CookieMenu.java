package setcookietocookie;

import burp.api.montoya.http.message.responses.HttpResponse;
import burp.api.montoya.logging.Logging;
import burp.api.montoya.ui.contextmenu.ContextMenuEvent;
import burp.api.montoya.ui.contextmenu.ContextMenuItemsProvider;
import burp.api.montoya.ui.contextmenu.MessageEditorHttpRequestResponse;

import javax.swing.JMenuItem;
import java.awt.Component;
import java.util.List;
import java.util.function.Consumer;

final class CookieMenu implements ContextMenuItemsProvider {
    private static final String INSPECT_ERROR = "Could not inspect the selected response.";
    private static final String CLIPBOARD_ERROR = "Could not write to the system clipboard.";

    private final Logging logging;
    private final Consumer<String> clipboard;

    CookieMenu(Logging logging, Consumer<String> clipboard) {
        this.logging = logging;
        this.clipboard = clipboard;
    }

    @Override
    public List<Component> provideMenuItems(ContextMenuEvent event) {
        try {
            var editor = event.messageEditorRequestResponse().orElse(null);
            if (editor == null || editor.selectionContext() != MessageEditorHttpRequestResponse.SelectionContext.RESPONSE) {
                return List.of();
            }
            HttpResponse response = editor.requestResponse().response();
            if (response == null || CookieHeader.from(response.headers()).isEmpty()) return List.of();

            JMenuItem item = new JMenuItem("Copy Set-Cookie as Cookie header");
            item.addActionListener(ignored -> copyCookies(response));
            return List.of(item);
        } catch (RuntimeException ignored) {
            logging.logToError(INSPECT_ERROR);
            return List.of();
        }
    }

    private void copyCookies(HttpResponse response) {
        String header;
        try {
            header = CookieHeader.from(response.headers());
        } catch (RuntimeException ignored) {
            reportError(INSPECT_ERROR);
            return;
        }
        if (header.isEmpty()) {
            logging.raiseInfoEvent("The selected response has no valid Set-Cookie headers.");
            return;
        }

        try {
            clipboard.accept(header);
        } catch (RuntimeException ignored) {
            reportError(CLIPBOARD_ERROR);
            return;
        }
        logging.raiseInfoEvent("Copied the Cookie header to the system clipboard.");
    }

    private void reportError(String message) {
        logging.logToError(message);
        logging.raiseErrorEvent(message);
    }
}

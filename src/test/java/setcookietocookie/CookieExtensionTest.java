package setcookietocookie;

import burp.api.montoya.BurpExtension;
import burp.api.montoya.http.message.HttpHeader;
import burp.api.montoya.http.message.HttpRequestResponse;
import burp.api.montoya.http.message.responses.HttpResponse;
import burp.api.montoya.logging.Logging;
import burp.api.montoya.ui.contextmenu.ContextMenuEvent;
import burp.api.montoya.ui.contextmenu.MessageEditorHttpRequestResponse;

import javax.swing.JMenuItem;
import java.awt.datatransfer.Clipboard;
import java.awt.datatransfer.DataFlavor;
import java.awt.datatransfer.StringSelection;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.ServiceLoader;

import static burp.api.montoya.ui.contextmenu.MessageEditorHttpRequestResponse.SelectionContext.REQUEST;
import static burp.api.montoya.ui.contextmenu.MessageEditorHttpRequestResponse.SelectionContext.RESPONSE;

public final class CookieExtensionTest {
    private static final List<HttpHeader> HEADERS = List.of(
            new Header("Set-Cookie", "session=demo-only; Path=/; HttpOnly"),
            new Header("sEt-CoOkIe", "lang=en-US; Expires=Wed, 21 Oct 2030 07:28:00 GMT"),
            new Header("Set-Cookie", "session=\"token==\"; Secure"),
            new Header("Set-Cookie", "empty=; Max-Age=0"),
            new Header("Set-Cookie", "bad=1, mixed=2"),
            new Header("Set-Cookie", "bad name=value"),
            new Header("Set-Cookie", "unclosed=\"value"),
            new Header("Set-Cookie", "unsafe=value\r\nX-Injected: synthetic"),
            new Header("Cookie", "request=already-set")
    );
    private static final String EXPECTED = "Cookie: session=demo-only; lang=en-US; session=\"token==\"; empty=";

    public static void main(String[] args) throws Exception {
        assert ServiceLoader.load(BurpExtension.class).findFirst().orElseThrow()
                instanceof SetCookieToCookieExtension;
        assert EXPECTED.equals(CookieHeader.from(HEADERS));
        assert CookieHeader.from(List.of()).isEmpty();
        menuCopiesOnlyAfterClick();
        clipboardFailureDoesNotLogCookieValues();
        System.out.println("CookieExtensionTest: OK");
    }

    private static void menuCopiesOnlyAfterClick() throws Exception {
        var clipboard = new Clipboard("synthetic test clipboard");
        var info = new ArrayList<String>();
        Logging logging = (Logging) Proxy.newProxyInstance(Logging.class.getClassLoader(),
                new Class<?>[]{Logging.class}, (proxy, method, arguments) -> {
                    assert method.getName().equals("raiseInfoEvent");
                    info.add((String) arguments[0]);
                    return null;
                });
        CookieMenu menu = new CookieMenu(logging, value -> clipboard.setContents(new StringSelection(value), null));
        assert menu.provideMenuItems(event(REQUEST, HEADERS)).isEmpty();
        assert menu.provideMenuItems(event(RESPONSE, List.of(new Header("Set-Cookie", "invalid")))).isEmpty();
        var items = menu.provideMenuItems(event(RESPONSE, HEADERS));
        assert items.size() == 1;
        assert clipboard.getContents(null) == null;
        ((JMenuItem) items.get(0)).doClick(0);
        assert EXPECTED.equals(clipboard.getData(DataFlavor.stringFlavor));
        assert info.equals(List.of("Copied the Cookie header to the system clipboard."));
    }

    private static void clipboardFailureDoesNotLogCookieValues() {
        var messages = new ArrayList<String>();
        Logging logging = (Logging) Proxy.newProxyInstance(Logging.class.getClassLoader(),
                new Class<?>[]{Logging.class}, (proxy, method, arguments) -> {
                    messages.add((String) arguments[0]);
                    return null;
                });
        CookieMenu menu = new CookieMenu(logging, ignored -> {
            throw new IllegalStateException(EXPECTED);
        });
        ((JMenuItem) menu.provideMenuItems(event(RESPONSE, HEADERS)).get(0)).doClick(0);
        assert messages.equals(List.of("Could not write to the system clipboard.",
                "Could not write to the system clipboard."));
    }

    private static ContextMenuEvent event(MessageEditorHttpRequestResponse.SelectionContext context,
                                          List<HttpHeader> headers) {
        HttpResponse response = mock(HttpResponse.class, Map.of("headers", headers));
        HttpRequestResponse exchange = mock(HttpRequestResponse.class, Map.of("response", response));
        MessageEditorHttpRequestResponse editor = mock(MessageEditorHttpRequestResponse.class,
                Map.of("selectionContext", context, "requestResponse", exchange));
        return mock(ContextMenuEvent.class, Map.of("messageEditorRequestResponse", Optional.of(editor)));
    }

    private static <T> T mock(Class<T> type, Map<String, Object> values) {
        return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[]{type},
                (proxy, method, arguments) -> values.get(method.getName())));
    }

    private record Header(String name, String value) implements HttpHeader {}
}

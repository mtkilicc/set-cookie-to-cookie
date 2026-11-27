package setcookietocookie;

import burp.api.montoya.BurpExtension;
import burp.api.montoya.MontoyaApi;
import burp.api.montoya.core.Registration;

import java.awt.Toolkit;
import java.awt.datatransfer.StringSelection;

public final class SetCookieToCookieExtension implements BurpExtension {
    static final String NAME = "Set-Cookie to Cookie";

    @Override
    public void initialize(MontoyaApi api) {
        api.extension().setName(NAME);
        CookieMenu menu = new CookieMenu(api.logging(), SetCookieToCookieExtension::copyToClipboard);
        Registration registration = api.userInterface().registerContextMenuItemsProvider(menu);
        api.extension().registerUnloadingHandler(registration::deregister);
        api.logging().logToOutput(NAME + " loaded. Right-click a response containing Set-Cookie.");
    }

    private static void copyToClipboard(String value) {
        Toolkit.getDefaultToolkit().getSystemClipboard().setContents(new StringSelection(value), null);
    }
}

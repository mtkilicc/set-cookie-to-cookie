package setcookietocookie;

import burp.api.montoya.http.message.HttpHeader;

import java.util.List;
import java.util.StringJoiner;
import java.util.regex.Pattern;

final class CookieHeader {
    private static final String OCTET = "[\\x21\\x23-\\x2b\\x2d-\\x3a\\x3c-\\x5b\\x5d-\\x7e]";
    private static final Pattern PAIR = Pattern.compile(
            "[ \\t]*([!#$%&'*+.^_\\x60|~0-9A-Za-z-]+)[ \\t]*=[ \\t]*(\"" + OCTET + "*\"|" + OCTET + "*)[ \\t]*");

    static String from(List<HttpHeader> headers) {
        StringJoiner result = new StringJoiner("; ", "Cookie: ", "").setEmptyValue("");
        for (HttpHeader header : headers) {
            if (!"Set-Cookie".equalsIgnoreCase(header.name())) continue;
            String value = header.value();
            if (value.indexOf('\r') >= 0 || value.indexOf('\n') >= 0) continue;

            int attributesStart = value.indexOf(';');
            int pairEnd = attributesStart >= 0 ? attributesStart : value.length();
            var pair = PAIR.matcher(value).region(0, pairEnd);
            if (pair.matches()) result.add(pair.group(1) + "=" + pair.group(2));
        }
        return result.toString();
    }
}

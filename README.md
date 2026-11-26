# Set-Cookie to Cookie

A Jython extension for Burp Suite that turns a response's `Set-Cookie` headers into a single request-ready `Cookie` header and copies it to the clipboard.

For example, Burp may receive a response with two cookie headers.

```http
Set-Cookie: session=demo-only; Path=/; Secure; HttpOnly
Set-Cookie: lang=en-US; Expires=Wed, 21 Oct 2030 07:28:00 GMT
```

The extension copies this line.

```http
Cookie: session=demo-only; lang=en-US
```

## Installation

1. In Burp, open **Settings > Extensions > Python environment** and select `jython-standalone-2.7.4.jar`.
2. Open **Extensions > Installed > Add**.
3. Set **Extension type** to **Python** and select `SetCookieToCookie.py`.
4. Confirm that the **Output** tab shows `Set-Cookie to Cookie loaded`.

Keep `cookie_header.py` next to `SetCookieToCookie.py`. The extension looks for it in the same directory.

## Usage

1. Open a response in Repeater, Proxy, or another Burp tool.
2. Right-click the response and select **Extensions > Set-Cookie to Cookie > Copy Set-Cookie as Cookie header**.
3. Paste the copied line into the request headers.

The extension preserves the order of valid cookies, including multiple cookies with the same name. It omits response attributes such as `Path`, `Domain`, `Expires`, `Secure`, `HttpOnly`, and `SameSite`. Commas in an `Expires` attribute are ignored. A header is skipped if its first cookie pair is invalid, including when that pair contains a comma.

The extension copies cookie values to the system clipboard on request. The operating system may retain them in its clipboard history.

## Tests

Run the parser tests from the repository root.

```bash
python3 -B -m unittest discover -s tests -v
```

To include the Burp API integration tests, set `JYTHON_JAR` and `BURP_JAR` to the paths of the Jython standalone JAR and the Burp Suite JAR.

```bash
java -Djava.awt.headless=true \
  -cp "${JYTHON_JAR:?Set the Jython standalone JAR path}:${BURP_JAR:?Set the Burp Suite JAR path}" \
  org.python.util.jython -B -m unittest discover -s tests -v
```

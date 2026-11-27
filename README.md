# Set-Cookie to Cookie

A Burp Suite extension that turns a response's `Set-Cookie` headers into one request-ready `Cookie` header and copies it to the clipboard.

## Installation

Download `set-cookie-to-cookie.jar` from [Releases](https://github.com/mtkilicc/set-cookie-to-cookie/releases). In Burp, open **Extensions > Installed > Add**, choose **Java**, and select the JAR. The current edition uses the Montoya API.

The [Python v1 release](https://github.com/mtkilicc/set-cookie-to-cookie/releases/tag/v1) includes the original Jython extension and its installation instructions.

## Usage

1. Open an HTTP response in Proxy, Repeater, or another Burp tool.
2. Right-click inside the response and choose **Extensions > Set-Cookie to Cookie > Copy Set-Cookie as Cookie header**.
3. Paste the copied line into the destination request headers.

Given these two response headers, the extension copies `Cookie: session=demo-only; lang=en-US`.

```http
Set-Cookie: session=demo-only; Path=/; Secure; HttpOnly
Set-Cookie: lang=en-US; Expires=Wed, 21 Oct 2030 07:28:00 GMT
```

The extension preserves the order of valid cookie pairs, including repeated names. It omits response attributes, such as `Path`, `Expires`, and `HttpOnly`, and skips malformed pairs. Copying runs locally and only after the user selects the command. The operating system may retain copied values in its clipboard history.

## Build and test

Run the Gradle wrapper from the repository root with Java 17 or later.

```sh
./gradlew build
```

The build runs synthetic parser and context menu tests and writes `dist/set-cookie-to-cookie.jar`.

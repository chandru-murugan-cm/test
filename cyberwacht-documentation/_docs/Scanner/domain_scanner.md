---
title: Domain Scanner
description: How to Add domain
---

# Domain Security Features

### 1. Backup file

- Detection of publicly accessible backup files, which may contain sensitive information such as source code or database credentials.

### 2. Weak credentials

- Exploiting weak or default credentials to gain unauthorized access to a system.

### 3. CRLF Injection

- Injecting carriage return and line feed characters to manipulate web server or response behaviors.

### 4. Content Security Policy Configuration

- Lack of proper configuration of Content Security Policy, leading to potential security risks.

### 5. Cross Site Request Forgery

- Attacker tricks a victim into executing unwanted actions on a web application where the user is authenticated.

### 6. Potentially dangerous file

- A file that could pose a security risk if accessed or executed (e.g., an executable file or script).

### 7. Command execution

- Exploiting vulnerabilities in web applications that allow attackers to execute arbitrary commands on the host server.

### 8. Path Traversal

- Manipulating file paths to access files and directories outside of the web root, potentially exposing sensitive data.

### 9. Fingerprint web application framework

- Detecting the specific web application framework in use, potentially revealing vulnerabilities.

### 10. Fingerprint web server

- Detecting the specific web server software in use, which can reveal vulnerabilities associated with the software.

### 11. Htaccess Bypass

- Exploiting misconfigurations in .htaccess files to bypass security restrictions.

### 12. HTML Injection

- Injecting HTML code that is executed by the browser, potentially altering the behavior of a web page.

### 13. Clickjacking Protection

- Without clickjacking protection, an attacker can load your site in an iframe and trick users into clicking unintended content.

### 14. HTTP Strict Transport Security (HSTS)

- HSTS ensures that HTTP connections are redirected to HTTPS to prevent downgrade attacks and man-in-the-middle attacks.

### 15. MIME Type Confusion

- Attackers exploit misconfigured MIME types that allow files to be executed when they should not.

### 16. HttpOnly Flag cookie

- HttpOnly flag is not set in the cookie, potentially allowing client-side scripts to access sensitive cookies.

### 17. Unencrypted Channels

- Communication channels are not encrypted, exposing data to interception and tampering.

### 18. LDAP Injection

- Exploiting vulnerabilities in LDAP queries to manipulate and extract data from the directory server.

### 19. Log4Shell

- Exploiting the Log4j vulnerability that allows remote code execution.

### 20. Open Redirect

- A web page allows redirection to external sites, which can be exploited to redirect users to malicious sites.

### 21. Reflected Cross Site Scripting

- Reflected XSS allows attackers to inject malicious scripts into web pages viewed by other users.

### 22. Secure Flag cookie

- The Secure flag is not set in the cookie, allowing the cookie to be sent over an insecure connection.

### 23. Spring4Shell

- Exploiting vulnerabilities in Spring Framework leading to remote code execution.

### 24. TLS/SSL misconfigurations

- Misconfigurations in TLS/SSL implementations, making the connection vulnerable to attacks like man-in-the-middle.

### 25. Server Side Request Forgery (SSRF)

- Trick the server into making requests to unauthorized locations (e.g., internal systems or malicious external sites).

### 26. Stored HTML Injection

- HTML Injection that is stored on the server and executed every time the page is loaded.

### 27. Stored Cross Site Scripting

- XSS attack that is stored on the server and executed every time the page is loaded.

### 28. Subdomain takeover

- Exploiting a misconfigured DNS to take control of subdomains that should belong to a target organization.

### 29. Blind SQL Injection

- Exploiting SQL injection vulnerabilities in which the attacker does not receive error messages, forcing them to infer information from behavior.

### 30. Unrestricted File Upload

- Uploading potentially harmful files (e.g., scripts) that could be executed on the server.

### 31. Vulnerable software

- Using software with known vulnerabilities that can be exploited by attackers.

### 32. SQL Injection

- Exploiting vulnerabilities in web applications by injecting malicious SQL queries into input fields to manipulate databases.

### 33. Cross Site Scripting (XSS)

- Injecting malicious scripts into web pages viewed by other users, allowing attackers to steal session cookies, deface websites, or redirect users.

### 34. Content Security Policy (CSP) Header Not Set

- CSP helps prevent XSS and other code injection attacks. If not set, attackers may be able to execute harmful scripts.

### 35. Missing Anti-clickjacking Header

- Without this header, an attacker can load your site in an iframe and trick users into clicking on content they didn’t intend to (clickjacking).

### 36. Sub Resource Integrity Attribute Missing

- This attribute ensures that the resources (e.g., JavaScript files) being fetched are not modified, helping to prevent attacks like supply chain attacks.

### 37. Cross-Domain JavaScript Source File Inclusion

- Loading JavaScript files from different domains without proper security checks can expose the site to XSS or data theft.

### 38. Permissions Policy Header Not Set

- Without this header, attackers can access browser features like geolocation, camera, and microphone without user consent.

### 39. Timestamp Disclosure - Unix

- Exposure of Unix timestamps can reveal sensitive information, such as when a particular action occurred.

### 40. Sub Resource Integrity Attribute Missing (duplicate)

- This attribute ensures that the resources (e.g., JavaScript files) being fetched are not modified, helping to prevent attacks like supply chain attacks.

### 41. X-Content-Type-Options Header Missing

- Without this header, browsers may incorrectly interpret file types, potentially leading to the execution of harmful scripts (MIME-type sniffing).

### 42. Information Disclosure - Suspicious Comments

- Web pages may contain comments with sensitive information that attackers can use for exploitation.

### 43. Re-examine Cache-control Directives

- Incorrect cache-control settings can expose sensitive data by allowing browsers to cache private information.

### 44. Dangerous JS Functions

- Use of insecure or deprecated JavaScript functions, which can be exploited for attacks like XSS or code injection.

### 45. Server Leaks Information via "X-Powered-By" HTTP Response Header Field(s)

- Exposing the server’s technology stack (e.g., PHP, ASP.NET) can help attackers target specific vulnerabilities.

### 46. Strict-Transport-Security Header Not Set

- Without this header, a site may be vulnerable to downgrade attacks and man-in-the-middle attacks over HTTP.

### 47. Server Leaks Version Information via 'Server' HTTP Response Header Field

- Leaking server version information can aid attackers in finding known vulnerabilities for that specific version.

### 48. Hidden File Found

- Hidden or sensitive files (e.g., .git, .env) accessible via the web server can expose configuration or sensitive information.

### 49. WSDL File Detection

- Detects the presence of WSDL (Web Services Description Language) files, which may reveal internal API details.

### 50. Content Cacheability

- Checks whether sensitive content is being cached by the browser, which could expose user data.

### 51. In Page Banner Information Leak

- Detects sensitive information leaks in page banners that may reveal system information or user data.

### 52. Java Serialization Object

- Identifies Java serialized objects, which may be vulnerable to deserialization attacks.

### 53. Permissions Policy Header Not Set (duplicate)

- Without this header, attackers can access browser features like geolocation, camera, and microphone without user consent.

### 54. HTTP Parameter Override

- Detects if an attacker can override HTTP parameters by injecting them into the request.

### 55. Insufficient Site Isolation Against Spectre Vulnerability

- Checks if the website is properly isolated to prevent Spectre-based attacks, where malicious code can read memory it shouldn’t.

### 56. Source Code Disclosure

- Detects exposed source code that may reveal sensitive application details or credentials.

### 57. Sub Resource Integrity Attribute Missing (duplicate)

- Detects the absence of a security feature that ensures the integrity of external resources (such as scripts or stylesheets) loaded by a website.

### 58. Application Error Disclosure

- Detects application errors visible to users, which may expose sensitive information to attackers.

### 59. Big Redirect Detected (Potential Sensitive Information Leak)

- Detects large redirects that could expose sensitive information in the URL.

### 60. Re-examine Cache-control Directives (duplicate)

- Checks if the cache-control settings are correctly configured to prevent the exposure of sensitive information.

### 61. Charset Mismatch

- Detects mismatch between the declared character set and the actual encoding of the page, which may cause security or compatibility issues.

### 62. Content-Type Header Missing

- Detects missing 'Content-Type' headers, which can cause browsers to incorrectly interpret content, potentially leading to security risks.

### 63. Cookie No HttpOnly Flag

- Detects cookies without the 'HttpOnly' flag, which can prevent them from being accessed via JavaScript, reducing XSS risks.

### 64. Loosely Scoped Cookie

- Detects cookies with overly broad domain or path scope, which may allow them to be accessed by unintended parties.

### 65. Cookie without SameSite Attribute

- Detects cookies without the 'SameSite' attribute, which can help mitigate cross-site request forgery (CSRF) attacks.

### 66. Cookie Without Secure Flag

- Detects cookies that are transmitted over insecure HTTP channels instead of secure HTTPS connections.

### 67. Cross-Domain Misconfiguration

- Detects improper configuration of cross-domain policies that may allow unauthorized access to resources or data.

### 68. Cross-Domain JavaScript Source File Inclusion

- Detects the inclusion of JavaScript files from different domains, which can introduce XSS vulnerabilities if not properly handled.

### 69. Absence of Anti-CSRF Tokens

- Detects missing CSRF tokens in forms, which are essential for preventing cross-site request forgery attacks.

### 70. Directory Browsing

- Detects if the web server is allowing directory browsing, potentially exposing sensitive files and directories.

### 71. Hash Disclosure

- Detects exposed password hashes or other cryptographic data, which attackers can use to crack passwords or other sensitive information.

### 72. Heartbleed OpenSSL Vulnerability (Indicative)

- Detects the potential presence of the Heartbleed vulnerability in OpenSSL, which allows attackers to read server memory and steal sensitive information.

### 73. Private IP Disclosure

- Detects exposure of private IP addresses in web pages, which can aid attackers in further reconnaissance.

### 74. Session ID in URL Rewrite

- Detects session IDs included in URLs, which can be intercepted by attackers and used to hijack user sessions.

### 75. Information Disclosure - Debug Error Messages

- Detects the presence of debug error messages that expose sensitive information about the web server or application.

### 76. Information Disclosure - Sensitive Information in URL

- Detects sensitive information (e.g., session IDs, authentication tokens) included in URLs, which can be logged or intercepted by attackers.

### 77. Information Disclosure - Sensitive Information in HTTP Referrer Header

- Detects when sensitive information (e.g., authentication tokens or personal data) is passed in the HTTP Referrer header, which can be intercepted.

### 78. Information Disclosure - Suspicious Comments

- Detects suspicious comments in the code, such as TODOs or developer notes, that may provide clues for attackers.

### 79. Weak Authentication Method

- Detects the use of weak authentication methods that do not provide sufficient security, such as plain text passwords.

### 80. HTTP to HTTPS Insecure Transition in Form Post

- Detects when a form is submitted via HTTP instead of HTTPS, making it vulnerable to man-in-the-middle attacks.

### 81. HTTPS to HTTP Insecure Transition in Form Post

- Detects when a secure form submission (HTTPS) downgrades to HTTP, exposing the data to interception.

### 82. Insecure JSF ViewState

- Detects vulnerabilities in JavaServer Faces (JSF) ViewState that could lead to data tampering or code injection.

### 83. Reverse Tabnabbing

- Detects vulnerabilities where an attacker could hijack the navigation of a newly opened tab, potentially leading to phishing attacks.

### 84. Secure Pages Include Mixed Content

- Detects when a secure (HTTPS) page includes insecure (HTTP) resources, such as scripts or images, which can be intercepted or manipulated.

### 85. PII Disclosure

- Detects potential exposure of Personally Identifiable Information (PII) in web pages, headers, or requests.

### 86. Script Served From Malicious Domain (polyfill)

- Detects scripts that are loaded from potentially malicious domains, which may serve harmful or unauthorized content.

### 87. Retrieved from Cache

- Detects if sensitive information is being retrieved from cache, which could expose data to unauthorized users.

### 88. HTTP Server Response Header

- Checks the HTTP response headers for security-related settings, such as cache control, security headers, and more.

### 89. Strict-Transport-Security Header

- Detects whether the HTTP Strict Transport Security (HSTS) header is properly set to prevent downgrade attacks.

### 90. Timestamp Disclosure

- Detects if sensitive timestamps (e.g., session creation or last access) are disclosed in HTTP responses or page content.

### 91. User Controllable Charset

- Checks if an attacker can control the character encoding of the web page, which could lead to security vulnerabilities like XSS.

### 92. Cookie Poisoning

- Detects vulnerabilities related to cookie manipulation, which could allow attackers to alter session information or perform other malicious actions.

### 93. User Controllable HTML Element Attribute (Potential XSS)

- Checks if an attacker can control HTML element attributes, which could lead to cross-site scripting (XSS) vulnerabilities.

### 94. User Controllable JavaScript Event (XSS)

- Detects if an attacker can control JavaScript events, potentially leading to cross-site scripting (XSS) attacks.

### 95. Open Redirect

- Detects open redirect vulnerabilities, where attackers can manipulate URLs to redirect users to malicious sites.

### 96. Username Hash Found

- Detects if a username hash is exposed, which could be leveraged for further attacks or to reveal user information.

### 97. Viewstate

- Detects the use of ViewState in ASP.NET applications, which can be exploited for malicious purposes if not properly secured.

### 98. X-AspNet-Version Response Header

- Checks if the `X-AspNet-Version` header is exposed in the response, which could reveal the version of ASP.NET used and potentially allow attackers to target known vulnerabilities.

### 99. X-Backend-Server Header Information Leak

- Detects if the `X-Backend-Server` header is exposed, potentially revealing the internal backend server information, which could be leveraged for further attacks.

### 100. X-ChromeLogger-Data (XCOLD) Header Information Leak

- Detects if the `X-ChromeLogger-Data` header is exposed, which can provide sensitive information about the server or application in use

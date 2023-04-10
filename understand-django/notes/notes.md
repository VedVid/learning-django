#### Chapter 1 – Browser to Django

##### Domains

Entering URL – making a request

DNS – Domain Name System

www [dot] example [dot] ***com*** – top-level domain (TLD)

www [dot] ***example*** [dot] com – domain name

***www*** [dot] example [dot] com – subdomain

Domain is like alias to the underlying IP address of server / website.

##### HTTP

http – Hypertext Transfer Protocol.

It uses a standard set of commands to communicate:
* `GET` – Fetch an existing resource
* `POST` – Create or update a resource
* `DELETE` – Delete a resource
* `PUT` – Update a resource

If you visit my website at https://www.mattlayman.com/about/, your browser will send a request like

```
GET /about/ HTTP/1.1
Host: www.mattlayman.com
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
```
 
First line is path to a resource in a website, and protocol version.  
After that, there is a list of headers providing more info about a request.  
`Host` header is required. All other headers (like `Accept` header) are optional.

Examples of headers:
* `User-Agent` – what kind of browser is making a request
* `Last-Modified` – when the resource was requested previously to determine if a new version should be returned
* `Accept-Encoding` – declare that the browser can compress the data (to save on bandwidth)

Most of the headers are handled automatically by browsers. Still, there are instances when user (developer) use the headers.

1. A browser sends an HTTP request to a URL
2. Request is resolved by the DNS system
3. That request arrives at a server that is connected to the IP address of the domain name.
4. Django lives on such a server and is responsible for answering requests with an HTTP response.

Webserver translates the raw HTTP request to WSGI (Web Server Gateway Interface) – format used by various Python web frameworks like Django and Flask. Django's job is to provide a response.

##### Starting project

Aftern installing Django:  
`django-admin startproject [projectname] [path]`, e.g.  
`django-admin startproject tutorial .`


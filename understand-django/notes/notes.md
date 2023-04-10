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
to create a server,  
`python manage.py startapp [appname]`, e.g.  
`python manage.py startapp application`  
to create an application within the server.  

App must be hooked to the Django server by adding the name of application to the `INSTALLED_APPS` list in `project\settings.py`.

You can run a server by  
`python manage.py runserver`.


#### Chapter 2 – URLs Lead The Way

##### URLconf and paths

URLs can come in many forms. Django follows the instructions set in `URLconf` inside `project\urls.py`.

URLconf is, kind of, list of URL paths that Django will try to match. When Django finds a matching path, it will route a HTTP request to a chunk of Python code (called *view*) that is associated with that path.

URLconf example:  
```python
# project/urls.py
from django.urls import path

from application import views

urlpatterns = [
    path("", views.home),
    path("about/", views.about),
    path("contact/", views.contact),
    path("terms/", views.terms),
]
```

urlpatterns is read from the start to the end, and Django stops scanning as soon as it finds the matching pattern.  
When scanning urlpatterns, Django ignores `http://`, domain, and slash after domain, so for example, `"about/"` is request to `https://www.example.com/about/`, and `""` is request to `https://www.example.com/`.  
String part of path is called *route*. It may be a plain string, but also can feature a structures like *converters*, like `"blog/<int:year>/<slug:slug>/"`.  
A good rule of thumb is to include path entries that match on ranges of values with converters after the specific values.

##### Views

A view is code that takes a request and returns a response.

Very basic view example:  
```python
from django.http import (
    HttpRequest,
    HttpResponse
)

def some_view(
    request: HttpRequest
) -> HttpResponse:
    return HttpResponse('Hello World')
```

Another example:  
```python
# urls
    path(
        "blog/<int:year>/",
        views.blog_by_year
    ),

(...)

# views
from django.http import HttpResponse

def blog_by_year(request, year):
    # ... some code to handle the year
    data = 'Some data set by code above'
    return HttpResponse(data)
```  
Looks like "year" part of the url converter is automatically parsed and passed to blog_by_year function.

Instead of `path` function, one can use `re_path` function and use regex strings.  
Example:  
```python
re_path(
    r"^blog/(?P<year>[0-9]{4})/(?P<slug>[\w-]+)/$",
    views.blog_post
),
```
* `r` – raw string, without escape characters
* `^` – the pattern must start here (so "blog..." is OK, and "myblog..." is NOK)
* `blog/` – literal interpretation
* `(?P<year>[0-9]{4})` – capture group; `?P<year>` is the name / argument, `[0-9]` means that only numbers are accepted, and `{4}` means that the number must match exactly four times
* `/` – literal interpretation
* `(?P<slug>[\w-]+)` – another capture group; `\w` means any word character from natural language, plus digits, plus underscores, `-` is literal dash, `+` means that the character class must match 1 or more times
* `/` – literal interpretation
* `$` – the pattern must end here

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

##### Grouping related URLs

Bad:  
```python
# project/urls.py
from django.urls import path

from schools import (
    views as schools_views,
)
from students import (
    views as students_views,
)

urlpatterns = [
    path(
        "schools/", schools_views.index
    ),
    path(
        "schools/<int:school_id>/",
        schools_views.school_detail,
    ),
    path(
        "students/",
        students_views.index,
    ),
    path(
        "students/<int:student_id>/",
        students_views.student_detail,
    ),
]
```

Good:  
```python
# project/urls.py
from django.urls import include, path

urlpatterns = [
    path(
        "schools/",
        include("schools.urls"),
    ),
    path(
        "students/",
        include("students.urls"),
    ),
]

(...)

# schools/urls.py
from django.urls import path

from schools import views

urlpatterns = [
    path("", views.index),
    path(
        "<int:school_id>/",
        views.school_detail
    ),
]
```

##### Naming URLs

```python
# project/urls.py
from django.urls import path

from blog import views

urlpatterns = [
    ...
    path(
        "/marketing/blog/categories/",
        views.categories,
        name="blog_categories"  # <-- this
    ),
    ...
]

(...)

# application/views.py
from django.http import (
    HttpResponseRedirect
)
from django.urls import reverse

def old_blog_categories(request):
    return HttpResponseRedirect(
        reverse("blog_categories")  # <-- this
    )
```

The job of reverse is to look up any path name and return its route equivalent. That means that `reverse("blog_categories") == "/marketing/blog/categories/"`.

##### Name collisions

Both schools and students apps had an index view to represent the root of the respective portions of the project (i.e., schools/ and students/). If we wanted to refer to those views, we’d try to pick the easiest choice of index. Unfortunately, if you pick index, then Django can’t tell which one is the right view for index. The name is ambiguous.  
Providing a proper namespace is solution. One could prefix name, like that:  
```python
# schools/urls.py
from django.urls import path

from schools import views

urlpatterns = [
    path(
        "",
        views.index,
        name="schools_index"  # <-- 'schools_' is prefix
    ),
    path(
        "<int:school_id>/",
        views.school_detail,
        name="schools_detail"
    ),
]
```

But it's better to declare `app_name` that declares namespace to Django:  
```python
# schools/urls.py
from django.urls import path

from schools import views

app_name = "schools"  # <-- "schools" is namespace
urlpatterns = [
    path("", views.index, name="index"),
    path(
        "<int:school_id>/",
        views.school_detail,
        name="detail"
    ),
]
```

This approach requires reversing, just like in Naming ULRs: `reverse("schools:index") == "/schools/"`.


#### Views On Views

A view is a chunk of code that receives an HTTP request and returns an HTTP response.

##### Function Views

The function takes an HttpRequest instance as input and returns an HttpResponse (or one of its many subclasses) as output.  
Basic "Hello World" example:  
```python
# application/views.py
from django.http import HttpResponse

def hello_world(request):
    return HttpResponse('Hello World')
```

##### HttpRequest

HTTP is protocol, HttpRequest is Python class handling, well, HTTP requests. Example of such request:  
```
POST /courses/0371addf-88f7-49e4-ac4d-3d50bb39c33a/edit/ HTTP/1.1
Host: 0.0.0.0:5000
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded
Content-Length: 155
Origin: http://0.0.0.0:5000
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Pragma: no-cache
Cache-Control: no-cache


name=Science
&monday=on
&tuesday=on
&wednesday=on
&thursday=on
&friday=on
```
When Django receives a request like that, it parses the data and store it in HttpRequest instance.

Explanation:
* `method` – matches the HTTP method of POST
* `content_type` – instructs Django on how to handle the data in the request
* `POST` – for POST requests, Django processes the form data and stores the data into a dictionary-like structure; request.POST['name'] would be Science
* `GET` – anything added to the query string (i.e., the content after a `?` character such as `student=Matt` in `/courses/?student=Matt`) is stored in a dictionary-like attribute as well
* `headers` – this is where all the HTTP headers like Host, Accept-Language, and the others are stored; headers is also dictionary-like and can be accessed like request.headers['Host']

HttpRequest instances are a common place to attach extra data. Django requests pass through many pieces in the framework. This makes the objects great candidates for extra features that you may require.

##### HttpResponse

A response instance will include all the necessary information to create a valid HTTP response for a user’s browser.

Some of the HttpResponse attributes:
* `status_code` – indicates success / failure; 200 is the usual "success" code, everything up from 400 is error (e.g. code 404 when requested resource is not found)
* `content` – content you provide to the user, stored in bytes

When working with Django views, HttpResponse is not always used directly, as it has a variety of subclasses, e.g.:
* `HttpResponseRedirect` – used to send a user to a different page
* `HttpResponseNotFound` – creates "404 Not Found" response
* `HttpResponseForbidden` – to block a user from accessing part of the website ("403 Forbidden")

One can use other techniques, like `render` function, to return HttpResponse without creating an instance by onceself.  
While it is possible to return handcrafted html as a response, it is easier to rely on templates. `render` function is a tool for working with templates.

##### View Classes

Views may be functions, but also classes. Class-based views are commonly called CBVs. When one writes CBV, one can add instance methods that match up with HTTP methods.  
Example:  
```python
# application/views.py
from django.http import HttpResponse
from django.views.generic.base import View

class SampleView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Hello from a CBV!")
```
`get` method corresponds to a GET HTTP request. Both *args and *kwargs are required by Django for CBVs.  
That view may be connected to URLconf:  
```python
# project/urls.py
from django.urls import path

from application.views import SampleView

urlpatterns = [
    path("", SampleView.as_view()),
]
```

##### Out Of The Box Views

**RedirectView** sends the user to another place. One can either subclass `RedirectView` or use `as_view` method. Both ways is shown in the example below.  
```python
# project/urls.py
from django.urls import path
from django.views.generic.base import RedirectView

from application.views import NewView

class SubclassedRedirectView(RedirectView):
    pattern_name = 'new-view'

urlpatterns = [
    path("old-path/", SubclassedRedirectView.as_view()),
    # The RedirectView below acts like SubclassedRedirectView.
    path("old-path/", RedirectView.as_view(pattern_name='new-view')),
    path("new-path/", NewView.as_view(), name='new-view'),
]
```

**TemplateView** allows producing a response using nothing more than a template name. Example:  
```python
# application/views.py
from django.views.generic.base import TemplateView

class HomeView(TemplateView):
    template_name = 'home.html'
```

Django provides a wide array of view classes that serve a variety of purposes, among others:
* display and handle HTML forms so users can input data and send the data to the application
* pull data from a database and show an individual record to the user (e.g., a webpage to see facts about a particular movie)
* pull data from a database and show information from a collection of records to the user (e.g., showing the cast of actors from a movie)
* show data from specific time ranges like days, weeks, and months.

##### Useful Decorators

`@require_POST` – return "405 method not allowed" if method is not POST.
```python
# application/views.py
from django.http import HttpResponse
from django.view.decorators.http import require_POST

@require_POST
def the_view(request):
    return HttpResponse('Method was a POST.')
```

`@login_required` – an unauthicated user will be redirected to the login page.
```python
# application/views.py
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def the_view(request):
    return HttpResponse('This view is only viewable to authenticated users.')
```

`@user_passes_test` – controls which users should be allowed to access the view.
```python
# application/views.py
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse

@user_passes_test(lambda user: user.is_staff)
def the_view(request):
    return HttpResponse('Only visible to staff users.')
```

Decorators can be stacked together:
```python
# application/views.py
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.view.decorators.http import require_POST

@require_POST
@user_passes_test(lambda user: user.is_staff)
def the_view(request):
    return HttpResponse('Only staff users may POST to this view.')
```

##### Mixins to know

Mixin classes are to class-based views as decorators are to function-based views. CBVs still can use decorators, though.

```python
# application/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.base import TemplateView

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

class StaffProtectedView(UserPassesTestMixin, TemplateView):
    template_name = 'staff_eyes_only.html'

    def test_func(self):
        return self.request.user.is_staff
```

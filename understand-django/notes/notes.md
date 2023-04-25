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


#### Templates For User Interfaces

Data about templates is stored in `TEMPLATES` list in `settings.py` file.

If `'APP_DIRS'` key is set to True, then Django will look for the templates inside "template" directory in each application (including the third-party apps) directory.

Key `'DIRS'` let one specify directory where the user-created templates will be stored. E.g., setting it to the `[BASE_DIR / "templates"]` will make Django look for the templates inside "tempaltes" directory in the root project folder.

Templates render user interface combining dynamic data with static template.

Naive example:  
```python
# application/views.py

from django.shortcuts import render

def hello_view(request):
    context = {'name': 'Johnny'}
    return render(
        request,
        'hello.txt',
        context
    )

(...)

# templates/hello.txt
Hello {{ name }}
```

Example of using template inside CBV:  
```python
# application/views.py

from django.views.generic.base import TemplateView

class HelloView(TemplateView):
    template_name = 'hello.txt'

    def get_context_data(
        self,
        *args,
        **kwargs
    ):
        context = super().get_context_data(
            *args, **kwargs)
        context['name'] = 'Johnny'
        return context
```

If `context` is more complex, e.g.:  
```python
context = {
    'address': {
        'street': '123 Main St.',
        'city': 'Beverly Hills',
        'state': 'CA',
        'zip_code': '90210',
    }
}
```

then accessing data by template by something like `{{ address['street'] }}` would not work. Instead, the dot notation should be used: `{{ address.street }}`.

Tags (programming-like constructs, like if-then-else) always look that way: `{% ...command... %}`. Example:  
```
{% if user.is_authenticated %}
    <h1>Welcome, {{ user.username }}</h1>
{% else %}
    <h1>Welcome, guest</h1>
{% endif %}
```

Another tag is a for loop:  
```html
<p>Prices:</p>
<ul>
{% for item in items %}
    <li>{{ item.name }} costs {{ item.price }}.</li>
{% endfor %}
</ul>
```

##### More context on context

Context processors are functions that receive an HttpRequest and must return a dictionary that merges with any other context that will be passed to a template. The “dark side” of context processors is that they run for all requests.

##### Reusable Chunks Of Templates

Non-reusable file:
```html
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" type="text/css" href="styles.css">
    </head>
    <body>
        <h1>Learn about our company</h1>
    </body>
</html>
```

Reusable file (e.g. `base.html`):
```html
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" type="text/css" href="styles.css">
    </head>
    <body>
        {% block main %}{% endblock %}
    </body>
</html>
```

Using reusable file:
```html
{% extends "base.html" %}

{% block main %}
    <h1>Hello from the Home page</h1>
{% endblock %}
```

Composition of multiple reusable files:
```html
<!DOCTYPE html>
<html>
    {% include "head.html" %}
    <body>
        {% include "navigation.html" %}
        {% block main %}{% endblock %}
    </body>
    {% include "footer.html" %}
</html>
```

##### The Templates Toolbox

*From this point, the fourth chapter needs to be revisited in the future. Learning all that theory without actually applying the knowledge in practice doesn't help that much.*

Other useful tags:  
```html
<a href="{% url "a_named_view" %}">Go to a named view</a>

&copy; {% now "Y" %} Your Company LLC.

{% spaceless %}
<ul class="navigation">
    <li><a href="/home/">Home</a></li>
    <li><a href="/about/">About</a></li>
</ul>
{% endspaceless %}
```

##### Tools to build templates

Put the tags in the correct location. `templatetags` Python package inside Django application is necessary, with a module inside. It should look like that:

```
application
+-- templatetags
|   +-- __init__.py
|   +-- custom_tags.py
+-- __init__.py
+-- ...
+-- models.py
+-- views.py
```

Next, one must make a filter and register it:
```python
# application/templatetags/custom_tags.py

import random
from django import template

register = template.Library()

@register.filter
def add_pizazz(value):
    pieces_of_flair = [
	    " Amazing!",
		" Wowza!",
		" Unbelievable!",
	]
	return value + random.choice(pieces_of_flair)
```

It may be used with variable like that:
```html
{% load custom_tags %}

{{ message|add_pizzazz}}
```
Note that loading custom_tags is necessary to use them.

Making tags is very similar to making filters:
```python
# application/templatetags/custom_tags.py

import random
from django import template

register = template.Library()

@register.simple_tag
def champion_welcome(name, level):
    if level > 42:
	    welcome = f"Hello great champion {name}!"
	elif level > 20:
	    welcome = f"Greeting noble warrior {name}!"
	elif level > 5:
	    welcome = f"Hello {name}."
	else:
	    welcome = "Oh, it's you."
	return welcome
```

```html
{% load custom_tags %}

{% champion_welcome "He-Man" 50 %}
```

Custom tags may be used like any other built-in tag.

#### Chapter 5 – User Interaction With Forms

Django forms are built upon web forms. HTML can describe what kind of data is expected, by using tags. The primary HTML tags are `form`, `input`, and `select`.

`form` tag is container for all data to be sent to the application. `form` has two cricital attributes: `action` and `method`.
`action` specifies where user data should be sent to. Leaving out `action` or using `action=""` will send data as HTTP request to the same URL that the user's browser is on.
`method` dictates which HTTP method to use: `GET` or `POST`.

Example:
```html
<form method="GET" action="/some/form/">
    <input type="text" name="message">
	<button type="submit">Send me!</button>
</form>
```

Since the form's method is `GET`, the data will be sent as a part of the URL in a querystring, like `/some/form/message=Hello`. Most useful when the data does not need to be saved, and when the user needs to query something (e.g. setting filters in a web shop).

`POST` method is used when data needs to be secure or saved withing an application. `POST` sends the data in the body of the HTTP request.

`input` tag lets developer set `name` and `type` attributes. `type` may be, among others, `checkbox`, `password` or `text`.

`select` tag lets users make a choice from a list of options.

##### Django Forms

Django forms act as a bridge between HTML forms and Python classes and data types.

Example of class form:
```python
# application/forms.py

from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
	    max_length=100
	)
	email = forms.EmailField()
	message = forms.CharField(
	    max_length=1000
	)
```

One can take this form and add it to a view's context as `form`, then render it in a template. By default form uses an HTML table, but it may be simplified with `as_p` method that will use paragraph tags instead of form elements.

```html
{{ form.as_p }}
```
will be rendered by Django as
```html
<p><label for="id_name">Name:</label>
    <input type="text" name="name" maxlength="100" required id="id_name"></p>
<p><label for="id_email">Email:</label>
    <input type="email" name="email" required id="id_email"></p>
<p><label for="id_message">Message:</label>
    <input type="text" name="message" maxlength="1000" required id="id_message"></p>
```

To make it possible to submit such form, the rendered output needs to be wrapped with a `form` tag, and include a submit button and CSRF token (security measure).

Naive example:
```html
<form action="{% url "some-form-url" %}" method="POST">
    {% csrf_token %}
	{{ form.as_p }}
	<p><input type="submit" value="Send the form!"></p>
</form>
```

```python
# application/views.py

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import ContactForm

def contact_us(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
		if form.is_valid():
		    # Do something with the form data,
			# like send an email.
			return HttpResponseRedirect(
		        reverse("some-form-success-url")
			)
	else:
	    form = ContactForm()
	
	return render(
	    request,
		"contact_form.html",
		{"form": form},
	)
```

The view pattern presented above is so common that Django provides a build-in view, called FormView, to what is done in the example.

```python
# application/views.py

from django.views.generic import FormView
from django.urls import reverse

from .forms import ContactForm

class ContactUs(FormView):
    form_class = ContactForm
	template_name = "contact_form.html"
	
	def get_success_url(self):
	    return reverse("some-form-success-view")
	
	def form_valid(self, form):
	    # Do something with the form data,
		# like send an email.
		return super().form_valid(form)
```

##### Form Fields

By default each value in form is a string, and that string is later parsed and converted to a correct datatype by Django.

Some fields are associated with particular Django widgets; e.g. `CheckboxInput` is default widget for `BooleanField`.

Most popular fields:
* CharField,
* EmailField,
* DateField,
* ChoiceField.

`required` marks a field as required, so it must have a value.

`label` sets the text used for the label tag that is rendered with a form `input`.

`help_text` will render additional text by a form field.

##### Validating Forms

Method `is_valid` handles each of the fields: checks for expected structure, final data types, etc. This process is called "cleaning". Each field must have a `clean` method that the form will call when `is_valid` is called.

When `is_valid` is `True`, the form's data will be in a dictionary named `cleaned_data` with keys that match the field names declared by the form.
With the validated data, one access `cleaned_data` to do the work.

Example:
```python
if form.is_valid():
    email = form.cleaned_data["email"]
	comment = form.cleaned_data["comment"]
	create_support_ticket(email, comment)
	return HttpResponseRedirect(
	    reverse("feedback-received")
	)
```

When `is_valid` is false, Django will store the errors in an `errors` attribute. This attribute will be used when the form is re-rendered on the page.

Developer can overwrite cleaning methods. The new method must have this form: `clean_<fieldname>`.
```python
# application/forms.py

class SignUpForm(forms.Form):
    email = forms.EmailField()
	password = forms.CharField(
	    widget=forms.PasswordInput
	)
	
	def clean_email(self):
	    email = self.cleaned_data["email"]
		if "bob" not in email:
		    raise forms.ValidationError(
			    "Sorry, you are not a Bob."
			)
		return email
```

Three points to remember about:
* `clean_email` will only try to clean the `email` field
* if validation fails, the code should raise a `ValidationError`; Django will handle that and will put the error in the right format in the `errors` attribute of the form
* if everything is good, be sure to return the cleaned data.

#### Chapter 6 – Store Data With Models

Django uses relational databases (like SQlite, PostreSQL) to store data, and represents data for a database using *models* classes.

Example of model class:
```python
# application/models.py

from django.db import models

class Employee(models.Model):
    first_name = models.CharField(
	    max_length=100
	)
	last_name = models.CharField(
	    max_length=100
	)
	job_title = models.CharField(
	    max_length=200
	)
```

Each model class represents one database table. Instance of class are rows in table.

##### Preparing A Database With Migrations

Migrations are necessary to match database structure and model definitions within project.

***makemigrations*** – command that will create migration files for pending model changes;
***migrate*** – takes migration files created by `makemigrations` and applies them to a database.

So, after creating a new `Employee` model, one would need to call `python manage.py makemigrations` first, and then `python manage.py migrate`.

One can also limit which migrations should be executed by providing an app name, like `python manage.py migrate applicationname`.

##### Working With Models

After migrating changes to database, the developer can save the rows to the tables using model's `save` method.

Using `save` on a model record is example of Django ORM (Object Relation Mapper) that translates Python's objects to a relational database.

Most of the ORM operations (like getting all rows from the database or updating a set of rows) work through Manager class that has methods designed for interacting with multiple rows.

Example:
```python
>>> from application.models import Employee
>>> bobs = Employee.objects.filter(first_name="Bob")
>>> for bob in bobs:
...     print(f"{bob.first_name} {bob.last_name}"")
...
Bob Ross
Bob Barker
Bob Marley
Bob Dylan
>>> print(bobs.query)
SELECT
    "application_employee"."id",
	"application_employee"."first_name",
	"application_employee"."last_name",
	"application_employee"."job_title"
FROM "application_employee"
WHERE "application_employee"."first_name" = Bob
>>> # The price is wrong, Bob!
>>> Employee.objects.filter(
... first_name="Bob",
... last_name="Barker").delete()
(1, {"application.Employee": 1})
```

`QuerySet` class has a bunch of methods useful when working with tables. Some of them return a new queryset – useful when it is necessary to apply additional logic for the query.
```python
from application.models import Employee

# employees is a QuerySet of all rows!
employees = Employee.objects.all()

if should_find_the_bobs:
    # New queryset!
	employees = employees.filter(
	    first_name="Bob"
	)
```

Some useful QuerySet methods:
```python
# create – alternative to creating a record instance and callig 'save'.
Employee.objects.create(
    first_name="Bobby",
	last_name="Tables"
)

# get – useful when one needs one and exactly one record; it raises expeption when query doesn't match or matches multiple returns
the_bob = Employee.objects.get(
    first_name="Bob",
	last_name="Marley"
)
Employee.objects.get(first_name="Bob")
# Snippet above raises
# application.models.Employee.MultipleObjectsReturned
Employee.objects.get(
    first_name="Bob",
	last_name="Sagat"
)
# Snippet above raises
# application.models.Employee.DoesNotExist

# exclude – excludes rows that may be part of the existing queryset
the_other_bobs = (
    Employee.objects.filter(first_name="Bob")
	.exclude(last_name="Ross")
)

# update – updates multiple rows in a single operation
Employee.objects.filter(
    first_name="Bob"
).update(first_name="Robert")

# exists – used to check if matching rows exist in the database
has_bobs = Employee.objects.filter(
    first_name="Bob"
).exists()

# count – checks how many rows match a condition
how_many_bobs = Employee.objects.filter(
    first_name="Bob"
).count()

# none – returns an empty queryset for the model; used when certain data access should be protected
employees = Employee.objects.all()
if not is_hr:
    employees = Employee.objects.none()

# first and last, with order by
a_bob = Employee.objects.filter(
    first_name="Bob").order_by(
	"last_name").last()
)
```

##### Types Of Model Data

There is a variety of fields (like `CharField`, `BooleanField`, `DateField`, `DateTimeField`) that share many common attributes, like the ones presented below.

`default` attribute – fills the field with default value, allowing creation model record without specifying certain values. The value may be literal or callable function that produces a value.
```python
import random

from django.db import models

def strength_generator():
    random.randint(1, 20)

class DungeonsAndDragonsCharacter(
    models.Model
):
    name = models.CharField(
	    max_length=100,
		default="Conan"
	)
	# Important! Pass the function,
	# do not call the function!
	strength = models.IntegerField(
	    default=strength_generator
	)
```

`unique` attribute – when a field value must be unique for all rows in the table (e.g. for identifiers)
```python
class ImprobableHero(models.Model):
    name = models.CharField(
	    max_length=100,
		unique=True
	)
```

`null` attribute – to store the absence of data.
```python
class Person(models.Model):
    # This field would always have a value since it can't be null.
	# Zero counts as a value and is not NULL.
	age = models.IntegerField()
	# This field could be unknown and contain NULL.
	# In Python, a NULL db value will appear as None.
	weight = models.IntegerField(
	    null=True
	)
```

`blank` attribute – often used with `null` attribute. `blank` allows form validation to permit an empty field.
```python
class Pet(models.Model):
    # Not all pets have tails,
	# so we want auto-generated forms
	# to allow no value.
	length_of_tail = models.IntegerField(
	    null=True,
		blank=True
	)
```

`help_text` attribute – help text that can be displayed with a field value in the Django administrator site.
```python
class Policy(models.Model):
    is_section_987_123_compliant = models.BooleanField(
	    default=False,
		help_text=(
		"For policies that only apply"
		" on leap days in accordance"
		" with Section 987.123"
		" of the Silly Draconian Order"
		)
	)
```

##### Relational Fields

Simple example of two separate, relational models.

```python
# application/models.py
from django.db import models

class Employee(models.Model):
    first_name = models.CharField(
	    max_length=100
	)
	last_name = models.CharField(
	    max_length=100
	)
	job_title = models.CharField(
	    max_length=200
	)

class PhoneNumber(models.Model):
    number = models.CharField(
	    max_length=32
	)
	PHONE_TYPES = (
	    (1, "Mobile"),
		(2, "Home"),
		(3, "Pager"),
		(4, "Fax"),
	)
	phone_type = models.IntegerField(
	    choices=PHONE_TYPES,
		default=1
	)
	# Every phone number must be associated with an employee record.
	employee = models.ForeignKey(
	    Employee,
		# When employee is deleted, then all related
		# phone number will be deleted too.
		on_delete=models.CASCADE
	)
```

Not sure if I understand this part of the tutorial correctly, but it seems that Django adds `AutoField` to *every* model created by the developer? And it's unique integer, so, in fact, it serves as `primary key`? Supposedly, it looks like that: `id = models.AutoField(primary_key=True)`. If model uses primary key of another model, it makes it a `foreig key`.

The code snippet above is example of one-to-many relationship (multiple rows from a table – PhoneNumber – can reference a single row in another table – Employee; in other words, an employee can have multiple phone numbers).

Many-to-many relationship is not that easy to emulate with only primary and foreign keys. However, Django makes it easy with its `ManyToManyField`:
```python
# application/models.py
from django.db import models

class Person(models.Model):
    name = models.CharField(
	    max_length=128
	)

class House(models.Model):
    address = models.CharField(
	    max_length=256
	)
	residents = models.ManyToManyField(
	    Person
	)
```

On the database level, Django adds new database table to map the relationship between House and Person models. It is necessary, because a single database column cannot hold multiple foreign keys.

#### Chapter 7 – Administer All The Things

##### What Is The Django Admin?

Accessed by `website.address/admin/` by default, but the location should be changed.

Django admin gives a quick ability to interact with models. One can register a model through the admin panel, and perform CRUD operations on the data.

CRUD is an acronym that describes the primary functions of many websites:
* **C**reate
* **R**ead
* **U**pdate
* **D**elete

##### Register A Model With The Admin

At the beginning of porject, `admin.py` is mostly empty. Admin site expect a ModelAdmin class for every model.
Crude example of modeling of a book:
```python
# application/models.py
from django.db import models

class Book(models.Model):
    title = models.CharField(
	    max_length=256
	)
	author = models.CharField(
	    max_length=256
	)
```
```python
# application/admin.py
from django.contrib import admin

from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass
```

Alternative to using `register` decorator is directly calling `register` after the class:
```python
# application/admin.py
from django.contrib import admin

from .models import Book

class BookAdmin(admin.ModelAdmin):
    pass

admin.site.register(Book, BookAdmin)
```

User account with all permissions is called superuser, and it can be created like that:
```
python manage.py createuser
Username: enter_your_name_here
Email address: name@example.com
Password:
Password (again):
Superuser created successfully.
```
Now it should be possible to log in to the admin site using recently created superuser.

##### Customizing Admin Panel

Django uses `ModelAdmin` class level attributes to define the behaviour of a class. Mastering the Django admin is all about mastering `ModelAdmin` options.

Common attributes:
* `list_display` – controls which fields will appear on the list page.
```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
```
* `list_filter` – gives admin list page ability to filter by, let's say, category.
```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
	list_filter = ("category")
```
* `date_hierarchy` – filters in time.
```python
class Book(models.Model):
    # ... title, author, category
	published_date = models.DateField(
	    default=datetime.date.today
	)
	# or, alternatively, use date_hierarchy as a attribute
	date_hierarchy = "published_date"
```
* `ordering` – allows ordering list by a cell, even if ordering is no specified in model's meta options
```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    date_hierarchy = "published_date"
	list_display = ("id", "title")
	list_filter = ("category",)
	ordering = ("title",)
```
* `search_fields` – adds search bar to the top of the page
```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # ...
	search_fields = ("author",)
```
* `raw_id_fields` – changes admin from using a dropdown to using a basic text input which will display the foreign key of the user record; if the record already has a foreign key for the field, then the string representation of the record will be displayed
```python
@admin.register(Book)
class Book(models.Model):
    # ...
	raw_id_fields = ("editor",)
	search_fields = ("author",)
```


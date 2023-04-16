from django.shortcuts import render

# Create your views here.

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader

from .models import Question


def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    #template = loader.get_template("polls/index.html")
    context = {
        "latest_question_list": latest_question_list,
    }
    #return HttpResponse(template.render(context, request))
    # Shortcut:
    return render(request, "polls/index.html", context)


def detail(request, question_id):
    #try:
    #    # pk --> primary key
    #    question = Question.objects.get(pk=question_id)
    #except Question.DoesNotExist:
    #    raise Http404("Question does not exist")
    # Shortcut:
    question = get_object_or_404(Question, pk=question_id)
    return render(
        request,
        "polls/detail.html",
        {"question": question},
    )


def results(request, question_id):
    response = f"You are looking at the results of question {question_id}."
    return HttpResponse(response)


def vote(request, question_id):
    return HttpResponse("You are voting on question %s." % question_id)

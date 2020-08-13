from django.http import HttpResponse
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.paginator import Paginator
from app.models import Question, Tag, Answer, User, QuestionRate
from django.http import Http404
from app import forms
import json

tags_list = Tag.objects.all()
users_list = User.objects.all()


def index(request):
    questions_list = Question.objects.fresh()
    page_obj, paginator = paginate(questions_list, request)
    return render(request, 'index.html', {
        'page_obj': page_obj,
        'tags': tags_list,
        'users': users_list
    })


def hot(request):
    questions_list = Question.objects.hot()
    page_obj, paginator = paginate(questions_list, request)
    return render(request, 'hot.html', {
        'page_obj': page_obj,
        'tags': tags_list,
        'users': users_list
    })


def tag(request, tname):
    questions_list = Question.objects.tag_question(tname)
    page_obj, paginator = paginate(questions_list, request)

    return render(request, 'tag.html', {
        'page_obj': page_obj,
        'tags': tags_list,
        'tname': tname,
    })


# @login_required
# def question(request, qid):
#     questions_object = Question.objects.filter(id=qid)[0]
#     answers = Answer.objects.filter(question=qid)
#     page_obj, paginator = paginate(answers, request)
#     return render(request, 'question.html', {
#         'question_object': questions_object,
#         'page_obj': page_obj,
#         'tags': tags_list,
#     })

def question(request, qid):
    questions_object = Question.objects.filter(id=qid)[0]
    answers = Answer.objects.filter(question=qid)
    page_obj, paginator = paginate(answers, request)

    # user = User.objects.get(user=request.user)
    # qrate = QuestionRate.objects.filter(user_id=user.id, question_id=qid).exists()
    # if not qrate:
    #     is_like = 0
    # else:
    #     qrate1 = QuestionRate.objects.get(user_id=user.id, question_id=qid)
    #     is_like = qrate1.is_like

    if Question.objects.filter(id=qid).exists():
        if request.method == 'POST':
            form = forms.AnswerForm(request.POST)
            if form.is_valid():
                answeredQuestion = Question.objects.filter(id=qid)[0]
                answer = Answer.objects.create(author=request.user,
                                               text=form.cleaned_data.get('text'),
                                               question_id=answeredQuestion.id)
                answer.save()
                return redirect('/question/{}/'.format(qid))
        else:
            form = forms.AnswerForm
        context = {
            'question_object': questions_object,
            'page_obj': page_obj,
            'tags': tags_list,
            'form': form,
            # 'is_like': is_like,
        }
        return render(request, 'question.html', context)
    else:
        raise Http404


def login(request):
    if request.method == 'GET':
        form = forms.LoginForm()
    else:
        form = forms.LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(request, **form.cleaned_data)
            if user is not None:
                auth.login(request, user)
                return redirect('/?next=%s' % request.path)
    return render(request, 'login.html', {
        'tags': tags_list, 'form': form
    })


def register(request):
    if request.method == 'GET':
        form = forms.SignupForm()
    else:
        form = forms.SignupForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            auth.login(request, user)
            return redirect("/ask")
    return render(request, 'register.html', {
        'tags': tags_list, 'form': form,
    })


@login_required
def ask(request):
    if request.method == 'GET':
        form = forms.QuestionForm(request.user)
        return render(request, 'ask.html', {
         'tags': tags_list, 'form': form,
        })
    form = forms.QuestionForm(request.user, data=request.POST)
    if form.is_valid():
        question = form.save()
        return redirect(reverse('question', kwargs={'qid': question.pk}))
    return render(request, 'ask.html', {
        'tags': tags_list, 'form': form,
    })


@login_required
def settings(request):
    user = get_object_or_404(User, username=request.user)
    if request.method == 'GET':
        form = forms.ProfileSettingsForm(instance=user)

    form = forms.ProfileSettingsForm(instance=user, data=request.POST)
    if form.is_valid():
        form.save()

        return redirect('/settings')
    return render(request, 'settings.html', {
        'tags': tags_list, 'form': form,
    })


def paginate(object_list, request):
    paginator = Paginator(object_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj, paginator


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')


@login_required
def rate(request):
    flag = request.POST.get('flag')
    qid = request.POST.get('qid')

    user = User.objects.get(user=request.user)
    qrate, was_created = QuestionRate.objects.get_or_create(user_id=user.id, question_id=qid)
    is_like = 1 if flag == 'true' else -1

    q = Question.objects.get(id=qid)
    qr = QuestionRate.objects.filter(id=qrate.id)
    if flag == 'true':
        if qrate.is_like == 1:
            qr.update(is_like=0)
            q.rating -= 1
        elif qrate.is_like == 0:
            qr.update(is_like=1)
            q.rating += 1
        elif qrate.is_like == -1:
            qr.update(is_like=1)
            q.rating += 2
    elif flag == 'false':
        if qrate.is_like == 1:
            qr.update(is_like=-1)
            q.rating -= 2
        elif qrate.is_like == 0:
            qr.update(is_like=-1)
            q.rating -= 1
        elif qrate.is_like == -1:
            qr.update(is_like=0)
            q.rating += 1
    q.save(update_fields=["rating"])
    return HttpResponse(json.dumps({
        'rating': q.rating
    }), content_type='application/json')


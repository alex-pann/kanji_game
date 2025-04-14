from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import Kanji, Score
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db import models
import random

question_count = 5

def home(request):
    for key in ['attempts', 'question_index', 'score', 'questions']:
        if key in request.session:
            del request.session[key]
    return render(request, 'game/home.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Score.objects.create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'game/register.html', {'form': form})

def dictionary(request):
    all_kanji = Kanji.objects.all()
    return render(request, 'game/dictionary.html', {'kanji_list': all_kanji})

def nopage(request):
    return render(request, 'game/nopage.html')

@login_required
def game_view(request):
    if 'questions' not in request.session:
        all_kanji = list(Kanji.objects.all())
        selected = random.sample(all_kanji, min(question_count, len(all_kanji)))
        request.session['questions'] = [k.id for k in selected]
        request.session['current'] = 0
        request.session['score'] = 0

    current_idx = request.session['current']
    question_ids = request.session['questions']

    if current_idx >= len(question_ids):
        Score.objects.filter(user=request.user).update(
            total_score=models.F('total_score') + request.session['score']
        )
        request.session.pop('questions', None)
        request.session.pop('current', None)
        request.session.pop('score', None)
        request.session.pop('options', None)
        request.session.pop('attempts', None)
        return redirect('ranking')

    kanji = Kanji.objects.get(id=question_ids[current_idx])

    if 'options' not in request.session or request.session.get('current_kanji_id') != kanji.id:
        other_kanji = Kanji.objects.exclude(id=kanji.id)
        wrong_choices = random.sample(list(other_kanji), 2) if other_kanji.count() >= 2 else []
        options = [kanji.correct_translation] + [k.correct_translation for k in wrong_choices]
        random.shuffle(options)
        request.session['options'] = options
        request.session['current_kanji_id'] = kanji.id
    else:
        options = request.session['options']

    if request.method == 'POST':
        answer = request.POST.get('answer')
        if answer == kanji.correct_translation:
            if 'attempts' not in request.session:
                request.session['score'] += 1
            request.session['current'] += 1
            request.session.pop('attempts', None)
            request.session.pop('options', None)
            request.session.pop('current_kanji_id', None)
            return redirect('game')
        else:
            request.session['attempts'] = True

    return render(request, 'game/game.html', {'kanji': kanji, 'options': options,
                                              'question_number': current_idx + 1})


def ranking(request):
    scores = Score.objects.select_related('user').order_by('-total_score')
    return render(request, 'game/ranking.html', {'scores': scores})

def delete_account(request):
    user = request.user
    logout(request)
    user.delete()
    return redirect('home')


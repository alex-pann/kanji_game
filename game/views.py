from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import Kanji, Score
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db import models
import random

question_count = 7

def home(request):
    return render(request, 'game/home.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Score.objects.create(user=user)
            login(request, user)
            return redirect('game')
    else:
        form = RegisterForm()
    return render(request, 'game/register.html', {'form': form})

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
        Score.objects.filter(user=request.user).update(total_score=models.F('total_score') + request.session['score'])
        del request.session['questions']
        return redirect('ranking')

    kanji = Kanji.objects.get(id=question_ids[current_idx])
    options = [kanji.correct_translation, kanji.wrong_option1, kanji.wrong_option2]
    random.shuffle(options)

    if request.method == 'POST':
        answer = request.POST.get('answer')
        if answer == kanji.correct_translation:
            if 'attempts' not in request.session:
                request.session['score'] += 1
            request.session['current'] += 1
            request.session.pop('attempts', None)
            return redirect('game')
        else:
            request.session['attempts'] = True

    return render(request, 'game/game.html', {'kanji': kanji, 'options': options})


def ranking(request):
    scores = Score.objects.select_related('user').order_by('-total_score')
    return render(request, 'game/ranking.html', {'scores': scores})

def delete_account(request):
    user = request.user
    logout(request)
    user.delete()
    return redirect('home')
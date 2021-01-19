import requests
from bs4 import BeautifulSoup
import random
from .models import Show
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.models import User
from film.models import UserRating

# Create your views here.

def home(request):
    films = list(Show.objects.all())
    random.shuffle(films)
    return render(request, 'film/home.html', {'shows': films[:10]})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Successfully registered, {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'film/register.html', {'form': form, 'title': 'Register'})


def profile(request, username: str = ""):
    if not username:
        return redirect('film-home')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('film-home')

    userfilms = UserRating.objects.filter(user=user)
    total = len(userfilms)
    average = 0
    for ur in userfilms:
        average += ur.rating
    if total:
        average = round(average/total, 2)

    sort_type = request.GET.get('sort')
    if not sort_type or not sort_type.isdigit():
        sort_type = 1
    sort_type = int(sort_type)
    if sort_type == 2:
        results = UserRating.objects.filter(user=user).order_by('rating')
    else:
        results = UserRating.objects.filter(user=user).order_by('-rating')

    for result in results:
        result.show.genres = result.show.genres.split(",")
    return render(request, 'film/profile.html', {'username': username,
                                                 'title': f"{username}'s profile",
                                                 'total': total,
                                              'average': average,
                                            'sort_type': sort_type,
                                            'results': results})



def search(request, query: str = ""):
    if request.method == 'POST' and 'query' in request.POST:
        query = request.POST['query']
    if not query:
        return render(request, 'film/search.html')
    url = "http://api.tvmaze.com/search/shows?q=%s" % query
    response = requests.get(url).json()
    if not response:
        return render(request, 'film/search.html', {'query': query})
    else:
        for each in response:
            if each["show"]["summary"]:
                each["show"]["summary"] = BeautifulSoup(each["show"]["summary"], "lxml").text
        context = {
            'results': response,
            'query': query,
            'title': "Search"
        }
        return render(request, 'film/search.html', context)


def show(request, showid: int = 0):
    if not showid:
        return redirect('film-home')
    url = f"http://api.tvmaze.com/shows/{showid}"
    response = requests.get(url).json()
    if response['status'] == 404:
        return redirect('films')
    if response["summary"]:
        response["summary"] = BeautifulSoup(response["summary"], "lxml").text

    if request.user.is_authenticated:
        try:
            sh = Show.objects.get(showid=showid)
            sh.image = response['image']['original']
            sh.status = response['status']
            sh.genres = ','.join(response['genres'])
            sh.name = response['name']
            sh.save()
        except Show.DoesNotExist:
            sh = Show.objects.create(showid=showid,
                                     image=response['image']['original'],
                                     status=response['status'],
                                     genres=','.join(response['genres']),
                                     name=response['name'])

        if request.method == 'POST':
            if "rating" in request.POST:
                value = int(request.POST['rating'])
                if value == 0:
                    UserRating.objects.get(show=sh, user=request.user).delete()
                    return render(request, 'film/show.html', {'show': response, 'title': response['name'],
                                                            'watched': False, 'rating': 0})
                else:
                    try:
                        ur = UserRating.objects.get(show=sh, user=request.user)
                    except UserRating.DoesNotExist:
                        ur = UserRating(show=sh, user=request.user)
                    ur.rating = value
                    ur.save()
                    return render(request, 'film/show.html', {'show': response,
                                                              'title': response['name'],
                                                              'watched': True,
                                                              'rating': value,
                                                              'position': ur.position})
            if "#" in request.POST:
                try:
                    value = int(request.POST['#'])
                except ValueError:
                    value = 0
                try:
                    ur = UserRating.objects.get(user=request.user, position=value)
                    ur.position = 0
                    ur.save()
                except UserRating.DoesNotExist:
                    pass
                ur = UserRating.objects.get(show=sh, user=request.user)
                ur.position = value
                ur.save()
                return render(request, 'film/show.html', {'show': response,
                                                          'title': response['name'],
                                                          'watched': True,
                                                          'rating': ur.rating,
                                                          'position': ur.position})

    if not request.user.is_authenticated:
        return render(request, 'film/show.html', {'show': response, 'title': response['name'],  "watched": False, "rating": 0})

    try:
        ur = UserRating.objects.get(show=Show.objects.get(showid=showid), user=request.user)
        return render(request, 'film/show.html', {'show': response, 'title': response['name'],  'watched': True,
                                                'rating': ur.rating,
                                                'position': ur.position})
    except UserRating.DoesNotExist:
        return render(request, 'film/show.html', {'show': response, 'title': response['name'],  "watched": False, "rating": 0})

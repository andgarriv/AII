from collections import Counter
from django.shortcuts import get_list_or_404, render
from main.populateDB import populate_database
from main.recommendations import load_similarities, recommend_artists
from main.forms import UserForm, ArtistForm
from main.models import UserArtist, UserTagArtist


# Create your views here.

def index(request):
    return render(request, 'index.html')

def populate_db(request):
    populate_database()
    return render(request, 'populate.html')

def load_rs(request):
    load_similarities()
    return render(request, 'loadRS.html')

def most_listened_artists(request):
    form = UserForm(request.GET, request.FILES)
    if form.is_valid():
        user = form.cleaned_data['id']
        user_artists = UserArtist.objects.filter(user=user).order_by('-listen_time')[:5]
        context = {'user_artists': user_artists, 'form': form}
    else:
        context = {'form': UserForm()}
    return render(request, 'mostListenedArtists.html', context)

def most_frequent_tags(request):
    form = ArtistForm(request.GET, request.FILES)
    if form.is_valid():
        artist = form.cleaned_data['id']
        user_tags = [t.tag.value for t in get_list_or_404(UserTagArtist, artist=artist)]
        tags = Counter(user_tags).most_common(10)
            
        context = {'tags': tags, 'form': form}
    else:
        context = {'form': ArtistForm()}

    return render(request, 'mostFrequentTags.html', context)

def recommended_artists(request):
    form = UserForm(request.GET, request.FILES)
    if form.is_valid():
        user = form.cleaned_data['id']
        artists = recommend_artists(int(user))
        context = {'artists': artists, 'form': form}
    else:
        context = {'form': UserForm()}
    return render(request, 'recommendedArtists.html', context)
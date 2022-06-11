# python
import json
import math
from datetime import timedelta, date

# django
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.db.models import Max
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.contrib.auth.models import User

# project
from endeavorapp.models import Card, Deck, UserCard, Word, WordInCard


def home(request):
    return redirect("login/")


def logout_view(request):
    logout(request)
    return redirect("/")


@user_passes_test(lambda user: user.is_superuser)
def admin_custom(request):
    users = []
    for user in User.objects.all():
        users.append(
            {
                "id": user.id,
                "name": f"{user.get_full_name()} ({user.username})",
            }
        )
    decks = []
    for deck in Deck.objects.all():
        decks.append(
            {
                "id": deck.id,
                "name": deck.name,
            }
        )

    return render(
        request=request,
        template_name="endeavorapp/admin_custom.html",
        context={"users": users, "decks": decks},
    )


@permission_required("endeavorapp.change_deck", raise_exception=True)
def manage_decks_access(request):
    request_body = json.loads(request.body)
    user = User.objects.get(id=request_body["user_id"])
    for deck_id in request_body["deck_ids"]:
        user.deck_set.add(Deck.objects.get(id=deck_id))
        for card in Card.objects.filter(deck_id=deck_id):
            card.users.add(user)
    return HttpResponse(status=204)  # TODO: http code constant instead of magic number


def login_view(request):
    if request.method == "GET":
        form = AuthenticationForm()
        login_view.next = request.GET.get("next", "/decks/")
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(login_view.next)
    return render(
        request=request, template_name="endeavorapp/login.html", context={"form": form}
    )


@login_required(login_url="/login/")
def decks(request):
    user = User.objects.get(id=request.user.id)
    decks = user.deck_set.all()
    return render(
        request=request,
        template_name="endeavorapp/decks.html",
        context={"decks": decks},
    )


@permission_required("endeavorapp.add_deck", raise_exception=True)
def create_deck(request):
    try:
        name = json.loads(request.body).get("name").strip()
        if not name:
            return HttpResponse(
                status=400,
                content="Empty name is not allowed!",
                content_type="text/plain",
            )
        deck = Deck.objects.create(name=name)
        # Super users should have access to all decks
        super_users = User.objects.filter(is_superuser=True)
        deck.users.add(*super_users)
        return HttpResponse(status=201)
    except Exception as e:
        return HttpResponse(status=400, content=str(e), content_type="text/plain")


@permission_required("endeavorapp.add_card", raise_exception=True)
def create_card(request):
    deck = Deck.objects.get(id=request.POST["deckId"])
    current_max_order = (
        deck.cards.aggregate(Max("order_in_deck")).get("order_in_deck__max") or 0
    )
    card = Card.objects.create(
        deck=deck,
        front_text=request.POST["frontText"].strip(),
        order_in_deck=current_max_order + 1,
        front_audio=request.FILES["frontAudio"],
    )
    # Add words to the card
    return HttpResponse(status=201)


# TODO: assign the word to the card currently being created/edited
@permission_required("endeavorapp.add_word", raise_exception=True)
def create_word(request):
    word = Word.objects.create(
        text=request.POST["text"].strip(),
        partOfSpeech=request.POST["partOfSpeech"].strip(),
        phonetic=request.POST["phonetic"].strip(),
        definition=request.POST["definition"].strip(),
    )
    return HttpResponse(status=201)


@login_required(login_url="/login/")
def study(request, deck_id):
    user = User.objects.get(id=request.user.id)
    # TODO: study all decks option >> remove deck_id filter
    cards = UserCard.objects.filter(user=user).filter(card__deck_id=deck_id)
    studied_cards = cards.filter(deadline__isnull=False)
    deadline_cards = studied_cards.filter(deadline__lte=date.today())
    not_yet_studied_cards = cards.difference(studied_cards)
    # TODO: set limit for new card
    displayed_cards = [
        _prepare_displayed_card(card.card, card.study_date, card.deadline)
        for card in list(deadline_cards) + list(not_yet_studied_cards)
    ]

    return render(
        request=request,
        template_name="endeavorapp/study.html",
        context={"cards": displayed_cards},
    )


def _prepare_displayed_card(card, study_date=None, deadline=None):
    displayed_card = {"id": card.id}
    # Front
    displayed_card["front_text"] = card.front_text
    displayed_card["front_audio"] = (
        card.front_audio.url if card.front_audio.name else None
    )

    # Back
    words = []
    for word in card.words.all():
        words.append(
            {
                "text": word.text,
                "definition": word.definition,
                "image": word.image.url if word.image.name else None,
                "video": word.video.url if word.video.name else None,
            }
        )
    displayed_card["words"] = words

    # Intervals
    GRADUATING_INTERVAL = 1
    EASE_PERCENTAGE = 2.5
    INTERVAL_MODIFIER = 1
    EASY_BONUS = 1.3
    HARD_INTERVAL = 1.2
    if study_date == None or deadline <= study_date:  # new/again card
        interval = GRADUATING_INTERVAL
    else:
        interval = (deadline - study_date).days
    displayed_card["hard"] = math.floor(interval * HARD_INTERVAL * INTERVAL_MODIFIER)
    displayed_card["good"] = math.floor(interval * EASE_PERCENTAGE * INTERVAL_MODIFIER)
    displayed_card["easy"] = math.floor(
        interval * EASE_PERCENTAGE * INTERVAL_MODIFIER * EASY_BONUS
    )

    return displayed_card


@login_required(login_url="/login/")
def schedule(request, card_id):
    interval = int(request.GET.get("interval"))
    studied_card, created = UserCard.objects.update_or_create(
        user=User.objects.get(id=request.user.id),
        card=Card.objects.get(id=card_id),
        defaults={
            "study_date": date.today(),
            "deadline": date.today() + timedelta(days=interval),
        },
    )
    return HttpResponse(status=204)


def done(request):
    return render(request=request, template_name="endeavorapp/done.html")

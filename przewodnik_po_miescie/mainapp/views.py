from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm, LogInForm, StartLocation
from .models import Atrakcja, Koszyk, Plan, Znizka, PlanyUzytkownika
from django.http import HttpResponse
from django.contrib import messages
from .maps import generate_static_map, generate_interactive_map
from .pdf import generate_pdf
from io import BytesIO
from django.core.mail import EmailMessage
import os
from django.conf import settings
from django.utils import timezone
import logging
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse


logger = logging.getLogger('mainapp')


def user_signup(request):
    """
    Widok rejestracji użytkownika.

    GET: Wyświetla formularz rejestracji.
    POST: Obsługuje przesłany formularz rejestracji.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    """
    if request.method == 'POST':
        logger.debug("Rozpoczęcie rejestracji użytkownika")
        form = SignUpForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Pomyślnie zarejestrowano.')
            logger.info(f"Nowy użytkownik zarejestrowany: {form.cleaned_data['username']}")

            return redirect('home')
        else:
            logger.warning(f"Nieudana próba rejestracji: {form.errors}")
    else:
        form = SignUpForm()
    return render(request, 'rejestracja.html', {'form': form})


def user_login(request):
    """
    Widok logowania użytkownika.

    GET: Wyświetla formularz logowania.
    POST: Obsługuje przesłany formularz logowania.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    """
    source = request.GET.get('source', None)
    if request.method == 'POST':
        logger.debug("Rozpoczęcie logowania użytkownika")
        form = LogInForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                logger.info(f"Użytkownik zalogowany: {username}", )

                if source == 'koszyk':
                    return redirect('/koszyk/')
                else:
                    messages.success(request, 'Zalogowano.')
                    return redirect('home')
            else:
                logger.warning(f"Nieudane logowanie dla użytkownika: {username}")
                messages.error(request, 'Nieprawidłowe dane. Podaj prawidłowy login oraz hasło.')

    else:
        form = LogInForm()
    return render(request, 'logowanie.html', {'form': form})


def user_logout(request):
    """
    Wylogowanie użytkownika.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    """
    logout(request)
    logger.info(f"Użytkownik wylogowany")
    messages.success(request, "Wylogowano")

    return redirect("/login/")


def privacy_policy(request):
    """
    Widok polityki prywatności.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    """
    logger.debug("Wyświetlenie polityki prywatności")
    return render(request, 'privacy_policy.html')


def dodaj_do_koszyka_home(request, atrakcja_id):
    """
    Dodaje atrakcję do koszyka z widoku home.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    atrakcja_id (int): Identyfikator atrakcji, która ma zostać dodana do koszyka.

    GET: Przekierowuje na stronę logowania jeśli użytkownik nie jest zalogowany.
    POST: Dodaje atrakcję do koszyka lub zwiększa ilość jeśli już jest w koszyku.
    """
    if request.user.is_authenticated:
        logger.debug(f"Rozpoczęcie dodawania do koszyka z widoku home: atrakcja_id={atrakcja_id}")

        atrakcja = get_object_or_404(Atrakcja, pk=atrakcja_id)
        koszyk = Koszyk.objects.filter(id_atrakcji=atrakcja, id_klienta=request.user, cena_koncowa=atrakcja.cena_podstawowa).first()

        if koszyk:
            koszyk.ilosc += 1
            koszyk.save()
            messages.success(request, 'Produkt dodany do koszyka ponownie')
            logger.info(f"Dodano ponownie do koszyka: {atrakcja_id}")
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        else:
            koszyk = Koszyk.objects.create(id_atrakcji=atrakcja, id_klienta=request.user, cena_koncowa=atrakcja.cena_podstawowa)
            koszyk.save()
            messages.success(request, 'Produkt dodano do koszyka')
            logger.info(f"Dodano do koszyka: {atrakcja_id}")
            return redirect(request.META.get('HTTP_REFERER', 'home'))
    else:
        logger.warning(f"Niezalogowany użytkownik próbował dodać do koszyka: {atrakcja_id}")
        return redirect('/login/')

    

def dodaj_do_koszyka(request, atrakcja_id):
    """
    Dodaje atrakcję do koszyka.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    atrakcja_id (int): Identyfikator atrakcji, która ma zostać dodana do koszyka.

    GET: Przekierowuje na stronę logowania jeśli użytkownik nie jest zalogowany.
    POST: Dodaje atrakcję do koszyka lub zmienia ilość już dodanej atrakcji.
    """
    if request.user.is_authenticated:
        atrakcja = get_object_or_404(Atrakcja, pk=atrakcja_id)

        if request.method == 'POST':
            if 'action' in request.POST:
                action = request.POST['action']
                if action == 'increase':
                    koszyk = Koszyk.objects.filter(id_atrakcji=atrakcja, id_klienta=request.user).first()
                    if koszyk:
                        koszyk.ilosc += 1
                        messages.success(request, 'Dodano do koszyka')
                        koszyk.save()
                        logger.info(f"Zwiększono ilość w koszyku: {atrakcja_id}")
                    else:
                        Koszyk.objects.create(id_atrakcji=atrakcja, id_klienta=request.user, cena_koncowa=atrakcja.cena_podstawowa, ilosc=1)
                        logger.info(f"Dodano do koszyka: {atrakcja_id}")
                elif action == 'decrease':
                    koszyk = Koszyk.objects.filter(id_atrakcji=atrakcja, id_klienta=request.user).first()
                    if koszyk and koszyk.ilosc > 1:
                        koszyk.ilosc -= 1
                        koszyk.save()
                        messages.success(request, 'Usunięto z koszyka')
                        logger.info(f"Zmniejszono ilość w koszyku: {atrakcja_id}")
                    elif koszyk and koszyk.ilosc == 1:
                        koszyk.delete()
                        messages.success(request, 'Usunięto atrakcję z koszyka')
                        logger.info(f"Usunięto atrakcję z koszyka: {atrakcja_id}")
            return redirect('koszyk')
    else:
        logger.warning(f"Niezalogowany użytkownik próbował dodać do koszyka: {atrakcja_id}")
        return redirect('/login/')



def usun_z_koszyka(request, item_id):
    """
    Usuwa pozycję z koszyka.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    item_id (int): Identyfikator pozycji w koszyku, która ma zostać usunięta.

    POST: Usuwa wybraną pozycję z koszyka.
    """
    if request.method == 'POST':
        logger.debug(f"Rozpoczęcie usuwania z koszyka: item_id={item_id}")

        item = get_object_or_404(Koszyk, pk=item_id)
        item.delete()

        messages.success(request, 'Usunięto atrakcję z koszyka')
        logger.info(f"Usunięto atrakcję z koszyka: {item_id}")
    return redirect('koszyk')



def trasa(request):
    """
    Generuje trasę zwiedzania.

    GET: Wyświetla formularz do wyboru lokalizacji początkowej i trybu podróży.
    POST: Generuje trasę na podstawie wybranych atrakcji i lokalizacji początkowej.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    """
    if request.method == 'POST':
        logger.debug("Rozpoczęcie generowania trasy")
        form = StartLocation(request.POST)

        if form.is_valid():
            start_loc = form.cleaned_data['start_location']
            koszyk_items = Koszyk.objects.filter(id_klienta=request.user)
            loc_list = [item.id_atrakcji for item in koszyk_items]
            mode = form.cleaned_data['mode']

            static_url, places = generate_static_map(start_loc, loc_list, mode=mode)
            interactive_url = generate_interactive_map(start_loc, loc_list, mode=mode)
            logger.info("Trasy zakończone")

            return render(request, 'trasa.html', {'form': form, 'places': places, 'static_url': static_url, 'interactive_url': interactive_url, 'start_loc': start_loc, 'mode': mode})
    else:
        form = StartLocation()
    return render(request, 'trasa.html', {'form': form})


def pojedynczy_plan(request, plan_id):
    """
    Wyświetla pojedynczy plan podróży.

    GET: Wyświetla informacje o planie oraz formularz do wyboru lokalizacji początkowej i trybu podróży.
    POST: Generuje trasę dla wybranego planu na podstawie lokalizacji początkowej.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    plan_id (int): Identyfikator planu, który ma być wyświetlony.
    """
    plan = get_object_or_404(Plan, pk=plan_id)
    atrakcje = plan.atrakcje.all()
    obrazy = [atrakcja.obraz.split(";")[0] for atrakcja in atrakcje]

    if request.method == 'POST':
        form = StartLocation(request.POST)

        if form.is_valid():
            mode = form.cleaned_data['mode']
            start_loc = form.cleaned_data['start_location']
            static_url, places = generate_static_map(start_loc, atrakcje, mode=mode)

            logger.info("Generowanie trasy dla planu zakończone.")

            return render(request, 'pojedynczy_plan.html', {'form': form, 'plan': plan, 'plan_id': plan_id, 'places': places, 'url': static_url, 'start_loc': start_loc, 'obrazy': zip(atrakcje, obrazy), 'mode': mode})
    else:
        form = StartLocation()
    return render(request, 'pojedynczy_plan.html', {'form': form, 'plan': plan, 'obrazy': zip(atrakcje, obrazy)})


def plany(request):
    """
    Wyświetla listę dostępnych planów podróży.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    """
    logger.debug("Rozpoczęcie wyświetlania głównego widoku aplikacji")

    plany = Plan.objects.all()
    photos_path = os.path.join(settings.BASE_DIR, 'mainapp', 'static', 'plan_photos')
    photos = sorted(os.listdir(photos_path))
    plans_with_photos = zip(plany, photos)

    logger.info("Załadowano plany")
    return render(request, 'plany.html', {'plans_with_photos': plans_with_photos})


def main(request):
    """
    Główny widok aplikacji.

    Wyświetla listę dostępnych atrakcji.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    """
    logger.debug("Rozpoczęcie wyświetlania głównego widoku aplikacji")

    atrakcje = Atrakcja.objects.all()
    for atrakcja in atrakcje:
        atrakcja.obrazy = atrakcja.obraz.split(';')

    logger.info("Załadowano atrakcje")
    return render(request, 'home.html', {'atrakcje': atrakcje})


def koszyk(request):
    """
    Wyświetla zawartość koszyka zakupów.

    GET: Wyświetla zawartość koszyka oraz sumę cen.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    """
    if request.user.is_authenticated:
        logger.debug("Rozpoczęcie wyświetlania koszyka zakupów")
        znizki = Znizka.objects.all()
        koszyk_items = Koszyk.objects.filter(id_klienta=request.user)
        suma = sum(item.ilosc * item.cena_koncowa for item in koszyk_items)

        for item in koszyk_items:
            item.pierwszy_obraz = item.id_atrakcji.obraz.split(';')[0]

        logger.info("Załadowano koszyk zakupów")
    else:
        koszyk_items = None
        suma = 0
    return render(request, 'koszyk.html', {'koszyk_items': koszyk_items, 'suma_cen': suma, 'znizki': znizki})


def dodaj_do_planu(plan_id, atrakcja_id):
    """
    Dodaje atrakcję do planu podróży.

    Argumenty:
    plan_id (int): Identyfikator planu, do którego ma zostać dodana atrakcja.
    atrakcja_id (int): Identyfikator atrakcji, która ma zostać dodana do planu.
    """
    logger.debug(f"Rozpoczęcie dodawania atrakcji do planu: plan_id={plan_id}, atrakcja_id={atrakcja_id}")

    plan = get_object_or_404(Plan, pk=plan_id)
    atrakcja = get_object_or_404(Atrakcja, pk=atrakcja_id)

    if not plan.pk:
        plan.save()

    plan.atrakcje.add(atrakcja)

    plan.save()

    logger.info(f"Dodano atrakcję do planu: plan_id={plan_id}, atrakcja_id={atrakcja_id}")
    return redirect('plan')


def pdf_download(request):
    """
    Generuje i zwraca plik PDF z wybranymi atrakcjami.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    """
    logger.debug("Rozpoczęcie generowania pliku PDF")

    from_basket = request.GET.get('from_basket')
    start_loc = request.GET.get('start_loc')
    mode = request.GET.get('mode')
    plan_id = request.GET.get('plan_id')

    if from_basket == "True":
        koszyk_items = Koszyk.objects.filter(id_klienta=request.user)
        loc_list = [item.id_atrakcji for item in koszyk_items]
        quantities = [item.ilosc for item in koszyk_items]
    else:
        plan = get_object_or_404(Plan, pk=plan_id)
        loc_list = plan.atrakcje.all()
        quantities = [1 for _ in range(len(loc_list))]

    pdf = generate_pdf(start_loc, loc_list, quantities=quantities, mode=mode)

    pdf_bytes = BytesIO()
    pdf.output_pdf(pdf_bytes)

    pdf_bytes.seek(0)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="plan.pdf"'

    logger.info("Wygenerowano plik PDF")
    return response


def send_mail(request):
    """
    Funkcja wysyła wiadomość e-mail z załączonym plikiem PDF zawierającym plan zwiedzania.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    """
    logger.debug("Rozpoczęcie wysyłania wiadomości e-mail z plikiem PDF")

    from_basket = request.GET.get('from_basket')
    start_loc = request.GET.get('start_loc')
    mode = request.GET.get('mode')
    plan_id = request.GET.get('plan_id')

    if from_basket == "True":
        koszyk_items = Koszyk.objects.filter(id_klienta=request.user)
        loc_list = [item.id_atrakcji for item in koszyk_items]
        quantities = [item.ilosc for item in koszyk_items]
    else:
        plan = get_object_or_404(Plan, pk=plan_id)
        loc_list = plan.atrakcje.all()
        quantities = [1 for _ in range(len(loc_list))]

    pdf = generate_pdf(start_loc, loc_list, quantities=quantities, mode=mode)

    pdf_bytes = BytesIO()
    pdf.output_pdf(pdf_bytes)
    pdf_bytes.seek(0)


    email = EmailMessage(
        'Atrakcje Warszawy',
        'W załączniku znajduje się plik PDF zawierający Twój plan zwiedzania. Dziękujemy za skorzystanie z naszych usług.',
        settings.EMAIL_USER,
        [request.user.email],
    )

    email.attach('Plan_zwiedzania.pdf', pdf_bytes.read(), 'application/pdf')
    email.send()

    messages.success(request, 'Pomyślnie wysłano wiadomość email.')
    logger.info("Wysłano wiadomość e-mail z załączonym plikiem PDF")

    return redirect('koszyk')


def atrakcja(request, atrakcja_id):
    """
    Wyświetla szczegóły wybranej atrakcji.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    atrakcja_id (int): Identyfikator atrakcji, której szczegóły mają zostać wyświetlone.
    """
    logger.debug(f"Rozpoczęcie wyświetlania szczegółów atrakcji: {atrakcja_id}")

    atrakcja = get_object_or_404(Atrakcja, pk=atrakcja_id)
    obrazy = atrakcja.obraz.split(';')
    pierwszy_obraz = obrazy[0]

    logger.info(f"Załadowano szczegóły atrakcji: {atrakcja_id}")
    return render(request, 'atrakcja.html', {'atrakcja': atrakcja, 'pierwszy_obraz': pierwszy_obraz})


def plan_uzytkownika(request):
    """
    Wyświetla plany użytkownika wraz z powiązanymi atrakcjami.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    """
    logger.debug("Rozpoczęcie wyświetlania planów użytkownika")

    plany = PlanyUzytkownika.objects.filter(id_klienta=request.user).prefetch_related('atrakcje')
    plany_z_atrakcjami = []

    for plan in plany:
        atrakcje_z_obrazami = []
        for atrakcja in plan.atrakcje.all():
            obrazy = atrakcja.obraz.split(';')
            pierwsze_zdjecie = obrazy[0] if obrazy else None
            atrakcje_z_obrazami.append({
                'atrakcja': atrakcja,
                'pierwsze_zdjecie': pierwsze_zdjecie
            })
        plany_z_atrakcjami.append({
            'plan': plan,
            'atrakcje': atrakcje_z_obrazami
        })

    logger.info("Wyświetlono plany użytkownika")
    return render(request, 'plan_uzytkownika.html', {'plany_z_atrakcjami': plany_z_atrakcjami})


def zapisz_plan(request):
    """
    Zapisuje nowy plan użytkownika na podstawie elementów w koszyku.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    """
    if request.method == "POST":
        logger.debug("Rozpoczęcie zapisywania planu użytkownika")
        plan_name = request.POST.get('plan_name')
        koszyk_items = Koszyk.objects.filter(id_klienta=request.user)
        plan = PlanyUzytkownika.objects.create(
            id_klienta=request.user,
            nazwa_planu_uzytkownika=plan_name,
            data_utworzenia=timezone.now()
        )
        for item in koszyk_items:
            plan.atrakcje.add(item.id_atrakcji)
        plan.save()

        messages.success(request, 'Zapisano plan')
        logger.info(f"Zapisano plan: {plan_name}")
        return redirect('plan_uzytkownika')

    return render(request, 'zapisz_plan.html')


def usun_z_planu(request, plan_id):
    """
    Usuwa plan użytkownika z bazy danych.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    plan_id (int): Identyfikator planu, który ma zostać usunięty.
    """
    if request.method == "POST":
        logger.debug("Usuwanie planu uzytkownika")

        plan = PlanyUzytkownika.objects.get(id=plan_id)
        plan.delete()

        messages.success(request, 'Usunięto z planu')
        logger.info("Usunięto plan użytkownika")
        return redirect('plan_uzytkownika')

    return redirect('plan_uzytkownika')


def plan_do_koszyka(request, plan_id):
    """
    Wczytuje atrakcje z wybranego planu do koszyka użytkownika.

    Argumenty:
    request (HttpRequest): Obiekt żądania HTTP.
    plan_id (int): Identyfikator planu, z którego mają być wczytane atrakcje.
    """
    logger.debug("Rozpoczęcie wczytywania planu do koszyka")

    koszyk_items = Koszyk.objects.filter(id_klienta=request.user)
    koszyk_items.delete()

    plan = PlanyUzytkownika.objects.get(id=plan_id)

    for atrakcja in plan.atrakcje.all():
        koszyk = Koszyk.objects.create(id_atrakcji=atrakcja, id_klienta=request.user, cena_koncowa=atrakcja.cena_podstawowa, ilosc=1)
        koszyk.save()

    messages.success(request, 'Wczytano plan do koszyka')
    logger.info("Wczytano plan do koszyka")
    return redirect('koszyk')

@login_required
def docs_redirect(request):
    if request.user.is_staff:
        return HttpResponseRedirect('/static/docs/index.html')
    else:
        return redirect('logout')
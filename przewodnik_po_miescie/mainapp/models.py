from django.contrib.auth.models import User
from django.db import models
from decimal import Decimal


class Kategorie(models.Model):
    """
    Przechowuje pojedynczą kategorię, która może być przypisana do wielu atrakcji.
    """
    nazwa_kategorii = models.CharField(max_length=50, primary_key=True)


class Atrakcja(models.Model):
    """
    Przechowuje pojedynczą atrakcję, związaną z modelem `Kategorie`.
    """
    nazwa_atrakcji = models.CharField(max_length=50, default="Atrakcja")
    opis = models.TextField(max_length=1100)
    kategoria = models.ForeignKey(Kategorie, on_delete=models.CASCADE)
    cena_podstawowa = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    wiek_min = models.IntegerField()
    wiek_max = models.IntegerField()
    godzina_otwarcia = models.TimeField()
    godzina_zamkniecia = models.TimeField()
    czas_na_zwiedzanie = models.PositiveIntegerField()
    obraz = models.CharField(max_length=10000, default="")

    def __str__(self):
        return self.nazwa_atrakcji


class Adres_atrakcji(models.Model):
    """
    Przechowuje adres pojedynczej atrakcji, związany z modelem `Atrakcja`.
    """
    id_atrakcji = models.ForeignKey(Atrakcja, on_delete=models.CASCADE)
    kraj = models.CharField(max_length=50)
    miasto = models.CharField(max_length=50)
    kod_pocztowy = models.CharField(max_length=10)
    ulica = models.CharField(max_length=50)
    nr_budynku = models.CharField(max_length=50)
    nr_lokalu = models.CharField(max_length=50)


class Znizka(models.Model):
    """
    Przechowuje pojedynczą zniżkę, która może być stosowana do różnych atrakcji lub planów.
    """
    nazwa_znizki = models.CharField(max_length=30)
    mnoznik = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1.00'))

    def __str__(self):
        return self.nazwa_znizki


class Plan(models.Model):
    """
    Przechowuje pojedynczy plan utworzony przez użytkownika, związany z modelem `auth.User` oraz
    wieloma `Atrakcja` przez model `PrzypisanieAtrakcji`.
    """
    id_klienta = models.ForeignKey(User, on_delete=models.CASCADE)
    nazwa_planu = models.CharField(max_length=50)
    opis_planu = models.TextField(max_length=1100)
    atrakcje = models.ManyToManyField(Atrakcja, through="PrzypisanieAtrakcji")
    data_utworzenia = models.DateField()
    obraz = models.CharField(max_length=10000, default="")

    def __str__(self):
        return self.nazwa_planu
    
    def save(self, *args, **kwargs):
        """
        Niestandardowa metoda zapisu obliczająca końcową cenę planu
        na podstawie cen zawartych atrakcji.
        """
        if not self.pk:
            super().save(*args, **kwargs)

        self.cena_koncowa = sum(atrakcja.cena_podstawowa for atrakcja in self.atrakcje.all())
        super().save(*args, **kwargs)


class PrzypisanieAtrakcji(models.Model):
    """
    Model pośredni dla relacji wiele-do-wielu między modelami `Plan` i
    `Atrakcja`.
    """
    atrakcja = models.ForeignKey(Atrakcja, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)


class Koszyk(models.Model):
    """
    Przechowuje pojedynczy przedmiot w koszyku użytkownika, związany z modelami `Atrakcja` i
    `auth.User`.
    """
    id_atrakcji = models.ForeignKey(Atrakcja, on_delete=models.CASCADE)
    id_klienta = models.ForeignKey(User, on_delete=models.CASCADE)
    cena_koncowa = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    ilosc = models.IntegerField(default=1)


class PlanyUzytkownika(models.Model):
    id_klienta = models.ForeignKey(User, on_delete=models.CASCADE)
    nazwa_planu_uzytkownika = models.CharField(max_length=50)
    atrakcje = models.ManyToManyField(Atrakcja)
    data_utworzenia = models.DateField()
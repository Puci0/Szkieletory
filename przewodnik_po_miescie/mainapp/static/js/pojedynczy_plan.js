document.addEventListener('DOMContentLoaded', function() {
        const prevButton = document.getElementById('prevButton');
        const nextButton = document.getElementById('nextButton');
        const nazwaAtrakcji = document.getElementById('nazwa_atrakcji');
        const opisAtrakcji = document.getElementById('opis_atrakcji');
        const obrazAtrakcji = document.getElementById('obraz-atrakcji');

        let index = 0;
        const atrakcje = document.querySelectorAll('.plan .atrakcja');

        // Funkcja do aktualizacji opisu atrakcji
        function updateAtrakcja(index) {
            const atrakcja = atrakcje[index];
            nazwaAtrakcji.innerHTML = atrakcja.getAttribute('data-nazwa');
            opisAtrakcji.innerHTML = atrakcja.getAttribute('data-opis');
            obrazAtrakcji.src = atrakcja.getAttribute('data-obraz');
        }

        prevButton.addEventListener('click', function() {
            index = (index - 1 + atrakcje.length) % atrakcje.length;
            updateAtrakcja(index);
        });

        nextButton.addEventListener('click', function() {
            index = (index + 1) % atrakcje.length;
            updateAtrakcja(index);
        });

        updateAtrakcja(index);
    });
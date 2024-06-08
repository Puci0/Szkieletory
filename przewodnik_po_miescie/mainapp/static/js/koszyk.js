function pokazTabele(itemId) {
            var tabela = document.getElementById("tabela_" + itemId);
            if (tabela.style.display === "none") {
                tabela.style.display = "table";
            } else {
                tabela.style.display = "none";
            }
        }

        function obliczCenePoZnizce(itemId, select) {
            var wybranaZnizkaId = select.value;
            var mnoznikZnizki = parseFloat(select.options[select.selectedIndex].getAttribute('data-mnoznik'));
            var cenaPodstawowa = parseFloat(select.parentNode.previousElementSibling.innerText);
            var cenaPoZnizce = cenaPodstawowa - (cenaPodstawowa * mnoznikZnizki / 100);
            var tdCenaPoZnizce = select.parentNode.nextElementSibling;
            tdCenaPoZnizce.innerText = cenaPoZnizce.toFixed(2);

            var cenaKoncowaElement = document.getElementById("cena_po_znizce_" + itemId);
            var iloscElement = document.getElementById("ilosc_" + itemId);
            var cenaKoncowa = parseFloat(cenaPoZnizce) - (parseFloat(cenaPoZnizce) * parseInt(iloscElement.innerText)/100);

            obliczLacznaCene();
        }

        function obliczLacznaCene() {
            var sumaCen = 0;
            var cenaKoncowaElements = document.querySelectorAll('[id^="cena_po_znizce_"]');
            cenaKoncowaElements.forEach(function(element) {
                sumaCen += parseFloat(element.innerText);
            });

            var lacznaCenaElement = document.getElementById("laczna_cena");
            lacznaCenaElement.innerText = "Łączna cena: " + sumaCen.toFixed(2) + " zł";
        }
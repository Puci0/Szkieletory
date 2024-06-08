    function crossfadeOut(obraz, nowyObrazSrc) {
        var opacity = 1;
        var interval = setInterval(function() {
            opacity -= 0.05;
            obraz.style.opacity = opacity;
            if (opacity <= 0) {
                clearInterval(interval);
                obraz.src = nowyObrazSrc;
                crossfadeIn(obraz);
            }
        }, 15);
    }

    function crossfadeIn(obraz) {
        var opacity = 0;
        var interval = setInterval(function() {
            opacity += 0.05;
            obraz.style.opacity = opacity;
            if (opacity >= 1) {
                clearInterval(interval);
                obraz.style.opacity = 1;
            }
        }, 15);
    }

    function poprzedniObraz(obrazy, numerAtrakcji) {
        var obraz = document.getElementById('obraz-atrakcji-' + numerAtrakcji);
        var index = obrazy.indexOf(obraz.src) - 1;
        if (index < 0) {
            index = obrazy.length - 1;
        }
        crossfadeOut(obraz, obrazy[index]);
    }

    function nastepnyObraz(obrazy, numerAtrakcji) {
        var obraz = document.getElementById('obraz-atrakcji-' + numerAtrakcji);
        var index = obrazy.indexOf(obraz.src) + 1;
        if (index >= obrazy.length) {
            index = 0;
        }
        crossfadeOut(obraz, obrazy[index]);
    }
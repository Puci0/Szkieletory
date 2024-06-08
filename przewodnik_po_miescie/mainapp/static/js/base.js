$(document).ready(function() {
    function showMessagesSequentially() {
        var $messages = $('.messages li');
        var index = 0;

        function showMessage() {
            if (index < $messages.length) {
                var $currentMessage = $messages.eq(index);
                $currentMessage.fadeIn(500, function() {
                    setTimeout(function() {
                        $currentMessage.fadeOut(1000, function() {
                            index++;
                            showMessage();
                        });
                    }, 1000);
                });
            }
        }

        $messages.hide();
        showMessage();
    }
    showMessagesSequentially();
});

document.addEventListener('DOMContentLoaded', (event) => {
    let scrollPos = localStorage.getItem('scrollPos');
    if (scrollPos) {
        window.scrollTo({ top: parseInt(scrollPos), behavior: 'smooth' });
        localStorage.removeItem('scrollPos');
    }
});

window.addEventListener('beforeunload', (event) => {
    localStorage.setItem('scrollPos', window.scrollY);
});
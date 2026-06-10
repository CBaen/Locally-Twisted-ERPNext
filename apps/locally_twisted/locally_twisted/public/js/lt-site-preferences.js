(function () {
    'use strict';

    var STORAGE_KEY = 'lt_cookie_consent';
    var COOKIE_NAME = 'lt_cookie_consent';

    function getStoredChoice() {
        try {
            return window.localStorage.getItem(STORAGE_KEY);
        } catch (err) {
            return null;
        }
    }

    function storeChoice(choice) {
        try {
            window.localStorage.setItem(STORAGE_KEY, choice);
        } catch (err) {
            /* localStorage may be unavailable; keep the cookie fallback. */
        }
        try {
            document.cookie = COOKIE_NAME + '=' + encodeURIComponent(choice) + '; path=/; max-age=31536000; SameSite=Lax';
        } catch (err) {
            /* ignore cookie write failures */
        }
        window.dispatchEvent(new CustomEvent('lt-cookie-consent', { detail: { choice: choice } }));
    }

    function removeBanner(banner) {
        if (banner && banner.parentNode) {
            banner.parentNode.removeChild(banner);
        }
    }

    function buildBanner() {
        var banner = document.createElement('section');
        banner.className = 'lt-cookie-consent';
        banner.setAttribute('aria-label', 'Cookie and tracking choices');

        var copy = document.createElement('p');
        copy.className = 'lt-cookie-consent__copy';
        copy.textContent = 'We use cookies and similar tools for cart/session features, analytics, advertising, and marketing measurement.';

        var link = document.createElement('a');
        link.className = 'lt-cookie-consent__link';
        link.href = '/privacy';
        link.textContent = 'Privacy details';
        copy.appendChild(document.createTextNode(' '));
        copy.appendChild(link);

        var actions = document.createElement('div');
        actions.className = 'lt-cookie-consent__actions';

        var decline = document.createElement('button');
        decline.type = 'button';
        decline.className = 'lt-cookie-consent__button lt-cookie-consent__button--secondary';
        decline.textContent = 'Decline optional';

        var accept = document.createElement('button');
        accept.type = 'button';
        accept.className = 'lt-cookie-consent__button lt-cookie-consent__button--primary';
        accept.textContent = 'Accept';

        decline.addEventListener('click', function () {
            storeChoice('declined');
            removeBanner(banner);
        });
        accept.addEventListener('click', function () {
            storeChoice('accepted');
            removeBanner(banner);
        });

        actions.appendChild(decline);
        actions.appendChild(accept);
        banner.appendChild(copy);
        banner.appendChild(actions);
        return banner;
    }

    function init() {
        var choice = getStoredChoice();
        window.LT_COOKIE_CONSENT = {
            getChoice: getStoredChoice,
            accept: function () { storeChoice('accepted'); },
            decline: function () { storeChoice('declined'); },
            hasAcceptedOptional: function () { return getStoredChoice() === 'accepted'; }
        };

        if (choice === 'accepted' || choice === 'declined') {
            return;
        }
        var banner = buildBanner();
        var homeReviews = document.querySelector('.lt-reviews-block');
        var formSurface = document.querySelector('.lt-contact__grid, .lt-btfp__booking-grid');
        var loginSurface = document.querySelector('[data-lt-customer-login]');
        if (homeReviews) {
            banner.classList.add('lt-cookie-consent--inline');
            homeReviews.insertAdjacentElement('afterend', banner);
            return;
        }
        if (formSurface) {
            banner.classList.add('lt-cookie-consent--inline');
            formSurface.insertAdjacentElement('afterend', banner);
            return;
        }
        if (loginSurface) {
            banner.classList.add('lt-cookie-consent--inline');
            loginSurface.insertAdjacentElement('afterend', banner);
            return;
        }
        document.body.appendChild(banner);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
}());

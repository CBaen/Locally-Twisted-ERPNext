(function () {
  "use strict";

  var GA4_MEASUREMENT_ID = "G-0Z0WY5XQRB";
  var GTAG_SRC = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(GA4_MEASUREMENT_ID);
  var SCRIPT_ID = "lt-ga4-measurement";
  var loaded = false;

  function consentAccepted() {
    return !!(
      window.LT_COOKIE_CONSENT &&
      typeof window.LT_COOKIE_CONSENT.hasAcceptedOptional === "function" &&
      window.LT_COOKIE_CONSENT.hasAcceptedOptional()
    );
  }

  function initDataLayer() {
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () {
      window.dataLayer.push(arguments);
    };
  }

  function loadGA4() {
    if (loaded || !consentAccepted()) return false;
    loaded = true;

    initDataLayer();
    window.gtag("js", new Date());
    window.gtag("config", GA4_MEASUREMENT_ID, {
      send_page_view: true
    });

    if (!document.getElementById(SCRIPT_ID)) {
      var script = document.createElement("script");
      script.id = SCRIPT_ID;
      script.async = true;
      script.src = GTAG_SRC;
      document.head.appendChild(script);
    }
    return true;
  }

  function onConsent(event) {
    if (event && event.detail && event.detail.choice === "accepted") {
      loadGA4();
    }
  }

  window.LT = window.LT || {};
  window.LT.marketingMeasurement = {
    ga4MeasurementId: GA4_MEASUREMENT_ID,
    loadGA4: loadGA4,
    isLoaded: function () { return loaded; }
  };

  window.addEventListener("lt-cookie-consent", onConsent);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadGA4);
  } else {
    loadGA4();
  }
})();

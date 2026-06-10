(function () {
  "use strict";

  var DEFAULT_GA4_MEASUREMENT_ID = "G-0Z0WY5XQRB";
  var GTAG_SCRIPT_ID = "lt-gtag-measurement";
  var GTM_SCRIPT_ID = "lt-gtm-measurement";
  var loaded = false;

  function readConfig() {
    var node = document.getElementById("lt-marketing-tracking-config");
    if (!node) return {};
    try {
      return JSON.parse(node.textContent || "{}") || {};
    } catch (error) {
      return {};
    }
  }

  var config = readConfig();

  function cleanId(value) {
    return String(value || "").trim();
  }

  function trackingEnabled() {
    return config.enabled !== false;
  }

  function ga4MeasurementId() {
    return cleanId(config.ga4_measurement_id) || DEFAULT_GA4_MEASUREMENT_ID;
  }

  function googleAdsConversionId() {
    return cleanId(config.google_ads_conversion_id);
  }

  function gtmContainerId() {
    return cleanId(config.gtm_container_id);
  }

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

  function loadExternalScript(id, src) {
    if (document.getElementById(id)) return;
    var script = document.createElement("script");
    script.id = id;
    script.async = true;
    script.src = src;
    document.head.appendChild(script);
  }

  function loadGtag() {
    var ga4Id = ga4MeasurementId();
    var adsId = googleAdsConversionId();
    var firstId = ga4Id || adsId;
    if (!firstId) return false;

    initDataLayer();
    window.gtag("js", new Date());
    if (ga4Id) {
      window.gtag("config", ga4Id, {
        send_page_view: true
      });
    }
    if (adsId) {
      window.gtag("config", adsId);
    }
    loadExternalScript(
      GTAG_SCRIPT_ID,
      "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(firstId)
    );
    return true;
  }

  function loadGTM() {
    var containerId = gtmContainerId();
    if (!containerId) return false;

    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      "gtm.start": new Date().getTime(),
      event: "gtm.js"
    });
    loadExternalScript(
      GTM_SCRIPT_ID,
      "https://www.googletagmanager.com/gtm.js?id=" + encodeURIComponent(containerId)
    );
    return true;
  }

  function loadMarketingMeasurement() {
    if (loaded || !trackingEnabled() || !consentAccepted()) return false;
    loaded = true;
    var loadedGtag = loadGtag();
    var loadedTagManager = loadGTM();
    return loadedGtag || loadedTagManager;
  }

  function onConsent(event) {
    if (event && event.detail && event.detail.choice === "accepted") {
      loadMarketingMeasurement();
    }
  }

  window.LT = window.LT || {};
  window.LT.marketingMeasurement = {
    config: config,
    ga4MeasurementId: ga4MeasurementId(),
    gtmContainerId: gtmContainerId(),
    googleAdsConversionId: googleAdsConversionId(),
    loadGA4: loadMarketingMeasurement,
    loadMarketingMeasurement: loadMarketingMeasurement,
    isLoaded: function () { return loaded; }
  };

  window.addEventListener("lt-cookie-consent", onConsent);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadMarketingMeasurement);
  } else {
    loadMarketingMeasurement();
  }
})();

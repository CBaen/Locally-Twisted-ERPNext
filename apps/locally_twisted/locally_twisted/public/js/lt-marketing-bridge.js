(function () {
  "use strict";

  var STORAGE_KEY = "lt_marketing_attribution_v1";
  var FORM_FIELD = "lt_marketing_attribution";
  var ALLOWED_PARAMS = [
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "gbraid",
    "wbraid",
    "fbclid"
  ];

  function clean(value) {
    return String(value || "")
      .replace(/\s+/g, " ")
      .replace(/[^a-zA-Z0-9 _.,:/?&=+#@%~-]+/g, "")
      .slice(0, 180)
      .trim();
  }

  function currentAttribution() {
    var params = new URLSearchParams(window.location.search || "");
    var data = {};
    ALLOWED_PARAMS.forEach(function (key) {
      var value = clean(params.get(key));
      if (value) data[key] = value;
    });
    data.landing_path = clean(window.location.pathname || "/");
    if (document.referrer) {
      try {
        var referrer = new URL(document.referrer);
        data.referrer = clean(referrer.origin + referrer.pathname);
      } catch (err) {
        data.referrer = clean(document.referrer.split("?")[0].split("#")[0]);
      }
    }
    return data;
  }

  function hasCampaignSignal(data) {
    return ALLOWED_PARAMS.some(function (key) {
      return !!data[key];
    });
  }

  function readStored() {
    try {
      return JSON.parse(window.sessionStorage.getItem(STORAGE_KEY) || "{}") || {};
    } catch (err) {
      return {};
    }
  }

  function store(data) {
    try {
      window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (err) {}
  }

  function attributionPayload() {
    var fresh = currentAttribution();
    if (hasCampaignSignal(fresh)) {
      store(fresh);
      return fresh;
    }
    return readStored();
  }

  function attachAttribution(form) {
    var data = attributionPayload();
    if (!Object.keys(data).length) return;
    var input = form.querySelector("input[name='" + FORM_FIELD + "']");
    if (!input) {
      input = document.createElement("input");
      input.type = "hidden";
      input.name = FORM_FIELD;
      form.appendChild(input);
    }
    input.value = JSON.stringify(data);
  }

  function bindForms() {
    document.querySelectorAll("form").forEach(function (form) {
      form.addEventListener("submit", function () {
        attachAttribution(form);
      });
    });
  }

  function primeAttribution() {
    attributionPayload();
  }

  function ready() {
    primeAttribution();
    bindForms();
  }

  window.LT = window.LT || {};
  window.LT.marketingBridge = {
    attributionPayload: attributionPayload,
    attachAttribution: attachAttribution
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ready);
  } else {
    ready();
  }
})();

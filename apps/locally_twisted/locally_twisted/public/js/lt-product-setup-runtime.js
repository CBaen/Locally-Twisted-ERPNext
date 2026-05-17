(() => {
  "use strict";

  let schema = null;

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  function setupSchema() {
    if (schema) return schema;
    const script = document.querySelector(".js-lt-product-setup-schema");
    if (!script) return null;
    try {
      schema = JSON.parse(script.textContent || "{}");
    } catch (error) {
      schema = null;
    }
    return schema;
  }

  function setupGroups() {
    const current = setupSchema();
    if (!current || current.source !== "lt_product_setup") return [];
    return (current.selection_groups || []).filter((group) => group.payload_target === "configuration_groups");
  }

  function approvedMediaRules() {
    const current = setupSchema();
    if (!current || current.source !== "lt_product_setup") return [];
    return (current.media_rules || []).filter((rule) => rule.approved_for_customer && rule.image);
  }

  function text(value) {
    return String(value || "").trim();
  }

  function slug(value) {
    return text(value).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "selection";
  }

  function el(tag, attrs, content) {
    const node = document.createElement(tag);
    Object.keys(attrs || {}).forEach((key) => {
      if (key === "class") node.className = attrs[key];
      else if (key === "text") node.textContent = attrs[key];
      else node.setAttribute(key, attrs[key]);
    });
    if (content !== undefined && content !== null) node.textContent = content;
    return node;
  }

  function renderSetupGroups() {
    const form = document.querySelector(".lt-product__configure");
    if (!form) return;
    const mount = form.querySelector(".js-lt-product-setup-groups");
    if (!mount) return;
    const groups = setupGroups();
    mount.replaceChildren();
    if (!groups.length) return;

    groups.forEach((group, index) => {
      const key = group.key || slug(group.label);
      const wrapper = el("div", {
        class: "lt-product__attr js-lt-product-setup-group",
        "data-setup-key": key,
        "data-setup-label": group.label || key,
        "data-document-output": group.document_output || "Customer and operator",
        "data-min-selections": group.min_selections || 0,
        "data-max-selections": group.max_selections || 0
      });
      const labelId = `lt-setup-${index + 1}`;
      wrapper.appendChild(el("label", { class: "lt-product__attr-label", id: labelId, text: group.label || key }));
      renderGroupControl(wrapper, group, key, labelId);
      mount.appendChild(wrapper);
    });
  }

  function renderGroupControl(wrapper, group, key, labelId) {
    const values = group.values || [];
    const control = group.control_type || "Single select";
    if (control === "Text" || control === "Number" || control === "File upload" || !values.length) {
      const input = el("input", {
        class: "lt-product__select js-lt-product-setup-input",
        "data-setup-key": key,
        type: control === "Number" ? "number" : "text",
        "aria-labelledby": labelId
      });
      wrapper.appendChild(input);
      return;
    }

    const isMulti = control === "Multi select";
    const list = el("div", {
      class: "lt-product__chips",
      role: isMulti ? "group" : "radiogroup",
      "aria-labelledby": labelId
    });
    values.forEach((value) => {
      const choice = el("label", { class: "lt-product__chip" });
      const input = el("input", {
        class: "lt-product__chip-input js-lt-product-setup-input",
        type: isMulti ? "checkbox" : "radio",
        name: `lt-setup-${key}`,
        value: value,
        "data-setup-key": key
      });
      choice.appendChild(input);
      choice.appendChild(el("span", { class: "lt-product__chip-label", text: value }));
      list.appendChild(choice);
    });
    wrapper.appendChild(list);
  }

  function collectConfigurationGroups(form) {
    const root = form || document;
    const rows = [];
    root.querySelectorAll(".js-lt-product-setup-group").forEach((group) => {
      const values = selectedGroupValues(group);
      if (!values.length) return;
      rows.push({
        key: group.getAttribute("data-setup-key") || "",
        label: group.getAttribute("data-setup-label") || "",
        values,
        document_output: group.getAttribute("data-document-output") || "Customer and operator"
      });
    });
    return rows;
  }

  function selectedGroupValues(group) {
    const inputs = Array.from(group.querySelectorAll(".js-lt-product-setup-input"));
    const checked = inputs.filter((input) => (input.type === "checkbox" || input.type === "radio") && input.checked);
    if (checked.length) return checked.map((input) => input.value).filter(Boolean);
    const typed = inputs.find((input) => input.type !== "checkbox" && input.type !== "radio");
    return typed && text(typed.value) ? [text(typed.value)] : [];
  }

  function selectedValueMap(form) {
    const values = {};
    const root = form || document;
    root.querySelectorAll(".lt-product__attr[data-attribute-name]").forEach((group) => {
      const label = group.getAttribute("data-attribute-name") || "";
      const selected = Array.from(group.querySelectorAll(".js-lt-attr-input:checked")).map((input) => input.value);
      const select = group.querySelector("select.js-lt-attr-input");
      const valueList = selected.length ? selected : (select && select.value ? [select.value] : []);
      if (!valueList.length) return;
      values[label] = valueList;
      values[slug(label)] = valueList;
    });
    collectConfigurationGroups(root).forEach((group) => {
      values[group.label] = group.values;
      values[group.key] = group.values;
      values[slug(group.label)] = group.values;
    });
    return values;
  }

  function selectedMediaRule(form, variantCode) {
    const rules = approvedMediaRules();
    if (!rules.length) return null;
    const values = selectedValueMap(form);
    const matches = rules
      .filter((rule) => mediaRuleMatches(rule, values, variantCode))
      .map((rule) => ({ rule, score: mediaRuleScore(rule) }))
      .sort((a, b) => b.score - a.score);
    return matches.length ? matches[0].rule : null;
  }

  function mediaRuleMatches(rule, values, variantCode) {
    const type = rule.rule_type || "Selection group";
    const conditions = mediaRuleConditions(rule);
    if (type === "Exact resolved variant") {
      return rule.variant_item === variantCode && conditionsMatch(conditions, values);
    }
    if (type === "Selection combination") {
      return conditions.length > 0 && conditionsMatch(conditions, values);
    }
    if (type === "Selection group") {
      const groupValues = values[rule.selection_group] || values[slug(rule.selection_group)];
      return Array.isArray(groupValues) && groupValues.indexOf(rule.selection_value) !== -1;
    }
    return false;
  }

  function mediaRuleScore(rule) {
    const type = rule.rule_type || "Selection group";
    const count = mediaRuleConditions(rule).length;
    if (type === "Exact resolved variant" && count) return 200 + count;
    if (type === "Selection combination") return 100 + count;
    if (type === "Exact resolved variant") return 80;
    if (type === "Selection group") return 10;
    return 0;
  }

  function conditionsMatch(conditions, values) {
    return conditions.every((condition) => {
      const group = condition.group || condition.selection_group || "";
      const value = condition.value || condition.selection_value || "";
      const groupValues = values[group] || values[slug(group)] || [];
      return Array.isArray(groupValues) && groupValues.indexOf(value) !== -1;
    });
  }

  function mediaRuleConditions(rule) {
    if (Array.isArray(rule.conditions)) return rule.conditions;
    const textValue = text(rule.selection_conditions);
    if (!textValue) return [];
    return textValue.split(/\r?\n/).map((line) => {
      const separator = line.indexOf("=") !== -1 ? "=" : ":";
      const parts = line.split(separator);
      if (parts.length < 2) return null;
      return { group: text(parts[0]), value: text(parts.slice(1).join(separator)) };
    }).filter((condition) => condition && condition.group && condition.value);
  }

  function enforceMaxSelections(event) {
    const input = event.target && event.target.closest ? event.target.closest(".js-lt-product-setup-input") : null;
    if (!input || input.type !== "checkbox" || !input.checked) return;
    const group = input.closest(".js-lt-product-setup-group");
    const max = Number(group && group.getAttribute("data-max-selections")) || 0;
    if (!max) return;
    const checked = group.querySelectorAll(".js-lt-product-setup-input[type='checkbox']:checked");
    if (checked.length > max) {
      input.checked = false;
    }
  }

  ready(() => {
    renderSetupGroups();
    document.addEventListener("change", enforceMaxSelections);
  });

  window.LT_PRODUCT_SETUP = {
    collectConfigurationGroups,
    selectedMediaRule,
    setupSchema
  };
})();

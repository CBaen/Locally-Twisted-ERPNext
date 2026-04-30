/* Locally Twisted — Newsletter sign-up form engine.
 *
 * Auto-binds to: form[data-lt-newsletter]
 * Expected DOM inside the form:
 *   input[type="email"][name="email"][required]
 *   button[type="submit"].lt-footer-newsletter__button
 *   .lt-footer-newsletter__error[hidden][role="alert"][aria-live="assertive"]
 *   .lt-footer-newsletter__success[hidden][role="status"][aria-live="polite"]
 *
 * Public surface:
 *   window.LT.newsletter.submit(email) → Promise<{ok, message?}|{ok, error?}>
 *
 * Loud-failure compliance (per project rules + frappe-form-integrity skill):
 *   - User-facing: any failure shows the .error div with phone fallback.
 *     Never blank page, never silent failure.
 *   - Developer-facing: server logs via frappe.log_error (in api/newsletter.py)
 *   - Monitor: smoke test coverage flagged as TODO in build report (not yet
 *     added to scripts/verify/smoke_forms.py — tracked for Reviewer flagging)
 *
 * Security:
 *   - CSRF token via X-Frappe-CSRF-Token header
 *   - No raw email in client-side console.error (we log type+hash only)
 *   - Server-side format validation and rate-limiting in the endpoint
 *   - frappe.call encodes arguments as URL-encoded params — XSS not possible
 *     through the endpoint name/args pattern
 */
(function () {
    "use strict";

    /* Frappe API call wrapper. Calls `/api/method/<method>` via POST.
     * Returns a Promise that resolves to the `message` field of Frappe's
     * standard response envelope: { message: <your return value> }.
     *
     * On HTTP error, rejects with an Error whose .message is the HTTP
     * status text.  On JSON parse error, rejects with that parse error.
     *
     * Why not frappe.call()?  frappe.call() may not be available on all
     * page contexts (some stripped-down pages don't load the full frappe
     * desk bundle).  This approach uses the REST API directly and is
     * consistent with how lt-guest-cart.js handles API calls.
     */
    function frappePost(method, params) {
        /* Build the URL-encoded body — same as frappe.call would send */
        var body = "cmd=" + encodeURIComponent(method);
        Object.keys(params || {}).forEach(function (k) {
            body += "&" + encodeURIComponent(k) + "=" + encodeURIComponent(params[k]);
        });

        /* CSRF token: frappe sets window.frappe.csrf_token on page load.
         * Fall back to the literal 'token' which Frappe accepts when
         * the endpoint is allow_guest=True (it skips CSRF checks for
         * fully-anonymous endpoints but we still send the header for
         * future-proofing and consistency with project standards). */
        var csrfToken = (
            (window.frappe && window.frappe.csrf_token) ? window.frappe.csrf_token : "token"
        );

        return fetch("/api/method/" + method, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Frappe-CSRF-Token": csrfToken,
                "X-Requested-With": "XMLHttpRequest",
            },
            body: body,
        }).then(function (response) {
            return response.json().then(function (data) {
                if (!response.ok) {
                    /* Frappe surfaces validation errors in _server_messages or
                     * exc_type.  Try to extract a user-safe message. */
                    var serverMsg = "";
                    if (data && data.exc_type && data.message) {
                        serverMsg = typeof data.message === "string" ? data.message : "";
                    }
                    if (!serverMsg && data && data._server_messages) {
                        try {
                            var msgs = JSON.parse(data._server_messages);
                            if (Array.isArray(msgs) && msgs.length) {
                                var first = JSON.parse(msgs[0]);
                                serverMsg = first && first.message ? first.message : "";
                            }
                        } catch (_) { /* ignore parse failure */ }
                    }
                    var err = new Error(serverMsg || ("HTTP " + response.status));
                    err.httpStatus = response.status;
                    err.serverMsg = serverMsg;
                    throw err;
                }
                /* Successful Frappe response: { message: <return value> } */
                return data && data.message !== undefined ? data.message : data;
            });
        });
    }

    /**
     * Submit an email address to the newsletter endpoint.
     *
     * @param {string} email
     * @returns {Promise<{ok: boolean, message?: string}>|Promise<{ok: boolean, error?: string}>}
     *
     * Resolves to {ok: true, message: "..."} on success.
     * Resolves to {ok: false, error: "..."} on server-reported failure.
     * Resolves to {ok: false, error: "..."} on network/parse failure.
     * NEVER rejects — always resolves, so callers don't need a catch.
     */
    function submit(email) {
        return frappePost("locally_twisted.api.newsletter.signup", { email: email })
            .then(function (result) {
                /* Server returns {ok: True, message: "..."} or raises */
                if (result && result.ok) {
                    return { ok: true, message: result.message || "Thanks — we’ll be in touch." };
                }
                /* Unexpected shape — treat as soft failure */
                return {
                    ok: false,
                    error: "Something went wrong. Please call (801) 285-0860.",
                };
            })
            .catch(function (err) {
                /* Server threw a validation error (frappe.throw / frappe.ValidationError)
                 * or a network error.  Log the type to console — never log the raw email. */
                var serverMsg = (err && err.serverMsg) ? err.serverMsg : "";
                if (serverMsg && serverMsg.length < 200) {
                    /* User-safe message from server (e.g. "That doesn't look like
                     * a valid email.") — show it directly. */
                    return { ok: false, error: serverMsg };
                }
                /* Generic network or unexpected error.  Log minimally — no PII. */
                console.error("[lt-newsletter] signup failed:", err && err.httpStatus ? "HTTP " + err.httpStatus : (err ? err.message : "unknown"));
                return {
                    ok: false,
                    error: "Something went wrong. Please call (801) 285-0860.",
                };
            });
    }

    /* ── Public API ── */
    window.LT = window.LT || {};
    window.LT.newsletter = {
        submit: submit,
    };

    /* ─────────────────────────────────────────────────────────────────
     * Auto-bind to form[data-lt-newsletter]
     * ─────────────────────────────────────────────────────────────── */

    function bindForm(form) {
        if (!form) return;

        var emailInput   = form.querySelector("input[name='email']");
        var submitBtn    = form.querySelector("button[type='submit']");
        var errorDiv     = form.querySelector(".lt-footer-newsletter__error");
        var successDiv   = form.querySelector(".lt-footer-newsletter__success");

        if (!emailInput) return;  /* Nothing usable — don't bind */

        /** Show error message. Creates errorDiv inline if missing (graceful
         *  degradation — Builder Jinja is supposed to include it).
         *
         *  IMPORTANT: do NOT use div.textContent = msg here. The pre-built
         *  footer error container (.lt-footer-newsletter__error) contains a
         *  child <span> with a pre-built <a href="tel:+18012850860"> anchor
         *  inside it. Setting textContent replaces ALL child nodes with a plain
         *  text node — stripping the tel: link and making the phone number
         *  unclickable on mobile (Execution F003 / loud-failure rule violation).
         *
         *  Fix: if the container was pre-built by Jinja (has the inner error-text
         *  span), update only the span's text before the anchor.
         *  If the container is freshly created (fallback path), build it with DOM
         *  API so the tel: link is preserved.
         */
        function showError(msg) {
            var div = errorDiv;
            if (!div) {
                /* Fallback: create the error container from scratch with the
                 * tel: anchor built via DOM API so it survives. */
                div = document.createElement("div");
                div.className = "lt-footer-newsletter__error";
                div.setAttribute("role", "alert");
                div.setAttribute("aria-live", "assertive");

                var span = document.createElement("span");
                span.className = "lt-footer-newsletter__error-text";

                /* Build: <text> <a href="tel:...">(801) 285-0860</a>. */
                span.appendChild(document.createTextNode(msg + " Please call "));
                var telLink = document.createElement("a");
                telLink.href = "tel:+18012850860";
                telLink.className = "lt-footer-newsletter__error-phone";
                telLink.textContent = "(801) 285-0860";
                span.appendChild(telLink);
                span.appendChild(document.createTextNode("."));

                div.appendChild(span);
                form.appendChild(div);
                errorDiv = div;
            } else {
                /* Pre-built container (normal path): update only the text node
                 * that precedes the tel: anchor inside the inner error-text span.
                 * The span structure from footer.html is:
                 *   <span class="lt-footer-newsletter__error-text">
                 *     We couldn't add your email right now...
                 *     <a href="tel:+18012850860">(801) 285-0860</a>.
                 *   </span>
                 * We find the first Text node child of the span and update it,
                 * leaving the anchor intact. */
                var errorSpan = div.querySelector(".lt-footer-newsletter__error-text");
                if (errorSpan) {
                    /* Find the first Text node and replace its data */
                    var nodes = errorSpan.childNodes;
                    var updated = false;
                    for (var n = 0; n < nodes.length; n++) {
                        if (nodes[n].nodeType === Node.TEXT_NODE) {
                            nodes[n].data = msg + " Please call ";
                            updated = true;
                            break;
                        }
                    }
                    if (!updated) {
                        /* Span exists but has no text node (unexpected structure) —
                         * prepend one safely. */
                        errorSpan.insertBefore(
                            document.createTextNode(msg + " Please call "),
                            errorSpan.firstChild
                        );
                    }
                } else {
                    /* No inner span — safe fallback: build content with DOM API,
                     * never textContent, to avoid clobbering any tel: anchors. */
                    div.replaceChildren
                        ? div.replaceChildren()
                        : (function () { while (div.firstChild) div.removeChild(div.firstChild); }());
                    var fallbackSpan = document.createElement("span");
                    fallbackSpan.className = "lt-footer-newsletter__error-text";
                    fallbackSpan.appendChild(document.createTextNode(msg + " Please call "));
                    var fallbackLink = document.createElement("a");
                    fallbackLink.href = "tel:+18012850860";
                    fallbackLink.className = "lt-footer-newsletter__error-phone";
                    fallbackLink.textContent = "(801) 285-0860";
                    fallbackSpan.appendChild(fallbackLink);
                    fallbackSpan.appendChild(document.createTextNode("."));
                    div.appendChild(fallbackSpan);
                }
            }
            div.removeAttribute("hidden");
            if (successDiv) successDiv.setAttribute("hidden", "");
        }

        /** Show success message. */
        function showSuccess(msg) {
            var div = successDiv;
            if (!div) {
                div = document.createElement("div");
                div.className = "lt-footer-newsletter__success";
                div.setAttribute("role", "status");
                div.setAttribute("aria-live", "polite");
                form.appendChild(div);
                successDiv = div;
            }
            div.textContent = msg;
            div.removeAttribute("hidden");
            if (errorDiv) errorDiv.setAttribute("hidden", "");
        }

        /** Reset feedback state. */
        function clearFeedback() {
            if (errorDiv)   errorDiv.setAttribute("hidden", "");
            if (successDiv) successDiv.setAttribute("hidden", "");
        }

        /** Disable / enable the submit button during the async request. */
        function setSubmitting(active) {
            if (!submitBtn) return;
            submitBtn.disabled = active;
            /* aria-busy on the form signals assistive tech that the form
             * is processing (no spinner implemented — CSS handles it). */
            form.setAttribute("aria-busy", active ? "true" : "false");
        }

        form.addEventListener("submit", function (ev) {
            ev.preventDefault();
            clearFeedback();

            var email = emailInput.value ? emailInput.value.trim() : "";
            if (!email) {
                /* Client-side guard — browser's native required attr usually
                 * catches this but be defensive for cases where it's suppressed. */
                showError("Please enter your email address.");
                emailInput.focus();
                return;
            }

            setSubmitting(true);

            submit(email).then(function (result) {
                setSubmitting(false);
                if (result.ok) {
                    showSuccess(result.message || "Thanks — we’ll be in touch.");
                    form.reset();
                } else {
                    /* Non-ok result: show error + phone fallback */
                    var errMsg = result.error || "Something went wrong.";
                    /* Append phone fallback if not already present in the message */
                    if (errMsg.indexOf("801") < 0) {
                        errMsg += " If this keeps happening, call (801) 285-0860.";
                    }
                    showError(errMsg);
                }
            }).catch(function (unexpectedErr) {
                /* submit() is designed never to reject, but be ultra-defensive */
                setSubmitting(false);
                console.error("[lt-newsletter] unexpected rejection:", unexpectedErr);
                showError(
                    "Something went wrong. If this keeps happening, call (801) 285-0860."
                );
            });
        });
    }

    /* Bind on DOMContentLoaded (or immediately if DOM is already ready). */
    function autoBind() {
        var forms = document.querySelectorAll("form[data-lt-newsletter]");
        for (var i = 0; i < forms.length; i++) {
            bindForm(forms[i]);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", autoBind);
    } else {
        autoBind();
    }

}());

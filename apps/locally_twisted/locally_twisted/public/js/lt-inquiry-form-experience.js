(function () {
    'use strict';

    var FORM_SELECTOR = "form[data-form-contract='inquiry-v1']";
    var ENDPOINT = '/api/method/locally_twisted.www.book.submit_book_inquiry';
    var FALLBACK_ERROR = 'Tiny snag: your request did not send. Please try again, or call (801) 285-0860 or email hi@locallytwisted.com and we will help.';
    var DEFAULT_SUCCESS = 'A confirmation of your request will be sent to your email address shortly. We will be in contact within 24 hours!';
    var FIELD_ERROR = {
        contact_name: 'Please tell us your name.',
        email_from: 'Please enter a valid email address.',
        email_invalid: 'Please enter a valid email address.',
        phone: 'Please enter a phone number so we have a second way to contact you about your inquiry.',
        preferred_contact_method: 'Please choose how you prefer to be contacted.',
        x_occasion_type: 'Please choose an event type.',
        x_event_date: 'Please choose the event date.',
        x_event_location: 'Please tell us the city or location for the event.'
    };
    var COMMON_EMAIL_DOMAINS = [
        'gmail.com',
        'yahoo.com',
        'icloud.com',
        'hotmail.com',
        'outlook.com',
        'aol.com',
        'msn.com',
        'live.com',
        'comcast.net',
        'me.com'
    ];
    var EMAIL_DOMAIN_FIXES = {
        'gamil.com': 'gmail.com',
        'gmail.con': 'gmail.com',
        'gmal.com': 'gmail.com',
        'gmial.com': 'gmail.com',
        'gnail.com': 'gmail.com',
        'yaho.com': 'yahoo.com',
        'yahoo.con': 'yahoo.com',
        'hotmial.com': 'hotmail.com',
        'hotmail.con': 'hotmail.com',
        'outlok.com': 'outlook.com',
        'outlook.con': 'outlook.com',
        'iclod.com': 'icloud.com',
        'icloud.con': 'icloud.com'
    };

    var STATUS_COPY = {
        details: {
            title: 'Checking your details',
            message: 'We are making sure the basics are ready before your request goes to the team.',
            activeStep: 'details'
        },
        send: {
            title: 'Sending to Locally Twisted',
            message: 'Your event notes are on their way.',
            activeStep: 'send'
        },
        save: {
            title: 'Saving your request',
            message: 'We are checking that the request is saved before we call this done.',
            activeStep: 'save'
        },
        success: {
            title: 'Request received',
            message: DEFAULT_SUCCESS,
            activeStep: 'save'
        },
        error: {
            title: 'Let us try that again',
            message: FALLBACK_ERROR,
            activeStep: null
        }
    };

    function ready(fn) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', fn);
        } else {
            fn();
        }
    }

    function textOf(field) {
        return field && field.value ? field.value.trim() : '';
    }

    function safeFocus(field) {
        if (!field) return;
        try {
            field.focus({ preventScroll: true });
        } catch (err) {
            field.focus();
        }
        field.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function statusFor(form) {
        return form.querySelector('[data-lt-form-status]');
    }

    function setStatus(form, state, message) {
        var status = statusFor(form);
        if (!status) return;

        var copy = STATUS_COPY[state] || STATUS_COPY.details;
        var titleEl = status.querySelector('[data-lt-form-status-title]');
        var messageEl = status.querySelector('[data-lt-form-status-message]');
        var steps = status.querySelectorAll('[data-lt-form-status-step]');

        status.hidden = false;
        status.dataset.state = state;
        status.setAttribute('role', state === 'error' ? 'alert' : 'status');

        if (titleEl) titleEl.textContent = copy.title;
        if (messageEl) messageEl.textContent = message || copy.message;

        Array.prototype.forEach.call(steps, function (step) {
            var name = step.getAttribute('data-lt-form-status-step');
            var active = name === copy.activeStep;
            var complete = state === 'success' || (
                copy.activeStep === 'send' && name === 'details'
            ) || (
                copy.activeStep === 'save' && (name === 'details' || name === 'send')
            );

            step.toggleAttribute('data-active', active);
            step.toggleAttribute('data-complete', complete);
        });
    }

    function describedByTokens(field) {
        return (field.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
    }

    function clearFieldError(field) {
        var errorId;
        var tokens;
        if (!field) return;

        errorId = field.dataset.ltErrorDescribedBy || '';
        if (errorId) {
            tokens = describedByTokens(field).filter(function (token) {
                return token !== errorId;
            });
            if (tokens.length) {
                field.setAttribute('aria-describedby', tokens.join(' '));
            } else {
                field.removeAttribute('aria-describedby');
            }
            delete field.dataset.ltErrorDescribedBy;
        }
        field.removeAttribute('aria-invalid');
    }

    function clearFeedback(form) {
        var feedback = form.querySelector('#book_feedback');
        if (feedback) {
            feedback.textContent = '';
            feedback.classList.remove('is-error');
        }
        Array.prototype.forEach.call(form.querySelectorAll('[data-lt-field-error-for]'), function (error) {
            error.textContent = '';
            error.hidden = true;
        });
        Array.prototype.forEach.call(form.querySelectorAll('[aria-invalid="true"]'), function (field) {
            clearFieldError(field);
        });
    }

    function showFieldError(form, field, message) {
        var error = field && field.name ? form.querySelector('[data-lt-field-error-for="' + field.name + '"]') : null;
        var tokens;
        if (!error) return;

        error.textContent = message;
        error.hidden = false;

        if (!error.id) return;
        tokens = describedByTokens(field);
        if (tokens.indexOf(error.id) === -1) {
            tokens.push(error.id);
            field.setAttribute('aria-describedby', tokens.join(' '));
        }
        field.dataset.ltErrorDescribedBy = error.id;
    }

    function editDistance(a, b) {
        var matrix = [];
        var i;
        var j;
        for (i = 0; i <= b.length; i += 1) matrix[i] = [i];
        for (j = 0; j <= a.length; j += 1) matrix[0][j] = j;
        for (i = 1; i <= b.length; i += 1) {
            for (j = 1; j <= a.length; j += 1) {
                matrix[i][j] = b.charAt(i - 1) === a.charAt(j - 1)
                    ? matrix[i - 1][j - 1]
                    : Math.min(
                        matrix[i - 1][j - 1] + 1,
                        matrix[i][j - 1] + 1,
                        matrix[i - 1][j] + 1
                    );
            }
        }
        return matrix[b.length][a.length];
    }

    function suggestedEmail(email) {
        var value = (email || '').trim();
        var at = value.lastIndexOf('@');
        if (at <= 0 || at === value.length - 1) return '';
        var local = value.slice(0, at);
        var domain = value.slice(at + 1).toLowerCase();
        var suggestion = EMAIL_DOMAIN_FIXES[domain] || '';
        if (!suggestion) {
            COMMON_EMAIL_DOMAINS.some(function (known) {
                if (domain === known) return true;
                if (Math.abs(domain.length - known.length) > 2) return false;
                if (editDistance(domain, known) <= 2) {
                    suggestion = known;
                    return true;
                }
                return false;
            });
        }
        return suggestion ? local + '@' + suggestion : '';
    }

    function emailMessageWithSuggestion(message, email) {
        var suggestion = suggestedEmail(email);
        return suggestion ? message + ' Did you mean ' + suggestion + '?' : message;
    }

    function setEmailSuggestion(form) {
        var field = form.elements.email_from;
        var hint = form.querySelector('#book_email_hint');
        if (!field || !hint) return;
        var suggestion = suggestedEmail(textOf(field));
        hint.textContent = suggestion ? 'Did you mean ' + suggestion + '?' : '';
    }

    function showError(form, message, fieldName) {
        var finalMessage = message || FALLBACK_ERROR;
        var feedback = form.querySelector('#book_feedback');
        var field = fieldName ? form.elements[fieldName] : null;

        setStatus(form, 'error', finalMessage);
        if (feedback) {
            feedback.textContent = finalMessage;
            feedback.classList.add('is-error');
        }
        if (field) {
            field.setAttribute('aria-invalid', 'true');
            showFieldError(form, field, finalMessage);
            safeFocus(field);
            return;
        }

        var status = statusFor(form);
        if (status) status.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function validate(form) {
        if (!textOf(form.elements.x_event_date)) {
            return { ok: false, field: 'x_event_date', message: FIELD_ERROR.x_event_date };
        }
        if (!textOf(form.elements.x_event_location)) {
            return { ok: false, field: 'x_event_location', message: FIELD_ERROR.x_event_location };
        }
        if (!textOf(form.elements.x_occasion_type)) {
            return { ok: false, field: 'x_occasion_type', message: FIELD_ERROR.x_occasion_type };
        }
        if (!textOf(form.elements.contact_name)) {
            return { ok: false, field: 'contact_name', message: FIELD_ERROR.contact_name };
        }
        var emailField = form.elements.email_from;
        var email = textOf(emailField);
        if (!email) {
            return { ok: false, field: 'email_from', message: FIELD_ERROR.email_from };
        }
        if (emailField && !emailField.checkValidity()) {
            return {
                ok: false,
                field: 'email_from',
                message: emailMessageWithSuggestion(FIELD_ERROR.email_invalid, email)
            };
        }
        if (!textOf(form.elements.phone)) {
            return { ok: false, field: 'phone', message: FIELD_ERROR.phone };
        }
        if (!textOf(form.elements.preferred_contact_method)) {
            return {
                ok: false,
                field: 'preferred_contact_method',
                message: FIELD_ERROR.preferred_contact_method
            };
        }
        setEmailSuggestion(form);
        return { ok: true };
    }

    function setBusy(form, busy) {
        var submit = form.querySelector('[data-lt-form-submit]');
        var label = submit ? submit.querySelector('[data-lt-submit-label]') : null;
        form.setAttribute('aria-busy', busy ? 'true' : 'false');
        form.dataset.ltSubmitState = busy ? 'submitting' : 'idle';
        if (submit) {
            submit.disabled = busy;
            submit.classList.toggle('is-loading', busy);
        }
        if (label) label.textContent = busy ? 'Sending' : 'Send request';
    }

    function isSubmitting(form) {
        return form.dataset.ltSubmitState === 'submitting';
    }

    function isCustomerSafeMessage(message) {
        if (typeof message !== 'string') return false;
        var value = message.trim();
        if (!value) return false;
        return !/(Traceback|Exception|Error:|frappe\.|pymysql|DocType|doctype|SQL|stack)/i.test(value);
    }

    function parseServerError(body) {
        if (!body) return null;
        if (body._server_messages) {
            try {
                var msgs = JSON.parse(body._server_messages);
                if (Array.isArray(msgs) && msgs.length) {
                    var first = JSON.parse(msgs[0]);
                    if (isCustomerSafeMessage(first.message)) return first.message;
                }
            } catch (err) {
                return null;
            }
        }
        if (isCustomerSafeMessage(body.message)) return body.message;
        return null;
    }

    function responseJson(resp) {
        return resp.json().then(function (body) {
            return { status: resp.status, body: body };
        }).catch(function () {
            return { status: resp.status, body: null };
        });
    }

    function successMessage(result) {
        var uploadSummary = result && result.photo_uploads ? result.photo_uploads : {};
        var issueCount = (uploadSummary.rejected || []).length + (uploadSummary.failed || []).length;
        if (uploadSummary.submitted > 0 && issueCount > 0 && uploadSummary.customer_message) {
            return uploadSummary.customer_message;
        }
        return DEFAULT_SUCCESS;
    }

    function openModal(message) {
        var modal = document.getElementById('received');
        if (!modal) return;

        var messageEl = document.getElementById('received_message');
        var card = modal.querySelector('.lt-book__modal-card');
        if (messageEl) messageEl.textContent = message || DEFAULT_SUCCESS;

        modal.classList.add('lt-book__modal--open');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        if (card) card.focus();
    }

    function closeModal() {
        var modal = document.getElementById('received');
        if (!modal) return;
        modal.classList.remove('lt-book__modal--open');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        if (window.location.hash === '#received' && window.history && window.history.replaceState) {
            window.history.replaceState(null, '', window.location.pathname + window.location.search);
        }
    }

    function wireModal() {
        var modal = document.getElementById('received');
        if (!modal) return;

        var close = modal.querySelector("[data-lt-modal-action='stay']");
        var backdrop = modal.querySelector('.lt-book__modal-backdrop');
        if (close) close.addEventListener('click', closeModal);
        if (backdrop) backdrop.addEventListener('click', closeModal);

        document.addEventListener('keydown', function (event) {
            if (event.key !== 'Escape') return;
            if (!modal.classList.contains('lt-book__modal--open')) return;
            closeModal();
        });

    }

    function resetAfterSuccess(form) {
        form.reset();
        setEmailSuggestion(form);
        if (window.LT_INQUIRY_FORM && typeof window.LT_INQUIRY_FORM.updateConditionals === 'function') {
            window.LT_INQUIRY_FORM.updateConditionals();
        }
    }

    function submitForm(event) {
        event.preventDefault();

        var form = event.currentTarget;
        if (isSubmitting(form)) return;

        clearFeedback(form);

        var validation = validate(form);
        if (!validation.ok) {
            showError(form, validation.message, validation.field);
            return;
        }

        var data = new FormData(form);
        setBusy(form, true);
        setStatus(form, 'details');

        window.setTimeout(function () {
            if (isSubmitting(form)) setStatus(form, 'send');
        }, 160);

        fetch(ENDPOINT, {
            method: 'POST',
            headers: {
                'X-Frappe-CSRF-Token': (window.frappe && window.frappe.csrf_token) || 'token',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: data,
            credentials: 'same-origin'
        }).then(function (resp) {
            if (isSubmitting(form)) setStatus(form, 'save');
            return responseJson(resp);
        }).then(function (result) {
            setBusy(form, false);
            if (result.status >= 200 && result.status < 300 && result.body && result.body.message && result.body.message.ok) {
                var message = successMessage(result.body.message);
                resetAfterSuccess(form);
                setStatus(form, 'success', message);
                if (window.location.hash !== '#received') {
                    window.location.hash = 'received';
                }
                openModal(message);
                return;
            }
            showError(form, parseServerError(result.body) || FALLBACK_ERROR);
        }).catch(function (err) {
            setBusy(form, false);
            showError(form, FALLBACK_ERROR);
            if (window.console && console.error) console.error('Inquiry form submit failed', err);
        });
    }

    function bindForm(form) {
        if (!form || form.dataset.ltExperienceBound === 'true') return;
        form.dataset.ltExperienceBound = 'true';
        form.setAttribute('aria-busy', 'false');
        form.addEventListener('submit', submitForm);
        if (form.elements.email_from) {
            form.elements.email_from.addEventListener('input', function () {
                setEmailSuggestion(form);
            });
            form.elements.email_from.addEventListener('blur', function () {
                setEmailSuggestion(form);
            });
        }
    }

    ready(function () {
        Array.prototype.forEach.call(document.querySelectorAll(FORM_SELECTOR), bindForm);
        wireModal();
    });
}());

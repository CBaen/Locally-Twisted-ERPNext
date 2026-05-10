(function () {
    'use strict';

    var FORM_SELECTOR = "form[data-form-contract='inquiry-v1']";
    var ENDPOINT = '/api/method/locally_twisted.www.book.submit_book_inquiry';
    var FALLBACK_ERROR = 'Tiny snag: your request did not send. Please try again, or call (801) 285-0860 or email hi@locallytwisted.com and we will help.';
    var DEFAULT_SUCCESS = 'Thanks, we got it and will follow up soon.';
    var FIELD_ERROR = {
        contact_name: 'Please tell us your name.',
        email_from: 'Please give us an email so we can reply.'
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
            message: 'We will review it and follow up soon.',
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

    function clearFeedback(form) {
        var feedback = form.querySelector('#book_feedback');
        if (feedback) {
            feedback.textContent = '';
            feedback.classList.remove('is-error');
        }
        Array.prototype.forEach.call(form.querySelectorAll('[aria-invalid="true"]'), function (field) {
            field.removeAttribute('aria-invalid');
        });
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
            safeFocus(field);
            return;
        }

        var status = statusFor(form);
        if (status) status.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function validate(form) {
        if (!textOf(form.elements.contact_name)) {
            return { ok: false, field: 'contact_name', message: FIELD_ERROR.contact_name };
        }
        if (!textOf(form.elements.email_from)) {
            return { ok: false, field: 'email_from', message: FIELD_ERROR.email_from };
        }
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
        if (label) label.textContent = busy ? 'Sending' : 'Send';
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
    }

    ready(function () {
        Array.prototype.forEach.call(document.querySelectorAll(FORM_SELECTOR), bindForm);
        wireModal();
    });
}());

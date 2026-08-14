/* Volunteer + yard-sign form behaviour. Loaded with `defer` on volunteer.html
 * and yard-sign.html in all six languages.
 *
 * Same rule as site.v3.js: everything here is progressive enhancement. With no
 * JS the form is a plain <form method="post"> that posts straight to the Apps
 * Script endpoint and gets a thank-you page back, the conditional address
 * question is simply visible instead of revealed, and nothing is unreachable.
 * People sign up for this campaign from old phones on bad connections; the
 * form working is not allowed to depend on a script running.
 *
 * No user-facing English lives in this file. Every message is markup in the
 * page (#form-success, #form-error) or a data- attribute, so the Spanish,
 * Russian, Somali, Vietnamese and French pages translate normally and share
 * this file.
 *
 * Filename is versioned on purpose -- it is the cache key.
 */
(function () {
  'use strict';

  var form = document.querySelector('[data-signup-form]');
  if (!form) return;

  var PLACEHOLDER = 'PASTE_YOUR_WEB_APP_URL_HERE';
  var TIMEOUT_MS = 25000;

  var successPanel = document.getElementById('form-success');
  var errorPanel = document.getElementById('form-error');
  var unconfigured = document.getElementById('form-unconfigured');
  var submitBtn = form.querySelector('button[type="submit"]');

  /* ===============================================================
   * 1. Unconfigured endpoint.
   * Better to say so plainly than to accept someone's details into a
   * form that quietly throws them away.
   * ============================================================= */
  if (form.getAttribute('action').indexOf(PLACEHOLDER) !== -1) {
    if (unconfigured) unconfigured.hidden = false;
    form.setAttribute('aria-hidden', 'true');
    form.hidden = true;
    return;
  }

  document.documentElement.classList.add('js-forms');

  /* ===============================================================
   * 2. Conditional blocks.
   * A checkbox with data-reveals="id" shows or hides that block. The
   * CSS only collapses [data-collapsed] under .js-forms, so if this
   * never runs the block stays open and answerable.
   * ============================================================= */
  Array.prototype.forEach.call(
    form.querySelectorAll('[data-reveals]'),
    function (toggle) {
      var target = document.getElementById(toggle.getAttribute('data-reveals'));
      if (!target) return;

      function sync() {
        if (toggle.checked) {
          target.removeAttribute('data-collapsed');
        } else {
          target.setAttribute('data-collapsed', '');
          // Clear what is now hidden: a stale address left behind by an
          // unticked box would still be submitted.
          Array.prototype.forEach.call(
            target.querySelectorAll('input, textarea'),
            function (f) { f.value = ''; }
          );
        }
        // Only demand the address while the question is actually on screen.
        Array.prototype.forEach.call(
          target.querySelectorAll('[data-required-when-shown]'),
          function (f) {
            if (toggle.checked) f.setAttribute('required', '');
            else f.removeAttribute('required');
          }
        );
        toggle.setAttribute('aria-expanded', toggle.checked ? 'true' : 'false');
      }

      toggle.setAttribute('aria-controls', target.id);
      toggle.addEventListener('change', sync);
      sync(); // respect a value the browser restored on back-navigation
    }
  );

  /* ===============================================================
   * 3. "Phone or email, your choice."
   * The markup marks phone `required` so a no-JS submission still
   * carries a way to reach someone. With JS we can accept either.
   * ============================================================= */
  // Selecting every input in the fieldset would sweep in the name and
  // neighbourhood fields, and a filled-in name would then satisfy "we can reach
  // you" -- so the two fields that actually are contact details say so.
  var contactPair = form.querySelector('[data-contact-pair]');
  var contactFields = contactPair
    ? Array.prototype.slice.call(contactPair.querySelectorAll('input[data-contact]'))
    : [];

  contactFields.forEach(function (f) {
    f.removeAttribute('required');
    f.addEventListener('input', function () { f.setCustomValidity(''); });
  });

  function contactGiven() {
    if (!contactFields.length) return true;
    return contactFields.some(function (f) { return f.value.trim() !== ''; });
  }

  /* ===============================================================
   * 4. Submit into a hidden iframe.
   *
   * Not fetch(): an Apps Script web app answers a cross-origin POST
   * with a redirect to googleusercontent.com, and reading that back
   * depends on CORS behaviour that has broken more than once. A form
   * posting to a named iframe is the same request the browser would
   * make anyway, involves no CORS at all, and keeps the visitor on
   * the page. The trade is that we cannot read the response body --
   * hence the timeout below, and the endpoint check in SETUP.md.
   * ============================================================= */
  var sink = document.createElement('iframe');
  sink.name = 'signup-sink';
  sink.className = 'hp';
  sink.setAttribute('aria-hidden', 'true');
  sink.setAttribute('tabindex', '-1');
  sink.setAttribute('title', '');
  document.body.appendChild(sink);
  form.setAttribute('target', sink.name);

  var submitted = false;
  var timer = null;

  function finish(panel) {
    if (timer) { window.clearTimeout(timer); timer = null; }
    submitted = false;

    if (panel === successPanel) {
      form.hidden = true;
      var intro = document.querySelector('[data-form-intro]');
      if (intro) intro.hidden = true;
    } else if (submitBtn) {
      submitBtn.disabled = false;
      if (submitBtn.dataset.idleLabel) submitBtn.textContent = submitBtn.dataset.idleLabel;
    }

    if (!panel) return;
    panel.hidden = false;
    // Move the reading position to the outcome; a status panel that appears
    // above a scrolled-down form is invisible to the person who just submitted.
    panel.focus();
    if (panel.scrollIntoView) panel.scrollIntoView({ block: 'center' });
  }

  sink.addEventListener('load', function () {
    // Fires once on the blank initial document too -- only a load that follows
    // a submission is a response.
    if (!submitted) return;
    finish(successPanel);
  });

  form.addEventListener('submit', function (ev) {
    if (submitted) { ev.preventDefault(); return; }

    if (!contactGiven()) {
      ev.preventDefault();
      var first = contactFields[0];
      first.setCustomValidity(contactPair.getAttribute('data-invalid-msg') || ' ');
      first.reportValidity();
      return;
    }
    if (!form.checkValidity()) return; // let the browser show its own messages

    if (errorPanel) errorPanel.hidden = true;
    submitted = true;

    if (submitBtn) {
      submitBtn.dataset.idleLabel = submitBtn.textContent;
      submitBtn.disabled = true;
      if (submitBtn.dataset.sendingLabel) submitBtn.textContent = submitBtn.dataset.sendingLabel;
    }

    timer = window.setTimeout(function () { finish(errorPanel); }, TIMEOUT_MS);
  });

  /* ===============================================================
   * 5. Date bounds. Nobody can volunteer for a day that has passed or
   * for one after the election, so say so in the picker rather than
   * catching it later by hand.
   * ============================================================= */
  Array.prototype.forEach.call(
    form.querySelectorAll('input[type="date"]'),
    function (input) {
      if (input.getAttribute('min')) return;
      var now = new Date();
      var pad = function (n) { return (n < 10 ? '0' : '') + n; };
      input.setAttribute(
        'min',
        now.getFullYear() + '-' + pad(now.getMonth() + 1) + '-' + pad(now.getDate())
      );
    }
  );
})();

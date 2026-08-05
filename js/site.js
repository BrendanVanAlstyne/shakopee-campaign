/* Shared site behaviour. Loaded with `defer` on every page.
 *
 * Everything here is progressive enhancement: with JS off, or if an API is
 * missing, the page must still be fully readable. That rule is not cosmetic —
 * this site carries legally required disclaimer text and neighbours' accounts of
 * ICE raids, and none of it may depend on a script running.
 */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------------------------------------------------------
   * 1. Hover-to-preview on <details> disclosures.
   *
   * The markup is a plain <details>/<summary>, so click-to-expand and
   * keyboard access work with no JS at all. This only adds the pointer
   * affordance on top: hovering previews the panel, clicking pins it open.
   * Touch devices get click only — hover on touch produces sticky states.
   * ------------------------------------------------------------- */
  var canHover = window.matchMedia &&
    window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  if (canHover) {
    Array.prototype.forEach.call(
      document.querySelectorAll('details.disclosure'),
      function (d) {
        d.addEventListener('mouseenter', function () {
          if (d.dataset.pinned !== 'true') d.open = true;
        });
        d.addEventListener('mouseleave', function () {
          if (d.dataset.pinned !== 'true') d.open = false;
        });
        // A real click (or Enter/Space on the summary) pins the current state,
        // so it survives the pointer leaving.
        var summary = d.querySelector('summary');
        if (summary) {
          summary.addEventListener('click', function () {
            // At click time d.open is still the pre-toggle value.
            d.dataset.pinned = d.open ? 'false' : 'true';
          });
        }
      }
    );
  }

  /* ---------------------------------------------------------------
   * 2. Reveal statement boxes as they scroll into view.
   *
   * The hidden start state lives behind .js-reveal on <html>, which is only
   * added below. No JS, old browser, or reduced-motion preference => the class
   * is never added and every box renders normally.
   * ------------------------------------------------------------- */
  if (reduceMotion || !('IntersectionObserver' in window)) return;

  var SELECTOR = [
    '.priorities > li',   // direct children only: a nested sub-list would
    '.story',             // otherwise animate inside an animating parent
    '.vote-card',
    '.candidate-card'
  ].join(', ');

  var all = document.querySelectorAll(SELECTOR);
  if (!all.length) return;

  // Only ever hide what starts BELOW the fold. Anything already on screen is
  // left alone, so a script that never runs its observer can't blank the page.
  var boxes = Array.prototype.filter.call(all, function (el) {
    return el.getBoundingClientRect().top > window.innerHeight * 0.9;
  });
  if (!boxes.length) return;

  document.documentElement.classList.add('js-reveal');

  // Stagger within each group so a row of cards cascades instead of popping
  // in together. Reset per parent so a long list doesn't accumulate delay.
  var seen = [];
  boxes.forEach(function (el) {
    el.classList.add('reveal');
    var parent = el.parentNode;
    if (seen.indexOf(parent) === -1) { seen.push(parent); parent._revealCount = 0; }
    var n = parent._revealCount++;
    if (n < 6) el.style.transitionDelay = (n * 70) + 'ms';
  });

  function show(el) {
    el.classList.add('is-visible');
    el.style.transitionDelay = el.style.transitionDelay || '';
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      show(entry.target);
      io.unobserve(entry.target);   // one-shot: never re-hide read content
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });

  boxes.forEach(function (el) { io.observe(el); });

  // Backup for the same job, in case the observer never fires (odd embedded
  // viewports, non-compositing frames). Cheap, throttled by rAF, and it stops
  // itself once everything has been shown.
  var pending = boxes.slice();
  function sweep() {
    for (var i = pending.length - 1; i >= 0; i--) {
      var r = pending[i].getBoundingClientRect();
      if (r.top < window.innerHeight * 0.95 && r.bottom > 0) {
        show(pending[i]);
        io.unobserve(pending[i]);
        pending.splice(i, 1);
      }
    }
    if (!pending.length) {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
    }
  }
  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(function () { ticking = false; sweep(); });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  window.setTimeout(sweep, 600);
})();

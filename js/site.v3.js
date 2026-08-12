/* Shared site behaviour. Loaded with `defer` on every page.
 *
 * Everything here is progressive enhancement: with JS off, or if an API is
 * missing, the page must still be fully readable and every story reachable.
 * That rule is not cosmetic — this site carries legally required disclaimer
 * text and neighbours' accounts of ICE raids, and none of it may depend on a
 * script running.
 *
 * Filename is versioned on purpose. It is the cache key: editing in place
 * leaves returning visitors on stale JS behind the CDN.
 */
(function () {
  'use strict';

  var mq = function (q) {
    return window.matchMedia ? window.matchMedia(q).matches : false;
  };
  var reduceMotion = mq('(prefers-reduced-motion: reduce)');
  var canHover = mq('(hover: hover) and (pointer: fine)');

  /* ===============================================================
   * 1. Hover-to-preview on <details class="disclosure">.
   * Click and keyboard already work natively; this only adds the
   * pointer affordance. Touch is excluded — hover on touch sticks.
   * ============================================================= */
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
        var summary = d.querySelector('summary');
        if (summary) {
          summary.addEventListener('click', function (e) {
            // d.open is still the pre-toggle value at click time.
            if (d.open && d.dataset.pinned !== 'true') {
              // Open only because the pointer is over it. The native toggle
              // would close it, which reads as "clicking dismissed what I was
              // reading" — so swallow the toggle and pin it open instead.
              e.preventDefault();
              d.dataset.pinned = 'true';
              return;
            }
            d.dataset.pinned = d.open ? 'false' : 'true';
          });
        }
      }
    );
  }

  /* ===============================================================
   * 2. Story carousel: arrows on desktop, native swipe on touch.
   *
   * The track is a plain overflow-x scroller with CSS scroll-snap, so
   * swiping and trackpad scrolling work with no JS at all. This adds
   * the arrow buttons and keeps their state in sync. With a single
   * story the arrows stay hidden — nothing to page to.
   * ============================================================= */
  Array.prototype.forEach.call(
    document.querySelectorAll('[data-carousel]'),
    function (root) {
      var track = root.querySelector('.carousel-track');
      var prev = root.querySelector('.carousel-prev');
      var next = root.querySelector('.carousel-next');
      if (!track || !prev || !next) return;

      var slides = track.querySelectorAll('.story');
      if (slides.length < 2) {
        root.classList.add('carousel-single');   // hides arrows via CSS
        return;
      }
      root.classList.add('carousel-active');

      function step() {
        var first = track.querySelector('.story');
        return first ? first.getBoundingClientRect().width + 24 : track.clientWidth;
      }
      function go(dir) {
        track.scrollBy({
          left: dir * step(),
          behavior: reduceMotion ? 'auto' : 'smooth'
        });
      }
      prev.addEventListener('click', function () { go(-1); });
      next.addEventListener('click', function () { go(1); });

      function sync() {
        // Tolerance is deliberately loose: snap points and the inter-slide gap
        // leave scrollLeft a few px short of the true max on the last slide,
        // which at a tight threshold leaves "next" looking clickable at the end.
        var max = track.scrollWidth - track.clientWidth;
        prev.disabled = track.scrollLeft <= 8;
        next.disabled = track.scrollLeft >= max - 8;
      }
      var ticking = false;
      track.addEventListener('scroll', function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(function () { ticking = false; sync(); });
      }, { passive: true });
      window.addEventListener('resize', sync, { passive: true });
      sync();
    }
  );

  /* ===============================================================
   * 3. Reveal statement boxes as they scroll into view.
   *
   * The hidden start state lives behind .js-reveal on <html>, added only
   * below. No JS, no IntersectionObserver, a reduced-motion preference, or
   * a viewport too small to reason about => never added, everything visible.
   * ============================================================= */
  if (reduceMotion || !('IntersectionObserver' in window)) return;

  // Guard against degenerate viewports (embedded frames that report 0px).
  // Below-the-fold maths is meaningless there and would hide everything.
  var vh = window.innerHeight || 0;
  if (vh < 240) return;

  var SELECTOR = [
    '.priorities > li',   // direct children only — a nested sub-list must not
    '.story',             // animate inside an already-animating parent
    '.vote-card',
    '.candidate-card'
  ].join(', ');

  var boxes = Array.prototype.slice.call(document.querySelectorAll(SELECTOR));
  if (!boxes.length) return;

  document.documentElement.classList.add('js-reveal');

  var seen = [];
  boxes.forEach(function (el) {
    el.classList.add('reveal');
    var parent = el.parentNode;
    if (seen.indexOf(parent) === -1) { seen.push(parent); parent._revealCount = 0; }
    var n = parent._revealCount++;
    if (n < 8) el.style.transitionDelay = (n * 90) + 'ms';
  });

  function show(el) { el.classList.add('is-visible'); }

  // Reveal whatever is already on screen right now, in this same tick — no
  // paint happens in between, so there is no flash and nothing above the fold
  // is ever left hidden. Position is NOT measured once and trusted: `defer`
  // runs before images load, so a headshot resolving later shifts everything
  // down. That shift previously made every bullet look above-the-fold and
  // silently disabled the whole effect. Hence the load/scroll sweeps below.
  function sweepNow() {
    for (var i = boxes.length - 1; i >= 0; i--) {
      var r = boxes[i].getBoundingClientRect();
      // No `r.bottom > 0` test: an element already scrolled PAST is above the
      // viewport and must count as seen. Requiring it to still be on screen
      // left anything skipped by an anchor jump or a fast scroll stuck hidden.
      if (r.top < (window.innerHeight || vh) * 0.95) show(boxes[i]);
    }
  }
  sweepNow();

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      show(entry.target);
      io.unobserve(entry.target);   // one-shot: never re-hide read content
    });
  }, { rootMargin: '0px 0px -10% 0px', threshold: 0.05 });

  boxes.forEach(function (el) { io.observe(el); });

  // Backup for the same job, in case the observer never fires (odd embedded
  // viewports, non-compositing frames). Throttled, and it removes itself.
  var pending = boxes.filter(function (el) {
    return !el.classList.contains('is-visible');
  });
  function sweep() {
    for (var i = pending.length - 1; i >= 0; i--) {
      var r = pending[i].getBoundingClientRect();
      if (r.top < window.innerHeight * 0.95) {
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
  var sTick = false;
  function onScroll() {
    if (sTick) return;
    sTick = true;
    window.requestAnimationFrame(function () { sTick = false; sweep(); });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  // Images finishing late move everything down; re-check once they have.
  window.addEventListener('load', sweep);
  window.setTimeout(sweep, 600);
})();

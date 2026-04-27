/* ════════════════════════════════════════════════════════════
   SMART HOME — minimal vanilla JS
   ════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  // ── Year in footer ───────────────────────────────────────────
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // ── Mobile nav toggle ────────────────────────────────────────
  const toggle = document.querySelector('.nav-toggle');
  const navList = document.getElementById('nav-list');
  if (toggle && navList) {
    toggle.addEventListener('click', () => {
      const expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!expanded));
      navList.classList.toggle('is-open');
    });
    // close on link click (mobile)
    navList.querySelectorAll('a').forEach((a) => {
      a.addEventListener('click', () => {
        toggle.setAttribute('aria-expanded', 'false');
        navList.classList.remove('is-open');
      });
    });
  }

  // ── Sticky header background on scroll ───────────────────────
  const header = document.getElementById('site-header');
  if (header) {
    const onScroll = () => {
      header.classList.toggle('is-scrolled', window.scrollY > 16);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // ── Active section highlighting in nav ───────────────────────
  const sections = document.querySelectorAll('main section[id]');
  const navLinks = document.querySelectorAll('.nav-list a');
  if (sections.length && navLinks.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.id;
            navLinks.forEach((link) => {
              link.classList.toggle('is-active', link.getAttribute('href') === '#' + id);
            });
          }
        });
      },
      { rootMargin: '-40% 0px -55% 0px' }
    );
    sections.forEach((s) => observer.observe(s));
  }

  // ── Animated counter for hero stats ──────────────────────────
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length && 'IntersectionObserver' in window) {
    const animateCount = (el, target) => {
      const duration = 1500;
      const start = performance.now();
      const tick = (now) => {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(target * eased).toString();
        if (progress < 1) requestAnimationFrame(tick);
        else el.textContent = target.toString();
      };
      requestAnimationFrame(tick);
    };
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const target = parseInt(entry.target.dataset.count, 10);
            if (!isNaN(target)) animateCount(entry.target, target);
            obs.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );
    counters.forEach((c) => obs.observe(c));
  }
})();

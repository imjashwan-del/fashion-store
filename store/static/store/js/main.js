document.addEventListener('DOMContentLoaded', function () {
  // --- Sticky header shrink on scroll ---
  var header = document.getElementById('siteHeader');
  if (header) {
    var onScroll = function () {
      if (window.scrollY > 20) header.classList.add('is-scrolled');
      else header.classList.remove('is-scrolled');
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // --- Mobile nav toggle ---
  var navToggle = document.getElementById('navToggle');
  var mainNav = document.getElementById('mainNav');
  var navScrim = document.getElementById('navScrim');
  function closeNav() {
    if (mainNav) mainNav.classList.remove('is-open');
    if (navScrim) navScrim.classList.remove('is-open');
  }
  if (navToggle && mainNav) {
    navToggle.addEventListener('click', function () {
      mainNav.classList.toggle('is-open');
      if (navScrim) navScrim.classList.toggle('is-open');
    });
  }
  if (navScrim) navScrim.addEventListener('click', closeNav);
  if (mainNav) {
    mainNav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', closeNav);
    });
  }

  // --- Fade-in-up on scroll ---
  var fadeEls = document.querySelectorAll('.fade-in-up');
  if ('IntersectionObserver' in window && fadeEls.length) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    fadeEls.forEach(function (el) { observer.observe(el); });
  } else {
    fadeEls.forEach(function (el) { el.classList.add('is-visible'); });
  }

  // --- Quantity steppers (product detail + cart) ---
  document.querySelectorAll('.qty-stepper').forEach(function (stepper) {
    var input = stepper.querySelector('input[type="number"]');
    var max = parseInt(input.getAttribute('max') || '999', 10);
    stepper.querySelectorAll('button').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var val = parseInt(input.value || '1', 10);
        if (btn.dataset.action === 'increase') val = Math.min(max, val + 1);
        if (btn.dataset.action === 'decrease') val = Math.max(1, val - 1);
        input.value = val;
        input.dispatchEvent(new Event('change'));
      });
    });
  });

  // --- Auto-dismiss site messages ---
  document.querySelectorAll('.site-message').forEach(function (msg) {
    setTimeout(function () {
      msg.style.transition = 'opacity 500ms ease';
      msg.style.opacity = '0';
      setTimeout(function () { msg.remove(); }, 500);
    }, 5000);
  });
});

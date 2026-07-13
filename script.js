/* BAYT — scroll choreography (GSAP + ScrollTrigger) */
(function () {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduced || typeof gsap === 'undefined') return; // static fallback stays readable

  document.body.classList.add('js');
  gsap.registerPlugin(ScrollTrigger);

  /* ── progress bar ── */
  gsap.to('#progress-bar', {
    scaleX: 1,
    ease: 'none',
    scrollTrigger: { start: 0, end: 'max', scrub: 0.3 }
  });

  /* ── hero: wordmark shrinks & drifts up as you leave ── */
  gsap.to('#hero-wordmark', {
    scale: 0.55,
    yPercent: -18,
    opacity: 0.08,
    transformOrigin: '50% 100%',
    ease: 'none',
    scrollTrigger: { trigger: '#hero', start: 'top top', end: 'bottom top', scrub: true }
  });
  gsap.to('.hero-tag, .hero-kicker, .hero-scroll-hint', {
    opacity: 0,
    y: -30,
    ease: 'none',
    scrollTrigger: { trigger: '#hero', start: 'top top', end: '45% top', scrub: true }
  });

  /* ── statement: word-by-word ink-in, scrubbed ── */
  document.querySelectorAll('[data-split]').forEach((el) => {
    el.innerHTML = el.textContent.trim().split(/\s+/)
      .map((w) => `<span class="w">${w}</span>`).join(' ');
    gsap.to(el.querySelectorAll('.w'), {
      opacity: 1,
      stagger: 0.06,
      ease: 'none',
      scrollTrigger: { trigger: el, start: 'top 75%', end: 'bottom 45%', scrub: true }
    });
  });

  /* ── system: pinned, pillars swap on scrub ── */
  const pillars = gsap.utils.toArray('.pillar');
  const sysTl = gsap.timeline({
    scrollTrigger: {
      trigger: '#system',
      start: 'top top',
      end: '+=' + pillars.length * 90 + '%',
      pin: '.system-pin',
      scrub: 0.5
    }
  });

  /* the axo visual transforms through the three pillars on the same timeline:
     1 scattered fragments converge while the house draws itself (Optimize)
     2 the same house stamps out into copies (Productize)
     3 the house explodes into labelled parts (Localize) */
  if (document.getElementById('system-axo')) {
    gsap.set('#system-axo .hp', { strokeDasharray: 1, strokeDashoffset: 1 });

    // 1 — converge & draw
    sysTl.to('#system-axo .frag', {
      scale: 0.04, opacity: 0, svgOrigin: '200 210',
      stagger: 0.015, duration: 0.45, ease: 'power2.in'
    }, 0);
    sysTl.to('#system-axo .hp', {
      strokeDashoffset: 0, stagger: 0.03, duration: 0.5, ease: 'power1.inOut'
    }, 0.05);
    sysTl.to('#system-axo .hp-hidden', { opacity: 0.45, duration: 0.2 }, 0.65);

    // 2 — stamp copies
    sysTl.fromTo('#system-axo .axo-copy',
      { opacity: 0, y: 26 },
      { opacity: 0.55, y: 0, stagger: 0.12, duration: 0.4, ease: 'power2.out' }, 1.05);
    sysTl.to('#system-axo .axo-copy', { opacity: 0, duration: 0.25 }, 1.75);

    // 3 — explode into parts + labels
    const partMoves = [
      ['.axo-roof',       { x: 0,   y: -48 }],
      ['.axo-wall-left',  { x: -32, y: 16 }],
      ['.axo-wall-right', { x: 32,  y: 16 }],
      ['.axo-base',       { x: 0,   y: 20 }]
    ];
    partMoves.forEach(([sel, move]) => {
      sysTl.to('#system-axo ' + sel, {
        ...move, duration: 0.5, ease: 'power2.inOut'
      }, 2.05);
    });
    sysTl.to('#system-axo .axo-roof path', { stroke: '#b4552d', duration: 0.4 }, 2.05);
    sysTl.to('#system-axo .axo-label', { opacity: 1, stagger: 0.08, duration: 0.3 }, 2.4);
  }
  pillars.forEach((p, i) => {
    sysTl.set(p, { visibility: 'visible' }, i);
    sysTl.fromTo(p,
      { yPercent: i === 0 ? 0 : 12, opacity: i === 0 ? 1 : 0 },
      { yPercent: 0, opacity: 1, duration: 0.35, ease: 'power2.out' }, i);
    sysTl.fromTo(p.querySelector('h2'),
      { letterSpacing: '0.05em' },
      { letterSpacing: '-0.03em', duration: 0.5, ease: 'power2.out' }, i);
    if (i < pillars.length - 1) {
      sysTl.to(p, { yPercent: -10, opacity: 0, duration: 0.3, ease: 'power2.in' }, i + 0.7);
      sysTl.set(p, { visibility: 'hidden' }, i + 1);
    }
  });

  /* ── timeline: bars grow, labels fade in ── */
  gsap.utils.toArray('.tl-row').forEach((row) => {
    const oldBar = row.querySelector('.tl-old i');
    const newBar = row.querySelector('.tl-new i');
    oldBar.style.setProperty('--v', row.dataset.old);
    oldBar.parentElement.style.setProperty('--v', row.dataset.old);
    newBar.parentElement.style.setProperty('--v', row.dataset.new);
    gsap.timeline({
      scrollTrigger: { trigger: row, start: 'top 80%', end: 'top 45%', scrub: true }
    })
      .to(row.querySelector('.tl-old i'), { scaleX: 1, ease: 'none' }, 0)
      .to(row.querySelector('.tl-old b'), { opacity: 1 }, 0.35)
      .to(row.querySelector('.tl-new i'), { scaleX: 1, ease: 'none' }, 0.15)
      .to(row.querySelector('.tl-new b'), { opacity: 1 }, 0.5);
  });

  /* ── counters ── */
  gsap.utils.toArray('.count').forEach((el) => {
    const target = +el.dataset.count;
    const obj = { v: 0 };
    gsap.to(obj, {
      v: target,
      duration: 1.4,
      ease: 'power3.out',
      snap: { v: 1 },
      onUpdate: () => { el.textContent = obj.v; },
      scrollTrigger: { trigger: el, start: 'top 85%' }
    });
  });

  /* ── houses: pinned horizontal scroll ── */
  const track = document.querySelector('.houses-track');
  const housesST = () => -(track.scrollWidth - window.innerWidth + 2 * 16);
  gsap.to(track, {
    x: housesST,
    ease: 'none',
    scrollTrigger: {
      trigger: '#houses',
      start: 'top top',
      end: () => '+=' + (track.scrollWidth - window.innerWidth + 400),
      pin: '.houses-pin',
      scrub: 0.5,
      invalidateOnRefresh: true
    }
  });
  gsap.utils.toArray('.house').forEach((card) => {
    gsap.from(card, {
      y: 60,
      opacity: 0,
      duration: 0.7,
      ease: 'power2.out',
      scrollTrigger: { trigger: '#houses', start: 'top 70%' }
    });
  });

  /* ── generic reveals ── */
  gsap.utils.toArray('.reveal').forEach((el) => {
    gsap.from(el, {
      y: 44,
      opacity: 0,
      duration: 0.9,
      ease: 'power3.out',
      scrollTrigger: { trigger: el, start: 'top 85%' }
    });
  });

  /* ── footer lines rise in ── */
  gsap.from('.cta-big span', {
    yPercent: 110,
    opacity: 0,
    stagger: 0.12,
    duration: 0.9,
    ease: 'power3.out',
    scrollTrigger: { trigger: '#cta', start: 'top 70%' }
  });

  /* fonts/images settle → recalc pin distances */
  window.addEventListener('load', () => ScrollTrigger.refresh());
})();

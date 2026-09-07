/* ==========================================================================
   Andamana — site behaviour
   Vanilla JS, no dependencies. Every module is opt-in: it only runs when the
   markup it needs is present, so one bundle serves every page.
   ========================================================================== */
(function () {
  "use strict";

  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) {
    return Array.prototype.slice.call((ctx || document).querySelectorAll(sel));
  };
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var TOURS = window.ANDAMANA_TOURS || [];
  var DEPARTURES = window.ANDAMANA_DEPARTURES || [];

  var baht = function (n) { return n.toLocaleString("en-US") + " ฿"; };
  var esc = function (s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };
  var bySlug = function (slug) {
    for (var i = 0; i < TOURS.length; i++) if (TOURS[i].slug === slug) return TOURS[i];
    return null;
  };

  /* ---------------------------------------------------------------- cursor */
  function spotlight() {
    if (reduced || !window.matchMedia("(pointer: fine)").matches) return;
    var el = document.createElement("div");
    el.className = "spot";
    document.body.appendChild(el);
    var x = 0, y = 0, cx = 0, cy = 0, raf = null;

    document.addEventListener("pointermove", function (e) {
      x = e.clientX; y = e.clientY;
      el.classList.add("on");
      if (!raf) raf = requestAnimationFrame(loop);
    });
    document.addEventListener("pointerleave", function () { el.classList.remove("on"); });

    function loop() {
      cx += (x - cx) * 0.09;
      cy += (y - cy) * 0.09;
      el.style.transform = "translate3d(" + cx.toFixed(1) + "px," + cy.toFixed(1) + "px,0)";
      raf = Math.abs(x - cx) > 0.4 || Math.abs(y - cy) > 0.4 ? requestAnimationFrame(loop) : null;
    }
  }

  /* ------------------------------------------------------------------- nav */
  function nav() {
    var bar = $(".nav");
    if (!bar) return;
    var last = window.scrollY;

    var onScroll = function () {
      var y = window.scrollY;
      bar.classList.toggle("is-solid", y > 40);
      // hide while scrolling down past the fold, reveal on the way back up
      bar.classList.toggle("is-hidden", y > 460 && y > last && !$(".mega.open"));
      last = y;
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    /* mega menu ---------------------------------------------------------- */
    var trigger = $("[data-mega-trigger]");
    var mega = $("[data-mega]");
    if (trigger && mega) {
      var open = function (state) {
        mega.classList.toggle("open", state);
        trigger.setAttribute("aria-expanded", state ? "true" : "false");
      };
      // Hover opens it for mice, click/Enter toggles it for everyone else. A
      // click that closes the panel is suppressed from re-opening on hover
      // until the pointer actually leaves the header.
      var hoverBlocked = false;
      trigger.addEventListener("click", function (e) {
        e.preventDefault();
        var isOpen = mega.classList.contains("open");
        open(!isOpen);
        hoverBlocked = isOpen;
      });
      var host = $(".nav");
      host.addEventListener("pointerenter", function (e) {
        if (hoverBlocked || e.pointerType !== "mouse") return;
        if (e.target.closest && e.target.closest("[data-mega-trigger]")) open(true);
      }, true);
      var leave = function () { open(false); hoverBlocked = false; };
      host.addEventListener("pointerleave", leave);
      mega.addEventListener("pointerleave", leave);
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && mega.classList.contains("open")) { open(false); trigger.focus(); }
      });
      document.addEventListener("focusin", function (e) {
        if (!mega.contains(e.target) && e.target !== trigger) open(false);
      });

      // departure list is data-driven so the menu and catalogue never drift
      var cols = $("[data-departures]", mega);
      if (cols) {
        cols.innerHTML = DEPARTURES.map(function (d) {
          return '<a class="mega__item" href="tours.html?from=' + encodeURIComponent(d.name) + '">' +
            esc(d.name) + "<span>" + d.count + "</span></a>";
        }).join("");
      }
    }

    /* mobile drawer ------------------------------------------------------ */
    var burger = $("[data-burger]");
    var drawer = $("[data-drawer]");
    if (burger && drawer) {
      burger.addEventListener("click", function () {
        var state = !drawer.classList.contains("open");
        drawer.classList.toggle("open", state);
        document.body.classList.toggle("is-locked", state);
        burger.setAttribute("aria-expanded", state ? "true" : "false");
      });
      $$("a", drawer).forEach(function (a) {
        a.addEventListener("click", function () {
          drawer.classList.remove("open");
          document.body.classList.remove("is-locked");
          burger.setAttribute("aria-expanded", "false");
        });
      });
    }
  }

  /* ---------------------------------------------------------------- search */
  function search() {
    var panel = $("[data-search]");
    if (!panel) return;
    var input = $("input", panel);
    var out = $("[data-search-results]", panel);
    var chips = $$("[data-search-tag]", panel);
    var tag = "";

    var render = function () {
      var q = input.value.trim().toLowerCase();
      var hits = TOURS.filter(function (t) {
        var okTag = !tag || t.tags.indexOf(tag) > -1;
        var hay = (t.title + " " + t.lead + " " + t.departs + " " + t.tags.join(" ")).toLowerCase();
        return okTag && (!q || hay.indexOf(q) > -1);
      });
      if (!hits.length) {
        out.innerHTML = '<p class="search__empty">Nothing matches that yet. Try “kayak”, “dive”, “sunset” or a departure point.</p>';
        return;
      }
      out.innerHTML = hits.slice(0, 8).map(function (t) {
        return '<a class="search__row" href="tour.html?slug=' + t.slug + '">' +
          '<img src="' + t.img + '" alt="" loading="lazy">' +
          '<span><b class="h-card">' + esc(t.title) + '</b>' +
          '<span class="meta" style="display:block;margin-top:6px">' + esc(t.departs) + " &middot; " + esc(t.duration) + "</span></span>" +
          '<span class="price">' + baht(t.price) + "</span></a>";
      }).join("");
    };

    var toggle = function (state) {
      panel.classList.toggle("open", state);
      document.body.classList.toggle("is-locked", state);
      $$("[data-search-open]").forEach(function (b) {
        b.setAttribute("aria-expanded", state ? "true" : "false");
      });
      if (state) { render(); setTimeout(function () { input.focus(); }, 120); }
    };

    $$("[data-search-open]").forEach(function (b) {
      b.addEventListener("click", function () { toggle(!panel.classList.contains("open")); });
    });
    $$("[data-search-close]", panel).forEach(function (b) {
      b.addEventListener("click", function () { toggle(false); });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && panel.classList.contains("open")) toggle(false);
      if (e.key === "/" && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) {
        e.preventDefault(); toggle(true);
      }
    });
    input.addEventListener("input", render);
    chips.forEach(function (c) {
      c.addEventListener("click", function () {
        var t = c.getAttribute("data-search-tag");
        tag = tag === t ? "" : t;
        chips.forEach(function (o) {
          o.setAttribute("aria-pressed", o.getAttribute("data-search-tag") === tag ? "true" : "false");
        });
        render();
      });
    });
  }

  /* --------------------------------------------------------------- reveals */
  function reveals() {
    var items = $$("[data-reveal]");
    if (!items.length) return;
    if (reduced || !("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("in"); });
      return;
    }
    // stagger siblings inside any container marked data-stagger
    $$("[data-stagger]").forEach(function (group) {
      $$("[data-reveal]", group).forEach(function (el, i) {
        el.style.setProperty("--d", Math.min(i, 8) * 85 + "ms");
      });
    });
    // A clip-path on the target itself zeroes its own intersection rect, so
    // masked elements are watched through their parent instead.
    var watched = new WeakMap();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        (watched.get(en.target) || [en.target]).forEach(function (el) {
          el.classList.add("in");
        });
        io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });

    items.forEach(function (el) {
      var probe = el.getAttribute("data-reveal") === "mask" ? (el.parentElement || el) : el;
      var group = watched.get(probe) || [];
      group.push(el);
      watched.set(probe, group);
      io.observe(probe);
    });
  }

  /* -------------------------------------------------------------- parallax */
  function parallax() {
    var items = $$("[data-parallax]");
    if (!items.length || reduced) return;
    var raf = null;

    var frame = function () {
      var vh = window.innerHeight;
      items.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) return;
        var speed = parseFloat(el.getAttribute("data-parallax")) || 0.12;
        var mid = r.top + r.height / 2 - vh / 2;
        el.style.transform = "translate3d(0," + (-mid * speed).toFixed(1) + "px,0)";
      });
      raf = null;
    };
    var request = function () { if (!raf) raf = requestAnimationFrame(frame); };
    frame();
    window.addEventListener("scroll", request, { passive: true });
    window.addEventListener("resize", request);
  }

  /* ------------------------------------------------------------------ hero */
  function hero() {
    var stage = $("[data-hero]");
    if (!stage) return;
    var slides = $$(".hero__slide", stage);
    var words = $$("[data-hero-word] b");
    var kicker = $("[data-hero-kicker]");
    var title = $("[data-hero-title]");
    var copy = $("[data-hero-copy]");
    var dots = $$("[data-hero-dot]");
    if (slides.length < 2) return;
    var i = 0, timer = null;

    var show = function (n) {
      i = (n + slides.length) % slides.length;
      var s = slides[i];
      slides.forEach(function (el, k) { el.classList.toggle("on", k === i); });
      dots.forEach(function (d, k) { d.setAttribute("aria-current", k === i ? "true" : "false"); });
      var img = $("img", s).getAttribute("src");
      words.forEach(function (w) {
        w.textContent = s.getAttribute("data-word");
        w.style.backgroundImage = 'url("' + img + '")';
      });
      if (kicker) kicker.textContent = s.getAttribute("data-kicker");
      if (title) title.textContent = s.getAttribute("data-title");
      if (copy) copy.textContent = s.getAttribute("data-copy");
    };

    var play = function () {
      if (reduced) return;
      clearInterval(timer);
      timer = setInterval(function () { show(i + 1); }, 7200);
    };
    dots.forEach(function (d, k) {
      d.addEventListener("click", function () { show(k); play(); });
    });
    show(0);
    play();
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) clearInterval(timer); else play();
    });
  }

  /* -------------------------------------------------------------- counters */
  function counters() {
    var items = $$("[data-count]");
    if (!items.length) return;
    var run = function (el) {
      var to = parseFloat(el.getAttribute("data-count"));
      var suffix = el.getAttribute("data-suffix") || "";
      if (reduced) { el.textContent = to + suffix; return; }
      var t0 = performance.now(), dur = 1400;
      var step = function (now) {
        var p = Math.min(1, (now - t0) / dur);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(to * eased).toLocaleString("en-US") + suffix;
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    if (!("IntersectionObserver" in window)) { items.forEach(run); return; }
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (e) { if (e.isIntersecting) { run(e.target); io.unobserve(e.target); } });
    }, { threshold: 0.4 });
    items.forEach(function (el) { io.observe(el); });
  }

  /* --------------------------------------------------------------- marquee */
  function marquee() {
    $$("[data-marquee]").forEach(function (m) {
      var track = $(".marquee__track", m);
      if (!track) return;
      var clone = track.cloneNode(true);
      clone.setAttribute("aria-hidden", "true");
      m.appendChild(clone);
    });
  }

  /* ----------------------------------------------------------- tour grids */
  function cardHTML(t, i) {
    return '' +
      '<article class="card" data-tags="' + t.tags.join(" ") + '" data-from="' + esc(t.departs) + '"' +
      ' data-price="' + t.price + '" data-reveal>' +
      '<div class="card__media">' +
      '<img src="' + t.img + '" alt="' + esc(t.lead) + '" loading="' + (i < 4 ? "eager" : "lazy") + '" decoding="async">' +
      '<span class="card__tag">' + esc(t.badge) + "</span>" +
      '<span class="card__cta"><span>See details</span><i></i>' +
      '<svg width="14" height="10" viewBox="0 0 14 10" fill="none" aria-hidden="true">' +
      '<path d="M1 5h11M8.5 1.5 12 5l-3.5 3.5" stroke="currentColor" stroke-width="1.4"/></svg></span>' +
      "</div>" +
      '<div class="card__body">' +
      '<h3 class="h-card card__title"><a href="tour.html?slug=' + t.slug + '">' + esc(t.title) + "</a></h3>" +
      '<p class="meta card__meta">' + esc(t.duration) + " &middot; " + esc(t.departs) + "</p>" +
      '<div class="card__foot"><span class="price">' + baht(t.price) +
      "<small>from</small></span></div>" +
      "</div>" +
      '<a class="card__link" href="tour.html?slug=' + t.slug + '" tabindex="-1" aria-hidden="true"></a>' +
      "</article>";
  }

  function grids() {
    $$("[data-grid]").forEach(function (grid) {
      var limit = parseInt(grid.getAttribute("data-limit"), 10) || 0;
      var only = grid.getAttribute("data-tag");
      var skip = grid.getAttribute("data-exclude");
      var list = TOURS.filter(function (t) {
        return (!only || t.tags.indexOf(only) > -1) && t.slug !== skip;
      });
      if (limit) list = list.slice(0, limit);
      grid.innerHTML = list.map(cardHTML).join("");
    });
  }

  /* -------------------------------------------------------------- filters */
  function filters() {
    var bar = $("[data-filters]");
    var grid = $("[data-grid]");
    if (!bar || !grid) return;
    var count = $("[data-filter-count]");
    var params = new URLSearchParams(location.search);

    var apply = function (key, from) {
      var shown = 0;
      $$(".card", grid).forEach(function (card) {
        var okTag = key === "all" || card.getAttribute("data-tags").split(" ").indexOf(key) > -1;
        var okFrom = !from || card.getAttribute("data-from") === from;
        var out = !(okTag && okFrom);
        card.classList.toggle("is-out", out);
        if (!out) shown++;
      });
      if (count) count.textContent = shown;
      var empty = $("[data-filter-empty]");
      if (empty) empty.hidden = shown > 0;
    };

    var from = params.get("from") || "";
    var initial = params.get("tag") || "all";

    $$("[data-filter]", bar).forEach(function (btn) {
      if (btn.getAttribute("data-filter") === initial) btn.setAttribute("aria-pressed", "true");
      btn.addEventListener("click", function () {
        $$("[data-filter]", bar).forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
        btn.setAttribute("aria-pressed", "true");
        from = "";
        var note = $("[data-from-note]");
        if (note) note.hidden = true;
        apply(btn.getAttribute("data-filter"), "");
      });
    });

    var note = $("[data-from-note]");
    if (from && note) {
      note.hidden = false;
      $("[data-from-name]", note).textContent = from;
    }
    apply(initial, from);
  }

  /* ---------------------------------------------------------------- quotes */
  function quotes() {
    var wrap = $("[data-quotes]");
    if (!wrap) return;
    var items = $$(".quote", wrap);
    var dots = $$("[data-quote-dot]", wrap);
    var i = 0;
    var show = function (n) {
      i = (n + items.length) % items.length;
      items.forEach(function (q, k) { q.classList.toggle("on", k === i); });
      dots.forEach(function (d, k) { d.setAttribute("aria-current", k === i ? "true" : "false"); });
    };
    dots.forEach(function (d, k) { d.addEventListener("click", function () { show(k); }); });
    $$("[data-quote-next]", wrap).forEach(function (b) {
      b.addEventListener("click", function () { show(i + 1); });
    });
    $$("[data-quote-prev]", wrap).forEach(function (b) {
      b.addEventListener("click", function () { show(i - 1); });
    });
    show(0);
  }

  /* ----------------------------------------------------------- detail page */
  function detail() {
    var root = $("[data-detail]");
    if (!root) return;
    var slug = new URLSearchParams(location.search).get("slug");
    var t = bySlug(slug) || TOURS[1];

    document.title = t.title + " — Andamana island tours";
    var desc = $('meta[name="description"]');
    if (desc) desc.setAttribute("content", t.summary.slice(0, 155));

    var set = function (sel, value, attr) {
      $$(sel).forEach(function (el) {
        if (attr) el.setAttribute(attr, value); else el.textContent = value;
      });
    };
    set("[data-d-title]", t.title);
    set("[data-d-lead]", t.lead);
    set("[data-d-summary]", t.summary);
    set("[data-d-badge]", t.badge);
    set("[data-d-duration]", t.duration);
    set("[data-d-group]", t.group);
    set("[data-d-departs]", t.departs);
    set("[data-d-price]", baht(t.price));
    set("[data-d-crumb]", t.title);
    var wide = t.gallery.filter(function (g) { return g.indexOf("banner-") > -1; })[0];
    set("[data-d-hero]", wide || t.gallery[0] || t.img, "src");
    set("[data-d-hero]", t.lead, "alt");

    var hl = $("[data-d-highlights]");
    if (hl) {
      hl.innerHTML = t.highlights.map(function (h) {
        return "<li>" + tick() + "<span>" + esc(h) + "</span></li>";
      }).join("");
    }
    var steps = $("[data-d-itinerary]");
    if (steps) {
      steps.innerHTML = t.itinerary.map(function (s) {
        return '<div class="step"><div class="step__t">' + esc(s.t) + "</div>" +
          '<div class="step__c"><h4 class="h-card">' + esc(s.h) + "</h4>" +
          "<p>" + esc(s.c) + "</p></div></div>";
      }).join("");
    }
    var inc = $("[data-d-includes]");
    if (inc) inc.innerHTML = t.includes.map(function (x) {
      return "<li>" + tick() + "<span>" + esc(x) + "</span></li>";
    }).join("");
    var exc = $("[data-d-excludes]");
    if (exc) exc.innerHTML = t.excludes.map(function (x) {
      return "<li>" + cross() + "<span>" + esc(x) + "</span></li>";
    }).join("");

    var gal = $("[data-d-gallery]");
    if (gal) {
      gal.innerHTML = t.gallery.map(function (src, i) {
        return '<button type="button" data-lightbox="' + src + '" aria-label="View photo ' + (i + 1) + '">' +
          '<img src="' + src + '" alt="" loading="lazy"></button>';
      }).join("");
    }

    // related tours: same departure point first, then anything else
    var rel = $("[data-d-related]");
    if (rel) {
      var pool = TOURS.filter(function (o) { return o.slug !== t.slug; });
      pool.sort(function (a, b) {
        var sa = (a.departs === t.departs ? 0 : 1) + (a.tags[0] === t.tags[0] ? 0 : 0.5);
        var sb = (b.departs === t.departs ? 0 : 1) + (b.tags[0] === t.tags[0] ? 0 : 0.5);
        return sa - sb;
      });
      rel.innerHTML = pool.slice(0, 4).map(cardHTML).join("");
    }

    // live booking total
    var qty = $("[data-d-qty]");
    var total = $("[data-d-total]");
    if (qty && total) {
      var recalc = function () {
        var n = Math.max(1, Math.min(20, parseInt(qty.value, 10) || 1));
        total.textContent = baht(t.price * n);
      };
      qty.addEventListener("input", recalc);
      recalc();
    }
    reveals();
  }

  function tick() {
    return '<svg width="14" height="11" viewBox="0 0 14 11" fill="none" aria-hidden="true">' +
      '<path d="M1 5.5 5 9.5 13 1.5" stroke="currentColor" stroke-width="1.6"/></svg>';
  }
  function cross() {
    return '<svg width="11" height="11" viewBox="0 0 11 11" fill="none" aria-hidden="true" style="color:#7d8f90">' +
      '<path d="M1 1l9 9M10 1l-9 9" stroke="currentColor" stroke-width="1.5"/></svg>';
  }

  /* ------------------------------------------------------------- lightbox */
  function lightbox() {
    var box = $("[data-lightbox-root]");
    if (!box) return;
    var img = $("img", box);
    var list = [], at = 0;

    var open = function (src) {
      list = $$("[data-lightbox]").map(function (b) { return b.getAttribute("data-lightbox"); });
      at = Math.max(0, list.indexOf(src));
      img.src = src;
      box.classList.add("open");
      document.body.classList.add("is-locked");
      $("[data-lightbox-close]", box).focus();
    };
    var close = function () {
      box.classList.remove("open");
      document.body.classList.remove("is-locked");
    };
    var step = function (d) {
      at = (at + d + list.length) % list.length;
      img.src = list[at];
    };

    document.addEventListener("click", function (e) {
      var btn = e.target.closest ? e.target.closest("[data-lightbox]") : null;
      if (btn) { e.preventDefault(); open(btn.getAttribute("data-lightbox")); }
    });
    $$("[data-lightbox-close]", box).forEach(function (b) { b.addEventListener("click", close); });
    $$("[data-lightbox-next]", box).forEach(function (b) { b.addEventListener("click", function () { step(1); }); });
    $$("[data-lightbox-prev]", box).forEach(function (b) { b.addEventListener("click", function () { step(-1); }); });
    box.addEventListener("click", function (e) { if (e.target === box) close(); });
    document.addEventListener("keydown", function (e) {
      if (!box.classList.contains("open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowRight") step(1);
      if (e.key === "ArrowLeft") step(-1);
    });
  }

  /* ----------------------------------------------------------------- forms */
  function forms() {
    $$("[data-fake-form]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var note = $("[data-form-note]", form);
        var msg = form.getAttribute("data-fake-form");
        if (note) { note.textContent = msg; note.classList.add("ok"); }
        form.reset();
      });
    });
  }

  /* ------------------------------------------------------------------ misc */
  function misc() {
    $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
    // mark the current page in the nav
    var here = location.pathname.split("/").pop() || "index.html";
    $$(".nav__link[href]").forEach(function (a) {
      if (a.getAttribute("href") === here) a.classList.add("is-active");
    });
  }

  /* ------------------------------------------------------------------ boot */
  function boot() {
    misc(); nav(); search(); grids(); filters(); hero();
    marquee(); quotes(); detail(); lightbox(); forms();
    reveals(); parallax(); counters(); spotlight();
  }

  // Exposed so a single-file build (tools/build_preview.py) can re-initialise
  // the DOM-scoped modules after swapping one view for another. The page-level
  // modules — nav, search, lightbox, forms — bind to document once and stay.
  window.ANDAMANA = {
    remount: function () {
      grids(); filters(); hero(); marquee(); quotes(); detail();
      reveals(); parallax(); counters();
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();

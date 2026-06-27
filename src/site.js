(() => {
  const nav = document.querySelector("[data-nav]");
  const toggle = document.querySelector("[data-nav-toggle]");
  const links = nav ? Array.from(nav.querySelectorAll("a")) : [];
  const sections = Array.from(document.querySelectorAll("main section[id]"));

  const closeMenu = () => {
    if (!nav || !toggle) return;
    nav.dataset.open = "false";
    toggle.setAttribute("aria-expanded", "false");
  };

  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const isOpen = nav.dataset.open === "true";
      nav.dataset.open = String(!isOpen);
      toggle.setAttribute("aria-expanded", String(!isOpen));
    });

    links.forEach((link) => {
      link.addEventListener("click", () => {
        if (window.matchMedia("(max-width: 840px)").matches) {
          closeMenu();
        }
      });
    });
  }

  document.addEventListener("click", (event) => {
    if (!nav || !toggle) return;
    if (!nav.contains(event.target) && !toggle.contains(event.target)) {
      closeMenu();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMenu();
    }
  });

  if (!("IntersectionObserver" in window) || !links.length || !sections.length) {
    return;
  }

  const linkByTarget = new Map(
    links
      .map((link) => [link.getAttribute("href") || "", link])
      .filter(([href]) => href.startsWith("#"))
  );

  const setActive = (id) => {
    links.forEach((link) => link.removeAttribute("aria-current"));
    const active = linkByTarget.get(`#${id}`);
    if (active) {
      active.setAttribute("aria-current", "page");
    }
  };

  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

      if (visible && visible.target.id) {
        setActive(visible.target.id);
      }
    },
    {
      rootMargin: "-35% 0px -50% 0px",
      threshold: [0.1, 0.3, 0.5, 0.75],
    }
  );

  sections.forEach((section) => observer.observe(section));
})();

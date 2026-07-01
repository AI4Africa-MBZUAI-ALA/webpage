(() => {
  const nav = document.querySelector("[data-nav]");
  const toggle = document.querySelector("[data-nav-toggle]");
  const links = nav ? Array.from(nav.querySelectorAll("a")) : [];
  const sections = Array.from(document.querySelectorAll("main section[id]"));
  const programToolbar = document.querySelector("[data-program-toolbar]");
  const programFilters = programToolbar
    ? Array.from(programToolbar.querySelectorAll("[data-program-filter]"))
    : [];
  const programDays = Array.from(document.querySelectorAll("[data-program-day]"));
  const programBlocks = Array.from(document.querySelectorAll("[data-program-block]"));
  const programScroll = document.querySelector(".program-scroll");

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

  if (programFilters.length && programBlocks.length) {
    let activeCategory = "all";

    const syncProgramFilters = () => {
      programBlocks.forEach((block) => {
        const category = block.dataset.programCategory || "";
        const visible = activeCategory === "all" || activeCategory === category;
        block.classList.toggle("is-hidden", !visible);
      });

      programDays.forEach((day) => {
        const visibleBlock = Array.from(day.querySelectorAll("[data-program-block]")).some(
          (block) => !block.classList.contains("is-hidden")
        );
        day.classList.toggle("is-hidden", !visibleBlock);
      });

      programFilters.forEach((button) => {
        const filter = button.dataset.programFilter || "";
        const pressed = filter === activeCategory;
        button.setAttribute("aria-pressed", String(pressed));
        button.classList.toggle("is-active", pressed);
      });
    };

    programFilters.forEach((button) => {
      button.addEventListener("click", () => {
        const filter = button.dataset.programFilter || "";
        activeCategory = filter === "all" || activeCategory === filter ? "all" : filter;
        syncProgramFilters();
      });
    });

    syncProgramFilters();
  }

  if (programScroll && programDays.length) {
    const today = new Date();
    const todayIso = new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate()
    ).toISOString().slice(0, 10);
    const currentDay =
      programDays.find((day) => day.dataset.programDate === todayIso) ||
      programDays.find((day) => {
        const dayDate = day.dataset.programDate || "";
        return dayDate > todayIso;
      }) ||
      programDays[programDays.length - 1];

    if (currentDay) {
      requestAnimationFrame(() => {
        currentDay.scrollIntoView({
          behavior: "smooth",
          block: "nearest",
          inline: "start",
        });
      });
    }
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

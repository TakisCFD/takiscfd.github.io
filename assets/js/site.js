"use strict";

// Progressive enhancements. Core content and links work without JavaScript.
(() => {
  const menu = document.getElementById("site-navigation");
  const toggle = document.getElementById("menu-toggle");
  if (menu && toggle) {
    menu.dataset.expanded = "false";
    document.documentElement.classList.add("js-ready");
    toggle.hidden = false;
    const closeMenu = () => {
      toggle.setAttribute("aria-expanded", "false");
      menu.dataset.expanded = "false";
    };
    toggle.addEventListener("click", () => {
      const expanded = toggle.getAttribute("aria-expanded") !== "true";
      toggle.setAttribute("aria-expanded", String(expanded));
      menu.dataset.expanded = String(expanded);
    });
    menu.addEventListener("keydown", event => {
      if (event.key === "Escape") { closeMenu(); toggle.focus(); }
    });
    menu.addEventListener("click", event => {
      if (event.target.closest("a")) closeMenu();
    });
  }

  const publicationControls = document.getElementById("publication-controls");
  if (publicationControls) {
    const search = document.getElementById("publication-search");
    const year = document.getElementById("publication-year");
    const type = document.getElementById("publication-type");
    const topic = document.getElementById("publication-topic");
    const count = document.getElementById("publication-count");
    const empty = document.getElementById("publication-empty");
    const publications = Array.from(document.querySelectorAll("[data-publication]"));
    const normalise = value => value.toLocaleLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    const update = () => {
      const query = normalise(search.value.trim());
      let visible = 0;
      publications.forEach(publication => {
        const match = (!query || normalise(publication.dataset.search).includes(query)) &&
          (!year.value || publication.dataset.year === year.value) &&
          (!type.value || publication.dataset.type === type.value) &&
          (!topic.value || publication.dataset.topics.split("|").includes(topic.value));
        publication.hidden = !match;
        if (match) visible += 1;
      });
      count.textContent = visible + " of " + publications.length + " records";
      empty.hidden = visible !== 0;
    };
    const initialTopic = new URLSearchParams(window.location.search).get("topic");
    if (initialTopic && Array.from(topic.options).some(option => option.value === initialTopic)) topic.value = initialTopic;
    const initialType = new URLSearchParams(window.location.search).get("type");
    if (initialType && Array.from(type.options).some(option => option.value === initialType)) type.value = initialType;
    search.addEventListener("input", update);
    year.addEventListener("change", update);
    type.addEventListener("change", update);
    topic.addEventListener("change", update);
    publicationControls.hidden = false;
    update();
  }

  const filters = document.getElementById("gallery-filters");
  if (filters) {
    const items = Array.from(document.querySelectorAll("[data-gallery-category]"));
    const buttons = Array.from(filters.querySelectorAll("button"));
    const count = document.getElementById("gallery-count");
    filters.hidden = false;
    buttons.forEach(button => button.addEventListener("click", () => {
      const category = button.dataset.galleryFilter;
      let visible = 0;
      items.forEach(item => {
        item.hidden = Boolean(category && item.dataset.galleryCategory !== category);
        if (!item.hidden) visible += 1;
      });
      buttons.forEach(item => item.setAttribute("aria-pressed", String(item === button)));
      count.textContent = visible + (visible === 1 ? " image" : " images") + " shown";
    }));
  }

  const dialog = document.getElementById("image-dialog");
  if (dialog && typeof dialog.showModal === "function") {
    const image = document.getElementById("dialog-image");
    const title = document.getElementById("dialog-title");
    const caption = document.getElementById("dialog-caption");
    const credit = document.getElementById("dialog-credit");
    const close = document.getElementById("dialog-close");
    let trigger = null;
    document.querySelectorAll("[data-gallery-open]").forEach(link => link.addEventListener("click", event => {
      event.preventDefault();
      trigger = link;
      image.src = link.href;
      image.alt = link.querySelector("img").alt;
      title.textContent = link.dataset.title;
      caption.textContent = link.dataset.caption;
      credit.textContent = link.dataset.credit;
      dialog.showModal();
      close.focus();
    }));
    close.addEventListener("click", () => dialog.close());
    dialog.addEventListener("close", () => { if (trigger) trigger.focus(); });
    dialog.addEventListener("click", event => {
      if (event.target === dialog) {
        const box = dialog.getBoundingClientRect();
        if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
      }
    });
  }
})();

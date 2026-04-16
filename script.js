/* ===== Figma animated hero ===== */
(function () {
    const bg = document.querySelector(".hero-animated-bg");
    if (!bg) return;

    // --- Floating particles (50) ---
    for (let i = 0; i < 50; i++) {
        const p = document.createElement("div");
        p.className = "hero-particle";
        const size = Math.random() * 3 + 1;
        const isGold = Math.random() > 0.5;
        const dur  = (3 + Math.random() * 4).toFixed(2);
        const del  = (Math.random() * 5).toFixed(2);
        const dx   = (Math.random() * 20 - 10).toFixed(1);
        p.style.cssText = `
            left:${(Math.random()*100).toFixed(1)}%;
            top:${(Math.random()*100).toFixed(1)}%;
            width:${size}px; height:${size}px;
            background:${isGold ? "#D4AF37" : "#FFD700"};
            box-shadow:0 0 ${(Math.random()*10+5).toFixed(0)}px ${isGold ? "#D4AF37" : "#FFD700"};
            --dur:${dur}s; --delay:-${del}s; --dx:${dx}px;
            opacity:0.3;
        `;
        bg.appendChild(p);
    }

    // --- Film-reel perforation holes (16) ---
    const reel = document.getElementById("hero-reel");
    if (reel) {
        const radius = 225, cx = 250, cy = 250;
        for (let i = 0; i < 16; i++) {
            const angle = (i / 16) * Math.PI * 2;
            const x = Math.cos(angle) * radius + cx;
            const y = Math.sin(angle) * radius + cy;
            const hole = document.createElement("div");
            hole.className = "hero-film-reel-hole";
            hole.style.left  = x + "px";
            hole.style.top   = y + "px";
            reel.appendChild(hole);
        }
    }
})();

/* ===== Director Card Glow Injection ===== */
(function () {
    const directorColors = ["#4fc3f7", "#ef5350", "#ffb74d", "#fdd835"];
    document.querySelectorAll(".director-card").forEach(function (card, i) {
        const color = directorColors[i] || "#D4AF37";
        const glow = document.createElement("div");
        glow.className = "director-glow";
        glow.style.background = `radial-gradient(ellipse at 50% 0%, ${color}55 0%, transparent 70%)`;
        card.insertBefore(glow, card.firstChild);
    });
})();

/* ===== Genre Card Glow Injection ===== */
(function () {
    const glowColors = {
        "genre-card-red":    "rgba(239,68,68,0.18)",
        "genre-card-pink":   "rgba(236,72,153,0.18)",
        "genre-card-green":  "rgba(34,197,94,0.18)",
        "genre-card-blue":   "rgba(59,130,246,0.18)",
        "genre-card-gold":   "rgba(212,175,55,0.2)",
        "genre-card-violet": "rgba(168,85,247,0.18)",
    };
    document.querySelectorAll(".genre-card").forEach(function (card) {
        const colorKey = Object.keys(glowColors).find(k => card.classList.contains(k));
        if (!colorKey) return;
        const glow = document.createElement("div");
        glow.className = "genre-glow";
        glow.style.background = `radial-gradient(circle at 50% 0%, ${glowColors[colorKey]} 0%, transparent 70%)`;
        card.appendChild(glow);
    });
})();

/* ===== 3-D Card Tilt on Film Cards ===== */
document.querySelectorAll(".film-card").forEach(function (card) {
    card.addEventListener("mousemove", function (e) {
        const rect = card.getBoundingClientRect();
        const x = ((e.clientY - rect.top)  / rect.height - 0.5) * 18;
        const y = ((e.clientX - rect.left) / rect.width  - 0.5) * -18;
        card.dataset.tilting = "true";
        card.style.transform = `perspective(1000px) rotateX(${x}deg) rotateY(${y}deg)`;
    });
    card.addEventListener("mouseleave", function () {
        card.dataset.tilting = "false";
        card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg)";
        void card.offsetWidth; // reflow to retrigger transition
    });
});

const year = document.getElementById("year");
if (year) {
    year.textContent = new Date().getFullYear();
}

const header = document.querySelector(".site-header");
function updateHeader() {
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 18);
}

updateHeader();
window.addEventListener("scroll", updateHeader, { passive: true });

const anchors = document.querySelectorAll("a[href^='#']");
anchors.forEach((anchor) => {
    anchor.addEventListener("click", (event) => {
        const href = anchor.getAttribute("href");
        if (!href || href === "#") return;

        const target = document.querySelector(href);
        if (!(target instanceof HTMLElement)) return;

        event.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
});

const featuredTrack = document.getElementById("featured-track");
const sliderButtons = document.querySelectorAll("[data-slider]");

sliderButtons.forEach((button) => {
    button.addEventListener("click", () => {
        if (!featuredTrack) return;
        const direction = button.getAttribute("data-slider");
        const amount = direction === "prev" ? -320 : 320;
        featuredTrack.scrollBy({ left: amount, behavior: "smooth" });
    });
});

const newsletterForm = document.getElementById("newsletter-form");
newsletterForm?.addEventListener("submit", (event) => {
    event.preventDefault();
});

const authForms = document.querySelectorAll("#login-form, #register-form, #admin-form");
authForms.forEach((form) => {
    form.addEventListener("submit", (event) => {
        event.preventDefault();
    });
});

const paymentForm = document.getElementById("booking-payment-form");
paymentForm?.addEventListener("submit", (event) => {
    event.preventDefault();
});

const bookingFlow = document.querySelector("[data-booking-flow]");
if (bookingFlow instanceof HTMLElement) {
    const panels = Array.from(document.querySelectorAll("[data-booking-panel]"));
    const stepIndicators = Array.from(document.querySelectorAll("[data-step-indicator]"));
    const filmCards = Array.from(document.querySelectorAll("[data-film-card]"));
    const showtimeCards = Array.from(document.querySelectorAll("[data-showtime-card]"));
    const tierButtons = Array.from(document.querySelectorAll("[data-ticket-tier]"));
    const seatButtons = Array.from(document.querySelectorAll(".booking-seat[data-seat]"));
    const nextButtons = Array.from(document.querySelectorAll("[data-booking-next]"));
    const prevButtons = Array.from(document.querySelectorAll("[data-booking-prev]"));

    const summaryFilm = document.getElementById("summary-film");
    const summaryTime = document.getElementById("summary-time");
    const summaryTheater = document.getElementById("summary-theater");
    const summarySeats = document.getElementById("summary-seats");
    const summaryTier = document.getElementById("summary-tier");
    const summaryQuantity = document.getElementById("summary-quantity");
    const summaryTotal = document.getElementById("summary-total");

    const state = {
        step: 1,
        film: "Inception",
        showtime: "17:00",
        date: "Apr 15",
        theater: "Dolby Theater",
        tier: "Standard",
        price: 12,
        seats: ["C3", "D3"],
    };

    const updateSummary = () => {
        const quantity = state.seats.length;
        if (summaryFilm) summaryFilm.textContent = state.film;
        if (summaryTime) summaryTime.textContent = state.showtime;
        if (summaryTheater) summaryTheater.textContent = state.theater;
        if (summarySeats) summarySeats.textContent = state.seats.join(", ");
        if (summaryTier) summaryTier.textContent = state.tier;
        if (summaryQuantity) {
            summaryQuantity.textContent = `${quantity} ${quantity === 1 ? "ticket" : "tickets"}`;
        }
        if (summaryTotal) summaryTotal.textContent = `$${quantity * state.price}`;
    };

    const updateBookingUI = () => {
        panels.forEach((panel) => {
            const panelStep = Number(panel.getAttribute("data-booking-panel"));
            panel.hidden = panelStep !== state.step;
        });

        stepIndicators.forEach((indicator) => {
            const indicatorStep = Number(indicator.getAttribute("data-step-indicator"));
            const circle = indicator.querySelector(".booking-step-circle");
            indicator.classList.toggle("is-active", indicatorStep === state.step);
            indicator.classList.toggle("is-complete", indicatorStep < state.step);
            if (circle) {
                circle.innerHTML =
                    indicatorStep < state.step
                        ? '<svg class="icon"><use href="#i-check"></use></svg>'
                        : String(indicatorStep);
            }
        });

        filmCards.forEach((card) => {
            card.classList.toggle("is-selected", card.getAttribute("data-film-title") === state.film);
        });

        showtimeCards.forEach((card) => {
            card.classList.toggle("is-selected", card.getAttribute("data-time") === state.showtime);
        });

        tierButtons.forEach((button) => {
            button.classList.toggle("is-selected", button.getAttribute("data-tier") === state.tier);
        });

        seatButtons.forEach((button) => {
            const seatId = button.getAttribute("data-seat");
            button.classList.toggle("is-selected", !!seatId && state.seats.includes(seatId));
        });

        updateSummary();
    };

    filmCards.forEach((card) => {
        card.addEventListener("click", () => {
            const filmTitle = card.getAttribute("data-film-title");
            if (!filmTitle) return;
            state.film = filmTitle;
            updateBookingUI();
        });
    });

    showtimeCards.forEach((card) => {
        card.addEventListener("click", () => {
            const time = card.getAttribute("data-time");
            const date = card.getAttribute("data-date");
            const theater = card.getAttribute("data-theater");
            if (!time || !date || !theater) return;
            state.showtime = time;
            state.date = date;
            state.theater = theater;
            updateBookingUI();
        });
    });

    tierButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const tier = button.getAttribute("data-tier");
            const price = Number(button.getAttribute("data-price"));
            if (!tier || Number.isNaN(price)) return;
            state.tier = tier;
            state.price = price;
            updateBookingUI();
        });
    });

    seatButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const seat = button.getAttribute("data-seat");
            if (!seat) return;

            const isSelected = state.seats.includes(seat);
            if (isSelected) {
                state.seats = state.seats.filter((item) => item !== seat);
            } else if (state.seats.length < 2) {
                state.seats = [...state.seats, seat];
            } else {
                state.seats = [state.seats[1], seat];
            }
            updateBookingUI();
        });
    });

    nextButtons.forEach((button) => {
        button.addEventListener("click", () => {
            if (state.step < 4) {
                state.step += 1;
                updateBookingUI();
                window.scrollTo({ top: 0, behavior: "smooth" });
            }
        });
    });

    prevButtons.forEach((button) => {
        button.addEventListener("click", () => {
            if (state.step > 1) {
                state.step -= 1;
                updateBookingUI();
                window.scrollTo({ top: 0, behavior: "smooth" });
            }
        });
    });

    updateBookingUI();
}

const adminTabs = Array.from(document.querySelectorAll("[data-admin-tab]"));
const adminPanels = Array.from(document.querySelectorAll("[data-admin-panel]"));
const adminSearchInput = document.querySelector(".admin-search input");

if (adminTabs.length && adminPanels.length) {
    const updateAdminPanels = (activeTab) => {
        adminTabs.forEach((tab) => {
            const isActive = tab.getAttribute("data-admin-tab") === activeTab;
            tab.classList.toggle("is-active", isActive);
            tab.setAttribute("aria-selected", String(isActive));
        });

        adminPanels.forEach((panel) => {
            panel.hidden = panel.getAttribute("data-admin-panel") !== activeTab;
        });

        if (adminSearchInput instanceof HTMLInputElement) {
            adminSearchInput.value = "";
            const rows = document.querySelectorAll(
                `[data-admin-panel="${activeTab}"] tbody tr`,
            );
            rows.forEach((row) => {
                row.hidden = false;
            });
        }
    };

    adminTabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            const activeTab = tab.getAttribute("data-admin-tab");
            if (!activeTab) return;
            updateAdminPanels(activeTab);
        });
    });

    if (adminSearchInput instanceof HTMLInputElement) {
        adminSearchInput.addEventListener("input", () => {
            const activePanel = adminPanels.find((panel) => !panel.hidden);
            if (!(activePanel instanceof HTMLElement)) return;
            const query = adminSearchInput.value.trim().toLowerCase();
            const rows = activePanel.querySelectorAll("tbody tr");
            rows.forEach((row) => {
                const text = row.textContent?.toLowerCase() ?? "";
                row.hidden = !text.includes(query);
            });
        });
    }
}

const aiFeedbackButtons = Array.from(document.querySelectorAll("[data-ai-feedback]"));
aiFeedbackButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const cardActions = button.closest(".ai-card-actions");
        if (!(cardActions instanceof HTMLElement)) return;

        const siblings = cardActions.querySelectorAll("[data-ai-feedback]");
        siblings.forEach((sibling) => {
            sibling.classList.remove("is-selected");
            sibling.setAttribute("aria-pressed", "false");
        });

        button.classList.add("is-selected");
        button.setAttribute("aria-pressed", "true");
    });
});

const refreshRecommendationsButton = document.getElementById("refresh-recommendations");
refreshRecommendationsButton?.addEventListener("click", () => {
    refreshRecommendationsButton.classList.add("is-pressed");
    window.setTimeout(() => {
        refreshRecommendationsButton.classList.remove("is-pressed");
    }, 220);
});

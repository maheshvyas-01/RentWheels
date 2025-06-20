document.addEventListener("DOMContentLoaded", function () { 
    // 🔥 Hero Section Fade-Out Effect (Fixed)
    window.addEventListener("scroll", function () {
        let hero = document.querySelector(".hero1");
        if (hero) {
            hero.style.opacity = window.scrollY > 100 ? "0.5" : "1";
            hero.style.transition = "opacity 0.5s ease-in-out";
        }
    });

    // ✅ Fix: Click Event Listener for Manage Cars Button
    let manageCarsBtn = document.querySelector(".manage-cars-btn");
    if (manageCarsBtn) {
        manageCarsBtn.addEventListener("click", function () {
            window.location.href = this.getAttribute("data-url");
        });
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const faqItems = document.querySelectorAll(".faq-item");

    faqItems.forEach((item) => {
        const question = item.querySelector(".faq-question");
        question.addEventListener("click", () => {
            item.classList.toggle("active");
        });
    });
});

window.addEventListener('load', function() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const mainContent = document.getElementById('main');
    if (loadingOverlay && mainContent) {
        setTimeout(() => {
            loadingOverlay.style.display = 'none';
            mainContent.style.display = 'block';
            mainContent.classList.remove('_hidden');
        }, 1000);
    }
});

// Unified DOMContentLoaded handler
document.addEventListener('DOMContentLoaded', function() {
    // ===== CAROUSEL AND MODAL =====
    // Элементы карусели
    const slider = document.querySelector('.edu-slider');
    const slides = document.querySelector('.edu-slides');
    const slideItems = document.querySelectorAll('.edu-slide');
    const prevBtn = document.querySelector('.carousel-prev');
    const nextBtn = document.querySelector('.carousel-next');
    const indicators = document.querySelectorAll('.carousel-indicators button');

    // Элементы модального окна
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalCaption = document.getElementById('modalCaption');
    const closeModal = document.getElementById('closeModal');
    const modalPrev = document.getElementById('modalPrev');
    const modalNext = document.getElementById('modalNext');

    let currentIndex = 0;
    const slideCount = slideItems.length;

    // Функция для обновления карусели
    function updateCarousel() {
        if (!slides || indicators.length === 0) return;

        // Обновляем положение слайдов
        slides.style.transform = `translateX(-${currentIndex * 100}%)`;

        // Обновляем индикаторы
        indicators.forEach((indicator, index) => {
            if (index === currentIndex) {
                indicator.classList.add('bg-gray-800', 'indicator-active');
                indicator.classList.remove('bg-gray-300');
                indicator.setAttribute('aria-current', 'true');
            } else {
                indicator.classList.remove('bg-gray-800', 'indicator-active');
                indicator.classList.add('bg-gray-300');
                indicator.removeAttribute('aria-current');
            }
        });
    }

    // Переход к предыдущему слайду
    function goToPrevSlide() {
        if (slideCount === 0) return;
        currentIndex = (currentIndex - 1 + slideCount) % slideCount;
        updateCarousel();
    }

    // Переход к следующему слайду
    function goToNextSlide() {
        if (slideCount === 0) return;
        currentIndex = (currentIndex + 1) % slideCount;
        updateCarousel();
    }

    // Переход к конкретному слайду
    function goToSlide(index) {
        currentIndex = index;
        updateCarousel();
    }

    // Открытие модального окна
    function openModal(index) {
        if (!modal || !modalImage || !modalCaption || !slideItems[index]) return;
        const img = slideItems[index].querySelector('img');
        if (!img) return;
        modalImage.src = img.src;
        modalCaption.textContent = img.dataset.caption;
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden'; // Блокируем прокрутку страницы
        currentIndex = index;
    }

    // Закрытие модального окна
    function closeModalWindow() {
        if (!modal) return;
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = ''; // Разблокируем прокрутку страницы
    }

    // Обработчики событий для карусели
    if (prevBtn) prevBtn.addEventListener('click', goToPrevSlide);
    if (nextBtn) nextBtn.addEventListener('click', goToNextSlide);

    // Обработчики для индикаторов
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => goToSlide(index));
    });

    // Обработчики для открытия модального окна при клике на изображение
    slideItems.forEach((slide, index) => {
        const img = slide.querySelector('img');
        if (img) img.addEventListener('click', () => openModal(index));
    });

    // Обработчики для модального окна
    if (closeModal) closeModal.addEventListener('click', closeModalWindow);
    if (modalPrev) modalPrev.addEventListener('click', () => {
        goToPrevSlide();
        const img = slideItems[currentIndex].querySelector('img');
        if (img && modalImage && modalCaption) {
            modalImage.src = img.src;
            modalCaption.textContent = img.dataset.caption;
        }
    });
    if (modalNext) modalNext.addEventListener('click', () => {
        goToNextSlide();
        const img = slideItems[currentIndex].querySelector('img');
        if (img && modalImage && modalCaption) {
            modalImage.src = img.src;
            modalCaption.textContent = img.dataset.caption;
        }
    });

    // Закрытие модального окна при клике вне изображения
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModalWindow();
            }
        });
    }

    // Закрытие модального окна при нажатии Escape
    document.addEventListener('keydown', function(e) {
        if (!modal || modal.classList.contains('hidden')) return;
        
        if (e.key === 'Escape') {
            closeModalWindow();
        } else if (e.key === 'ArrowLeft') {
            if (modalPrev) modalPrev.click();
        } else if (e.key === 'ArrowRight') {
            if (modalNext) modalNext.click();
        }
    });

    // Свайп для мобильных устройств
    if (slider) {
        let touchStartX = 0;
        let touchEndX = 0;

        slider.addEventListener('touchstart', e => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        slider.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });

        function handleSwipe() {
            const swipeThreshold = 50; // Минимальное расстояние для свайпа
            if (touchEndX < touchStartX - swipeThreshold) {
                goToNextSlide();
            } else if (touchEndX > touchStartX + swipeThreshold) {
                goToPrevSlide();
            }
        }
    }

    // Инициализация карусели
    updateCarousel();

    // ===== MOBILE MENU =====
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            mobileMenu.classList.toggle('open');
        });

        // Закрывать меню при клике на ссылку
        const mobileLinks = mobileMenu.querySelectorAll('a');
        mobileLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenu.classList.add('hidden');
                mobileMenu.classList.remove('open');
            });
        });
    }

    // ===== MOBILE CARD ANIMATIONS =====
    const isMobile = window.innerWidth <= 768;
    if (isMobile) {
        const cards = document.querySelectorAll('#pricing .card-hover');
        cards.forEach(card => {
            card.classList.remove('card-hover');
            card.classList.add('card-static');

            const revealElements = card.querySelectorAll('.card-reveal');
            revealElements.forEach(el => {
                el.style.opacity = '1';
                el.style.transform = 'none';
            });

            const ctaElements = card.querySelectorAll('.card-cta');
            ctaElements.forEach(el => {
                el.style.opacity = '1';
                el.style.transform = 'none';
            });
        });
    }
});
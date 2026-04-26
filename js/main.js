window.addEventListener('load', function() {
    setTimeout(() => {
        document.getElementById('loadingOverlay').style.display = 'none';
        document.getElementById('main').style.display = 'block';
        document.getElementById('main').classList.remove('_hidden');
    }, 1000);
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
        currentIndex = (currentIndex - 1 + slideCount) % slideCount;
        updateCarousel();
    }

    // Переход к следующему слайду
    function goToNextSlide() {
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
        const img = slideItems[index].querySelector('img');
        modalImage.src = img.src;
        modalCaption.textContent = img.dataset.caption;
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden'; // Блокируем прокрутку страницы
        currentIndex = index;
    }

    // Закрытие модального окна
    function closeModalWindow() {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = ''; // Разблокируем прокрутку страницы
    }

    // Обработчики событий для карусели
    prevBtn.addEventListener('click', goToPrevSlide);
    nextBtn.addEventListener('click', goToNextSlide);

    // Обработчики для индикаторов
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => goToSlide(index));
    });

    // Обработчики для открытия модального окна при клике на изображение
    slideItems.forEach((slide, index) => {
        const img = slide.querySelector('img');
        img.addEventListener('click', () => openModal(index));
    });

    // Обработчики для модального окна
    closeModal.addEventListener('click', closeModalWindow);
    modalPrev.addEventListener('click', () => {
        goToPrevSlide();
        const img = slideItems[currentIndex].querySelector('img');
        modalImage.src = img.src;
        modalCaption.textContent = img.dataset.caption;
    });
    modalNext.addEventListener('click', () => {
        goToNextSlide();
        const img = slideItems[currentIndex].querySelector('img');
        modalImage.src = img.src;
        modalCaption.textContent = img.dataset.caption;
    });

    // Закрытие модального окна при клике вне изображения
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModalWindow();
        }
    });

    // Закрытие модального окна при нажатии Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
            closeModalWindow();
        } else if (e.key === 'ArrowLeft' && !modal.classList.contains('hidden')) {
            modalPrev.click();
        } else if (e.key === 'ArrowRight' && !modal.classList.contains('hidden')) {
            modalNext.click();
        }
    });

    // Свайп для мобильных устройств
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
            // Свайп влево - следующий слайд
            goToNextSlide();
        } else if (touchEndX > touchStartX + swipeThreshold) {
            // Свайп вправо - предыдущий слайд
            goToPrevSlide();
        }
    }

    // Инициализация карусели
    updateCarousel();

    // ===== MOBILE MENU =====
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');

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

    // ===== MOBILE CARD ANIMATIONS =====
    // Отключение анимации карточек на мобильных устройствах
    const isMobile = window.innerWidth <= 768;

    if (isMobile) {
        // Находим все карточки в блоке "О работе со мной"
        const cards = document.querySelectorAll('#pricing .card-hover');

        // Для каждой карточки
        cards.forEach(card => {
            // Удаляем класс card-hover и добавляем статический класс
            card.classList.remove('card-hover');
            card.classList.add('card-static');

            // Показываем скрытый контент
            const revealElements = card.querySelectorAll('.card-reveal');
            revealElements.forEach(el => {
                el.style.opacity = '1';
                el.style.transform = 'none';
            });

            // Показываем стрелки
            const ctaElements = card.querySelectorAll('.card-cta');
            ctaElements.forEach(el => {
                el.style.opacity = '1';
                el.style.transform = 'none';
            });
        });
    }
});
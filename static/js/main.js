// Global site interactions for Technoheaven
(function () {
  const initAOS = function () {
    if (typeof AOS === 'undefined') {
      return;
    }

    AOS.init({
      offset: 10,
      duration: 1000,
      easing: 'ease-in-out',
      delay: 0,
      once: false,
      anchorPlacement: 'top-bottom'
    });
  };

  const initCarousel = function () {
    if (typeof bootstrap === 'undefined') {
      return;
    }

    const carouselEl = document.getElementById('carouselExampleCaptions');
    if (carouselEl) {
      new bootstrap.Carousel(carouselEl, {
        interval: 2000,
        ride: 'carousel',
        pause: 'hover'
      });
    }
  };

  document.addEventListener('DOMContentLoaded', function () {
    initAOS();
    initCarousel();
  });
})();

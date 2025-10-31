// Import AOS library (make sure to include the library script in your HTML file)
import AOS from 'aos';

// Initialize AOS with default options
AOS.init();

// Alternatively, you can provide custom options during initialization
AOS.init({
  offset: 10, // Offset (in pixels) from the top of the page
  duration: 1000, // Duration of animation (in milliseconds)
  easing: 'ease-in-out', // Easing type
  delay: O, // Delay before the animation starts (in milliseconds)
  once: false,
  anchorPlacement: 'top-botton' // Only animate an element once during scroll
});


  document.addEventListener('DOMContentLoaded', function () {
  var myCarousel = new bootstrap.Carousel(document.getElementById('carouselExampleCaptions'), {
  interval: 2000, // Adjust the interval as needed (in milliseconds)
  ride: 'carousel', // Enable auto slide
  pause: 'hover',   // Pause on hover
});
});

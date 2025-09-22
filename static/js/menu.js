(function(){
  var idCounter = 0;

  function nextId(){
    idCounter += 1;
    return 'primary-navigation-' + idCounter;
  }

  function setMenuState(hamburger, links, isOpen){
    hamburger.classList.toggle('active', isOpen);
    links.classList.toggle('active', isOpen);
    hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  }

  function setupHamburger(hamburger){
    var nav = hamburger.closest('nav');
    var links = nav ? nav.querySelector('.link-container') : null;
    if (!links) return;

    hamburger.setAttribute('role', 'button');
    hamburger.setAttribute('aria-expanded', 'false');
    hamburger.setAttribute('aria-label', 'Abrir menu de navegacion');
    hamburger.setAttribute('tabindex', '0');
    if (!links.id) {
      links.id = nextId();
    }
    hamburger.setAttribute('aria-controls', links.id);

    var isOpen = false;

    function openMenu(){
      if (isOpen) return;
      isOpen = true;
      setMenuState(hamburger, links, true);
    }

    function closeMenu(){
      if (!isOpen) return;
      isOpen = false;
      setMenuState(hamburger, links, false);
    }

    hamburger.addEventListener('click', function(){
      if (isOpen) {
        closeMenu();
      } else {
        openMenu();
      }
    });

    hamburger.addEventListener('keydown', function(evt){
      if (evt.key === 'Enter' || evt.key === ' ') {
        evt.preventDefault();
        hamburger.click();
      } else if (evt.key === 'Escape') {
        closeMenu();
      }
    });

    links.addEventListener('click', function(evt){
      if (evt.target && evt.target.closest('a')) {
        closeMenu();
      }
    });

    document.addEventListener('keydown', function(evt){
      if (evt.key === 'Escape') {
        closeMenu();
      }
    });

    document.addEventListener('click', function(evt){
      if (!isOpen) return;
      if (hamburger.contains(evt.target)) return;
      if (links.contains(evt.target)) return;
      closeMenu();
    });
  }

  document.addEventListener('DOMContentLoaded', function(){
    var hamburgers = document.querySelectorAll('.hamburger');
    Array.prototype.forEach.call(hamburgers, setupHamburger);
  });
})();
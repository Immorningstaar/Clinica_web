// ====== MENÚ HAMBURGUESA RESPONSIVE ======
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const hamburger = document.querySelector('.hamburger');
    const linkContainer = document.querySelector('.link-container');
    const nav = document.querySelector('nav');
    
    // Verificar que los elementos existan
    if (!hamburger || !linkContainer) {
        console.error('Elementos del menú hamburguesa no encontrados');
        return;
    }
    
    // Función para abrir/cerrar menú
    function toggleMenu() {
        hamburger.classList.toggle('active');
        linkContainer.classList.toggle('active');
        
        // Agregar/remover clase para el body (opcional)
        document.body.classList.toggle('menu-open');
    }
    
    // Event listener para el botón hamburguesa
    hamburger.addEventListener('click', toggleMenu);
    
    // Cerrar menú al hacer clic en un enlace (móvil)
    const navLinks = linkContainer.querySelectorAll('a');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                hamburger.classList.remove('active');
                linkContainer.classList.remove('active');
                document.body.classList.remove('menu-open');
            }
        });
    });
    
    // Cerrar menú al redimensionar la ventana
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            hamburger.classList.remove('active');
            linkContainer.classList.remove('active');
            document.body.classList.remove('menu-open');
        }
    });
    
    // Cerrar menú al hacer clic fuera (opcional)
    document.addEventListener('click', (e) => {
        if (!nav.contains(e.target) && linkContainer.classList.contains('active')) {
            hamburger.classList.remove('active');
            linkContainer.classList.remove('active');
            document.body.classList.remove('menu-open');
        }
    });
    
    console.log('Menú hamburguesa inicializado correctamente');
});

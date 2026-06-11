// Inicializa AOS e efeitos globais da navbar.
(() => {
    if (window.AOS) {
        AOS.init({
            duration: 800,
            once: true,
            offset: 100,
            disable: () => window.matchMedia('(prefers-reduced-motion: reduce)').matches,
        });
    }

    const navbar = document.querySelector('.navbar-custom');
    if (!navbar) return;

    let ticking = false;
    let lastScrolled = null;

    const applyNavbarState = () => {
        const scrolled = window.scrollY > 50;
        // Só escreve no DOM quando o estado realmente muda (evita jank).
        if (scrolled !== lastScrolled) {
            lastScrolled = scrolled;
            if (scrolled) {
                navbar.style.padding = '5px 0';
                navbar.style.backgroundColor = 'rgba(17, 17, 17, 0.98)';
                navbar.style.boxShadow = '0 5px 20px rgba(0,0,0,0.5)';
            } else {
                navbar.style.padding = '15px 0';
                navbar.style.backgroundColor = 'rgba(17, 17, 17, 0.95)';
                navbar.style.boxShadow = 'none';
            }
        }
        ticking = false;
    };

    window.addEventListener('scroll', () => {
        if (!ticking) {
            ticking = true;
            window.requestAnimationFrame(applyNavbarState);
        }
    }, { passive: true });
})();

// Move todos os modais para serem filhos diretos de <body>.
// Evita que fiquem presos em um contexto de empilhamento de um ancestral
// (ex.: <main> com animação/opacity), o que os renderizaria atrás do backdrop.
(() => {
    document.querySelectorAll('.modal').forEach((modal) => {
        if (modal.parentElement !== document.body) {
            document.body.appendChild(modal);
        }
    });
})();

// Lê o valor de um cookie (ex.: csrftoken). Fonte única para todos os scripts.
function getCookie(name) {
    const match = document.cookie.match(`(^|;)\\s*${name}\\s*=\\s*([^;]+)`);
    return match ? match.pop() : '';
}

// Abre uma imagem em tela cheia no modal de lightbox.
function openLightbox(src) {
    const img = document.getElementById('lightboxImg');
    const modalEl = document.getElementById('lightboxModal');
    if (!img || !modalEl) return;
    img.src = src;
    new bootstrap.Modal(modalEl).show();
}

// Monta os slides do carrossel do modal de detalhe (botões acessíveis + zoom).
function buildLightboxSlides(images) {
    return images
        .filter(Boolean)
        .map((src, index) => `
            <div class="carousel-item${index === 0 ? ' active' : ''} h-100">
                <button type="button" class="zoom-btn" aria-label="Ampliar imagem" onclick="openLightbox(this.querySelector('img').src)">
                    <img src="${src}" class="d-block w-100 h-100" style="object-fit: cover;" alt="">
                </button>
            </div>`)
        .join('');
}

// Popula o carrossel do modal de detalhe e mostra/esconde os controles.
function setupDetailCarousel({ innerId, prevId, nextId, images }) {
    const inner = document.getElementById(innerId);
    const prev = document.getElementById(prevId);
    const next = document.getElementById(nextId);
    if (!inner || !prev || !next) return;

    const slides = images.filter(Boolean);
    inner.innerHTML = buildLightboxSlides(slides);

    const display = slides.length > 1 ? 'block' : 'none';
    prev.style.display = display;
    next.style.display = display;
}

// Aviso não-bloqueante (substitui alert). type: 'success' | 'danger' | 'info'
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) {
        alert(message);
        return;
    }

    const el = document.createElement('div');
    el.className = `app-toast app-toast-${type}`;
    el.setAttribute('role', type === 'danger' ? 'alert' : 'status');
    el.textContent = message;
    container.appendChild(el);

    requestAnimationFrame(() => el.classList.add('show'));
    setTimeout(() => {
        el.classList.remove('show');
        setTimeout(() => el.remove(), 300);
    }, 4500);
}

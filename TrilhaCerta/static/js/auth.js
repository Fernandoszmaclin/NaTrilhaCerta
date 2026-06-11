// Lógica do modal de autenticação (login + signup via AJAX).
(() => {
    const tabs = document.querySelectorAll('.auth-tab-btn');
    if (!tabs.length) return;

    const showAlert = (msg, success) => {
        const el = document.getElementById('authAlert');
        if (!el) return;
        el.textContent = msg;
        el.className = `alert mb-3 alert-${success ? 'success' : 'danger'}`;
    };

    tabs.forEach((btn) => {
        btn.addEventListener('click', () => {
            tabs.forEach((b) => b.classList.remove('active'));
            btn.classList.add('active');
            document.querySelectorAll('.auth-form').forEach((f) => f.classList.add('d-none'));
            const target = document.getElementById(btn.dataset.target);
            if (target) target.classList.remove('d-none');
            const alertEl = document.getElementById('authAlert');
            if (alertEl) alertEl.classList.add('d-none');
        });
    });

    const bindForm = (formId, url) => {
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const data = Object.fromEntries(new FormData(form));

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(data),
            })
                .then((r) => r.json().then((d) => ({ ok: r.ok, data: d })))
                .then((res) => {
                    showAlert(res.data.message, res.ok);
                    if (res.ok) setTimeout(() => location.reload(), 800);
                })
                .catch(() => {
                    showAlert('Erro de conexão. Tente novamente.', false);
                });
        });
    };

    const authRoot = document.getElementById('authModal');
    if (!authRoot) return;
    bindForm('loginForm', authRoot.dataset.loginUrl);
    bindForm('signupForm', authRoot.dataset.signupUrl);
})();

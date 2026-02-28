async function login() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    const res = await fetch(`http://127.0.0.1:8000/login?email=${email}&password=${password}`, {
        method: 'POST'
    });

    if (res.ok) {
        const data = await res.json();
        localStorage.setItem('admin_token', data.access_token);
        localStorage.setItem('admin_email', email);
        showDashboardAfterLogin();
    } else {
        document.getElementById('login-error').style.display = "block"
    }
}

function showDashboardAfterLogin() {
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('dashboard').style.display = 'flex';
}

window.onload = function() {
    const token = localStorage.getItem('admin_token');
    if (token) {
        showDashboardAfterLogin();
    }
}

function showAdminPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

    document.querySelectorAll('.navigation-item').forEach(item => item.classList.remove('active'));

    document.getElementById('page-' + page).classList.add('active');

    event.currentTarget.classList.add('active');

    const titles = {
        'reservations': 'Rezerwacje',
        'hairdressers': 'Fryzjerzy'
    };
    document.getElementById('topbar-title').textContent = titles[page];
}

function openAddHairdresser() {
    const modal = new bootstrap.Modal(document.getElementById('modal-add-hairdresser'));
    modal.show();
}
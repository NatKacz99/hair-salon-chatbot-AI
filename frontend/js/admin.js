URL_BASE = "http://127.0.0.1:8000";

let servicesMap = {};
let hairdressersMap = {};

async function login() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    const res = await fetch(`${URL_BASE}/login?email=${email}&password=${password}`, {
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

async function showDashboardAfterLogin() {
    document.getElementById('login-page').style.display = 'none';
    document.getElementById('dashboard').style.display = 'flex';

    await loadMaps();
    loadReservations();
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

let allReservations = [];
async function loadReservations() {
    const token = localStorage.getItem('admin_token');
    const res = await fetch(`${URL_BASE}/admin/bookings`, {
        headers: {'Authorization': `Bearer ${token}`}
    });

    if (!res.ok) {
        console.error('Błąd pobierania rezerwacji ', res.status);
        return
    }

    allReservations = await res.json();
    renderReservations(allReservations);
}

function filterReservations() {
    const status = document.getElementById('filter-status').value;

    if(!status) {
        renderReservations(allReservations);
    } else {
        const filtered = allReservations.filter(booking => booking.status === status);
        renderReservations(filtered);
    }
} 

async function loadMaps() {
    const [servicesRes, hairdressersRes] = await Promise.all([
        fetch(`${URL_BASE}/services`),
        fetch(`${URL_BASE}/hairdressers`)
    ]);

    const services = await servicesRes.json();
    const hairdressers = await hairdressersRes.json();

    services.forEach(service => servicesMap[service.id] = service.name);
    hairdressers.forEach(hairdresser => hairdressersMap[hairdresser.id] = hairdresser.first_name)
}

function openChangeStatus(bookingId) {
    document.getElementById('status-booking').value = bookingId;
    const modal = new bootstrap.Modal(document.getElementById('modal-change-status'));
    modal.show();
}

function renderReservations(bookings) {
    const tbody = document.getElementById('reservations-tbody');

    if (bookings.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9">
        <div class="empty-state">
            <div class="empty-state-icon">📋</div>
            <div class="empty-state-text">Brak rezerwacji</div>
        </div></td></tr>`;
        return;
    }

    tbody.innerHTML = bookings.map(booking => `
        <tr>
            <td>${booking.id}</td>
            <td>${booking.client_name}</td>
            <td>${booking.client_phone}</td>
            <td>${hairdressersMap[booking.hairdresser_id] || booking.hairdresser_id}</td>
            <td>${servicesMap[booking.service_id] || booking.service_id}</td>
            <td>${new Date(booking.booking_datetime).toLocaleString('pl-PL')}</td>
            <td>${booking.notes || '-'}</td>
            <td><span class="badge badge-${booking.status}">${booking.status}</span></td>
            <td><button class="btn btn-outline btn-sm" onClick="openChangeStatus(${booking.id})">Zmień status</button></td>
        </tr>`).join('');
}

async function changeStatus() {
    const token = localStorage.getItem('admin_token');
    const id = document.getElementById('status-booking').value;
    const status = document.getElementById('new-status').value;

    console.log('id:', id, 'status:', status);

    const res = await fetch(`${URL_BASE}/admin/bookings/${id}?status=${status}`, {
        method: 'PATCH',
        headers: {'Authorization': `Bearer ${token}`}
    });

    if (res.ok) {
        bootstrap.Modal.getInstance(document.getElementById('modal-change-status')).hide();
        loadReservations();
    } else {
        alert('Nie udało się zmienić statusu. Spróbuj ponownie.');
    }
}

function handleLogout() {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_email');
    document.getElementById('dashboard').style.display = 'none';
    document.getElementById('login-page').style.display = "flex";
}
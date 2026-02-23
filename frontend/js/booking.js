async function loadServices() {
    const res = await fetch('http://127.0.0.1:8000/services');
    const services = await res.json();
    const select = document.getElementById('select-service');
    services.forEach(service => {
        select.innerHTML += `<option value="${service.id}">${service.name} — ${service.price} PLN</option>`;
    });
}

async function loadHairdressers() {
    const res = await fetch('http://127.0.0.1:8000/hairdressers');
    const hairdressers = await res.json();
    const select = document.getElementById('select-hairdresser')
    hairdressers.forEach(hairdresser => {
        select.innerHTML += `<option value="${hairdresser.id}">${hairdresser.first_name}</option>`;
    });
}

async function loadFreeTerms() {
    const hairdresserId = document.getElementById('select-hairdresser').value;
    const date = document.getElementById('input-date').value;
    const service_id = document.getElementById('select-service').value;

    if (!hairdresserId || !date) return;

    const res = await fetch(`http://127.0.0.1:8000/available-slots?hairdresser_id=${hairdresserId}&date=${date}&service_id=${service_id}`);
    const outcome = await res.json();

    const select = document.getElementById('select-time');
    select.innerHTML = '';

    if(outcome.free_hours.length === 0) {
        select.innerHTML = '<option value="">— Brak wolnych terminów —</option>';
        return;
    }

    outcome.free_hours.forEach(hour => {
        select.innerHTML += `<option value="${hour}">${hour}</option>`
    });
}

async function sendBooking() {
    if (!validateBookingForm()) return;

    const hairdresserId = document.getElementById('select-hairdresser').value;
    const url = hairdresserId
    ? 'http://127.0.0.1:8000/bookings'
    : 'http://127.0.0.1:8000/bookings/any-hairdresser'

    const data = {
        hairdresser_id: hairdresserId ? parseInt(hairdresserId) : 0,
        service_id: parseInt(document.getElementById('select-service').value),
        client_name: document.getElementById('input-name').value,
        client_phone: document.getElementById('input-phone').value,
        booking_datetime: document.getElementById('input-date').value + 'T' 
        + document.getElementById('select-time').value + ':00',
        notes: document.getElementById('input-notes').value || null
    };

    const res = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    if (res.ok) {
        alert('Dziękujemy, wkrótce skontaktujemy się z potwierdzeniem rezerwacji!');
    } else {
        alert('Coś poszło nie tak, spróbuj ponownie!')
    }
}

loadServices();
loadHairdressers();
async function loadServices() {
    try {
        const res = await fetch(`${CONFIG.API_URL}/services`);

        if (!res.ok) {
            throw new Error(`HTTP {res.status}`)
        }

        const services = await res.json();
        const select = document.getElementById('select-service');
        services.forEach(service => {
            select.innerHTML += `<option value="${service.id}">${service.name} — ${service.price} PLN</option>`;
        });
    } catch(error) {
        console.error('Error services loading:', error);
        showApiError('Nie udało się załadować usług. Spróbuj ponownie później')
    }
}

async function loadHairdressers() {
    try {
        const res = await fetch(`${CONFIG.API_URL}/hairdressers`);
        const hairdressers = await res.json();
        const select = document.getElementById('select-hairdresser')
        hairdressers.forEach(hairdresser => {
            select.innerHTML += `<option value="${hairdresser.id}">${hairdresser.first_name}</option>`;
        });
    } catch(error) {
        console.error('Error barbers lading:', error);
        showApiError('Nie udało się załadować fryzjerów. Spróbuj ponownie później')
    }
}

async function loadFreeTerms() {
    try {
        const hairdresserId = document.getElementById('select-hairdresser').value;
        const date = document.getElementById('input-date').value;
        const service_id = document.getElementById('select-service').value;

        if (!hairdresserId || !date) return;

        const res = await fetch(`${CONFIG.API_URL}/available-slots?hairdresser_id=${hairdresserId}&date=${date}&service_id=${service_id}`);
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
    } catch(error) {
        console.error('Error free terms loading', error);
        showApiError('Błąd serwera przy ładowaniu wolnych godzin. Spróbuj ponownie później')
    }
}

async function sendBooking() {
    try {
        if (!validateBookingForm()) return;

        const hairdresserId = document.getElementById('select-hairdresser').value;
        const url = hairdresserId
        ? `${CONFIG.API_URL}/bookings`
        : `${CONFIG.API_URL}/bookings/any-hairdresser`

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
            showBookingMessage('Dziękujemy, wkrótce skontaktujemy się z potwierdzeniem rezerwacji!', 'success');
        } else {
            showBookingMessage('Coś poszło nie tak, spróbuj ponownie!', 'error')
        }
    } catch(error) {
        console.error('Error booking sending:', error);
        showApiError("Problem z przesłaniem rezerwacji. Spróbuj ponwnie później")
    }
}

function showBookingMessage(message, type) {
    const messageArea = document.getElementById('booking-message');
    messageArea.textContent = message;
    messageArea.className = type;
    messageArea.style.display = 'block';
}

function showApiError(message) {
    const errorDiv = document.getElementById('api-error');
    errorDiv.textConent = message;
    errorDiv.style.display = "block";
}

loadServices();
loadHairdressers();
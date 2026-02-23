function showError(id, message) {
    const el = document.getElementById(id);
    el.textContent = message;
    el.classList.add('visible');
}

function validateBookingForm() {
    let isValid = true;

    document.querySelectorAll('.error-message').forEach(el => {
        el.classList.remove('visible');
        el.textContent = '';
    });

    const name = document.getElementById('input-name').value.trim();
    const phone = document.getElementById('input-phone').value.trim();
    const service = document.getElementById('select-service').value;
    const date = document.getElementById('input-date').value;

    const nameRegex = /^[A-ZÀ-Ża-zà-ż]+([- ][A-ZÀ-Ża-zà-ż]+)+$/;
    if (!name) {
        showError('error-name', 'Imię i nazwisko nie może być puste');
        isValid = false;
    }
    else if (!nameRegex.test(name)) {
        showError('error-name', 'Twoje imię i nazwisko zawiera niepoprawne znaki. Wprowadź ponownie');
        isValid = false;
    }
    else {
        const nameParts = name.split(' ');
        const formattedName = nameParts.map(word => 
        word.charAt(0).toUpperCase() + 
        word.slice(1).toLowerCase()).join(' ');
        document.getElementById('input-name').value = formattedName;
    }

    if(!phone){
        showError('error-phone', 'Pole nie może być puste');
        isValid = false;
    }

    if(!service){
        showError('error-service', 'Wybierz rodzaj usługi');
        isValid = false;
    }

    if(!date){
        showError('error-date', 'Wybierz datę');
        isValid = false;
    }

    return isValid;
}


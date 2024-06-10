let sidebarOpen = false;

function toggleSidebar() {
    const sidebar = document.querySelector('.main-sidebar');
    const container = document.querySelector('.container');
    const toggleButton = document.querySelector('.toggle-sidebar');

    if (sidebarOpen) {
        sidebar.style.width = '0';
        container.style.filter = 'none';
        toggleButton.innerHTML = '☰';
    } else {
        container.style.filter = 'blur(3px)';
        sidebar.style.width = '270px';
        toggleButton.innerHTML = '✖';
    }

    sidebarOpen = !sidebarOpen;

    toggleButton.classList.toggle('opened', sidebarOpen);
}

const selectedSeats = new Set();

function toggleSeatSelection(element) {
    const seatId = element.getAttribute('data-seat-id');
    console.log('Toggling seat:', seatId);
    if (selectedSeats.has(seatId)) {
        selectedSeats.delete(seatId);
        element.classList.remove('selected');
    } else {
        selectedSeats.add(seatId);
        element.classList.add('selected');
    }
    console.log('Selected seats:', selectedSeats);
    updateSubmitButtonState();
}

function updateSubmitButtonState() {
    const submitButton = document.querySelector('button[id="booking-submit"]');
    if (selectedSeats.size === 0) {
        submitButton.classList.add('disabled');
        submitButton.disabled = true; // Also disable the button
    } else {
        submitButton.classList.remove('disabled');
        submitButton.disabled = false; // Enable the button
    }
    console.log('Submit button state updated:', submitButton.disabled);
}

document.addEventListener('DOMContentLoaded', function () {
    updateSubmitButtonState();
    document.getElementById('booking-form').addEventListener('submit', function (event) {
        const seatIdsInput = document.createElement('input');
        seatIdsInput.type = 'hidden';
        seatIdsInput.name = 'seat_ids';
        seatIdsInput.value = Array.from(selectedSeats).join(',');
        this.appendChild(seatIdsInput);
    });
});
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
    if (selectedSeats.has(seatId)) {
        selectedSeats.delete(seatId);
        element.classList.remove('selected');
    } else {
        selectedSeats.add(seatId);
        element.classList.add('selected');
    }
    document.querySelector('button[type="submit"]').disabled = selectedSeats.size === 0;
    document.querySelector('input[name="seat_ids"]').value = Array.from(selectedSeats);
}

document.getElementById('booking-form').addEventListener('submit', function (event) {
    const seatIdsInput = document.createElement('input');
    seatIdsInput.type = 'hidden';
    seatIdsInput.name = 'seat_ids';
    seatIdsInput.value = Array.from(selectedSeats).join(',');
    this.appendChild(seatIdsInput);
});


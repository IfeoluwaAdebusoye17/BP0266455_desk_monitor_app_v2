//Connect to the socket.IO server
const socket = io.connect(window.location.origin);

// Fetch desk statuses from the Flask backend
function fetchDeskStatuses() {
    fetch('/desks')
    .then(response => response.json())
    .then(desks => {
        const container = document.getElementById('desks-container');
        container.innerHTML = ''; //Clear previous data

        desks.forEach(desk => {
            const deskDiv = document.createElement('div');
            deskDiv.classList.add('desk');
            deskDiv.innerHTML = `
                <h3>Desk ${desk.docking_station_id}</h3>
                <p>Status: ${desk.status}</p>
                <p>Last Updated: ${desk.last_updated}</p>
                <p>Temperature: ${desk.temperature}</p>
                <p>Humidity: ${desk.humidity}</p>
                <p>Light: ${desk.light}</p>
                <p>Noise: ${desk.noise}</p>
            `;
            container.appendChild(deskDiv);
        });
    })
    .catch(error => console.error('Error fetching desk statuses:', error));
}


//Listen for real-time desk updates
socket.on('desk_update', data => {
    console.log('Desk update received', data);
    fetchDeskStatuses(); // refetch desk status 
});



//Initial fetch when page loads
fetchDeskStatuses();

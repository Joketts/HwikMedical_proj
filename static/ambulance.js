let registrationNumber = null;

// Login function
function loginAmbulance() {
    const regNumber = document.getElementById('registration_number').value;

    fetch('/ambulance/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ registration_number: regNumber }),
    })
        .then((response) => response.json())
        .then((data) => {
            const loginResponse = document.getElementById('login-response');
            if (data.message === 'Login successful') {
                registrationNumber = regNumber;
                loginResponse.innerHTML = `<p>${data.message}</p>`;
                window.location.href = '/index';
            } else {
                loginResponse.innerHTML = `<p>${data.message}</p>`;
            }
        })
        .catch((error) => console.error('Error:', error));
}

// Fetch and display call-outs
function fetchCallOuts() {
    fetch('/ambulance/callouts')
        .then(response => response.json())
        .then(data => {
            console.log('Fetched call-outs:', data); // Debugging log
            const tableBody = document.querySelector('#call-outs tbody');
            tableBody.innerHTML = ''; // Clear existing rows

            if (!data || data.length === 0) {
                console.log('No pending call-outs found');
                tableBody.innerHTML = '<tr><td colspan="5">No call-outs available</td></tr>';
                return;
            }

            data.forEach(callOut => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${callOut.patient_name}</td>
                    <td>${callOut.condition}</td>
                    <td>${callOut.incident_address}</td>
                    <td><button onclick="acceptCallOut(${callOut.id})">Accept</button></td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching call-outs:', error));
}

function acceptCallOut(callOutId) {
    fetch('/ambulance/accept_callout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: callOutId, registration_number: registrationNumber }),
    })
        .then((response) => response.json())
        .then((data) => {
            alert(data.message);
            if (data.message.includes("accepted")) {
                // Redirect to action page with call-out ID
                window.location.href = `/ambulance/actions/${callOutId}`;
            }
        })
        .catch((error) => console.error('Error:', error));
}

function submitActions() {
    const callOutId = window.location.pathname.split('/').pop(); // Extract call-out ID from URL
    const actionsTaken = document.getElementById('actions_taken').value;

    fetch('/ambulance/submit_actions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: callOutId,
            actions: actionsTaken,
            registration_number: registrationNumber,
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            const actionResponse = document.getElementById('action-response');
            actionResponse.innerHTML = `<p>${data.message}</p>`;

            if (data.message.includes("successfully")) {
                // Redirect to callouts page after 2 seconds
                actionResponse.classList.add('success'); // Add success style
                actionResponse.style.display = 'block'; // Show the response box
                setTimeout(() => {
                    window.location.href = '/index';
                }, 2000); // Delay to let user read the message
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Failed to submit actions. Please try again.');
        });
}


// Fetch call-outs every 5 seconds
setInterval(fetchCallOuts, 5000);
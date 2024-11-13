function submitIncident() {
    const name = document.getElementById("name").value;
    const nhs_number = document.getElementById("nhs_number").value;
    const address = document.getElementById("address").value;
    const condition = document.getElementById("condition").value;

    fetch('/add_incident', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: name,
            nhs_number: nhs_number,
            address: address,
            condition: condition
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("response").innerHTML = `<p>${data.message}</p>`;
        if (data.rescue_request) {
            document.getElementById("response").innerHTML += `<p>Rescue Request: ${JSON.stringify(data.rescue_request)}</p>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById("response").innerHTML = "<p>Error submitting incident</p>";
    });
}

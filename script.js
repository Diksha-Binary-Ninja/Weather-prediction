// Populate states and districts
window.onload = function() {
    fetch("/states").then(response => response.json()).then(data => {
        const stateSelect = document.getElementById("state");
        data.states.forEach(state => {
            let option = document.createElement("option");
            option.value = state;
            option.text = state;
            stateSelect.add(option);
        });

        stateSelect.onchange = function() {
            const selectedState = stateSelect.value;
            fetch(`/districts?state=${selectedState}`).then(response => response.json()).then(data => {
                const districtSelect = document.getElementById("district");
                districtSelect.innerHTML = "";
                data.districts.forEach(district => {
                    let option = document.createElement("option");
                    option.value = district;
                    option.text = district;
                    districtSelect.add(option);
                });
            });
        };
    });
};

// Handle prediction
function makePrediction() {
    const state = document.getElementById("state").value;
    const district = document.getElementById("district").value;
    const month = document.getElementById("month").value;

    fetch("/predict", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: state, district: district, month: month })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("result").innerText = data.prediction;
    });
}
const rainfallData = {
        labels: ['Historical Average', 'Predicted Rainfall'],
        datasets: [{
            label: 'Rainfall Amount (mm)',
            data: [151.70, 141.52], // Replace with your data
            backgroundColor: ['rgba(75, 192, 192, 0.2)', 'rgba(153, 102, 255, 0.2)'],
            borderColor: ['rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)'],
            borderWidth: 1
        }]
    };

    const config = {
        type: 'bar',
        data: rainfallData,
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    };

    // Render the chart
    var ctx = document.getElementById('rainfallChart').getContext('2d');
    new Chart(ctx, config);
// Handle voice recognition
function startVoiceRecognition() {
    fetch("/voice")
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById("state").value = data.text;  // You can adapt this to fill the right field
        }
    });
}

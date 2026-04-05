let currentIndex = 0;
let roadsOrder = [];
let signalTimes = {};
let latestData = null;
let timerInterval;

async function analyzeTraffic() {
    const road1 = document.getElementById("road1").files[0];
    const road2 = document.getElementById("road2").files[0];
    const road3 = document.getElementById("road3").files[0];
    const road4 = document.getElementById("road4").files[0];
    const emergencyRoad = document.getElementById("emergencyRoad").value;

    if (!road1 || !road2 || !road3 || !road4) {
        alert("Please upload all 4 images.");
        return;
    }

    const formData = new FormData();
    formData.append("road1", road1);
    formData.append("road2", road2);
    formData.append("road3", road3);
    formData.append("road4", road4);
    formData.append("emergencyRoad", emergencyRoad);

    try {
        const response = await fetch("/predict", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        latestData = data;

        document.getElementById("dashboard").style.display = "block";

        renderMainJunction(data);
        renderLaneCards(data);
        startSignalSystem(data);
    } catch (error) {
        console.error(error);
        alert("Error analyzing traffic.");
    }
}

function getTrafficColor(level) {
    if (level === "Low Traffic") return "#22c55e";
    if (level === "Medium Traffic") return "#facc15";
    if (level === "High Traffic") return "#ef4444";
    return "#94a3b8";
}

function clearVehicles() {
    document.querySelectorAll(".vehicle").forEach(v => v.remove());
    document.querySelectorAll(".mini-vehicle").forEach(v => v.remove());
}

function createVehicles(roadId, count, direction) {
    const road = document.getElementById(roadId);
    const visibleVehicles = Math.min(count, 12);

    for (let i = 0; i < visibleVehicles; i++) {
        const vehicle = document.createElement("div");
        vehicle.className = "vehicle";

        if (direction === "down") {
            vehicle.style.left = `${50 + (i % 3) * 25}px`;
            vehicle.style.top = `${(i * 20) % 150}px`;
            vehicle.style.animation = `moveDown 3s linear infinite`;
        } else if (direction === "left") {
            vehicle.style.top = `${50 + (i % 3) * 25}px`;
            vehicle.style.right = `${(i * 25) % 150}px`;
            vehicle.style.animation = `moveLeft 3s linear infinite`;
        } else if (direction === "up") {
            vehicle.style.left = `${50 + (i % 3) * 25}px`;
            vehicle.style.bottom = `${(i * 20) % 150}px`;
            vehicle.style.animation = `moveUp 3s linear infinite`;
        } else {
            vehicle.style.top = `${50 + (i % 3) * 25}px`;
            vehicle.style.left = `${(i * 25) % 150}px`;
            vehicle.style.animation = `moveRight 3s linear infinite`;
        }

        vehicle.style.animationPlayState = "paused";
        road.appendChild(vehicle);
    }
}

function createMiniVehicles(containerId, count) {
    const container = document.getElementById(containerId);
    const visibleVehicles = Math.min(count, 10);

    for (let i = 0; i < visibleVehicles; i++) {
        const vehicle = document.createElement("div");
        vehicle.className = "mini-vehicle";
        vehicle.style.top = `${15 + (i % 3) * 25}px`;
        vehicle.style.left = `${(i * 25) % 120}px`;
        vehicle.style.animation = `moveMini ${2 + Math.random() * 2}s linear infinite`;
        vehicle.style.animationPlayState = "paused";
        container.appendChild(vehicle);
    }
}

function renderMainJunction(data) {
    const roads = ["Road1", "Road2", "Road3", "Road4"];
    const directions = ["down", "left", "up", "right"];

    clearVehicles();

    roads.forEach((road, index) => {
        const level = data.predictions[road];
        const vehicleCount = data.vehicle_counts[road];
        const roadBox = document.getElementById(`junction-road${index + 1}`);

        roadBox.style.background = getTrafficColor(level);
        roadBox.style.border = "2px solid #475569";

        createVehicles(`junction-road${index + 1}`, vehicleCount, directions[index]);
    });
}

function renderLaneCards(data) {
    const laneGrid = document.getElementById("laneGrid");
    laneGrid.innerHTML = "";

    const roads = ["Road1", "Road2", "Road3", "Road4"];

    roads.forEach((road, index) => {
        const level = data.predictions[road];
        const confidence = data.confidences[road];
        const vehicleCount = data.vehicle_counts[road];
        const density = data.density_scores[road];
        const signal = data.signal_times[road];
        const imageUrl = data.image_urls[road];
        const color = getTrafficColor(level);
        const barWidth = Math.min(vehicleCount * 4, 100);
        const isEmergency = data.emergency_road === road;

        const card = document.createElement("div");
        card.className = "lane-card";
        card.id = `lane-card-${road}`;

        card.innerHTML = `
            <h3>${road} ${isEmergency ? "🚑" : ""}</h3>
            <img src="${imageUrl}" class="lane-preview" alt="${road} preview" />
            <p><strong>Traffic Level:</strong> ${level}</p>
            <p><strong>Estimated Vehicles:</strong> ${vehicleCount}</p>
            <p><strong>Confidence:</strong> ${confidence}%</p>
            <p><strong>Density Score:</strong> ${density}</p>
            <p><strong>Allocated Green Time:</strong> ${signal} sec</p>
            <p><strong>Current Status:</strong> <span id="status-${road}" class="signal-badge red">RED</span></p>
            <div class="bar-container">
                <div class="bar" style="background:${color}; width:${barWidth}%"></div>
            </div>
            <div class="mini-road" id="mini-road-${road}"></div>
        `;

        laneGrid.appendChild(card);
        createMiniVehicles(`mini-road-${road}`, vehicleCount);
    });
}

function startSignalSystem(data) {
    if (timerInterval) clearInterval(timerInterval);

    if (data.emergency_road && data.emergency_road !== "") {
        const others = Object.keys(data.vehicle_counts)
            .filter(r => r !== data.emergency_road)
            .sort((a, b) => data.vehicle_counts[b] - data.vehicle_counts[a]);

        roadsOrder = [data.emergency_road, ...others];
    } else {
        roadsOrder = Object.keys(data.vehicle_counts)
            .sort((a, b) => data.vehicle_counts[b] - data.vehicle_counts[a]);
    }

    signalTimes = data.signal_times;
    currentIndex = 0;
    runSignalCycle();
}

function runSignalCycle() {
    clearInterval(timerInterval);

    const currentRoad = roadsOrder[currentIndex];
    let timeLeft = signalTimes[currentRoad];

    updateSignals(currentRoad);
    updateLaneStatuses(currentRoad);

    const timerDisplay = document.getElementById("timer");
    timerDisplay.innerText = `${currentRoad} GREEN: ${timeLeft}s`;

    timerInterval = setInterval(() => {
        timeLeft--;
        timerDisplay.innerText = `${currentRoad} GREEN: ${timeLeft}s`;

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            currentIndex = (currentIndex + 1) % roadsOrder.length;
            runSignalCycle();
        }
    }, 1000);
}

function updateSignals(activeRoad) {
    const roads = ["Road1", "Road2", "Road3", "Road4"];

    roads.forEach((road, index) => {
        const roadBox = document.getElementById(`junction-road${index + 1}`);

        if (road === activeRoad) {
            roadBox.style.border = "4px solid #22c55e";
            activateVehicles(`junction-road${index + 1}`);
        } else {
            roadBox.style.border = "2px solid red";
            stopVehicles(`junction-road${index + 1}`);
        }
    });
}

function updateLaneStatuses(activeRoad) {
    const roads = ["Road1", "Road2", "Road3", "Road4"];

    roads.forEach((road) => {
        const statusEl = document.getElementById(`status-${road}`);
        const laneCard = document.getElementById(`lane-card-${road}`);
        const miniRoad = document.getElementById(`mini-road-${road}`);

        laneCard.classList.remove("priority");

        if (road === activeRoad) {
            statusEl.innerText = "GREEN";
            statusEl.className = "signal-badge green";
            laneCard.classList.add("priority");
            activateMiniVehicles(miniRoad);
        } else {
            statusEl.innerText = "RED";
            statusEl.className = "signal-badge red";
            stopMiniVehicles(miniRoad);
        }
    });
}

function activateVehicles(roadId) {
    const vehicles = document.querySelectorAll(`#${roadId} .vehicle`);
    vehicles.forEach(v => v.style.animationPlayState = "running");
}

function stopVehicles(roadId) {
    const vehicles = document.querySelectorAll(`#${roadId} .vehicle`);
    vehicles.forEach(v => v.style.animationPlayState = "paused");
}

function activateMiniVehicles(container) {
    const vehicles = container.querySelectorAll(".mini-vehicle");
    vehicles.forEach(v => v.style.animationPlayState = "running");
}

function stopMiniVehicles(container) {
    const vehicles = container.querySelectorAll(".mini-vehicle");
    vehicles.forEach(v => v.style.animationPlayState = "paused");
}
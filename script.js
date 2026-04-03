document.addEventListener("DOMContentLoaded", () => {

const BASE_URL = "http://127.0.0.1:8000";

let rewardHistory = [];
let prevState = null;
let autoRunning = false;

const ctx = document.getElementById("rewardChart").getContext("2d");

const rewardChart = new Chart(ctx, {
  type: "bar",
  data: {
    labels: [],
    datasets: [{
      label: "Reward",
      data: [],
      backgroundColor: "rgba(59, 130, 246, 0.7)",
      borderRadius: 8
    }]
  },
  options: {
    animation: false,
    responsive: true,
    plugins: {
      legend: { display: true }
    },
    scales: {
      y: { beginAtZero: false }
    }
  }
});

window.resetEnv = async function () {
  stopAuto();

  const task = document.getElementById("taskSelect").value;
  const res = await fetch(`${BASE_URL}/reset?task_id=${task}`, { method: "POST" });
  const data = await res.json();

  rewardHistory = [];
  prevState = null;

  rewardChart.data.labels = [];
  rewardChart.data.datasets[0].data = [];
  rewardChart.update('none');

  updateUI(data.state, 0, {});
};

window.takeStep = async function (action) {
  const res = await fetch(`${BASE_URL}/step`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({action})
  });

  const data = await res.json();
  updateUI(data.state, data.reward, data.info);

  if (data.state.done) {
    stopAuto();
  }
};

function chooseBestAction(state) {
  let decision = "";

  if (state.emergency_lane) {
    decision = `Emergency in Lane ${state.emergency_lane}`;
    document.getElementById("aiDecision").textContent = decision;
    return state.emergency_lane;
  }

  const lanes = {
    1: state.lane_1_cars,
    2: state.lane_2_cars,
    3: state.lane_3_cars
  };

  const best = Object.keys(lanes).reduce((a, b) => lanes[a] > lanes[b] ? a : b);
  decision = `Priority to Lane ${best} (highest traffic)`;
  document.getElementById("aiDecision").textContent = decision;

  return Number(best);
}

window.startAuto = async function () {
  if (!prevState || autoRunning) return;

  autoRunning = true;

  while (autoRunning && prevState)  {
    const bestAction = chooseBestAction(prevState);
    await takeStep(bestAction);

    await new Promise(resolve => setTimeout(resolve, 900)); // smooth delay
  }
};

window.stopAuto = function () {
  autoRunning = false;
};

function updateUI(state, reward, info) {

  if (prevState && JSON.stringify(prevState) === JSON.stringify(state)) return;
  prevState = JSON.parse(JSON.stringify(state));

  document.getElementById("lane1Cars").textContent = state.lane_1_cars;
  document.getElementById("lane2Cars").textContent = state.lane_2_cars;
  document.getElementById("lane3Cars").textContent = state.lane_3_cars;

  document.getElementById("currentSignal").textContent = `Lane ${state.current_signal}`;
  document.getElementById("stepCount").textContent = `${state.step_count} / ${state.max_steps}`;
  document.getElementById("rewardBox").textContent = Number(reward).toFixed(2);
  document.getElementById("totalWaitingTop").textContent =
    state.lane_1_cars + state.lane_2_cars + state.lane_3_cars;

  document.getElementById("emergencyLane").textContent =
    state.emergency_lane ? `Lane ${state.emergency_lane}` : "None";

  for (let i = 1; i <= 3; i++) {
    const lane = document.getElementById(`lane${i}`);
    const count = state[`lane_${i}_cars`];
    const status = document.getElementById(`lane${i}Status`);
    const em = document.getElementById(`em${i}`);

    lane.classList.remove("traffic-low","traffic-medium","traffic-high","active-signal","emergency-highlight");

    if (count <= 6) {
      lane.classList.add("traffic-low");
      status.textContent = "Low Traffic";
    } else if (count <= 12) {
      lane.classList.add("traffic-medium");
      status.textContent = "Moderate Traffic";
    } else {
      lane.classList.add("traffic-high");
      status.textContent = "High Traffic";
    }

    if (state.current_signal === i) {
      lane.classList.add("active-signal");
    }

    if (state.emergency_lane === i) {
      em.classList.remove("hidden");
      lane.classList.add("emergency-highlight");
    } else {
      em.classList.add("hidden");
    }
  }

  rewardHistory.push(reward);
  rewardChart.data.labels = rewardHistory.map((_,i)=>i+1);
  rewardChart.data.datasets[0].data = rewardHistory;
  rewardChart.update('none');
}

});
const dashboard = new PowerSnifferDashboard();
const startedAt = Date.now();

function simulateMeasurements() {
  const now = Date.now();
  const elapsedSeconds = (now - startedAt) / 1000;

  // 20 seconds idle, 60 seconds connected, 10 seconds idle.
  const phase = elapsedSeconds % 90;
  const connected = phase >= 20 && phase < 80;

  let voltage = 0;
  let current = 0;

  if (connected) {
    const loadSeconds = phase - 20;

    // Startup spike, then several distinct consumption levels.
    const baseCurrent =
      loadSeconds < 2 ? 1.8 :
      loadSeconds < 20 ? 0.7 :
      loadSeconds < 40 ? 1.2 : 0.9;

    current = baseCurrent + (Math.random() - 0.5) * 0.08;
    voltage = 5.1 - current * 0.1;
  }

  // Battery is measured even when the load is disconnected.
  const batteryVoltage =
    4.05 - current * 0.15 + (Math.random() - 0.5) * 0.02;

  dashboard.addLiveMeasurement({
    type: "voltage",
    date: now,
    value: voltage
  });

  dashboard.addLiveMeasurement({
    type: "current",
    date: now,
    value: current
  });

  dashboard.addLiveMeasurement({
    type: "battery_voltage",
    date: now,
    value: batteryVoltage
  });
}

simulateMeasurements();
setInterval(simulateMeasurements, 1000);
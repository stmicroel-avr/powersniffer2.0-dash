class PowerSnifferDashboard extends EventTarget {
  constructor() {
    super();

    this.windowMs = 5 * 60 * 1000;
    this.latestTime = Date.now();

    this.liveInput = document.getElementById("live");
    this.feed = document.getElementById("incoming-data");
    this.rangeFrom = document.getElementById('range-from');
    this.rangeTo = document.getElementById('range-to');
    this.rangeGroup = document.getElementsByName('time-range');

    this.metrics = {
      voltage: {
        chartId: "load-voltage-chart",
        outputId: "load-voltage",
        label: "Voltage",
        unit: "V",
        color: "#357fc2"
      },
      current: {
        chartId: "load-current-chart",
        outputId: "load-current",
        label: "Current",
        unit: "A",
        color: "#a97a22"
      },
      battery_voltage: {
        chartId: "battery-voltage-chart",
        outputId: "battery-voltage",
        label: "Battery",
        unit: "V",
        color: "#328365"
      }
    };

    for (const metric of Object.values(this.metrics)) {
      metric.points = [];
      metric.value = 0;
      metric.output = document.getElementById(metric.outputId);
      metric.chart = echarts.init(
        document.getElementById(metric.chartId)
      );

      metric.chart.setOption({
        animation: false,
        grid: {
          left: 50,
          right: 20,
          top: 15,
          bottom: 30
        },
        tooltip: {
          trigger: "axis"
        },
        xAxis: {
          type: "time"
        },
        yAxis: {
          type: "value",
          min: 0
        },
        series: [{
          type: "line",
          showSymbol: false,
          lineStyle: {
            width: 2
          },
          itemStyle: {
            color: metric.color
          },
          data: []
        }]
      });
    }

    this.addEventListeners();
    this.renderCharts();
  }

  initRange() {
    this.setRange(15);
  }

  addEventListeners() {
    this.liveInput.addEventListener("change", () => {
      if (this.liveInput.checked) {
        this.renderCharts();
      }
    });

    this
        .rangeGroup
        .forEach((el) => el.addEventListener(
            'click',
            (el) => this.setRange(el.target.value)
        ));

    window.addEventListener("resize", () => {
      for (const metric of Object.values(this.metrics)) {
        metric.chart.resize();
      }
    });

    this.rangeFrom.addEventListener("change", () => this.applyRange());
    this.rangeTo.addEventListener("change", () => this.applyRange());
  }

  addMeasurement({ type, date, value }) {
    const metric = this.metrics[type];

    if (!metric) return;

    const timestamp = new Date(date).getTime();

    if (!Number.isFinite(timestamp) || !Number.isFinite(value)) return;

    metric.value = value;
    metric.points.push([timestamp, value]);
    metric.output.textContent = value.toFixed(2);

    this.latestTime = Math.max(this.latestTime, timestamp);

    // Keep only the visible five-minute window in memory.
    const cutoff = this.latestTime - this.windowMs;

    for (const item of Object.values(this.metrics)) {
      while (item.points.length && item.points[0][0] < cutoff) {
        item.points.shift();
      }
    }

    this.updateLoadStatus();
    this.addFeedItem(metric, timestamp, value);

    if (this.liveInput.checked) {
      this.renderCharts();
    }
  }

  renderCharts() {
    const from = this.latestTime - this.windowMs;
    const to = this.latestTime;

    for (const metric of Object.values(this.metrics)) {
      metric.chart.setOption({
        xAxis: {
          min: from,
          max: to
        },
        series: [{
          data: metric.points.slice()
        }]
      });
    }

    document.getElementById("selected-range").textContent =
      `${new Date(from).toLocaleString()} — ${new Date(to).toLocaleString()}`;
  }

  updateLoadStatus() {
    const connected =
      this.metrics.voltage.value !== 0 ||
      this.metrics.current.value !== 0;

    const status = document.getElementById("load-status");

    status.textContent = connected ? "Connected" : "Disconnected";
    status.classList.toggle("text-bg-success", connected);
    status.classList.toggle("text-bg-secondary", !connected);
  }

  addFeedItem(metric, timestamp, value) {
    const item = document.createElement("li");

    item.className = "list-group-item small";
    item.textContent =
      `${new Date(timestamp).toLocaleTimeString()} · ` +
      `${metric.label}: ${value.toFixed(2)} ${metric.unit}`;

    this.feed.prepend(item);

    while (this.feed.children.length > 50) {
      this.feed.lastElementChild.remove();
    }
  }

  setRange(minutes) {
    const to = new Date();
    const from = new Date(to.getTime() - (1000 * 60 * minutes));
    this.rangeTo.value =
        `${to.getFullYear()}-${String(to.getMonth()+1).padStart(2,"0")}-${String(to.getDate()).padStart(2,"0")}` +
        `T${String(to.getHours()).padStart(2, "0")}:${String(to.getMinutes()).padStart(2, "0")}`;
    this.rangeFrom.value =
        `${from.getFullYear()}-${String(from.getMonth()+1).padStart(2,"0")}-${String(from.getDate()).padStart(2,"0")}` +
        `T${String(from.getHours()).padStart(2, "0")}:${String(from.getMinutes()).padStart(2, "0")}`;
    this.applyRange();
  }

  applyRange() {
    this.dispatchEvent(new CustomEvent("rangechange", {
      detail: {
        from: this.rangeFrom.value,
        to: this.rangeTo.value
      },
    }));
  }
}
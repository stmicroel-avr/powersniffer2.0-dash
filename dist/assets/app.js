const dashboard = new PowerSnifferDashboard();
dashboard.addEventListener('rangechange', (data) => console.log(data));
dashboard.initRange();
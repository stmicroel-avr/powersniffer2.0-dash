const load = (params) => {
    console.log(params);
    fetch(`api/v1/measurements/v?date_from=${params?.from}&date_to=${params.to}`)
        .then((response) => response.json())
        .then((payload) => console.log(payload));
};

const dashboard = new PowerSnifferDashboard();
dashboard.addEventListener('rangechange', (e) => load(e.detail));
dashboard.initRange();
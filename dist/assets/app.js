const load = (params) => {
    console.log(params);
    fetch(`api/v1/measurements/v?date_from=${params?.from}&date_to=${params.to}`)
        .then((response) => console.log(response.json()));
};

const dashboard = new PowerSnifferDashboard();
dashboard.addEventListener('rangechange', (e) => load(e.detail));
dashboard.initRange();
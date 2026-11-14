const dashboard = new PowerSnifferDashboard();
const load = (params) => {
    const measurements = {
        'v': 'voltage',
        'a': 'current',
        'vcc': 'battery_voltage',
    };

    for(let key in measurements) {
        if (key === undefined) {
            continue;
        }
        fetch(`api/v1/measurements/v?date_from=${params?.from}&date_to=${params.to}`)
            .then((response) => response.json())
            .then((payload) => updateMeasurements(measurements[key], payload?.items));
    }
};
const updateMeasurements = (type, items) => {
    if(!items || !Array.isArray(items)) {
        console.error('Items is not exists or not iterable');
        return;
    }

    items.forEach((item) => console.log(item));
};

dashboard.addEventListener('rangechange', (e) => load(e.detail));
dashboard.initRange();
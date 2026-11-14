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
        fetch(`api/v1/measurements/${key}?date_from=${params?.from}&date_to=${params.to}`)
            .then((response) => response.json())
            .then((payload) => updateMeasurements(measurements[key], payload?.items));
    }
};
const updateMeasurements = (type, items) => {
    if(!items || !Array.isArray(items)) {
        console.error('Items is not exists or not iterable');
        return;
    }

    items = items.map((item) => {
        return {
            type: type,
            date: new Date(item?.timestamp),
            value: item?.value,
        };
    });

    dashboard.setMeasurements(type, items);
};

const ws_init = () => {
    let ws = new WebSocket('/ws');
    ws.addEventListener(
        "message",
        (e) => {
            try {
                const json = JSON.parse(e.data);
                console.log(`Message from server ${json?.msg ? json.msg : json}`);
            } catch (e) {
                console.log("Error parsing msg. Original from server", e.data);
            }

        }
    );
};

dashboard.addEventListener('rangechange', (e) => load(e.detail));
dashboard.initRange();
ws_init();
from dataclasses import dataclass

from powersniffer.models.measurement import Measurement


@dataclass
class MeasurementValueConverter:
    measurement: Measurement

    def resolve_value(self) -> float:
        match self.measurement.unit.lower():
            case 'vcc':
                return self.measurement.value / 1000
            case 'v':
                return self.measurement.value / 1000
            case 'a':
                return self.measurement.value / 1000
            case _:
                raise NotImplementedError

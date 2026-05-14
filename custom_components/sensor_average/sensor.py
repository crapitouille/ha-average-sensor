"""Plateforme sensor pour WattKeeper - Sensor Average."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_SOURCE_SENSOR, DOMAIN
from .coordinator import SensorAverageCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Crée l'entité capteur à partir de la config entry."""
    coordinator: SensorAverageCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SensorAverageEntity(coordinator, entry)], update_before_add=True)


class SensorAverageEntity(CoordinatorEntity[SensorAverageCoordinator], SensorEntity):
    """Capteur qui expose la moyenne glissante d'un capteur source."""

    _attr_has_entity_name = True
    _attr_name = "Average"

    def __init__(
        self,
        coordinator: SensorAverageCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialise l'entité."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_average"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Sensor Average — {entry.data[CONF_SOURCE_SENSOR]}",
            manufacturer="WattKeeper",
            model="Sensor Average",
        )

    @property
    def native_value(self) -> float | None:
        """Valeur principale : la moyenne arrondie à 2 décimales."""
        if self.coordinator.data is None:
            return None
        return round(self.coordinator.data["average"], 2)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Hérite l'unité du capteur source."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("unit_of_measurement")

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Hérite la device_class du capteur source si disponible."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get("device_class")
        try:
            return SensorDeviceClass(raw) if raw else None
        except ValueError:
            return None

    @property
    def state_class(self) -> SensorStateClass:
        """Toujours MEASUREMENT pour permettre les statistiques long-terme."""
        return SensorStateClass.MEASUREMENT

    @property
    def extra_state_attributes(self) -> dict:
        """Attributs supplémentaires exposés dans l'UI."""
        if self.coordinator.data is None:
            return {}
        return {
            "source_sensor": self._entry.data[CONF_SOURCE_SENSOR],
            "last_value": self.coordinator.data.get("last_value"),
            "sample_count": self.coordinator.data.get("sample_count"),
        }

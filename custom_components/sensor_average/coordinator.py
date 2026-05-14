"""DataUpdateCoordinator for WattKeeper - Sensor Average."""
from __future__ import annotations

import logging
from collections import deque
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_FREQUENCY,
    CONF_SOURCE_SENSOR,
    DEFAULT_FREQUENCY,
    DOMAIN,
    MAX_HISTORY_SIZE,
)

_LOGGER = logging.getLogger(__name__)


class SensorAverageCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator qui collecte les valeurs d'un capteur source et calcule leur moyenne."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialise le coordinator."""
        self._entry = entry

        # La fréquence peut venir des options (modifiées après coup) ou des data initiales
        frequency: int = int(
            entry.options.get(
                CONF_FREQUENCY,
                entry.data.get(CONF_FREQUENCY, DEFAULT_FREQUENCY),
            )
        )

        # Historique glissant : on conserve au maximum MAX_HISTORY_SIZE valeurs
        self._history: deque[float] = deque(maxlen=MAX_HISTORY_SIZE)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.data[CONF_SOURCE_SENSOR]}",
            update_interval=timedelta(minutes=frequency),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Lit la valeur du capteur source et met à jour la moyenne glissante."""
        source_entity_id: str = self._entry.data[CONF_SOURCE_SENSOR]
        state = self.hass.states.get(source_entity_id)

        if state is None:
            raise UpdateFailed(
                f"Le capteur source '{source_entity_id}' est introuvable."
            )

        if state.state in ("unavailable", "unknown", None):
            raise UpdateFailed(
                f"Le capteur source '{source_entity_id}' est dans l'état : {state.state}."
            )

        try:
            value = float(state.state)
        except (ValueError, TypeError) as err:
            raise UpdateFailed(
                f"Impossible de convertir la valeur '{state.state}' en nombre : {err}"
            ) from err

        self._history.append(value)
        average = sum(self._history) / len(self._history)

        return {
            "average": round(average, 4),
            "last_value": value,
            "sample_count": len(self._history),
            "unit_of_measurement": state.attributes.get("unit_of_measurement"),
            "device_class": state.attributes.get("device_class"),
        }

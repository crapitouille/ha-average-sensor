"""Config flow et Options flow pour WattKeeper - Sensor Average."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import CONF_FREQUENCY, CONF_SOURCE_SENSOR, DEFAULT_FREQUENCY, DOMAIN


def _frequency_selector() -> selector.NumberSelector:
    """Retourne un sélecteur numérique pour la fréquence en minutes."""
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=1,
            max=1440,
            step=1,
            mode=selector.NumberSelectorMode.BOX,
            unit_of_measurement="min",
        )
    )


class SensorAverageConfigFlow(ConfigFlow, domain=DOMAIN):
    """Gère le flux de configuration initial depuis l'interface graphique."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Étape principale : l'utilisateur choisit le capteur source et la fréquence."""
        errors: dict[str, str] = {}

        if user_input is not None:
            source_entity_id: str = user_input[CONF_SOURCE_SENSOR]

            # Vérification que le capteur source existe bien dans HA
            state = self.hass.states.get(source_entity_id)
            if state is None:
                errors[CONF_SOURCE_SENSOR] = "sensor_not_found"
            else:
                # Unicité : un seul suivi par capteur source
                await self.async_set_unique_id(source_entity_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Average — {source_entity_id}",
                    data={
                        CONF_SOURCE_SENSOR: source_entity_id,
                        CONF_FREQUENCY: int(user_input[CONF_FREQUENCY]),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_SOURCE_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),
                vol.Required(CONF_FREQUENCY, default=DEFAULT_FREQUENCY): _frequency_selector(),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> SensorAverageOptionsFlow:
        """Retourne le flux d'options (modification de la fréquence après configuration)."""
        return SensorAverageOptionsFlow()


class SensorAverageOptionsFlow(OptionsFlow):
    """Permet de modifier la fréquence après l'ajout initial de l'intégration."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Étape unique : modifier la fréquence de mise à jour."""
        if user_input is not None:
            return self.async_create_entry(
                data={CONF_FREQUENCY: int(user_input[CONF_FREQUENCY])}
            )

        # Valeur actuelle : options > data initiales > défaut
        current_frequency: int = int(
            self.config_entry.options.get(
                CONF_FREQUENCY,
                self.config_entry.data.get(CONF_FREQUENCY, DEFAULT_FREQUENCY),
            )
        )

        schema = vol.Schema(
            {
                vol.Required(CONF_FREQUENCY, default=current_frequency): _frequency_selector(),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )

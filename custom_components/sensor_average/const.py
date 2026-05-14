"""Constants for the WattKeeper - Sensor Average integration."""

DOMAIN = "sensor_average"

CONF_SOURCE_SENSOR = "source_sensor"
CONF_FREQUENCY = "frequency"

DEFAULT_FREQUENCY = 1  # minutes

# Nombre maximum de valeurs conservées pour le calcul de la moyenne glissante
MAX_HISTORY_SIZE = 1440  # 24h à 1 mesure/minute

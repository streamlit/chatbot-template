import paho.mqtt.client as mqtt
from app.config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC_PREFIX, get_logger

logger = get_logger(__name__)

def publish_command(device: str, command: str):
    """
    Publishes a command to a specific MQTT topic.

    Args:
        device (str): The device to control (e.g., 'light', 'ac').
        command (str): The command to send (e.g., 'ON', 'OFF', '25').
    """
    topic = f"{MQTT_TOPIC_PREFIX}/{device}/command"
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(topic, command)
        client.disconnect()
        logger.info(f"Published to MQTT topic '{topic}' with message: '{command}'")
        return True
    except Exception as e:
        logger.error(f"Failed to publish to MQTT topic '{topic}': {e}", exc_info=True)
        return False

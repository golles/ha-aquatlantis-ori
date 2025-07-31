"""Test helpers."""

from typing import Any
from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant

from aquatlantis_ori import Device, DynamicModeType, LightType, ModeType, PowerType, SensorType, SensorValidType
from aquatlantis_ori.http.models import LatestFirmwareResponseData, ListAllDevicesResponseDevice
from aquatlantis_ori.mqtt.models import MQTTRetrievePayloadParam


def check_state_value(hass: HomeAssistant, entity_id: str, expected_state: str | None, attributes: dict[str, Any] | None = None) -> None:
    """Helper function to check the state of an entity."""
    state = hass.states.get(entity_id)
    assert state, f"State for {entity_id} not found"
    assert state.state == expected_state
    if attributes is not None:
        for attr, value in attributes.items():
            assert state.attributes.get(attr) == value, f"Attribute {attr} for {entity_id} is {state.attributes.get(attr)}, expected {value}"


def create_test_device(data: dict[str, Any] | None = None) -> Device:
    """Create a test device with sensible defaults.

    Note that raw keys and values need to be provided, as the Device will parse them.
    """
    if data is None:
        data = {}

    device = Device(
        MagicMock(),
        ListAllDevicesResponseDevice(
            id=data.get("device_id", "device123"),
            brand=data.get("brand", "Aquatlantis"),
            name=data.get("name", "Test Device"),
            status=data.get("status", 1),
            picture=data.get("picture"),
            pkey=data.get("pkey", "testpkey"),
            pid=data.get("pid", 0),
            subid=data.get("subid", 0),
            devid=data.get("devid", "testdevid"),
            mac=data.get("mac", "00:11:22:33:44:55"),
            bluetoothMac=data.get("bluetoothMac", "00:11:22:33:44:66"),
            extend=data.get("extend"),
            param=None,
            version=None,
            enable=data.get("enable", True),
            clientid=data.get("clientid", "client123"),
            username=data.get("username", "testuser"),
            ip=data.get("ip", "192.168.1.100"),
            port=data.get("port", 8080),
            onlineTime=data.get("onlineTime", "1719400000000"),
            offlineTime=data.get("offlineTime", "1719500000000"),
            offlineReason=data.get("offlineReason"),
            userid=None,
            icon=None,
            groupName=data.get("groupName", "Test Group"),
            groupId=data.get("groupId", 1),
            creator=data.get("creator", "creator123"),
            createTime=data.get("createTime", "2023-01-01 12:00:00"),
            updateTime=data.get("updateTime", "2023-01-02 12:00:00"),
            appNotiEnable=data.get("appNotiEnable", False),
            emailNotiEnable=data.get("emailNotiEnable", False),
            notiEmail=data.get("notiEmail"),
            isShow=None,
            bindDevices=[],
        ),
    )

    device.update_firmware_data(
        LatestFirmwareResponseData(
            id=data.get("id", "firmware123"),
            brand=data.get("brand", "Aquatlantis"),
            pkey=data.get("pkey", "testpkey"),
            subid=data.get("subid"),
            firmwareVersion=data.get("firmwareVersion", 10),
            firmwareName=data.get("firmwareName", "testpkey_V10.bin"),
            firmwarePath=data.get("firmwarePath", "https://example.com/testpkey_V10.bin"),
        )
    )

    # Update device with MQTT data
    device.update_mqtt_data(
        MQTTRetrievePayloadParam(
            timeoffset=data.get("timeoffset", "3600"),
            rssi=data.get("rssi", -70),
            device_time=data.get("device_time", 1719400000000),
            version=data.get("version", "10"),
            ssid=data.get("ssid", "TestWiFi"),
            ip=data.get("ip", "192.168.1.100"),
            intensity=data.get("intensity", 80),
            custom1=data.get("custom1", [75, 255, 128, 64, 200]),
            custom2=data.get("custom2", [50, 200, 100, 50, 150]),
            custom3=data.get("custom3"),
            custom4=data.get("custom4"),
            timecurve=data.get("timecurve", [2, 8, 0, 50, 10, 20, 30, 40, 18, 30, 80, 60, 70, 80, 90]),
            preview=data.get("preview", 0),
            light_type=data.get("light_type", LightType.RGBW_ULTRA.value),
            dynamic_mode=data.get("dynamic_mode", DynamicModeType.OFF.value),
            mode=data.get("mode", ModeType.MANUAL.value),
            power=data.get("power", PowerType.ON.value),
            sensor_type=data.get("sensor_type", SensorType.TEMPERATURE.value),
            water_temp=data.get("water_temp", 250),
            sensor_valid=data.get("sensor_valid", SensorValidType.VALID.value),
            water_temp_thrd=data.get("water_temp_thrd", [200, 300]),
            air_temp_thrd=data.get("air_temp_thrd", [150, 250]),
            air_humi_thrd=data.get("air_humi_thrd"),
            ch1brt=data.get("ch1brt", 10),
            ch2brt=data.get("ch2brt", 20),
            ch3brt=data.get("ch3brt", 30),
            ch4brt=data.get("ch4brt", 40),
        )
    )

    return device

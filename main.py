# Playback for Wärtsilä NTPro 5000 log files
import logging
from environs import Env
from paho.mqtt.client import Client as MQTT
from streamz import Stream

import utils
import NTproLogToDF

from datetime import datetime
from brefv.envelope import Envelope
from brefv.messages.observations.rudder import Rudder
from brefv.messages.observations.rate_of_turn import RateOfTurn
from brefv.messages.observations.heading import Heading
from brefv.messages.observations.ground_velocity import GroundVelocity
from brefv.messages.playback.playback_file import PlaybackOfFile
import json
import threading

# Reading config from environment variables
env = Env()

MQTT_BROKER_HOST = env("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = env.int("MQTT_BROKER_PORT", 1883)
MQTT_CLIENT_ID = env("MQTT_CLIENT_ID", None)
MQTT_TRANSPORT = env("MQTT_TRANSPORT", "tcp")
MQTT_TLS = env.bool("MQTT_TLS", False)
MQTT_USER = env("MQTT_USER", None)
MQTT_PASSWORD = env("MQTT_PASSWORD", None)
MQTT_BASE_TOPIC = env("MQTT_BASE_TOPIC", "/NTpro")

LOG_LEVEL = env.log_level("LOG_LEVEL", logging.DEBUG)

# Setup logger
logging.basicConfig(level=LOG_LEVEL)
LOGGER = logging.getLogger("crowsnest-connector-playback")


def to_mqtt(data):
    """Push data to a mqtt topic"""
    subtopic, envelope = data
    topic = MQTT_BASE_TOPIC + subtopic
    LOGGER.debug("Publishing on %s", topic)
    # LOGGER.debug("Publishing envelope %s", envelope)

    try:
        mq.publish(topic, envelope)
    except Exception as e:  # pylint: disable=broad-except
        print("Failed publishing to broker!", e)


def rudderACT_to_brefv(obj, id):
    """Create rudder angel actual to brefv fromat"""
    rudderAngle = float(obj["value"])

    rud = Rudder(sensor_id=id, angle=utils.corrRuderAngle(rudderAngle))

    envelope = Envelope(
        sent_at=utils.formatTimeToEnvelop(obj["time"]),
        message_type="https://mo-rise.github.io/brefv/0.1.0/messages/observations/rudder.json",
        message=rud.dict(exclude_none=True, exclude_unset=True, exclude_defaults=True),
    )

    return f"/observations/rudder/{id}", envelope.json()  # envelope


def rot_to_brefv(obj, id):
    """Rate of turn to brefv fromat"""
    ROT = float(obj["value"])
    rotVal = RateOfTurn(sensor_id=id, rot=ROT)

    envelope = Envelope(
        sent_at=utils.formatTimeToEnvelop(obj["time"]),
        message_type="https://mo-rise.github.io/brefv/0.1.0/messages/observations/rudder.json",
        message=rotVal.dict(exclude_none=True, exclude_unset=True, exclude_defaults=True),
    )

    return f"/observations/rot/{id}", envelope.json()  # envelope


def heading_to_brefv(obj, id):
    """Heading to brefv fromat"""
    valObj = Heading(sensor_id=id, heading=float(obj["value"]), type="True")

    envelope = Envelope(
        sent_at=utils.formatTimeToEnvelop(obj["time"]),
        message_type="https://mo-rise.github.io/brefv/0.1.0/messages/observations/rudder.json",
        message=valObj.dict(exclude_none=True, exclude_unset=True, exclude_defaults=True),
    )

    return f"/observations/heading/{id}", envelope.json()  # envelope


def ground_velocity_to_brefv(obj, id):
    """Corse over ground to brefv fromat"""
    valObj = GroundVelocity(
        sensor_id=id,
        cog=float(obj["COG"]),
        sog=float(obj["SOG"]),
        sog_transverse_bow=float(obj["Transverse speed at ship's bow"]),
        sog_transverse_stern=float(obj["Transverse speed at ship's stern"]),
    )

    envelope = Envelope(
        sent_at=utils.formatTimeToEnvelop(obj["time"]),
        message_type="https://mo-rise.github.io/brefv/0.1.0/messages/observations/rudder.json",
        message=valObj.dict(exclude_none=True, exclude_unset=True, exclude_defaults=True),
    )

    return f"/observations/ground_velocity/{id}", envelope.json()  # envelope


def playback_state_to_brefv(row):
    """Create playback state to brefv fromat"""
    playbackTimePosition = row["time"]
    timeArr = playbackTimePosition.split(":")
    timelinePosition = (int(timeArr[0]) * 3600) + (int(timeArr[1]) * 60) + (int(timeArr[2]))

    timeStamp = datetime.now().isoformat()

    valObj = PlaybackOfFile(time_stamp=timeStamp, timeline_position=timelinePosition)

    envelope = Envelope(
        sent_at=datetime.now().isoformat(),
        message_type="https://mo-rise.github.io/brefv/0.1.0/messages/observations/rudder.json",
        message=valObj.dict(exclude_none=True, exclude_unset=True, exclude_defaults=True),
    )

    return f"/playback", envelope.json()


def playback_init_to_brefv(data):
    """Create playback state to brefv fromat"""

    valObj = PlaybackOfFile(duration=data['duration'], is_playing=data['isPlaying'])

    envelope = Envelope(
        sent_at=datetime.now().isoformat(),
        message_type="https://mo-rise.github.io/brefv/0.1.0/messages/observations/rudder.json",
        message=valObj.dict(exclude_none=True, exclude_unset=True, exclude_defaults=True),
    )

    return f"/playback", envelope.json()


def on_message(client, userdata, message):
    global isPlaying
    global pointer
    msg = message.payload.decode("utf-8")

    payload = json.loads(msg)

    if "actionPlay" in payload:
        action = payload["actionPlay"]
        if action == "start":
            isPlaying = True
        else:
            isPlaying = False

        print("isPlaying", isPlaying)
    elif "timeLinePos" in payload:
        actionValue = payload["timeLinePos"]
        pointer = actionValue


def threadMQTT():
    mq.loop_forever()


def columnSelector(row, columnName):
    value = row[columnName]
    time = row["time"]
    return {"value": value, "time": time}


def columnSelectorMulti(row, columnNameList):
    parameters = {}
    for column in columnNameList:
        parameters[column] = row[column]
    parameters["time"] = row["time"]
    return parameters


def main():
    LOGGER.info("Startign playback application...")

    global isPlaying, pointer, mq
    isPlaying = False
    startPointer = 0

    pathToFiles = "data/*"  # glob reader path syntax

    df, metadata = NTproLogToDF.readInNTproFilesFrom(pathToFiles)
    # TODO: Create vessel profiles and utilize file metadata

    ################################################
    # Stream process

    # Init MQTT
    mq = MQTT(client_id=MQTT_CLIENT_ID, transport=MQTT_TRANSPORT)
    mq.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    mq.subscribe("/playback/action")
    mq.on_message = on_message

    # continue MQTT on new thread
    mqttThread = threading.Thread(target=threadMQTT, args=())
    mqttThread.start()

    ###############
    # Playback

    totalTimeStr = df["time"].max()
    durationArr = totalTimeStr.split(":")
    duration = (int(durationArr[0]) * 3600) + (int(durationArr[1]) * 60) + (int(durationArr[2]))  # H + min + sec
    LOGGER.debug("Total simulation duration: %s", duration)

    # Send init playback to MQTT broker
    initMsg = playback_init_to_brefv({"duration": duration, "isPlaying": False})
    to_mqtt(initMsg)

    ###########################################
    # Init STREAM
    entrypoint = Stream()
    start = entrypoint.rate_limit(1)  # send rate

    play = start.map(playback_state_to_brefv).sink(to_mqtt)

    # Rudders
    rudderACTps = (
        start.map(lambda x: columnSelector(x, "Port rudder angle"))
        .unique(maxsize=1, key=lambda x: x["value"])
        .map(lambda x: rudderACT_to_brefv(x, "1"))
        .sink(to_mqtt)
    )
    rudderACTsb = (
        start.map(lambda x: columnSelector(x, "Starboard rudder angle"))
        .unique(maxsize=1, key=lambda x: x["value"])
        .map(lambda x: rudderACT_to_brefv(x, "2"))
        .sink(to_mqtt)
    )

    # ROT
    rot = (
        start.map(lambda x: columnSelector(x, "Rate of turn"))
        .unique(maxsize=1, key=lambda x: x["value"])
        .map(lambda x: rot_to_brefv(x, "1"))
        .sink(to_mqtt)
    )

    # Heading
    heading = (
        start.map(lambda x: columnSelector(x, "Heading"))
        .unique(maxsize=1, key=lambda x: x["value"])
        .map(lambda x: heading_to_brefv(x, "1"))
        .sink(to_mqtt)
    )

    # Ground velocity
    cog = (
        start.map(
            lambda x: columnSelectorMulti(
                x, ["COG", "SOG", "Transverse speed at ship's bow", "Transverse speed at ship's stern"]
            )
        )
        .unique(
            maxsize=1,
            key=lambda x: str(x["COG"])
            + str(x["SOG"])
            + str(x["Transverse speed at ship's bow"])
            + str(x["Transverse speed at ship's stern"]),
        )
        .map(lambda x: ground_velocity_to_brefv(x, "1"))
        .sink(to_mqtt)
    )

    # Player
    indexArr = df.index
    indexSize = len(indexArr)
    pointer = startPointer

    while True:

        if isPlaying == True:
            currentRow = df.loc[indexArr[pointer], :]
            entrypoint.emit(currentRow)
            pointer += 1

            # End of DF start over
            if pointer >= indexSize:
                pointer = indexArr[0]


if __name__ == "__main__":
    main()

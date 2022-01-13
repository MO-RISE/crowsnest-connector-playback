# Playback for Wärtsilä NTPro 5000 log files
import logging
from environs import Env
from paho.mqtt.client import Client as MQTT
from streamz import Stream
import glob
import pandas as pd
import utils
from pandasgui import show  # Debug
import asyncio
from datetime import datetime
from brefv.envelope import Envelope
from brefv.messages.observations.rudder import Rudder

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


async def to_mqtt(data):
    """Push data to a mqtt topic"""
    subtopic, envelope = data
    topic = MQTT_BASE_TOPIC + subtopic
    # topic = f"{MQTT_BASE_TOPIC}"
    # topic = "NTpro"
    LOGGER.debug("Publishing on %s", topic)
    LOGGER.debug("Publishing envelope %s", envelope)

    try:
        mq.publish(topic, envelope)
    except Exception as e:  # pylint: disable=broad-except
        print("Failed publishing to broker!", e)


def rudder_to_brefv(row):
    """Create rudder brefv fromat"""
    rudderAngle = row["Port rudder angle"]

    rud = Rudder(sensor_id="1", angle=rudderAngle)

    # Setting timestamp to simulation time with current timezone and date
    timeStamp = datetime.now()
    hour = int(row["time"].split(":")[0])
    min = int(row["time"].split(":")[1])
    sec = int(row["time"].split(":")[2])
    timeStamp = timeStamp.replace(hour=hour, minute=min, second=sec)

    envelope = Envelope(
        sent_at=timeStamp.isoformat(),
        message_type="https://mo-rise.github.io/brefv/0.1.0/messages/observations/rudder.json",
        message=rud.dict(exclude_none=True, exclude_unset=True, exclude_defaults=True),
    )

    LOGGER.debug("Envelope:\n%s", envelope)
    return f"/observations/rudder/1", envelope.json()  # envelope


async def main():
    LOGGER.info("Startign playback application...")

    # Read in files from data folder
    files = glob.glob("data/*")

    # Check files inputted
    if len(files) != 4:
        LOGGER.error("Wrong amount of files in data read folder!")
    isFileThere = [False, False, False, False]

    for fileLocation in files:
        LOGGER.debug("Imported file: " + str(fileLocation))

        fileMetadata = utils.getNTproFileMetadata(fileLocation)
        # TODO: Create vessel profiles and utilize file metadata

        # TODO: Crate unit checker for input files
        dfTEMP = pd.read_csv(fileLocation, header=8)
        dfTEMP.drop(0, inplace=True)

        # Dropping columns containing local coordinates
        cols = [c for c in dfTEMP.columns if c.find("Local position") < 0]
        dfTEMP = dfTEMP[cols]

        if fileLocation.find("Log") > 0:
            df_log = dfTEMP
            df_log = df_log.drop(
                columns=[
                    "Heading",
                    "Rate of turn",
                    "Port engine RPM",
                    "Starboard engine RPM",
                    "Port propeller pitch",
                    "Starboard propeller pitch",
                    "Port rudder angle",
                    "Bow thruster gained power",
                    "Stern thruster gained power",
                    "Transverse speed at ship's bow",
                    "Transverse speed at ship's stern",
                ]
            )
            isFileThere[0] = True
        elif fileLocation.find("ShipDynamics") > 0:
            df_dyn = dfTEMP
            df_dyn = df_dyn.drop(columns=["Heading"])
            isFileThere[1] = True
        elif fileLocation.find("Traffic") > 0:
            df_traffic = dfTEMP
            isFileThere[2] = True
        elif fileLocation.find("Forces") > 0:
            df_forces = dfTEMP
            isFileThere[3] = True

    # Check all files found
    if all(isFileThere) == False:
        LOGGER.error(
            "Some of the following files are not found ShipDynamics "
            + str(isFileThere[1])
            + ", Log "
            + str(isFileThere[0])
            + ", Forces "
            + str(isFileThere[3])
            + " or Traffic "
            + str(isFileThere[2])
        )

    # Generating main DF
    df = pd.merge(df_log, df_dyn, how="inner", on="time")
    df = pd.merge(df, df_forces, how="inner", on="time")
    df = pd.merge(df, df_traffic, how="inner", on="time")

    # DF insight / debug window
    # show(df)

    ################################################
    # Stream process

    # Init MQTT
    global mq
    mq = MQTT(client_id=MQTT_CLIENT_ID, transport=MQTT_TRANSPORT)
    mq.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)

    # Init STREAM
    entrypoint = Stream()
    start = entrypoint.rate_limit(1)  # send rate

    start.filter(lambda x: pd.notna(x["Port rudder angle"])).map(rudder_to_brefv).unique(maxsize=1).sink(to_mqtt)

    ###############
    # TODO: Playback actions 
    # totalTime = df["time"].max()
    # LOGGER.debug("Total simulation time: %s", totalTime)
    # # Send init playback to MQTT broker
    # initMsg = "path", {
    #     "totalPlaybackTime": totalTime,
    #     "readyToStart": True,
    # }
    # to_mqtt(initMsg)

    # Pipline flow
    for index, row in df.iterrows():
        entrypoint.emit(row)

    # mq.loop_forever()


if __name__ == "__main__":
    asyncio.run(main())

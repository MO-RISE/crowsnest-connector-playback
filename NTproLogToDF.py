from pandasgui import show  # Debug
import logging
from environs import Env
import glob
import utils
import pandas as pd

env = Env()
LOG_LEVEL = env.log_level("LOG_LEVEL", logging.DEBUG)
logging.basicConfig(level=LOG_LEVEL)
LOGGER = logging.getLogger("NTpro-file-reader")


def readInNTproFilesFrom(pathToFiles):
    """Read in NTpro log fils for one OWN ship with traffic"""

    files = glob.glob("data/*")

    # Check files inputted
    if len(files) != 4:
        LOGGER.error("Wrong amount of files in data read folder!")
    isFileThere = [False, False, False, False]

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

    for fileLocation in files:
        LOGGER.debug("Imported file: " + str(fileLocation))

        fileMetadata = utils.getNTproFileMetadata(fileLocation)

        dfTEMP = pd.read_csv(fileLocation, header=8)

        for column in dfTEMP.columns:

            # Check if files units are in m/s, if convert to knots
            if "meters_per_second" in dfTEMP[[column]].values:
                dfTEMP.loc[1:, column] = pd.to_numeric(dfTEMP.loc[1:, column]) * 1.94384449  # m/s to knots
                print("CONVERT: ", column)

            dfTEMP[column] = pd.to_numeric(dfTEMP[column], downcast="float", errors="ignore")

        dfTEMP.drop(0, inplace=True)  # Dropping units

        # Dropping columns containing local coordinates
        cols = [c for c in dfTEMP.columns if c.find("Local position") < 0]
        dfTEMP = dfTEMP[cols]

        # Files specifc operations
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

    # Generating main DF
    df = pd.merge(df_log, df_dyn, how="inner", on="time")
    df = pd.merge(df, df_forces, how="inner", on="time")
    df = pd.merge(df, df_traffic, how="inner", on="time")

    # DF insight / debug window
    # show(df)

    return df, fileMetadata

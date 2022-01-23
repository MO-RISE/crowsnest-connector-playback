# Crowsnest Playback

**Supporting**

- Wärtsilä NTPro 5000 log files (partly)

## Setup dev env

1. Create python virtual environment
2. Clone brefv to brefv-spec
3. Run:

- datamodel-codegen --input brefv-spec/envelope.json --input-file-type jsonschema --output brefv/envelope.py
- datamodel-codegen --input brefv-spec/messages --input-file-type jsonschema --reuse-model --output brefv/messages

Playback container for NTPro log files. Following brefv message standard.

## Run applcation

1. Insert following log files into the data folder. Keep only active files in the folder.
   - Traffic
   - Log
   - ShipDynamics
   - Forces
2. Build docker image
3. Start docker image

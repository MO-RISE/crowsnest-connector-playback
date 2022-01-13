# Crowsnest Playback 

- Wärtsilä NTPro 5000 log files

## Setup dev env

1. Create python virtual environment
2. Clone brefv to brefv-spec
3. Run:

- datamodel-codegen --input brefv-spec/envelope.json --input-file-type jsonschema --output brefv/envelope.py
- datamodel-codegen --input brefv-spec/messages --input-file-type jsonschema --reuse-model --output brefv/messages

Playback container for NTPro log files. Following brefv message standard.

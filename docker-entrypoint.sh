#!/bin/sh
set -e
if [ -z "$STRUKTON_DATA_ROOT" ] || [ ! -d "$STRUKTON_DATA_ROOT" ]; then
  echo "railai image is ready (headless pipeline, no desktop UI)."
  echo "Mount measurements and run detection:"
  echo "  docker run --rm \\"
  echo "    -v \"\$PWD/data:/data\" \\"
  echo "    -e STRUKTON_DATA_ROOT=/data/Groningen \\"
  echo "    railai"
  python -c "from railai.features import extract_features; from railai.detection import isolation_forest; print('imports ok')"
  exit 0
fi
exec python -m railai "$@"

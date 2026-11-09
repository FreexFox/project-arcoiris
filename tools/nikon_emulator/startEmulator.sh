#!/bin/bash
# startEmulator.sh - Launch the Nikon DSLR Full Hardware / FR80 Emulator GUI

# Convert file arguments to absolute paths before cd
RESOLVED_ARGS=()
for arg in "$@"; do
    if [ -f "$arg" ]; then
        RESOLVED_ARGS+=("$(realpath "$arg")")
    else
        RESOLVED_ARGS+=("$arg")
    fi
done

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Locate Java binary
JAVA_CMD="java"
if ! command -v java &>/dev/null; then
    STEAM_JAVA="/home/inrnbws/.local/share/Steam/steamapps/common/ProjectZomboid/projectzomboid/jre64/bin/java"
    if [ -x "$STEAM_JAVA" ]; then
        JAVA_CMD="$STEAM_JAVA"
    else
        echo "Error: Java runtime not found. Please install JRE (OpenJDK 8+) or ensure java is in PATH."
        exit 1
    fi
fi

echo "Starting Nikon DSLR Hardware / FR80 Emulator using: $JAVA_CMD"

CP="./NikonEmulator.jar:./lib/commons-io-2.1.jar:./lib/commons-lang3-3.1.jar:./lib/xstream-1.4.2.jar:./lib/jacksum.jar:./lib/jgraphx.jar:./lib/rsyntaxtextarea.jar:./lib/miglayout-4.0.jar:./lib/glazedlists-1.8.0_java15.jar"

JAVA_OPTS="--add-opens java.base/java.util=ALL-UNNAMED \
--add-opens java.base/java.util.concurrent=ALL-UNNAMED \
--add-opens java.base/java.lang=ALL-UNNAMED \
--add-opens java.base/java.lang.reflect=ALL-UNNAMED \
--add-opens java.base/java.text=ALL-UNNAMED \
--add-opens java.base/java.io=ALL-UNNAMED \
--add-opens java.base/java.nio=ALL-UNNAMED \
--add-opens java.desktop/java.awt=ALL-UNNAMED \
--add-opens java.desktop/java.awt.font=ALL-UNNAMED \
--add-opens java.desktop/java.awt.image=ALL-UNNAMED \
--add-opens java.desktop/java.awt.color=ALL-UNNAMED \
--add-opens java.desktop/javax.swing=ALL-UNNAMED \
--add-opens java.desktop/javax.swing.plaf=ALL-UNNAMED \
--add-opens jdk.unsupported/sun.misc=ALL-UNNAMED"

exec "$JAVA_CMD" -Xmx1024m $JAVA_OPTS -cp "$CP" com.nikonhacker.gui.EmulatorUI "${RESOLVED_ARGS[@]}"

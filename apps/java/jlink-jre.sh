#!/bin/sh
# Build a stripped JRE 21 for the Spring Boot fat jar (jdeps + jlink).
set -eu
JAR="${1:?usage: jlink-jre.sh <jar> [output-dir]}"
OUT="${2:-/jre}"

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"
jar xf "$JAR"

cp=$(find BOOT-INF/lib -name '*.jar' | paste -sd: -)
deps=$(
  jdeps \
    --ignore-missing-deps \
    --print-module-deps \
    --multi-release 21 \
    --recursive \
    --class-path "$cp" \
    BOOT-INF/classes \
    2>/dev/null | tail -n 1
)

# Modules often loaded reflectively by Spring Boot / Tomcat / TLS.
extra="jdk.unsupported,java.instrument,jdk.crypto.ec,jdk.management,java.security.jgss,java.desktop"

jlink \
  --add-modules "${deps},${extra}" \
  --strip-debug \
  --no-header-files \
  --no-man-pages \
  --compress=2 \
  --output "$OUT"

#!/usr/bin/env bash
# Gera app/src/main/res/font/archivo_bold.ttf — Archivo, peso 700, largura 100 —
# a partir da fonte variável oficial do google/fonts (D-AV36, 26/09/2026).
#
# Por que instância estática: nas APIs 21 a 25 o Android não varia o peso de uma
# fonte variável, e o app só usa a Archivo em títulos, peso 700 (o site e o app da
# VPN usam a Archivo só nos títulos). 121 KB contra 658 KB da variável.
#
# Origem: https://github.com/google/fonts, ofl/archivo/Archivo[wdth,wght].ttf,
# commit 23e54b51ddffbc7713c583748e3bd86f62b1fa4a (main em 26/09/2026), SHA-256
# 0e094a7d3c7c4c25cf1310c4b30014f1dae9332220b1c2c88f4fa996f0b05053
# Licença: SIL Open Font License 1.1, sem nome de fonte reservado (OFL-Archivo.txt,
# ao lado). A instância leva o copyright e a licença nos metadados da própria
# fonte (tabela name, IDs 0, 13 e 14), como a OFL permite.
#
# Reproduzível: com SOURCE_DATE_EPOCH fixo o fontTools grava a mesma data e o
# arquivo sai idêntico (medido em 26/09/2026). Resultado esperado, SHA-256:
# 5401db640c3da2e3600aa2aa72b1b77ab8d41df70981face6d9f8c0c5a195d66
set -euo pipefail
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
curl -sSfL -o "$T/Archivo.ttf" "https://raw.githubusercontent.com/google/fonts/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/archivo/Archivo%5Bwdth,wght%5D.ttf"
echo "0e094a7d3c7c4c25cf1310c4b30014f1dae9332220b1c2c88f4fa996f0b05053  $T/Archivo.ttf" | shasum -a 256 -c -
SOURCE_DATE_EPOCH=1790380800 fonttools varLib.instancer "$T/Archivo.ttf" wght=700 wdth=100 \
  --update-name-table -o "$T/archivo_bold.ttf"
echo "5401db640c3da2e3600aa2aa72b1b77ab8d41df70981face6d9f8c0c5a195d66  $T/archivo_bold.ttf" | shasum -a 256 -c -
cp "$T/archivo_bold.ttf" "$(dirname "$0")/../../app/src/main/res/font/archivo_bold.ttf"

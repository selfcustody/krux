#!/bin/sh

locales=("de-DE" "en-US" "es-MX" "fr-FR" "pt-BR" "vi-VN")
devices=("maixpy_m5stickv" "maixpy_amigo_tft")

rm -rf krux-screenshots

for locale in "${locales[@]}"
do
    for device in "${devices[@]}"
    do
        ./generate-device-screenshots.sh $device $locale
        mkdir -p krux-screenshots/$device/
        cp -r screenshots krux-screenshots/$device/$locale
    done
done

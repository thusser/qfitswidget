cd qfitswidget/qt/
for f in *.ui; do pyuic5 --from-imports ${f} > "${f%.ui}.py"; done

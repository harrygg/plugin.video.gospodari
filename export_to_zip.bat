@ECHO OFF

set Zip_Name=plugin.video.gospodari.zip

ECHO Output filename: %Zip_Name%

ECHO Compressing files
"C:\Program Files\7-Zip\7za" a -tzip %Zip_Name% @build_files.txt -mx5

endlocal
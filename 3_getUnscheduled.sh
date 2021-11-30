fileName=unscheduled-full.txt
pathName=SixRoutesCombined/unscheduled_combine.txt
folderName=/SixRoutesCombined/
destFile=SixRoutesCombined/unscheduled.txt

route1=~/satwik/1_NDLS-MMCT/simulator_input/$fileName
route2=~/satwik/2_NDLS-MAS/simulator_input/$fileName
route3=~/satwik/3_HWH-MAS/simulator_input/$fileName
route4=~/satwik/4_HWH-CSMT/simulator_input/$fileName
route5=~/satwik/5_MASB-CSMT/simulator_input/$fileName
route6=~/satwik/6_NDLS-HWH/simulator_input/$fileName

unschedFile=unscheduled_new.txt
cat $route1 > $unschedFile
tail -n+3 $route2 >> $unschedFile
tail -n+3 $route3 >> $unschedFile
tail -n+3 $route4 >> $unschedFile
tail -n+3 $route5 >> $unschedFile
tail -n+3 $route6 >> $unschedFile

header=$(head -2 $unschedFile)

exit

if test -f $pathName;
then
    backup=unsheduledBackup-$(date +%F-%T)
    mv $pathName $backup
    mv $unschedFile $pathName
    python3 unschedule_generator.py $folderName
    #rm $pathName
    mv $backup $pathName
else
    mv $unschedFile $pathName
    python3 unschedule_generator.py $folderName
    #rm $pathName
fi

echo /*route-enabled*/ > $destFile
echo $header >> $destFile

keepTrainWithMoreHalts.sh unscheduled_combine_new.txt >> $destFile


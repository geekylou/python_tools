#!/bin/bash
# This is adapted from a script I found years ago.
# to run type: ./backup-rsync <source> <dest folder> <backup-id>
# This will create a folder with daily/weekly (as appropriate)
# containing an incremental backup of source.
backup_id="$3"

DAILY_BACKUP_TIME='8'
WEEKLY_BACKUP_DAY='0' # Do our weekly backup on Saturday

mkdir -p /ramtmp/shutdown_locks
touch /ramtmp/shutdown_locks/$backup_id

src="$1"
base="$2"
date=`date "+%Y-%m-%dT%H:%M:%S"`

echo "src: $src"
echo "base: $base"

hour=`date +%H`
day_of_week=`date +%w`

#dest=$base/hourly/backup-$date/files

if [ "$4" = 'daily' ]
then
     dest_base=$base/daily/backup-$date
     dest_tmp=$base/daily/backup-$date-in-progress
     mkdir -p $base/daily
else
     dest_base=$base/manual/backup-$date
     dest_tmp=$base/manual/backup-$date-in-progress
     mkdir -p $base/manual
fi

if [ $day_of_week -eq $WEEKLY_BACKUP_DAY ] && [ "$4" = 'daily' ]
then
   dest_base=$base/weekly/backup-$date
   dest_tmp=$base/weekly/backup-$date-in-progress
   mkdir -p $base/weekly
   #ln -s $base/weekly/backup-$date $base/daily/backup-$date 
   #ln -s $base/weekly/backup-$date $base/hourly/backup-$date
fi

echo 'Backing up to' $dest', starting backup:' $dest_base
echo 'start time'`date`

echo $base/current

rsync -v --numeric-ids --exclude-from $base/backup-exclusions.txt --delete --fake-super -a $src $base/backup/files #2>/ramtmp/backup_output.txt
rsync_ret=$?

echo "Rsync return value" $rsync_ret

if [ $rsync_ret -eq 0 ] || [ $rsync_ret -eq 23 ]
then
  sudo btrfs subvolume snapshot $base/backup $dest_base -r
  rm $base/current
  ln -s $dest_base $base/current
  echo "Backup succeeded"
else
  echo "Backup failed" $dest_tmp $dest_failed 
#  mail -s "[Backup] Failure" "root" </ramtmp/backup_output.txt 
fi
echo "--- backup completed output ---"
cat /ramtmp/backup_output.txt

echo "end time:"`date`

rm /ramtmp/shutdown_locks/$backup_id
rm /ramtmp/shutdown_locks/default

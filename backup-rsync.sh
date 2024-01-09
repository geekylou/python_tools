#!/bin/bash
# This is adapted from a script I found years ago.
# to run type: ./backup-rsync <source> <dest folder> <backup-id>
# This will create a folder with daily/weekly (as appropriate)
# containing an incremental backup of source.
backup_id="$3"

DAILY_BACKUP_TIME='6'
WEEKLY_BACKUP_DAY='6' # Do our weekly backup on Saturday

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

#if [ $hour -eq $DAILY_BACKUP_TIME ]
#then
     dest_base=$base/daily/backup-$date
     dest_tmp=$base/daily/backup-$date-in-progress
#dest_success=$base/daily/backup-$date
#fi

if [ $day_of_week -eq $WEEKLY_BACKUP_DAY ] && [ $hour -eq $DAILY_BACKUP_TIME ]
then
   dest_base=$base/weekly/backup-$date
   dest_tmp=$base/weekly/backup-$date-in-progress
   
   ln -s $base/weekly/backup-$date $base/daily/backup-$date 
   #ln -s $base/weekly/backup-$date $base/hourly/backup-$date
fi

echo 'Backing up to' $dest', starting backup:' $dest_tmp
echo 'start time'`date`

mkdir -p $dest_tmp
rsync --exclude-from ~/backup-exclusions.txt --fake-super  --link-dest=$base/current -a $src $dest_tmp/files 2>/ramtmp/backup_output.txt
rsync_ret=$?

echo "Rsync return value" $rsync_ret

if [ $rsync_ret -eq 0 ] || [ $rsync_ret -eq 23 ]
then
  echo "Backup succeeded"
  dest_success=$dest_base
  mv "$dest_tmp" "$dest_success"
  rm -f $base/current
  ln -s $dest_success/files $base/current
else
  echo "Backup failed" $dest_tmp $dest_failed 
  dest_failed=$dest_base-failed
  mv "$dest_tmp" "$dest_failed"
#  mail -s "[Backup] Failure" "root" </ramtmp/backup_output.txt 
fi
echo "--- backup completed output ---"
cat /ramtmp/backup_output.txt

echo "end time:"`date`

rm /ramtmp/shutdown_locks/$backup_id
rm /ramtmp/shutdown_locks/default

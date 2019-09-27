#! /bin/bash

tmpdir=$1
jplag_dir=$2
lang=$3
home="$(dirname "$0")"

mkdir $tmpdir/workdir
mkdir $tmpdir/workdir/course
mkdir $tmpdir/workdir/submissions
tar -zxf $tmpdir/input/course.tgz -C $tmpdir/workdir/course > /dev/null 2> /dev/null
tar -zxf $tmpdir/input/submissions.tgz -C $tmpdir/workdir/submissions > /dev/null 2> /dev/null

# Verify that the task exists
taskid=$(cat $tmpdir/input/task.txt)
if [ ! -e "$tmpdir/workdir/course/$taskid" ]
then
    >&2 echo "Task id $taskid not found in course"
    exit 1
fi
if [ ! -e "$tmpdir/workdir/submissions/$taskid" ]
then
    >&2 echo "Task id $taskid not found in submissions"
    exit 1
fi

# Extract the archives
find $tmpdir/workdir/submissions/$taskid -iname \*.zip | sed -e 's/^\(.*\)\(\.zip\)$/"\1.zip" -d "\1"/' | xargs -n 3 unzip > /dev/null 2> /dev/null

# Copy the submissions to a proper location
mkdir $tmpdir/todo
for userdir in `find $tmpdir/workdir/submissions/$taskid/ -mindepth 1 -maxdepth 1 -type d`
do
    username=${userdir#"$tmpdir/workdir/submissions/$taskid/"}
    mkdir "$tmpdir/todo/$username/"
    cp -R $tmpdir/workdir/submissions/$taskid/$username/*/archive/* $tmpdir/todo/$username/
    cp -R $tmpdir/workdir/submissions/$taskid/$username/*/uploaded_files/* $tmpdir/todo/$username/
    cp $tmpdir/workdir/submissions/$taskid/$username/*/submission.test $tmpdir/todo/$username/
    python3.5 $home/write_code.py $tmpdir/todo/$username/
    echo $PWD
    rm -f $tmpdir/todo/$username/__feedback.json > /dev/null 2> /dev/null
done

# Parse the language
if [ -e "$tmpdir/workdir/course/$taskid/jplag_lang.txt" ]
then
    lang=$(cat "$tmpdir/workdir/course/$taskid/jplag_lang.txt")
fi
if [ -s "$tmpdir/input/lang.txt" ]
then
    lang=$(cat "$tmpdir/input/lang.txt")
fi

# Parse the basic arguments
jplag_args="-s -l $lang"

# Base code
basecodedir=""
if [ -e "$tmpdir/workdir/course/$taskid/jplag_basecode" ]
then
    basecodedir="$tmpdir/workdir/course/$taskid/jlang_basecode"
    jplag_args="$jplag_args -bc jplag_basecode"
    cp -R $basecodedir $tmpdir/todo/jplag_basecode
fi
if [ -s "$tmpdir/input/template.txt" ]
then
    basecodedir=$(cat "$tmpdir/input/template.txt")
    basecodedir="$tmpdir/workdir/course/$basecodedir"
    jplag_args="$jplag_args -bc jplag_basecode"
    cp -R $basecodedir $tmpdir/todo/jplag_basecode
fi

# Add the exclude file if it exists
if [ -e "$tmpdir/workdir/course/$taskid/jplag_exclude.txt" ]
then
    jplag_args="$jplag_args -x $tmpdir/workdir/course/$taskid/jplag_exclude.txt"
fi

# If there are additionnal arguments, add them
if [ -s "$tmpdir/input/args.txt" ]
then
    add_arg=$(cat $tmpdir/input/args.txt)
    jplag_args="$jplag_args $add_arg"
fi

# Verify the presence of old_submissions
if [ -s "$tmpdir/input/old_submissions.tgz" ]
then
    # It exists, untar it
    mkdir $tmpdir/workdir/old_submissions
    tar -zxf $tmpdir/input/old_submissions.tgz -C $tmpdir/workdir/old_submissions > /dev/null 2> /dev/null
    if [ $? -ne 0 ]; then
        >&2 echo "Unable to untar the old submission archive"
        exit 1
    fi

    # Check the format of the archive
    if [ -e "$tmpdir/workdir/old_submissions/$taskid" ] #INGInious format
    then
        for userdir in `find $tmpdir/workdir/old_submissions/$taskid/ -mindepth 1 -maxdepth 1 -type d`
        do
            username=${userdir#"$tmpdir/workdir/old_submissions/$taskid/"}
            mkdir "$tmpdir/todo/old-$username/"
            cp -R $tmpdir/workdir/old_submissions/$taskid/$username/*/archive/* $tmpdir/todo/old-$username/
            # drop __feedback.json, not needed here
            rm -f $tmpdir/todo/old-$username/__feedback.json > /dev/null 2> /dev/null
        done
    else #compat format
        for userdir in `find $tmpdir/workdir/old_submissions -mindepth 2 -maxdepth 2 -type d`
        do
            username=${userdir##$tmpdir/workdir/old_submissions/[^/]*/}
            mkdir "$tmpdir/todo/old-$username/"
            cp -R $userdir/* $tmpdir/todo/old-$username/
            # drop __feedback.json, not needed here
            rm -f $tmpdir/todo/old-$username/__feedback.json > /dev/null 2> /dev/null
        done
    fi
fi

jplag_args="$jplag_args -r $tmpdir/output $tmpdir/todo"
java -jar $jplag_dir/jplag.jar $jplag_args > $tmpdir/output/jplag_stdout.txt 2> $tmpdir/output/jplag_stderr.txt

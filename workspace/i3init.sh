#!/bin/bash
echo "Usage: With one argument --all arguments script will initialize all of the workspaces
But with 2 arguments provided i3init.sh what where it will initialize particular screen (what) and put it on particular workspace (where)
Example: ./i3init.sh sketch 8"
WHAT=$1
WHERE=$2

if [ "$WHAT" == "Run it with --all argument or what where 2 arguments" ]
then
    echo ""
    exit 1
fi

function initMe {
    /usr/bin/sudo service mongod start
}

function cakInit {
    echo "/usr/bin/sudo whoami
. ./initc -c "
}

function cakLayer {
    echo "cak layer start ldap
cak app init runall"
}

function gradleBuild {
    PROJECT_FOLDER=$1
    COMMAND=$( cat $PROJECT_FOLDER/README.org | grep "Application from command line" -A 200 | grep "#+begin_src bash" -A 300 | grep "#+end_src EXECUTION" -B 300 | tail -n +2 | head -n -1 )
    echo "$COMMAND"
}

function cakInitConsole {
    PROJECT_FOLDER=$1
    echo "cd $PROJECT_FOLDER"
    cakInit
    if [[ "$2" != "" ]]
    then
        cakLayer
        gradleBuild $PROJECT_FOLDER
    fi
}

function openTstFolder {
    PROJECT_FOLDER=$1
    echo "cd $PROJECT_FOLDER/tst/ws-tests/"
}

function setupProject {
    WORKSPACE=$1
    PROJECT_FOLDER=~/workspaces/$2
    DB=$3

    # PROJECT WORKSPACE
    cakInitConsole $PROJECT_FOLDER > /tmp/WHAT_TO_SOURCE
    i3-msg "
        workspace $WORKSPACE;
        exec i3-sensible-terminal;
        exec emacs $PROJECT_FOLDER/shared/core/core-bl/src/main/groovy/com/gratex/upm3/core/policy/model/Policy.groovy $PROJECT_FOLDER/tst/ws-tests/runAllWsTests.sh $PROJECT_FOLDER/README.org $PROJECT_FOLDER/bl/src/main/groovy/com/gratex/upm3/customization/app/config/Upm3Config.groovy --eval '(spacemacs/window-split-grid)'"
    sleep 2
    openTstFolder $PROJECT_FOLDER > /tmp/WHAT_TO_SOURCE
    i3-msg '
        exec i3-sensible-terminal; '
    sleep 2
    cakInitConsole $PROJECT_FOLDER "WITH_CAK_LAYER" > /tmp/WHAT_TO_SOURCE
    i3-msg '
        focus left;
        focus left;
        split h;
        exec i3-sensible-terminal; '

    sleep 2
    openTstFolder $PROJECT_FOLDER > /tmp/WHAT_TO_SOURCE
    i3-msg '
        focus right;
        focus right;
        split h;
        exec i3-sensible-terminal -e 'mongo $DB';
        exec i3-sensible-terminal; '
    sleep 1
    rm /tmp/WHAT_TO_SOURCE
}

function appAndJenins {
    # SUU
    i3-msg "
        split v;
        workspace $1;
        exec google-chrome --new-window 'http://dh10.dsdev.cloud:62225/suu/app/ui/'; "
    sleep 3
    i3-msg '
        exec google-chrome --new-window "http://buildsrv01.hq.gratex.com:8080/view/pvzp/job/upm2/job/suu/job/suu/job/dev%252Fmain/"; '

    # MUM
    sleep 3
    i3-msg '
        focus left;
        split v;
        exec google-chrome --new-window "http://dh10.dsdev.cloud:63559/mum/app/ui/login?redirectUrl=%2Fmum%2Fapp%2Fui%2F"; '
    sleep 3
    i3-msg '
        focus right;
        split v;
        exec google-chrome --new-window "http://buildsrv01.hq.gratex.com:8080/view/mum/job/upm2/job/mum/job/mum/job/dev%252Fmain/"; '
}

function fw {
    i3-msg '
        workspace 7;
        exec i3-sensible-terminal;
        exec emacs ~/workspaces/spring-boot-libs/;'
}

function sketch {
    i3-msg "
        workspace $1;
        exec i3-sensible-terminal;
        exec emacs ~/sketch"
}

function core {
    i3-msg "
        workspace $1;
        exec i3-sensible-terminal;
        exec emacs ~/workspaces/upm3-core/;"
}

function keyboard {
    i3-msg "
        workspace $1;
        exec i3-sensible-terminal;
        exec emacs ~/qmk_firmware/keyboards/keebio/iris/keymaps/default/keymap.c;"
}

function mailCommunication {
    # TODO: how to open a M mu4e on startup ?
    i3-msg "
        workspace $1;
        exec google-chrome --new-window 'https://mail2.gratex.com';"
    sleep 2
    i3-msg "
        workspace $1;
        exec emacs;"
}

function todos {
    i3-msg "
        workspace $1;
        exec google-chrome --new-window 'https://gko.gratex.com';"
    sleep 2
    i3-msg '
        exec emacs ~/workspaces/kelemen-linux/doc/useful.org ~/workspaces/kelemen-linux/doc/todos.org;'
}

function environments {
    i3-msg "
        workspace $1;
        exec emacs ~/workspaces/kelemen-linux/doc/environments.org;
        move workspace to output right "
}

function study {
    PAGES=$( cat ~/workspaces/kelemen-linux/doc/study-notes.org | grep "^http" | sed 's/^/"/g' | sed 's/$/"/g' | tr '\n' ' ')
    i3-msg "
        workspace $1;
        exec i3-sensible-terminal;
        exec google-chrome --new-window --new-tab ${PAGES};"
    sleep 2
    i3-msg '
        exec emacs ~/workspaces/kelemen-linux/doc/study-notes.org'
}

if [ "WHAT" == "--all" ]
then
    initMe

    # WORKSPACE 1
    setupProject 1 upm2-mum mum-local
    sleep 5

    # WORKSPACE 2
    setupProject 2 suu suu-local
    sleep 5

    # WORKSPACE 3
    setupProject 3 pvzp-gdf3 pvzp-gdf3-local
    sleep 5

    # WORKSPACE 4
    core 4
    sleep 5

    # WORKSPACE 5
    study 5
    sleep 5

    # WORKSPACE 6
    keyboard 6
    sleep 5

    # WORKSPACE 8
    sketch 8
    sleep 5

    # WORKSPACE 11
    appAndJenins 11
    sleep 5

    # WORKSPACE 12
    todos 12
    sleep 5

    # WORKSPACE 13
    mailCommunication 13
    sleep 5


    # WORKSPACE 14
    environments 14
else
    if [ "$WHERE" == "" ]
    then
        echo "Second Where argument missing. Specify id of the workspace"
        exit 1
    fi
    $WHAT $WHERE
fi

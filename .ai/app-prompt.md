# BASE LINE

Here you can find a list of GIF files:
https://github.com/healthy-programmer/healthy-programmer/tree/main/exercise/images

# 1)
Please develop a CLI program in Python in the folder ./script/
- It should run in the background.
- Every 30 minutes (configurable argument), the system will pop up a GIF file in a window.

The goal of the program is to encourage people who sit for long periods to move every 30 minutes to
reduce stiffness.

# 2)
Running:
python3 move_reminder.py
causes this error:

Traceback (most recent call last):
  File "/home/............../healthy-programmer/script/move_reminder.py", line 9, in <module>
    from tkinter import Tk, Label, PhotoImage
  File "/home/linuxbrew/.linuxbrew/Cellar/python@3.10/3.10.10/lib/python3.10/tkinter/__init__.py", line 37, in <module>
    import _tkinter # If this fails your Python may not be configured for Tk
ModuleNotFoundError: No module named '_tkinter'

In the same folder, please create a robust bash script that
installs all necessary dependencies for this Python script and then executes the script.

# 3)
./script/move_reminder.py
Ok, when the GIFF shows up i want you to keep the FOCUS on the application
the user is working currently. is that possible ?

# 4)
./script/move_reminder.py
The popup window show on the particular position.
add argument of the script whether to pop it up: top-left, top-right, bottom-left, bottom-right, center.
default is bottom-right.

# 5)
Rewrite README.org the way that first thing you will mention is the script
move-reminder. How to install, how to run, my story: 44 years old, all day / wholle live behind computer.
6 years I only stay, no more pain in knees, back, ... read all ORG files
about excerices and make some summary and this READ Me make attractive,
focus on the script, with parameters described etc ...

./run_move_reminder.sh --interval 1 --duration 15 --help
=== Move Reminder Setup & Run Script ===
Using Python interpreter: /usr/bin/python3
Running move_reminder.py ...
usage: move_reminder.py [-h] [--interval INTERVAL] [--duration DURATION] [--position {top-left,top-right,bottom-left,bottom-right,center}]

Remind yourself to move every N minutes by popping up a random exercise GIF.

options:
-h, --help            show this help message and exit
--interval INTERVAL   Interval in minutes between reminders (default: 30)
--duration DURATION   How long (seconds) to show the GIF window (default: 30)
--position {top-left,top-right,bottom-left,bottom-right,center}
Popup window position: top-left, top-right, bottom-left, bottom-right, center (default: bottom-right)

# 6)
Into README.org. Somethere mention that:
I will contribute with more excercises weekly basis.
TODOs:
- to categorize excercises by: body area (neck ,back, hips, knees, ankles)
- and also by dificulity.

# 7)
We have this script: script/move_reminder.py
For each photo in exercise/images you will find related text in exercise.org
What I want to achieve is this GOAL:
- while GIF is played by script, under the GIF there will be description
- description about which areas are you currently stretching / streightening

In order to do SO:
- we need to create a MAPPING table: GIF file VS description. create it in the exercise/reminder-data
- how to get this description ? read it per GIF file in exercise.org and do the summary from the text
  which body area is affected, and whether it is stretching or strenghtening.

When having this DONE, ammend the script/move_reminder.py to display GIF together with data.

# 8) 
We have this script: script/move_reminder.py
Add the button "Next exercise". After pressing it, randomly find another and display its gif and description.
And of course restore the counder DURATION.

# 9)
../exercise/reminder-data.csv
This format is not very comofortable for editing. As there can be multi line descriptions. can you change it
to the CHAPER - TEXT format somehow ? Markdown maybe ? chapter is the GIF file, TEXT inside is the description.
But also adapt this script ../exercise/reminder-data.csv to read the data properly

# 10)
exercise/reminder-data.md
Not everybody want to exercise every exercise from the list. Now I need you to add into:
script/move_reminder.py the following functionality:

"icon: ozubene kolecko" by clickin on it setup page will open. on this screen there will be list
of exercises with thumbnails moving GIFs and for each of them there will be description and CHECKBOX.
Mind that list of the exercises can be huge. So add some scroll bars. user can tick any exercise
that he wants to have in the personalized list. By clicking SAVE button, this personalized setup
will be stored next to this script.

Than adjust the random functionality that random only from those exercises that are ticked in the existing
personalised config. if no personalised config exists, than add ingore it and fallback to the random
exercise from the reminder-data.md.

# 11)
2 things: while setup is open, do not close the window based on the duration timer. (duration). Thumbnails should be movable GIFs.

# 12)
in script/move_reminder.py SETUP Page
2 more things: thumbnails... small resized GIFs, ... add buttons. Select all / Deselect all, After pressing SAVE close the setup window.

# 13)
By pressing NEXT NEXT NEXT or SETUP can happend that WINDOW is still open at the time when NEXT PERIOD of OCCURANCE happend
and in this case the window is open second time simultanously. How can that it be fixed ? can you fix that ?

# 14)
script/move_reminder.py
The Setup page and the GIFF thumbnails... they load too long on start..
can you make a GIFF animated thumbnails, save them into on disc resized to enhance loading performance ?

# 15)
exercise/reminder-data.md
Need to add category field (name it the best you can) that has enum values:
- sitting, standing, wall assisted. And I need to categorize each video. Can you do it by watching GIFFs ?

# 16)
Into: exercise/reminder-data.md added category to each item. Get the unique list of categories.
Here in this script: script/setup_page.py
Add filter: Multi item selectbox (default all selected) filter by category.
Than filter the list by categories

# 17)
firstly read:
script/move_reminder.py
script/setup_page.py
exercise/reminder-data.md

In folder script implement following file: script/exercise_log.py with following features:
- on every exercise (poped-up, or by next button pressed) create a log entry into file: exercise_log.log with following data:
- date and time of the excercise, jpg file.
- then implement log viewer screen accessible by pressing button "Log" from the reminder screen.
  this viewer is display calendar and by pressing particular day open the screen with list of
  exercises performed that day based on the log file. Display everything about the exercise as per setup page.
  thumbnail with description.

# 18)
script/exercise_log.py
Same as per setup_page.py, while log screen is open, do not close the window after DURATION passed.

# 19)
Log screen
script/exercise_log.py
Button close to be displayed at the beginning of the page, like in case of setup page in scrip/setup_page.py

# 20)
Look at the script folder. the shell, python. The goal is to make similar SH script that will install and run
on Windows and mac platforms.

# 21)
Ativity log. Currently it is being stored into single file: exercise_log.log. by script exercise_log.py. Rewrite the
script the way, that you create for each day new file in folder 'log' next to folder 'script'. robust script
create folder if it doesn't exist. read data from there. Each day one file. Add the folder to .gitignore that exists
already in the workspace.

# 22)
Add new parameter into script: run_move_reminder.sh and also to the run_move_reminder.bat and run_move_reminder_mac.sh
Add optional parameter: --working-hours 8:00-16:30. This example is also default. And run the repetition only if
the time is between these hours. Reason: I want to avoid creation logs of activities when user is not by computer
and script is still running at this time. Update README.org accordingly.

# 23)
Log screen. When switching betwen days, restart the scroll bar accordingly. When I am on the day with lot of
activities, scroll bar is scrolled down. And when i switch to the day wiht only few activities, i cant see anything
i must scroll first to the area where are some activities because scroll bar remins BIG from the previous data day.

# 24)
Go read the script folder and README.org. Maybe it is time to split INSTALLATION and RUNNING of the script. What are your suggestions ?
And if you agree, than split it into install.sh/bat and run.sh/bat. Is the run good name for the script ? what do you suggest ?
and than change the README.org accordingly.

# 25)
The app is being deveoped and maintained with AI and user prompts in folder .ai. I would like to add this information
somewhere into bottom of the README.org. And than I want to push the .ai Folder int git. Mention the cross reference
into this folder in that paragraph about AI.

# 26)
Read the script folder, especially setup_page.py. Now what i want you to do is, that all CLI arguments
should appear as an alternative in the setup page. If the script is executed without arguments, these values
are taken into consideration. If executed with arguments, arguments will apply. When the script is executed
and user changes the settings via setup page. apply them imediately.
Mind that the current setup of selected exercises is stored in: script/personalized_exercises.json.
So maybe this should be renamed more generally like personal_setup.json and the config attribtes to be added there.
UX: Now on setup page there is list of exercises to be selected. How about to to create 2 tabs: 1 tab: general setup,
2 tab: selected excerices. Implement this requirement.

Additional prompts (bug fixing or this dificult one)

 - Add 1) the GRID with the exercises are not part of the Selected Exercises TAB. They are displayed always.
 - Add 2) i think that you are not reading exercises from new structure of personal_setup.json. i can see that they are random.
 - Add 3) Now I believe that buttons SAVE and CLOSE belong to the part of the window outside the TAB container to be visible regardless the tab selected
 - Add 4) i have changed the interval to 1 minute between exercises but it has no effect. Fix other attributes as well. and also write to the log that setup changed with new setup values.
 - Add 5) sorry not to log file. But to the console debug. remove writing the log for this case.

Michal's note: At this point I needed to understand the code, as AI is not helping a lot. This was too complex.

# 27) Time for some refactor before continue. Too much of spagethi code for my tate

- Extract methods def parse_working_hours(whours): def is_within_working_hours(dt): into lib.py
- Extract method def load_config_and_gifs() into config_utils.py
- In setup_page.py for reload config reuse method from config_utils.py load_config_and_gifs ... instead of this, no ?
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f) ...
- No in setup page GIFs are not dummy. you need to load them properly. You need them for setting the data in 
  second tab: selected exercises. So fully reload gifs from config and ammend this codes in setup_page.py
  def _dummy_get_gif_files():
  return []
  _, general_config = load_config_and_gifs(config_path, _dummy_get_gif_files)
  ///
  config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personal_setup.json")
  selected_gifs = set()
  gif_files_for_selection, _ = load_config_and_gifs(config_path, _dummy_get_gif_files)
  selected_gifs = set(os.path.basename(f) for f in gif_files_for_selection)
- In a setup_page.py ... where you save the new config into personal_setup.json extract this code into config_utils.py

# 28)
After save_config_to_file is called, new data are not loaded in the move_reminder.py main loop. Maybe reload it via load_config_and_gifs ?
I have changes interval from 2 to 5 minues.
But after pressing CLOSE button on reminder screen, in console I see: [DEBUG] Time to next exercise: 2m 0s which was
original value. Counter is not updated based on new config value.

# 27)
Multi languge support. We need this application to be delivered in 4 languages: EN (default), Espanol, Deutsh, Franch.
Selected language is the setup argument
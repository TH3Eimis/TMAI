Hi welcome to my project

OverView:

TMInterface - communicates with plugin server

Agent - controls car and agent parameters

Fitness - hold agent fitness parameters and test

Population - controls population of Agents

Vision - controls agents sight/look for side-lanes

Main - Connects to server and combines all components


do get started you will need to download

TrackMania Nations Forever (its free on steam)

Download the 2.1.4 testing branch for TMInterface https://donadigo.com/files/TMInterface/TMInterface_2.1.4.testing_Setup.exe

Download the plugin named NewAPI.as

Put the plugin file into TMinterface > plugins 

Run Trackmania Testing Launcher

Press ` to open console

go to settings > plugins

should see NewAPI.as plugin called PythonInterface

IMPORTANT IN CODE

in agent.py go to GetMapData() change map path to TrackmaniaNF Map Folder ( look at placement one should look similar )

Only change the start do not change after first

Create a simple test map to test the Agents

Start Map

Once in map, run main.py

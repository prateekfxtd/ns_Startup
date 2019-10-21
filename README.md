# ns_Startup v0.1.25 for Houdini

[![Vimeo](https://i.vimeocdn.com/video/823525142.jpg)](https://player.vimeo.com/video/367236737 "Vimeo")(Click to start Vimeo teaser)

This python script was created to starting Houdini easily with the right 
workgroups/renderers etc. without changing everytime the local env file.

Done with Python 2.7 & PyQt4. Including a WOL functionality for my FreeNAS fileserver and a preset/job system. 
The preset system can be used globally - and pushed, to make them accessible to other clients/workstations. 
I implemented a preset "Check" to make sure the workgroups/renderers are physically existing. 
If not, you will get a warning, so you can reinstall them.

![Inline image](ns_Startup_Screener.jpg)

Also onboard, a little chat client.

Chat Server: https://gitlab.com/e_noni/ns_startup_server

- Windows only right now
- You need a proper Python 2.7 and PyQT4 installation (other liberies as well), or you build a your own virtual environment. Easy with PyCharm.
- Check the init pathes in the ns_Startup.py

Further documentation will come soon...

https://www.enoni.de/wp/ns_startup/
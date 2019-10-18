# ns_Startup v0.1.25

This python script was created to starting Houdini easily with the right 
workgroups/renderers etc. without changing everytime the local env file.

Done with PyQt4. Including a WOL functionality for my FreeNAS fileserver and a preset/job system. 
The preset System can be used globally and pushed, to make them accessible to other clients/workstations. 
I implemented a Preset Check to make sure the workgroups/renderers are physically existing. 
If not, you will get a warning, so you can reinstall them.

Also a little chat client to communicate with other clients that are using this script.
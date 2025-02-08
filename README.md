# NUT-Victron-VRM-Dummy
I have a few APC UPSes that I manage via NUT. The NUT dashboard, while very looking dated, is very useful to see the status of all your UPSes very quickly.

I decided to replace one of the UPSes with a Victron Phoenix inverter and Victron Blue Smart Battery charger effectively creating an 'online' UPS

The challenge was now that I needed to go to 2 places to see the status of all the UPSes, NUT and Victron VRM.

All my UPSes provide power to my infrastructure sites and are remote, so each site has a Rasperry Pi Zero W or Pi Zero 2 W.

All the sites have WiFi.

The Pis at the APC sites run Raspberry OS with NUT running locally.

The Pi at the Victron site runs Venus OS. The Phoenix is connected to the Pi via VE.Direct cable.

At the office, I have a Virtual Machine that runs Debian with NUT on it also. This NUT installation produces the GUI and shows the status of all the sites 

The Office NUT installation polls the remote NUT installations for their statuses.

The Victron Inverter is also included as a 'NUT' inverter by 'faking' it as a simulated inverter. NUT has a dummy driver that basically loads the data from a file and treats that data as if it is coming from a device.

The python script connects to Victron VRM, gets the data and then writes it out to file that NUT is expecting.

A CRON job then runs the python script once every minute to get the latest data. Not realtime, but good enough for my purposes.

To configure the script you need to add the VRM API token and your installation ID.

You will need to create a new token in VRM by going to Preferences | Integrations | Access Tokens and then clicking on Add

You can get your installation ID by going to the installation Dashboard and looking at the URL, it should be

 https://vrm.victronenergy.com/installation/<Installation ID>/dashboard

 The other settings are there to simulate different NUT states.

 I haven't yet figured out how to get the Blue Smart Charger data into the script as it uses BlueTooth Low Energy (BLE), but that's the next step.

 So until then I have to infer some of the NUT battery and line voltage status from input voltage to the Inverter.

 The file output by the puthon script that NUT will pick up should have a .dev extension, this tells NUT to only import it if the timestamp on the file changes.

 I use msmtp for NUT to send email alerts

 Here are some useful links
 https://networkupstools.org/docs/man/dummy-ups.html
 https://networkupstools.org/docs/user-manual.chunked/Advanced_usage_scheduling_notes.html
 https://marlam.de/msmtp/









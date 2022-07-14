droppoint.php to POST anything to your web server.

Do you want to send data from anywhere to your web server where it can be processed :
<br> - as something to be mailed ?
<br> - as something to be put in a database ?
<br> - as something to be read by a domotica system ?
<br> - by whatever you can think of ?

droppoint.php is what you need.

droppoint.php receives POST requests and saves them in files with unique names in the folder ./data/inbox/

There is an example script to process the files in the inbox and has email functionality and more.

Full documentation on droppoint.php and the script is in droppoint.php including :
<br> - droppoint.php parameters :
<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; * formSubmit  : Submit|submit is required to tell droppoint.php you want to submit something.
<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; * requestType : Prefix of the file to be created like 'test','any,'mail' and whatever you configure in droppoint.php.
<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;( this prefix is what the scripts uses to decide what to do with a file )
<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; * payload     : Is what you want to be put in the file.
<br> - how to add your own requestType.
<br> - how to POST data from any application giving curl example commands for 'test' and 'mail'.
<br> - how to use the supplied example script to process 'test' requestType.
<br> - how to use the supplied example script to send mail based on the 'mail' requestType.

You can use curl, wget or any other application to send files but you can also create files from the web page : 
<br>When you use http : http://WebServerNameOrIPAddress/droppoint/droppoint.php
<br>When you use https:https://WebServerNameOrIPAddress/droppoint/droppoint.php
<br>You can select a requestType, enter a payload and hit a submit button.

Installation :

I expect you have a web server like apache with php enabled.

Just copy the folder droppoint with all subfolders and content to /var/www/html/droppoint.

When your root is note /var/www/html/droppoint but somewhere else you need to make a modification to the variable root in line 123 in the process_messages.py script in the script subfolder to make it find the files in the right location.

Change ownership to www-data : chown -R www-data: /var/www/html/droppoint

Add an entry to the root crontab :

crontab -e

And add a line to run the script every minute :

\* \* \* \* \* /var/www/html/droppoint/scripts/process_messages.py -phase inbox >/dev/null 2>&1

Or to create a log file like /tmp/droppoint_log.txt : 

\* \* \* \* \* /var/www/html/droppoint/scripts/process_messages.py -phase inbox >/tmp/droppoint_log.txt 2>&1

You probably know but you can see files moving from one folder to another folder with :
<br>watch 'find /var/www/html/droppoint/data/ -name "*"'

Thanks for reading and enjoy !

<?php
/*

---------- droppoint.php

Receive POST requests and save them in files with unique names in the folder ./data/inbox/

Parameters :
    formSubmit  : Submit|submit  <- the big 'S' is for the web form below, the small 's' for other applications
    requestType : Prefix of the file to be created like 'test' and 'mail'in the curl examples below.
                    You can add your own requestType's like 'any' in the php code and also in the html below.
    payload     : Is what you want to be put in the file

---------- Processing the files by a script :

You should put a script in place to process the files of your requestType and run that somehow.

An example script is my script which reads 'mail' type files and sends mail messages is in the scripts folder.

I use a crontab entry to schedule my script :
crontab -l | grep droppoint
# droppoint
* * * * * /var/www/html/droppoint/scripts/process_messages.py -phase inbox >/dev/null 2>&1

The 'any' type is not processed by the script and stays in the ./data/inbox/ folder.
Files which stay in the ./data/inbox/ folder are removed after 7 days to avoid too much polution there.

Successfully sent mails go to the ./data/done folder. 
Errors go to the ./data/error folder.

The script also processes 'test' files.
These are simply moved to the ./data/done folder.

The done folder is cleaned up so it only contains files of the last 7 days.

---------- Examples using curl

The examples below are using https. Change https in http and remove -k to POST over http.

POSTing 'test' data with a curl command :
Note on the command :
* The -k is to accept any certificate and is great for self signed certificates ;-)
curl --max-time 5 -d "formSubmit=submit&requestType=test&payload=testje" -k -X POST https://pi41.home/droppoint/droppoint.php
Results in a return code like :
created ./data/inbox/test.2022-07-13-17:20:16_62cee2b0e57a96.54028744.json !!!!!
And the file will contain :
[{"requestType":"test","payload":"testje"}]
The script will pick it up and move it to the folder ./data/done

POSTing 'mail' data to send an email with a curl command :
Notes on the command :
* The -k is to accept any certificate and is great for self signed certificates ;-)
* The payload json uses single quotes so I do not have to escape double quotes on the command line. 
  The script is created to expect this construction so when sending mail messages from other application use this format.
* m_usr and m_pw are empty so default user pwd of script will be used to send mail.
* You need to change m_to so it contains real mail receivers. (seperate by a ;)
* m_dp is not used by the mail sending process, it is just there so you can see you can also send optional fields
curl --max-time 5 -d "formSubmit=submit&requestType=mail&payload={'m_ena':'yes' , 'm_ssl':'yes' , 'a_id':'barometer' , 'm_prt':'465' , 'm_to':'reveiver1@gmail.com;receiver2@gmail.com' , 'm_usr':'' , 'm_hst':'smtp.gmail.com' , 'm_pwd':'' , 'm_dp':'https://pi41.home/droppoint/droppoint.php' , 'm_su':'This ia a message subject' , 'm_msg':'This is a message body'}" -k -X POST https://pi41.home/droppoint/droppoint.php
Results in a return code like :
created ./data/inbox/mail.2022-07-13-20:53:45_62cf14b956b972.30244593.json !!!!!
And the file will contain :
[{"requestType":"mail","payload":"{'m_ena':'yes' , ..... , 'm_msg':'This is a message body'}"}]
The script will pick it up send a mail to the recipients and move it to the folder ./data/done

---------- Below you first find the php code which does the file creation and after that the html for the web page which you couuld use to test.

*/
if ($_SERVER['REQUEST_METHOD'] == 'POST') {

    if( ($_POST['formSubmit'] == "Submit") || ($_POST['formSubmit'] == "submit") )
    {
        $errorMessage = "";
        $thanksMessage = "";
// Just for testing : Next line will cause a timeout for the curl examples above
//        sleep(10);
        if(empty($_POST['requestType']))
        {
            $errorMessage .= "<li>You forgot to select a Request Type.</li>";
        } else {

            if ( ! (
// Add your own requestType's below :
                    ($_POST['requestType'] == 'mail')
                 || ($_POST['requestType'] == 'test')
                 || ($_POST['requestType'] == 'any')
               ) )
            {
                $errorMessage .= "<li>You selected an unsupported Request Type : ".$_POST['requestType'] ."</li>";
            }
        }

        if(empty($_POST['payload']))
        {
            $errorMessage .= "<li>You forgot to enter a Payload.</li>";
        }
// Create a function to put the data in an array. This function is used in line 112
        function get_data() {
            $datae = array();
            $datae[] = array(
                'requestType' => $_POST['requestType'],
                'payload' => $_POST['payload'],
            );
            return json_encode($datae);
        }

        if(empty($errorMessage))
        {
            $id = uniqid( "", true) ;
            $file_name1 = './data/inbox/' .                         '.' . $id . '.json';
            $file_name2 = './data/inbox/' . $_POST['requestType'] . '.' . date('Y-m-d-H:i:s') . '_'. $id . '.json';
// First write the file and after completion rename it. 
// This avoids situations where the script opens the file while php still creates the file.

            if(file_put_contents( "$file_name1", get_data())) {
                rename( $file_name1, $file_name2);

// Note that the form uses 'S'ubmit and applications like wget, curl etc use 's'ubmit

                if ($_POST['formSubmit'] == "Submit")
                {
                    $thanksMessage .= $_POST['requestType'] ;
                } else {
                    echo 'created ' . $file_name2 . ' !!!!!'; // tools get this answer
                    exit;
                }

            } else {
// File creation failed :-(
                echo 'There is some file creation error !!!!!';
                if ($_POST['formSubmit'] == "submit")
                {
                    exit;
                }
            }
        } else {
// There is something wrong with the input            
            if ($_POST['formSubmit'] == "submit")
            {
                echo 'error ' . $errorMessage . ' !!!!!';
                exit;
            }
            // else ( $_POST['formSubmit'] == "Submit") and  $errorMessage will be put on the web page
        }
    } else {
// formSubmit is not one of the values Submit and submit
        echo 'error invalid formSubmit value !!!!!'; // tools get this answer when formSubmit has wrong value
        exit;
    }
}

?>

<html>
<head><title>Droppoint</title>
<meta name="viewport" content="width=device-width, height=device-height, initial-scale=1">
<style>
html{text-align: center;} h1{color: #0F3376; padding: 2vh;} p{font-size: 1.5rem} body { margin: 0}
#main {background-image: radial-gradient( #1fd8de, #a2e9eb, #1014ec); min-height: 750px}
.rnd_btn {  background-color: lightblue; border-radius: 50%; border-width : 3; border-color: gold; color: blue; width: 80px; height: 40px; text-align: center}
</style>
</head>
<body>
    <div id="main"><br><br><br><br><br><br>

    <?php
/*

Here we show the results after processing by droppoint.php above

*/
        if(!empty($thanksMessage))
        {
            echo("<p>Thanks for posting '" . $thanksMessage . "' !</p>\n");
        }
        if(!empty($errorMessage))
        {
            echo("<p>There was an error with your input:</p>\n");
            echo("<ul>" . $errorMessage . "</ul>\n");
        }
    ?>

<!-- Here we have the form which collects the data and sends it to droppoint.php which is this page itself -->

    <br><form action="droppoint.php" method="post">
    <p>
        <label for="requestType">Choose a Request Type :</label>
        <br><br>
        <select name="requestType" id="requestType">
            <option value=""></option>">
            <option value="mail">mail</option>
            <option value="test">test</option>
            <option value="any">any</option>
            <option value="error">error</option>
            <option value="other error">other error</option>
        </select>
    </p>
    <p>
        <label for="payload">Put your payload below :</label>
        <br><br>
        <input type="text" name="payload" size=40 maxlength="1024" value="<?=$payload;?>" />
    </p>
    <button class="rnd_btn" style="top:250; margin:0 auto;" name="formSubmit" value="Submit">Submit</button>
    </form>
    </div>
</body>
</html>


1. Installing and Executing the GUI:


Use the folloing commands

%tar xvfz  newgui.tgz

%cd newgui

%python3 main.py


It will ask for an username and password which are given below

username: test
password: 1test


2. Modifying the username and password

Edit the  userdata.py and change the line username="test"
with your preferred name. Then execute 

%python3 userdata.py  passwordstring


This will produce the following output

username= test
hashedpass= b'$2b$14$hoxiwEkaJiIVtCY94.gc.uMQqpbw9or1aLT81RkaiMJpbVaszfLia'


Copy these lines to tbe beginning of the userdata.py. Repalce original lines.
Add double quotes to the username.

   usename="test"


 


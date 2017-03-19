# item_catalog
Udacity FSND project

This is a learning project at Udacity FSND course. The application provides a list of items within a variety of categories
as well as provide a user registration and authentication system. Registered users will have the ability to post,
edit and delete their own items.
The project is a flask based python app with auth from Goggle and Facebook.
The Vagrant software is used to configure and manage the VM where the application is run.

## Here are the tools you'll need to install to get it running:

### Git

If you don't already have Git installed, you may download it from [git-scm.com](http://git-scm.com/downloads).

On Windows, Git will provide you with a Unix-style terminal and shell (Git Bash).  
(On Mac or Linux systems you can use the regular terminal program.)
You will need Git to install the configuration for the VM.

### VirtualBox

VirtualBox is the software that actually runs the VM.
You can download it from [virtualbox.org](https://www.virtualbox.org/wiki/Downloads).
You do not need to launch VirtualBox after installing it.

### Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem.
You can download it from [vagrantup.com](https://www.vagrantup.com/downloads). Install the version for your operating system.

## Fetch the Source Code and VM Configuration

**Windows:** Use the Git Bash program (installed with Git) to get a Unix-style terminal.  
**Other systems:** Use your favorite terminal program.

From the terminal clone this repo to a directory of your choice.
That folder will contain the source code for the application,
and configuration files for installing all of the necessary tools. 

## Run the virtual machine!

Using the terminal, change directory to the one where you cloned the repo,
then type **vagrant up** to launch your virtual machine.


## Running the Catalog App
Once it is up and running, type **vagrant ssh** to log into your VM.
This will log your terminal into the virtual machine, and you'll get a Linux shell prompt.

Change to the /vagrant directory by typing **cd /vagrant**.
This will take you to the shared folder between your virtual machine and host machine.

Type **ls** to ensure that you are inside the directory that contains project.py, database_setup.py,
and two directories named 'templates' and 'static'.

Now type **python database_setup.py** to initialize the database.

Type **python populate_db.py** to populate the database with restaurants and menu items. (Optional)

Type **python project.py** to run the Flask web server.
In your browser visit **http://localhost:5000** to view the restaurant menu app.
You should be able to view, add, edit, and delete items in the catalog.

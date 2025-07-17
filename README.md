# parseTHN-AI
Notice: This is a rough draft of an unfinished but working product.

This is a python3 script that will not only parse the news articles from https://www.thehackernews, it will ask openai to make a simple analysis on the article to provide an easy summary with listed products and keywords.

I use this to keep abreast of some of the Information Security News out there.  

It would be best to use a python virtual environment for your project using the following commands.
$ sudo apt-get install python3-venv
$ python3 -m venv myvenv

To activate the the virtual environment run the following:
$ source myenv/bin/activate

Install the required modules while you have your venv activated:
$ pip install requests bs4 openai os 

You must set your OPENAI_API_KEY in your shell before you execute this.
Also modify the os.chdir line to put your working directory where you want the collected data to be stored:  os.chdir('/home/lmicro/python/parseTHN/data')

Set this line to your configuration to get smtp to work if you want to receive an email with the summary or just comment it out if you don't want email sent.
send_email_with_attachment('you@gmail.com', 'your_app_password', 'recipient@example.com', 'Subject', 'Body text', 'path/to/file.txt')

If you use gmail as your sender you will have to configure and application password in your gmail setup:
https://support.google.com/mail/thread/205453566/how-to-generate-an-app-password?hl=en


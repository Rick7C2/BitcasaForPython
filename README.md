# Bitcasa for Python

#Disclaimer
This is just a script I made for myself that I wanted to share.  I make no promises of data safety or secruity.  Use at your own risk!

That being said, I'm releasing this under the GPLv3 license.  So feel free to change, tinker, remix, and make it your own.  Improvements and new ideas are always welcome.

## About
This is a rough python script that I threw together that can upload files to your [Bitcasa Infinite Drive][BID].  My plan is to expand the script into a command line utility and possibly a GUI.

This script uses the [Bitcasa Web Portal][BWP] to navigate your Bitcasa Drive and upload files.  Because it uses the web portal to upload the files, it is restricted by the limitations of the web portal.  Currently, I know of no way to create new directories via the web portal.

## Package Requirements

Currently, this script needs only one non-standard library package to function.  [Requests][rq] is used to upload the files via POST requests made to the web portal.  It is really just a wrapper around Python's standard library HTTP package, but it is much simpler to use.

## Supported Systems

In theory, this should work wherever you have Python 2.7 and all required packages installed.  I have only tested this on Mac OSX, so I'm not sure about Windows. I assume linux works just fine given that it worked on my Mac.

## How It Works

The idea behind the script is actaully quite simple.  All it really does is mimic what your browser does when you access the Bitcasa Web Portal.  So it requests the login page, sends your login credentials, then uses the returned session cookie to access your drive.  Once it has the session cookie, it can get the directory listings, download files, and upload files.  All of this is done through HTTP requests (GET and PUT).  Everything is still done over SSL, so your information should be safe.

## How To Run It

Just run
```python bitcasa.py```
from the command line and follow the prompts.

## Increasing Performance

If you have a sweet internet connection that isn't being fully utilized by 2 parallel connections (the default setting).  Just go into the code and change the line

```pool = Pool(processes=2, initializer=subprocess_init, initargs=[upload_dir_path, credentials])```

to

```pool = Pool(processes=X, initializer=subprocess_init, initargs=[upload_dir_path, credentials])```

where X is the number of simultaneous upload connections you want.  You might need to experiment to see what works best for you.

## Future Plans

I have a lot of performance improvements and feature ideas in my head that may or may not get implemented.  Here is the list so far:

- Auto tuning of the number of parallel connections for optimal connection utilization
- Directory navigation so that you can access more than just the root directories
- The capability to download files (and possible folders)
- Better session caching so that we don't reestablish a connection with each new file
- Better error handling
- MD5 verification (would make things slow but would be a nice option if you want to guarantee that everything is working)
- A hack that uses the bitcasa client to create directories so we can do a fully recursive upload
- Encrypted storage of credentials and sessions

In addition, I plan on making a command line utility that takes in your local files and their destination as args.  This way you could use it in other scripts (using it in cron jobs would be pretty sweet).

[BID]: http://www.bitcasa.com/
[BWP]: http://my.bitcasa.com/
[rq]: http://docs.python-requests.org/en/latest/
[tk]: http://docs.python.org/2/library/tkinter.html
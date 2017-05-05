Copyright &copy; 2009, [Brendan Doms](http://www.bdoms.com/)  
Licensed under the [MIT license](http://www.opensource.org/licenses/MIT)

NB: This is a fork with more limited functionality than the trunk! You may not find it useful, it's tweaked for my use and comprehension. Support for tags and CSV output are removed, for example.

# Tumblr Backup

Tumblr Backup is a tool for making an HTML backup of your Tumblr posts.


## Setup

There is one dependency: version 4 of [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/).
If you already have it installed globally then you can grab the single `.py` file and it should work.

Otherwise, install via pip:

```bash
pip install -r requirements.txt
```


## Use

If you have Python 3 installed make sure you use 2!

By default, a new folder with post data saved in individual HTML files will be created,
and resources like images will be saved in another subfolder of the parent:
```
script folder
	|_ 'output' folder
		|_ posts put into folders by year
		|_ images folder
```

To backup your account, just include the URL of your Tumblr website:

```bash
python2 tumblr_backup.py example.tumblr.com
```

If you use a custom domain, then that will also work:

```bash
python2 tumblr_backup.py www.example.com
```

You can also specify a different directory to save to with the command line option `save_folder`:

```bash
python tumblr_backup.py --save_folder=/path/to/folder example.tumblr.com
```

Specify the post number to start from (useful with bad internet connection to continue from the last posts group):
```bash
python tumblr_backup.py --start_post=N example.tumblr.com
```


## Supported Post Types

Tumblr has a lot of different types of posts. The ones currently supported by Tumblr Backup are:

 * Regular
 * Photo (single photos only)
 * Quote
 * Link
 * (to-do: Video)


## Notes

The default encoding is UTF-8. If you wish to change this, you can simply modify or override the
global `ENCODING` variable.

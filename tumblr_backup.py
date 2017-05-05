# standard Python library imports
import os
import sys
import urllib2
import codecs
import logging

# extra required packages
from bs4 import BeautifulSoup

# Tumblr specific constants
TUMBLR_URL = "/api/read"

# configuration variables
ENCODING = "utf-8"

# most filesystems have a limit of 255 bytes per name but we also need room for a '.html' extension
NAME_MAX_BYTES = 250


def unescape(s):
	""" replace Tumblr's escaped characters with ones that make sense for saving in an HTML file """

	if s is None:
		return ""

	# html entities
	s = s.replace("&#13;", "\r")

	# standard html
	s = s.replace("&lt;", "<")
	s = s.replace("&gt;", ">")
	s = s.replace("&amp;", "&") # this has to be last

	return s


# based on http://stackoverflow.com/a/13738452
def utf8_lead_byte(b):
	""" a utf-8 intermediate byte starts with the bits 10xxxxxx """
	return (ord(b) & 0xC0) != 0x80


def byte_truncate(text):
	""" if text[max_bytes] is not a lead byte, back up until one is found and truncate before that character """
	s = text.encode(ENCODING)
	if len(s) <= NAME_MAX_BYTES:
		return s

	if ENCODING == "utf-8":
		lead_byte = utf8_lead_byte
	else:
		raise NotImplementedError()

	i = NAME_MAX_BYTES
	while i > 0 and not lead_byte(s[i]):
		i -= 1
	return s[:i]

#	-	-	-	-	-	-	-	-	-	-	-	-	-	-	-	-	-
#
#	POST WRITING

def savePost(post, save_folder, header="", save_file=None):
	""" saves an individual post and any resources for it locally """

	slug = post["url-with-slug"].rpartition("/")[2]
	date_gmt = post["date-gmt"]
	date = date_gmt[:-7]

	slug = byte_truncate(slug)
	file_name = os.path.join(save_folder, date +" "+ slug + ".html")
	f = codecs.open(file_name, "w", encoding=ENCODING)

	#	Date info for all posts
	f.write('<article>\n\t<time datetime>' + date + '</time>\n\t')

#	POST KINDS	:

#	Text

	if post["type"] == "regular":
		title = ""
		title_tag = post.find("regular-title")
		if title_tag:
			title = unescape(title_tag.string)
		body = ""
		body_tag = post.find("regular-body")
		if body_tag:
			body = unescape(body_tag.string)

		if title:
			f.write("<h3>" + title + "</h3>\n\t")
		if body:
			f.write(body)

#	Photo

	if post["type"] == "photo":
		caption = ""
		caption_tag = post.find("photo-caption")
		if caption_tag:
			caption = unescape(caption_tag.string)
		image_url = post.find("photo-url", {"max-width": "1280"}).string

		image_filename = image_url.rpartition("/")[2].encode(ENCODING)
		image_folder = os.path.join(save_folder, "../images")
		if not os.path.exists(image_folder):
			os.mkdir(image_folder)
		local_image_path = os.path.join(image_folder, image_filename)

		if not os.path.exists(local_image_path):
			# only download images if they don't already exist
			print "Downloading a photo. This may take a moment."
			try:
				image_response = urllib2.urlopen(image_url)
				image_file = open(local_image_path, "wb")
				image_file.write(image_response.read())
				image_file.close()
			except urllib2.HTTPError, e:
				logging.warning('HTTPError = ' + str(e.code))
			except urllib2.URLError, e:
				logging.warning('URLError = ' + str(e.reason))
			except httplib.HTTPException, e:
				logging.warning('HTTPException')
			except Exception:
				import traceback
				logging.warning('generic exception: ' + traceback.format_exc())

		f.write(caption + '<img alt="' + caption.replace('"', '&quot;') + '" src="images/' + image_filename + '" />')

#	Quote

	if post["type"] == "quote":
		quote = ""
		quote_tag = post.find("quote-text")
		if quote_tag:
			quote = unescape(quote_tag.string)
		source = ""
		source_tag = post.find("quote-source")
		if source_tag:
			source = unescape(source_tag.string)

		if quote:
			f.write("<blockquote>\n\t\t<p>" + quote + "</p>\n\t\t")
			if source:
				f.write('<cite>' + source + '</cite>\n\t')
		if quote:
			f.write("</blockquote>")

#	Footer for all posts

	f.write("\n</article>")
	f.close()

#	-	-	-	-	-	-	-	-	-	-	-	-	-	-	-	-	-
#
#	SCRAPING

def backup(account, save_folder=None, start_post = 0):
	""" make an HTML file for each post on a public Tumblr blog account """

	print "Getting basic information ..."

	# make sure there's a folder to save in
	if not os.path.exists(save_folder):
		os.mkdir(save_folder)

	# start by calling the API with just a single post
	url = "http://" + account + TUMBLR_URL + "?num=1"
	response = urllib2.urlopen(url)
	soup = BeautifulSoup(response.read(), features="xml")

	# collect all the meta information
	tumblelog = soup.find("tumblelog")
	title = tumblelog["title"]
	description = tumblelog.string
	header = title

	# then find the total number of posts
	posts_tag = soup.find("posts")
	total_posts = int(posts_tag["total"])

	# then get the XML files from the API, which we can only do with a max of 50 posts at once
	for i in range(start_post, total_posts, 50):
		# find the upper bound
		j = i + 49
		if j > total_posts:
			j = total_posts

		print "Getting posts " + str(i) + " to " + str(j) + "."

		url = "http://" + account + TUMBLR_URL + "?num=50&start=" + str(i)
		response = urllib2.urlopen(url)
		soup = BeautifulSoup(response.read(), features="xml")

		posts = soup.findAll("post")
		for post in posts:
			savePost(post, save_folder, header=header)

	print "Backup Complete :)"


if __name__ == "__main__":

	account = None
	save_folder = None
	start_post = 0
	if len(sys.argv) > 1:
		for arg in sys.argv[1:]:
			if arg.startswith("--"):
				option, value = arg[2:].split("=")
				if option == "save_folder":
					save_folder = value
				if option == "start_post":
					start_post = int(value)
			else:
				account = arg

	assert account, "Invalid command line arguments. Please supply the name of your Tumblr account."

	if (save_folder == None):
		save_folder = os.path.join(os.getcwd(), account)

	backup(account, save_folder, start_post)

default: rss2mbox

rss2mbox:
	cp rss2mbox.py rss2mbox
	chmod +x ./rss2mbox

clean:
	rm rss2mbox

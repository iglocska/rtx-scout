## RTX scout

RTX scout is a dumb webshop crawler meant to address an even dumber situation - the current stock levels of RTX 3080 cards.

As many others, I've been trying to keep tabs on new stock showing up at the local webshops, to no avail. Despite having two separate pre-orders stuck in indefinite waiting queues with no delivery in sight, I wanted to make my own life easier to continuously keep an eye on potential stock.

This tool is just a straight forward, dirty quick first bash at it, so your mileage may vary.

The script crawls a list of websites, fetches the stock status and price of all rtx 3080 cards and generates a simple auto-refreshing html document out of it with a table.

The table lists items with stock first, followed by all cards that don't have stock.

To configure it, simply modify the config dictionary at the start of the file:

```
config = {
    'out': '/var/www/rtx/index.html',
    'regenerate': 3, #in seconds,
    'log': '/home/iglocska/rtx/log.log',
    'max_days': 30
}
```

out: define the output of the html page, if you have apache set up, you can just let it output in your /var/www dir

regenrate: the delay between each execution in seconds

log: if the script has an actual hit, it will append the time, url and stock status as a log entry to the file at the given path (expect this to be empty until you go to sleep and miss out on any potential restock)

max\_days: Some shops allow you to pre-order with some ridiculously distant potential delivery dates, I've set it to 30 days by default, anything beyond that is daft

Currently parsed websites:

caseking.de
alternate.de
proshop.de
mindfactory.de
~~computeruniverse.de~~ (doesn't work, they load everything via ajax)
cyberport.de

If you would like to improve this mess, any pull requests are much appreciated.

The bot purely fetches and logs data, no purchases are made and there are no plans to implement anything of the sort.

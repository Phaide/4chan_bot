# 4chan_bot
A bot parsing 4chan for specific keywords.

## Issue
Sometimes, you don't want to spend a whole lot of time going through a board to find something you're interested in.<br />
Life would be easier if something could do it for you, right ?<br />

## Solution
Well you're in the right place !<br />
This script, written in Python 3, parses through your favorite boards to find specific keywords, and filter only the relevant threads !<br />

## Future work
I intended to add an image recognition system, probably based on Google's API (if there is any, I didn't look into it atm).<br />


## Usage
First off, you'll need to install the modules "requests" and "curses", via pip for instance.
```
pip install requests
```
For curses, on Windows:
```
pip install windows-curses
```
And I believe it is installed by default on Linux distributions (to check !). Otherwise, it should be 
```
pip install curses
```
You should then modify the two lists "boards" and "terms" in the source to fit your needs.<br />
Finally, use the following command (Python 3) to launch it
```
python 4chan_bot.py
```
When launched, it will load for a while, collecting the info from 4chan.<br />

Once it is done, you will have a list of the terms you are looking for.<br />
Use the directionnal arrows to navigate :<br />
Up : select the previous entry<br />
Down : select the next entry<br />
Right : go to the next menu (if any is available) or open a link when you're in the thread menu<br />
Left : go to the previous menu<br />

On the main menu, you can press the right arrow on the "Exit" entry to quit the program.<br />
Finally, if you want to update the data, press "u" when on the main menu.<br />

## Contributing
If you want to contribute, please fork this repo and/or send pull requests. Thank you.<br />

## Supporting
If you want to support me, you can send some kind messages via my website (https://phaide.net/contact)<br />

And perhaps, consider making a donation<br />

    BTC: 178oEM3sUYtHVYVt2jbHv4HNjy2nfu1iiT
    ETH: 0x4f3290b22012f0d01900a87e4475c01a7f95ee93

With love,<br />
Phaide.

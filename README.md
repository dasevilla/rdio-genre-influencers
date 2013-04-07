# Genre Influencer


## Problem


Your friends on Rdio aren't listening to comedy and so it doesn't show up in your heavy rotation. It would be nice if there was a way to find Rdio users do who listen to comedy.


## Method

- Search The Echo Nest for artists in a particular genre
- Get recent listeners for those artists on Rdio
- Rank the listeners based on how many of the artists they've listened to


## Usage

Update `RDIO_API_TOKEN` and `ECHO_NEST_API_KEY` variables and then run:

    python genreinflucers.py

You can try searching other genres by updating the `ECHO_NEST_GENRE` variable. By default the Echo Nest artist search is sorted by hotness, you could try other sort orders by updating `ECHO_NEST_GENRE_SORT`.

Built at [Comedy Hack Day SF 2013](http://comedyhackday.org/)

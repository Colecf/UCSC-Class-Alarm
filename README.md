# UCSC-Class-Alarm
Repeatedly checks for an opening in a class and emails you when it finds one.
Classes with waitlists are considered open.

Requires BeautifulSoup4 and Mechanize. For python 2.7.

If you're on the UCSC timeshare, classalarm is already installed. You can get it by running `/tmp/wconfig`, and then running `classalarm`. As an alternative to wconfig, you can add the following to your bashrc:

```
export PYTHONPATH=/afs/cats.ucsc.edu/users/o/cfaust/programs/data/python/pymodules/:$PYTHONPATH
export PATH=/afs/cats.ucsc.edu/users/o/cfaust/programs/:$PATH
```

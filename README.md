# UCSC-Class-Alarm
Repeatedly checks for an opening in a class and emails you when it finds one.
Classes with waitlists are considered open.

Requires BeautifulSoup4 and Mechanize. For python 2.7.

If you're on the UCSC timeshare, classalarm is already installed. You can get it by adding the following to your bashrc, and then running `classalarm`.

```
export PYTHONPATH=/afs/cats.ucsc.edu/users/o/cfaust/programs/data/python/pymodules/:$PYTHONPATH
export PATH=/afs/cats.ucsc.edu/users/o/cfaust/programs/:$PATH
```

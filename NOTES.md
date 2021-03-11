Feature:
- add annotation method: superpixel (superpixels selection)

Repository:
https://github.com/stjosefb/fisheg
branch: feat-superpixel-method

Development server:
142.93.169.91
/home/josef/anntools/fisheg_revision

Installation:
- clone git repository
```
cd /home/josef/anntools
git clone https://github.com/stjosefb/fisheg fisheg_revision
git checkout --track origin/feat-superpixel-method
```
x - execute commands as seen in README.md x
- modify ./fisheg/settings.py, change value of ALLOWED_HOSTS as required
```
ALLOWED_HOSTS = ['142.93.169.91']
```

Run:
```
cd /home/josef/anntools/freelabel_revision
source /home/josef/.virtualenv/djangodev/bin/activate
python manage.py runserver 0.0.0.0:8009
```
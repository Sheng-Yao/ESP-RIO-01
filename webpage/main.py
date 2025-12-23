import shutil
import gzip

with open("index.html", "rb") as i, gzip.open("../webpage_gzip/index.html.gz", "wb") as o: shutil.copyfileobj(i, o)
with open("login.html", "rb") as i, gzip.open("../webpage_gzip/login.html.gz", "wb") as o: shutil.copyfileobj(i, o)
with open("settings.html", "rb") as i, gzip.open("../webpage_gzip/settings.html.gz", "wb") as o: shutil.copyfileobj(i, o)
with open("style.css", "rb") as i, gzip.open("../webpage_gzip/style.css.gz", "wb") as o: shutil.copyfileobj(i, o)
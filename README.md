
# Download TLE elements for ILRS active targets

A utility script that

1. Parses the [ILRS website] for the NORAD ID numbers of currently active satellites.
2. Retrieves the latest TLE lines for those targets from the [Space-Track] API.

Requires Python 3 with the `lxml` package.

A file called `Config.py` should contain the following dictionary with your Space-Track login credentials:

```
spacetrack_config = {
    "username" : "your email",
    "password" : "your password",
    "debug_level" : 2
}
```

Then just run `python get_ILRS_TLE.py`.

[ILRS website]: https://ilrs.cddis.eosdis.nasa.gov/missions/satellite_missions/current_missions/index.html
[Space-Track]: https://www.space-track.org/

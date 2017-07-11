Changelog of lizard-connector
===================================================


0.4 (unreleased)
----------------

- Compatible with python 2.7.


0.3 (2016-05-06)
----------------

- Http base urls are not allowed, throws exception when baseurl is not secure
  (i.e. does not start with https).
- Fixed a bug that caused a get to run two times.

0.2 (2016-05-04)
----------------

- Added Datatype classes.
- Renamed Endpoint get and post to download and upload.

0.1 (2016-03-29)
----------------

- Basic setup
- Added tests
- Initial project structure created with nensskel 1.37.dev0.

Changelog of lizard-connector
===================================================


0.7.3 (2020-12-17)
------------------

- Removed mentions of v2 API from docs.


0.7.2 (2020-12-17)
------------------

- Added FutureWarnings when using the v2 API (default is V3)

- Renamed REAMDE.md to README.rst


0.7.1 (2018-04-17)
------------------

- Nothing changed yet.


0.7 (2018-04-17)
----------------

- Added Client.

- Added parsers (scientific, json).

- Added callbacks.

- Renamed Endpoint `download...` methods to `get...`.


0.6 (2018-02-07)
----------------

- Add explicit py2/3 imports to mitigate problems with the ``future`` library.


0.5 (2017-10-16)
----------------

- Compatible with python 2.7.

- Refactored pagination.

- Added Async downloads with callback.

- Removes max_result on Endpoint initialisation.


0.4 (2016-06-05)
----------------

- Fixed bug in iteration over paginated results.

- When all_pages is set to False all methods involving get return the object as
  an iterator.


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

Changelog
=========

0.3.0 (2015-09-05)
------------------

- Changed print statement to logging. [João Ricardo]

  This fixes this issue: https://github.com/nficano/pytube/issues/61

- Bumped verison to 0.2.1. [Nick Ficano]

- Cleanup. [Nick Ficano]

  * pep8
  * removed \n from exceptions
  * normalized docstring parameters
  * fix bug causing exception to be raised if no download path is
    provided.
  * changed FileExistsError to OSError for 2.7.x compat.


- Clean up docstrings. [Nick Ficano]

- Cleanup!! [Nick Ficano]

  * added `from_url` method.
  * added `set_filename` method.
  * added deprecation warnings to setters.
  * fixed typos.
  * pep8.
  * removed old comments.
  * removed unnecessary TODOs.
  * removed unused `_fetch`. method.


- Vevovideonotworking : 1. Getting rid of default static function 2.
  downloading from assets js always 3. Using jsinterp instead of tinyjs
  since it was not working 4. vevo and everyother video with encrypted
  signature downloads in similar way. [vidyuthd]

- Vevo video download not working due to changed algo. [vidyuthd]

- Default to cwd for path arg. [Enrique Fernandez]

- Fix division by zero. [Enrique Fernandez]

- Refs #2: - added posibility to provide full path to file. [Eloar]

- Refs #1: - added argument to force file overwrite - changed exit to
  rise exception on file name conflict. [Eloar]

- Refs #4: - changed all exit usages to raise exceptions. [Eloar]

- - added info about 3.4 support to README and setup.py. [Eloar]

- - added __future__ import to example in README. [Eloar]

- - added import print_function from __future__ for backward
  compatibility to 2.6. [Janusz Paszyński]

- - ported example in README to 3.4.1. [Janusz Paszyński]

- - ported to 3.4.1 with backward compatibility. [Janusz Paszyński]

- - added requirements information to README file. [Janusz Paszyński]

0.2.0 (2014-09-28)
------------------

- Link PyVideos in readme. [Jose Diaz-Gonzalez]

- Fix codeblock formatting. [Jose Diaz-Gonzalez]

- Cleanup setup.py. [Jose Diaz-Gonzalez]

- Add empty requirements.txt. [Jose Diaz-Gonzalez]

  Many build/ci tools will see this and assume a python repository


- Combine README.nd and README.rst. [Jose Diaz-Gonzalez]

- Add missing MANIFEST.in. [Jose Diaz-Gonzalez]

- Move LICENSE to LICENSE.txt. [Jose Diaz-Gonzalez]

- Remove AUTHORS file. [Jose Diaz-Gonzalez]

- Add necessary gitignore entries. [Jose Diaz-Gonzalez]

  This will allow us to build packages without worrying about build artifacts


- Add release script. [Jose Diaz-Gonzalez]

- PEP8. [Jose Diaz-Gonzalez]

- Pep8. [Nick Ficano]

- Pep8. [Nick Ficano]

- Self-deprecating cleanup todos, defined encoding. [Nick Ficano]

- Explicit exception imports, removed unused method. [Nick Ficano]

- Commented, flake8, TODOs. [Nick Ficano]

- Add decryption support for vevo and dashmpd. Closes #25. [Jose Diaz-
  Gonzalez]

- Use proper indentation. [Jose Diaz-Gonzalez]

- Clean up logic behind indexing. [Jose Diaz-Gonzalez]

- Remove unnecessary imports. [Jose Diaz-Gonzalez]

  Also list out top-level imports separately


- Add missing whitespace between operators. [Jose Diaz-Gonzalez]

- Whitespace cleanup. [Jose Diaz-Gonzalez]

  As per PEP8, global functions need two newlines, class methods need 1, and all indentation should use spaces, not tabs


- Remove redundant backslashes. [Jose Diaz-Gonzalez]

  They are not necessary between parenthesis


- Fix for two videos with same extension and resolution. Two videos can
  have tha same extension and resolution but a different profile. api.py
  and models.py have been modified to set also the profile to be
  downloaded and avoid this problem. [jaimecosme]

- Added exit call when either resolution or extension is missed. [san]

- Covert relative path to absolute path at the time being passed from
  commad line, updated Downlaoding message to print where the file is
  saved to, check to make sure user passes both extension and resolution
  and print to shell if not sure what resolution to choose, and fix for
  progress bar dispay on windows. [san]

- Working progress bar on OSx. [san]

- Removed white spaces and call to _main in wrapper. [san]

- Added progress bar, and function to read size in human readable
  format, updated call to print_status function. [san]

- Fixed printing  status, flushes prvious status. [san]

- Fixed python 3 compatibility. [mursts]

- Convert tab to space. [mursts]

- Bug fixed and faster. [JMasip]

- Some optimizations. [JMasip]

- Now Pytube supports videos with signatures! [JMasip]

- _get_video_info(self) [insideou7]

  I removed the video signatures. They are already included in the URL string, and apparently the old way of grabbing stream_map["sig"] returns an empty list, which returns an error in line 242

- Fixed spelling mistake. [Jay Philips]

- Added README.rst, updated copy. [NFicano]

- Changed formatting. [b-mcg]

- Changed formatting, added error checking during download, and added
  downloading message. [b-mcg]

- Changed formatting. [b-mcg]

- Rearranged imports in cli. [NFicano]

- Part of previous commit. [NFicano]

- Renamed res arg to resolution for consistancy, moved pytube cli into
  repository root, renamed it pytubectl. [NFicano]

- Fixed malformed import. [NFicano]

- Removed unnecessary import of cli. [NFicano]

- Reorganized, rewrote setup.py using distutils. [NFicano]

- Reverted back to setuptools. cleaned up setup.py. [NFicano]

- Changed setuptools to distutils. [NFicano]

- Renamed LICENSE.txt to LICENSE. [NFicano]

- Fixed for PyPI! [NFicano]

  * added setup.cfg
  * updated setup.py
  * renamed COPYING to LICENCE.txt.


- Bump version number. [Richard Borcsik]

- Added error handling. [Richard Borcsik]

- Add a command line tool. [Richard Borcsik]

- Added myself to the AUTHORS file. [Richard Borcsik]

- PEP8 cleanup. [Richard Borcsik]

- Corrected variable. [Richard Borcsik]

- Correct indentation. [Richard Borcsik]

- Add callbacks to Video.download. Refactored console printing into
  utils.py. [Richard Borcsik]

- Use the correct variable for filename. [Richard Borcsik]

- Fixed handling of filename changes. Fix for #8. [Richard Borcsik]

- Fixed video info parsing. [Richard Borcsik]

- Fixed python 3 compatibility. [Richard Borcsik]

- Added print statement back in, changed to rev 0.0.5, (1.0 will include
  unit tests, and CLI), update README. [NFicano]

- Python 3.x! Reorganized file structure, removed print statements.
  [NFicano]

- Python 3 compatibility fixes. [Richard Borcsik]

  Signed-off-by: Richard Borcsik <richard@borcsik.com>


- Add video signature to download url. [Alejandro Blanco]

  YouTube has changed the API a bit, now it requires the video signature
  in the download url.


- Pep8, pyflakes, fixed typos, better comments. [NFicano]

- Rearranged/cleaned up instructions. [NFicano]

- AND a typo.. [NFicano]

- Modified installation instructions to use pip. [NFicano]

- Fixed syntax error in setup.py. [NFicano]

- Fixed classifier section of setup.py. [NFicano]

- Copy changes to README. [NFicano]

- Added better exception handling, fixed a ton of bugs, added setup.py.
  [NFicano]

- Fixed typos and added bugs to README. [NFicano]

- Evaluate the status code and do nothing upon failure. [Lorenzo Gil
  Sanchez]

- Remove trailing whitespace. [Lorenzo Gil Sanchez]

- Bug fixes, added ability to specify output directory. [Nick Ficano]

  * added ability to specify an output directory.
  * added missing quality profiles.
  * handled exception when unexcepted quality profile returned.
  * videos now get sorted by quality profile.


- General housekeeping, no code modified. [Nick Ficano]

  * Added TODO
  * Added AUTHORS
  * Moved Licence agreement into COPYING.


- Removed my hardcoded path I had lazily set. [Nick Ficano]

- Renamed file sanitizing function. [Nick Ficano]

- Fixed bug causing filename to truncate word. [Nick Ficano]

  filename sanitizing function was causing the last word in the filename
  to get truncated.


- Minor project reorganizing. [Nick Ficano]

  * Moved project into subdirectory, preparing to write setup script.


- Cleanup, Pep8, finished docstring, 100% std lib. [Nick Ficano]

  * A bit of tidying some odds and ends.
  * Pep8
  * Finished docstrings
  * Removed ``requests`` dependency making it compatible out of the box
  * Rewrote filename sanitization method, also fixing unicode error.


- AH! forgot a trailing quote. [Nick Ficano]

- Cleaned up the README a tad. [Nick Ficano]

- Initial commit. [Nick Ficano]



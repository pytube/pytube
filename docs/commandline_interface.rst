Command-line interface
======================

pytube also ships with a tiny cli interface for downloading and probing
videos.

Let's start with downloading (it will download the mp4 stream with the
highest resolution by default):

.. code:: bash

    $ pytube https://www.youtube.com/watch?v=aqz-KE-bpKQ

To view available streams:

.. code:: bash

    $ pytube https://www.youtube.com/watch?v=aqz-KE-bpKQ --list

To download a specific stream, use the itag

.. code:: bash

    $ pytube https://www.youtube.com/watch?v=aqz-KE-bpKQ --itag=22

To get a list of all subtitles (caption codes)

.. code:: bash

    $ pytube -c -v https://www.youtube.com/watch?v=hsQi4ouYYzI

To get a download a specific subtitle (caption code) - in this case the
english subtitles (in srt format)

.. code:: bash

    $ pytube -c en https://www.youtube.com/watch?v=hsQi4ouYYzI

It is also possible to just download the audio stream (default AAC/mp4):

.. code:: bash

    $ pytube -a https://www.youtube.com/watch?v=zwkzf-KUNPM&list=PLCgv34KYzfJ7Y0ZSCQ0QQTCME5cA1E7ma

To list all command line options, simply type

.. code:: bash

    $ pytube --help


Finally, if you're filing a bug report, the cli contains a switch called
``--build-playback-report``, which bundles up the state, allowing others
to easily replay your issue.

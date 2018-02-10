from pytube.contrib.playlist import Playlist


class TestApp:
    playListUrl = "https://www.youtube.com/playlist?list=PLysK5kM8r78sJFo--opGDHCdTgNJTIb-o"

    def run(self):

        pl = Playlist(self.playListUrl)
        pl.register_on_start_callback(self.on_start)
        pl.register_on_progress_callback(self.show_progress_bar)
        pl.register_on_complete_callback(self.on_complete)
        pl.download_all(location='/Users/kemalturk/Desktop/test_videos')

    def on_start(self, count):
        print "Download Started."
        print "Video count : " + str(count)

    def show_progress_bar(self, stream, chunk, file_handle, bytes_remaining):

        total = stream.filesize
        downloaded = total - bytes_remaining
        percentage = (downloaded / (float(total))) * 100

        print(percentage)

    def on_complete(self, stream, filehandle):

        print("Download Completed.")


if __name__ == '__main__':

    TestApp().run()
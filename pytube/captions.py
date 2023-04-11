import math
import os
import time
import xml.etree.ElementTree as ElementTree
from html import unescape
from typing import Dict, Optional

from pytube import request
from pytube.helpers import safe_filename, target_directory


class Caption:
    """Container for caption tracks."""

    def __init__(self, caption_track: Dict):
        """Construct a :class:`Caption <Caption>`.

        :param dict caption_track:
            Caption track data extracted from ``watch_html``.
        """
        self.url = caption_track.get("baseUrl")

        # Certain videos have runs instead of simpleText
        #  this handles that edge case
        name_dict = caption_track['name']
        if 'simpleText' in name_dict:
            self.name = name_dict['simpleText']
        else:
            for el in name_dict['runs']:
                if 'text' in el:
                    self.name = el['text']

        # Use "vssId" instead of "languageCode", fix issue #779
        self.code = caption_track["vssId"]
        # Remove preceding '.' for backwards compatibility, e.g.:
        # English -> vssId: .en, languageCode: en
        # English (auto-generated) -> vssId: a.en, languageCode: en
        self.code = self.code.strip('.')

    @property
    def xml_captions(self) -> str:
        """Download the xml caption tracks."""
        return request.get(self.url)

    @property
    def json_captions(self) -> dict:
        """Download and parse the json caption tracks."""
        json_captions_url = self.url.replace('fmt=srv3','fmt=json3')
        text = request.get(json_captions_url)
        parsed = json.loads(text)
        assert parsed['wireMagic'] == 'pb3', 'Unexpected captions format'
        return parsed

    def generate_srt_captions(self) -> str:
        """Generate "SubRip Subtitle" captions.

        Takes the xml captions from :meth:`~pytube.Caption.xml_captions` and
        recompiles them into the "SubRip Subtitle" format.
        """
        return self.xml_caption_to_srt(self.xml_captions)

    @staticmethod
    def float_to_srt_time_format(d: float) -> str:
        """Convert decimal durations into proper srt format.

        :rtype: str
        :returns:
            SubRip Subtitle (str) formatted time duration.

        float_to_srt_time_format(3.89) -> '00:00:03,890'
        """
        fraction, whole = math.modf(d)
        time_fmt = time.strftime("%H:%M:%S,", time.gmtime(whole))
        ms = f"{fraction:.3f}".replace("0.", "")
        return time_fmt + ms

    def xml_caption_to_srt(self, xml_captions: str) -> str:
        """Convert xml caption tracks to "SubRip Subtitle (srt)".

        :param str xml_captions:
            XML formatted caption tracks.


        Bug fixed @2023-04-11 by tsaijamey@github :
        原代码运行时报错  KeyError 'start'，所以根据最新的xml进行了修正。
        xml的结构已经发生了变化，样例如下：
        ```
            <body>
                <w t="0" id="1" wp="1" ws="1"/>
                    <p t="60" d="6180" w="1">
                        <s ac="248">I</s>
                        <s t="599" ac="248"> created</s>
                        <s t="960" ac="248"> a</s>
                        <s t="1200" ac="248"> graphic</s>
                        <s t="1560" ac="248"> novel</s>
                        <s t="1860" ac="248"> using</s>
                        <s t="2400" ac="248"> nothing</s>
                    </p>
                    <p t="2690" d="3550" w="1" a="1">
                    </p>
                    <p t="2700" d="6720" w="1">
                        <s ac="248">but</s>
                        <s t="479" ac="248"> chat</s>
                        <s t="1140" ac="223"> GPT</s>
                        <s t="1700" ac="243"> mid-journey</s>
                        <s t="2700" ac="215"> and</s>
                        <s t="3240" ac="245"> Affinity</s>
                    </p>
                    <p t="6230" d="3190" w="1" a="1">
                    </p>
        ```
        不包含 a=1 的<p>表示的是整段字幕区域，<s>是该段字幕中每个单词出现的顺序和时间点；
        包含 a=1 的<p>标签表示的应该是字幕区域，它的t值对于生成srt文件没有意义。
        所以实际的时间轴解析应该是从不包含的<p>标签中获取每段字幕的起始时间t，并以下一段字幕的出现时间-1毫秒作为结束时间。
        -1毫秒的目的是让前后两段时间轴保持间隔，避免在使用字幕渲染时出现交叠情况。
        """
        segments = []
        root = ElementTree.fromstring(xml_captions)
        p_tags = root.findall('.//p')
        subtitles = []

        for p in p_tags:
            if p.get("a") is None:
                start_time = float(p.get("t"))
                subtitle_text = " ".join([s.text for s in p.findall("s") if s.text is not None])
                subtitle_text = subtitle_text.replace("  ", " ") + " "
                subtitles.append((start_time, subtitle_text))

        for i, (start_time, subtitle_text) in enumerate(subtitles):
            if i + 1 < len(subtitles):
                end_time = subtitles[i + 1][0] - 1
            else:
                end_time = start_time + int(subtitles[-1][0]) - 1

            sequence_number = i + 1  # convert from 0-indexed to 1.
            line = "{seq}\n{start} --> {end}\n{text}\n".format(
                seq=sequence_number,
                start=self.float_to_srt_time_format(start_time),
                end=self.float_to_srt_time_format(end_time),
                text=subtitle_text,
            )
            segments.append(line)

        return "\n".join(segments).strip()

    def download(
        self,
        title: str,
        srt: bool = True,
        output_path: Optional[str] = None,
        filename_prefix: Optional[str] = None,
    ) -> str:
        """Write the media stream to disk.

        :param title:
            Output filename (stem only) for writing media file.
            If one is not specified, the default filename is used.
        :type title: str
        :param srt:
            Set to True to download srt, false to download xml. Defaults to True.
        :type srt bool
        :param output_path:
            (optional) Output path for writing media file. If one is not
            specified, defaults to the current working directory.
        :type output_path: str or None
        :param filename_prefix:
            (optional) A string that will be prepended to the filename.
            For example a number in a playlist or the name of a series.
            If one is not specified, nothing will be prepended
            This is separate from filename so you can use the default
            filename but still add a prefix.
        :type filename_prefix: str or None

        :rtype: str
        """
        if title.endswith(".srt") or title.endswith(".xml"):
            filename = ".".join(title.split(".")[:-1])
        else:
            filename = title

        if filename_prefix:
            filename = f"{safe_filename(filename_prefix)}{filename}"

        filename = safe_filename(filename)

        filename += f" ({self.code})"

        if srt:
            filename += ".srt"
        else:
            filename += ".xml"

        file_path = os.path.join(target_directory(output_path), filename)

        with open(file_path, "w", encoding="utf-8") as file_handle:
            if srt:
                file_handle.write(self.generate_srt_captions())
            else:
                file_handle.write(self.xml_captions)

        return file_path

    def __repr__(self):
        """Printable object representation."""
        return '<Caption lang="{s.name}" code="{s.code}">'.format(s=self)

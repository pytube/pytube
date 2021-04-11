"""This module contains a lookup table of YouTube's itag values."""
from typing import Dict

PROGRESSIVE_VIDEO = {
    5: ("240p", "64kbps"),
    6: ("270p", "64kbps"),
    13: ("144p", None),
    17: ("144p", "24kbps"),
    18: ("360p", "96kbps"),
    22: ("720p", "192kbps"),
    34: ("360p", "128kbps"),
    35: ("480p", "128kbps"),
    36: ("240p", None),
    37: ("1080p", "192kbps"),
    38: ("3072p", "192kbps"),
    43: ("360p", "128kbps"),
    44: ("480p", "128kbps"),
    45: ("720p", "192kbps"),
    46: ("1080p", "192kbps"),
    59: ("480p", "128kbps"),
    78: ("480p", "128kbps"),
    82: ("360p", "128kbps"),
    83: ("480p", "128kbps"),
    84: ("720p", "192kbps"),
    85: ("1080p", "192kbps"),
    91: ("144p", "48kbps"),
    92: ("240p", "48kbps"),
    93: ("360p", "128kbps"),
    94: ("480p", "128kbps"),
    95: ("720p", "256kbps"),
    96: ("1080p", "256kbps"),
    100: ("360p", "128kbps"),
    101: ("480p", "192kbps"),
    102: ("720p", "192kbps"),
    132: ("240p", "48kbps"),
    151: ("720p", "24kbps"),
    300: ("720p", "128kbps"),
    301: ("1080p", "128kbps"),
}

DASH_VIDEO = {
    # DASH Video
    133: ("240p", None),  # MP4
    134: ("360p", None),  # MP4
    135: ("480p", None),  # MP4
    136: ("720p", None),  # MP4
    137: ("1080p", None),  # MP4
    138: ("2160p", None),  # MP4
    160: ("144p", None),  # MP4
    167: ("360p", None),  # WEBM
    168: ("480p", None),  # WEBM
    169: ("720p", None),  # WEBM
    170: ("1080p", None),  # WEBM
    212: ("480p", None),  # MP4
    218: ("480p", None),  # WEBM
    219: ("480p", None),  # WEBM
    242: ("240p", None),  # WEBM
    243: ("360p", None),  # WEBM
    244: ("480p", None),  # WEBM
    245: ("480p", None),  # WEBM
    246: ("480p", None),  # WEBM
    247: ("720p", None),  # WEBM
    248: ("1080p", None),  # WEBM
    264: ("1440p", None),  # MP4
    266: ("2160p", None),  # MP4
    271: ("1440p", None),  # WEBM
    272: ("4320p", None),  # WEBM
    278: ("144p", None),  # WEBM
    298: ("720p", None),  # MP4
    299: ("1080p", None),  # MP4
    302: ("720p", None),  # WEBM
    303: ("1080p", None),  # WEBM
    308: ("1440p", None),  # WEBM
    313: ("2160p", None),  # WEBM
    315: ("2160p", None),  # WEBM
    330: ("144p", None),  # WEBM
    331: ("240p", None),  # WEBM
    332: ("360p", None),  # WEBM
    333: ("480p", None),  # WEBM
    334: ("720p", None),  # WEBM
    335: ("1080p", None),  # WEBM
    336: ("1440p", None),  # WEBM
    337: ("2160p", None),  # WEBM
    394: ("144p", None),  # MP4
    395: ("240p", None),  # MP4
    396: ("360p", None),  # MP4
    397: ("480p", None),  # MP4
    398: ("720p", None),  # MP4
    399: ("1080p", None),  # MP4
    400: ("1440p", None),  # MP4
    401: ("2160p", None),  # MP4
    402: ("4320p", None),  # MP4
    571: ("4320p", None),  # MP4
}

DASH_AUDIO = {
    # DASH Audio
    139: (None, "48kbps"),  # MP4
    140: (None, "128kbps"),  # MP4
    141: (None, "256kbps"),  # MP4
    171: (None, "128kbps"),  # WEBM
    172: (None, "256kbps"),  # WEBM
    249: (None, "50kbps"),  # WEBM
    250: (None, "70kbps"),  # WEBM
    251: (None, "160kbps"),  # WEBM
    256: (None, "192kbps"),  # MP4
    258: (None, "384kbps"),  # MP4
    325: (None, None),  # MP4
    328: (None, None),  # MP4
}

ITAGS = {
    **PROGRESSIVE_VIDEO,
    **DASH_VIDEO,
    **DASH_AUDIO,
}

HDR = [330, 331, 332, 333, 334, 335, 336, 337]
_3D = [82, 83, 84, 85, 100, 101, 102]
LIVE = [91, 92, 93, 94, 95, 96, 132, 151]


def get_format_profile(itag: int) -> Dict:
    """Get additional format information for a given itag.

    :param str itag:
        YouTube format identifier code.
    """
    itag = int(itag)
    if itag in ITAGS:
        res, bitrate = ITAGS[itag]
    else:
        res, bitrate = None, None
    return {
        "resolution": res,
        "abr": bitrate,
        "is_live": itag in LIVE,
        "is_3d": itag in _3D,
        "is_hdr": itag in HDR,
        "is_dash": (
            itag in DASH_AUDIO
            or itag in DASH_VIDEO
        ),
    }

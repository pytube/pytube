"""
This module contains all logic necessary to decipher the signature.

YouTube's strategy to restrict downloading videos is to send a ciphered version
of the signature to the client, along with the decryption algorithm obfuscated
in JavaScript. For the clients to play the videos, JavaScript must take the
ciphered version, cycle it through a series of "transform functions," and then
signs the media URL with the output.

This module is responsible for (1) finding and extracting those "transform
functions" (2) maps them to Python equivalents and (3) taking the ciphered
signature and decoding it.

"""
import logging
import re
from itertools import chain
from typing import Any, Callable, Dict, List, Optional, Tuple

from pytube.exceptions import RegexMatchError
from pytube.helpers import cache, regex_search
from pytube.parser import find_object_from_startpoint, throttling_array_split

logger = logging.getLogger(__name__)


class Cipher:
    def __init__(self, js: str):
        self.transform_plan: List[str] = get_transform_plan(js)
        var_regex = re.compile(r"^\w+\W")
        var_match = var_regex.search(self.transform_plan[0])
        if not var_match:
            raise RegexMatchError(
                caller="__init__", pattern=var_regex.pattern
            )
        var = var_match.group(0)[:-1]
        self.transform_map = get_transform_map(js, var)
        self.js_func_patterns = [
            r"\w+\.(\w+)\(\w,(\d+)\)",
            r"\w+\[(\"\w+\")\]\(\w,(\d+)\)"
        ]

        self.throttling_plan = get_throttling_plan(js)
        self.throttling_array = get_throttling_function_array(js)

    def get_signature(self, ciphered_signature: str) -> str:
        """Decipher the signature.

        Taking the ciphered signature, applies the transform functions.

        :param str ciphered_signature:
            The ciphered signature sent in the ``player_config``.
        :rtype: str
        :returns:
            Decrypted signature required to download the media content.
        """
        signature = list(ciphered_signature)

        for js_func in self.transform_plan:
            name, argument = self.parse_function(js_func)  # type: ignore
            signature = self.transform_map[name](signature, argument)
            logger.debug(
                "applied transform function\n"
                "output: %s\n"
                "js_function: %s\n"
                "argument: %d\n"
                "function: %s",
                "".join(signature),
                name,
                argument,
                self.transform_map[name],
            )

        return "".join(signature)

    @cache
    def parse_function(self, js_func: str) -> Tuple[str, int]:
        """Parse the Javascript transform function.

        Break a JavaScript transform function down into a two element ``tuple``
        containing the function name and some integer-based argument.

        :param str js_func:
            The JavaScript version of the transform function.
        :rtype: tuple
        :returns:
            two element tuple containing the function name and an argument.

        **Example**:

        parse_function('DE.AJ(a,15)')
        ('AJ', 15)

        """
        logger.debug("parsing transform function")
        for pattern in self.js_func_patterns:
            regex = re.compile(pattern)
            parse_match = regex.search(js_func)
            if parse_match:
                fn_name, fn_arg = parse_match.groups()
                return fn_name, int(fn_arg)

        raise RegexMatchError(
            caller="parse_function", pattern="js_func_patterns"
        )


def get_initial_function_name(js: str) -> str:
    """Extract the name of the function responsible for computing the signature.
    :param str js:
        The contents of the base.js asset file.
    :rtype: str
    :returns:
        Function name from regex match
    """

    function_patterns = [
        r"\b[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*encodeURIComponent\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(",  # noqa: E501
        r"\b[a-zA-Z0-9]+\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*encodeURIComponent\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(",  # noqa: E501
        r'(?:\b|[^a-zA-Z0-9$])(?P<sig>[a-zA-Z0-9$]{2})\s*=\s*function\(\s*a\s*\)\s*{\s*a\s*=\s*a\.split\(\s*""\s*\)',  # noqa: E501
        r'(?P<sig>[a-zA-Z0-9$]+)\s*=\s*function\(\s*a\s*\)\s*{\s*a\s*=\s*a\.split\(\s*""\s*\)',  # noqa: E501
        r'(["\'])signature\1\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
        r"\.sig\|\|(?P<sig>[a-zA-Z0-9$]+)\(",
        r"yt\.akamaized\.net/\)\s*\|\|\s*.*?\s*[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*(?:encodeURIComponent\s*\()?\s*(?P<sig>[a-zA-Z0-9$]+)\(",  # noqa: E501
        r"\b[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(",  # noqa: E501
        r"\b[a-zA-Z0-9]+\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(",  # noqa: E501
        r"\bc\s*&&\s*a\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(",  # noqa: E501
        r"\bc\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(",  # noqa: E501
        r"\bc\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(",  # noqa: E501
    ]
    logger.debug("finding initial function name")
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            logger.debug("finished regex search, matched: %s", pattern)
            return function_match.group(1)

    raise RegexMatchError(
        caller="get_initial_function_name", pattern="multiple"
    )


def get_transform_plan(js: str) -> List[str]:
    """Extract the "transform plan".

    The "transform plan" is the functions that the ciphered signature is
    cycled through to obtain the actual signature.

    :param str js:
        The contents of the base.js asset file.

    **Example**:

    ['DE.AJ(a,15)',
    'DE.VR(a,3)',
    'DE.AJ(a,51)',
    'DE.VR(a,3)',
    'DE.kT(a,51)',
    'DE.kT(a,8)',
    'DE.VR(a,3)',
    'DE.kT(a,21)']
    """
    name = re.escape(get_initial_function_name(js))
    pattern = r"%s=function\(\w\){[a-z=\.\(\"\)]*;(.*);(?:.+)}" % name
    logger.debug("getting transform plan")
    return regex_search(pattern, js, group=1).split(";")


def get_transform_object(js: str, var: str) -> List[str]:
    """Extract the "transform object".

    The "transform object" contains the function definitions referenced in the
    "transform plan". The ``var`` argument is the obfuscated variable name
    which contains these functions, for example, given the function call
    ``DE.AJ(a,15)`` returned by the transform plan, "DE" would be the var.

    :param str js:
        The contents of the base.js asset file.
    :param str var:
        The obfuscated variable name that stores an object with all functions
        that descrambles the signature.

    **Example**:

    >>> get_transform_object(js, 'DE')
    ['AJ:function(a){a.reverse()}',
    'VR:function(a,b){a.splice(0,b)}',
    'kT:function(a,b){var c=a[0];a[0]=a[b%a.length];a[b]=c}']

    """
    pattern = r"var %s={(.*?)};" % re.escape(var)
    logger.debug("getting transform object")
    regex = re.compile(pattern, flags=re.DOTALL)
    transform_match = regex.search(js)
    if not transform_match:
        raise RegexMatchError(caller="get_transform_object", pattern=pattern)

    return transform_match.group(1).replace("\n", " ").split(", ")


def get_transform_map(js: str, var: str) -> Dict:
    """Build a transform function lookup.

    Build a lookup table of obfuscated JavaScript function names to the
    Python equivalents.

    :param str js:
        The contents of the base.js asset file.
    :param str var:
        The obfuscated variable name that stores an object with all functions
        that descrambles the signature.

    """
    transform_object = get_transform_object(js, var)
    mapper = {}
    for obj in transform_object:
        # AJ:function(a){a.reverse()} => AJ, function(a){a.reverse()}
        name, function = obj.split(":", 1)
        fn = map_functions(function)
        mapper[name] = fn
    return mapper


def get_throttling_function_name(js: str) -> str:
    """Extract the name of the function that computes the throttling parameter.

    :param str js:
        The contents of the base.js asset file.
    :rtype: str
    :returns:
        The name of the function used to compute the throttling parameter.
    """
    function_patterns = [
        # https://github.com/ytdl-org/youtube-dl/issues/29326#issuecomment-865985377
        # a.C&&(b=a.get("n"))&&(b=Dea(b),a.set("n",b))}};
        # In above case, `Dea` is the relevant function name
        r'''a\.C&&\(b=a\.get\("n"\)\)&&\(b=([^(]+)\(b\),a\.set\("n",b\)\)}};''',
    ]
    logger.debug('Finding throttling function name')
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            logger.debug("finished regex search, matched: %s", pattern)
            return function_match.group(1)

    raise RegexMatchError(
        caller="get_throttling_function_name", pattern="multiple"
    )


def get_throttling_function_code(js: str) -> str:
    """Extract the raw code for the throttling function.

    :param str js:
        The contents of the base.js asset file.
    :rtype: str
    :returns:
        The name of the function used to compute the throttling parameter.
    """
    # Begin by extracting the correct function name
    name = re.escape(get_throttling_function_name(js))

    # Identify where the function is defined
    pattern_start = r"%s=function\(\w\)" % name
    regex = re.compile(pattern_start)
    match = regex.search(js)

    # Extract the code within curly braces for the function itself, and merge any split lines
    code_lines_list = find_object_from_startpoint(js, match.span()[1]).split('\n')
    joined_lines = "".join(code_lines_list)

    # Prepend function definition (e.g. `Dea=function(a)`)
    return match.group(0) + joined_lines


def get_throttling_function_array(js: str) -> List[Any]:
    """Extract the "c" array.

    :param str js:
        The contents of the base.js asset file.
    :returns:
        The array of various integers, arrays, and functions.
    """
    raw_code = get_throttling_function_code(js)

    array_start = r",c=\["
    array_regex = re.compile(array_start)
    match = array_regex.search(raw_code)

    array_raw = find_object_from_startpoint(raw_code, match.span()[1]-1)
    str_array = throttling_array_split(array_raw)

    converted_array = []
    for el in str_array:
        try:
            converted_array.append(int(el))
            continue
        except ValueError:
            # Not an integer value.
            pass

        if el == 'null':
            converted_array.append(None)
            continue

        # if el == '"pop"':
        #    TODO: Figure out how this is meant to work. It's weird that it's a string

        if el.startswith('function'):
            mapper = (
                (r"{for\(\w=\(\w%\w\.length\+\w\.length\)%\w\.length;\w--;\)\w\.unshift\(\w.pop\(\)\)}", throttling_unshift),  # noqa:E501
                (r"{\w\.reverse\(\)}", reverse),
                (r"{\w\.push\(\w\)}", push),
                (r";var\s\w=\w\[0\];\w\[0\]=\w\[\w\];\w\[\w\]=\w}", swap),
            )

            found = False
            for pattern, fn in mapper:
                if re.search(pattern, el):
                    converted_array.append(fn)
                    found = True
            if found:
                continue

        converted_array.append(el)

    for i in range(len(str_array)):
        print(f'{str_array[i]}: {converted_array[i]}')


def get_throttling_plan(js: str):
    """Extract the "throttling plan".

    The "throttling plan" is a list of tuples used for calling functions
    in the c array. The first element of the tuple is the index of the
    function to call, and any remaining elements of the tuple are arguments
    to pass to that function.

    :param str js:
        The contents of the base.js asset file.
    :returns:
        The full function code for computing the throttlign parameter.
    """
    raw_code = get_throttling_function_code(js)

    transform_start = r"try{"
    plan_regex = re.compile(transform_start)
    match = plan_regex.search(raw_code)

    transform_plan_raw = find_object_from_startpoint(raw_code, match.span()[1]-1)

    # Steps are either c[x](c[y]) or c[x](c[y],c[z])
    step_start = r"c\[(\d+)\]\(c\[(\d+)\](,c(\[(\d+)\]))?\)"
    step_regex = re.compile(step_start)
    matches = step_regex.findall(transform_plan_raw)
    transform_steps = []
    for match in matches:
        if match[4] != '':
            transform_steps.append((match[0],match[1],match[4]))
        else:
            transform_steps.append((match[0],match[1]))

    return transform_steps


def reverse(arr: List, _: Optional[Any]):
    """Reverse elements in a list.

    This function is equivalent to:

    .. code-block:: javascript

        function(a, b) { a.reverse() }

    This method takes an unused ``b`` variable as their transform functions
    universally sent two arguments.

    **Example**:

    >>> reverse([1, 2, 3, 4])
    [4, 3, 2, 1]
    """
    return arr[::-1]


def splice(arr: List, b: int):
    """Add/remove items to/from a list.

    This function is equivalent to:

    .. code-block:: javascript

        function(a, b) { a.splice(0, b) }

    **Example**:

    >>> splice([1, 2, 3, 4], 2)
    [1, 2]
    """
    return arr[b:]


def swap(arr: List, b: int):
    """Swap positions at b modulus the list length.

    This function is equivalent to:

    .. code-block:: javascript

        function(a, b) { var c=a[0];a[0]=a[b%a.length];a[b]=c }

    **Example**:

    >>> swap([1, 2, 3, 4], 2)
    [3, 2, 1, 4]
    """
    r = b % len(arr)
    return list(chain([arr[r]], arr[1:r], [arr[0]], arr[r + 1 :]))


def push(d: list, e: Any):
    """Pushes an element onto a list."""
    d.append(e)
    return d


def throttling_mod_func(d: list, e: int):
    """Perform the modular function from the throttling array functions.

    In the javascript, the modular operation is as follows:
    e = (e % d.length + d.length) % d.length

    We simply translate this to python here.
    """
    return (e % len(d) + len(d)) % len(d)


def throttling_unshift(d: list, e: int):
    """Rotates the elements of the list to the right.

    In the javascript, the operation is as follows:
    for(e=(e%d.length+d.length)%d.length;e--;)d.unshift(d.pop())
    """
    e = throttling_mod_func(d, e)
    return d[0-e:] + d[:0-e]


def map_functions(js_func: str) -> Callable:
    """For a given JavaScript transform function, return the Python equivalent.

    :param str js_func:
        The JavaScript version of the transform function.
    """
    mapper = (
        # function(a){a.reverse()}
        (r"{\w\.reverse\(\)}", reverse),
        # function(a,b){a.splice(0,b)}
        (r"{\w\.splice\(0,\w\)}", splice),
        # function(a,b){var c=a[0];a[0]=a[b%a.length];a[b]=c}
        (r"{var\s\w=\w\[0\];\w\[0\]=\w\[\w\%\w.length\];\w\[\w\]=\w}", swap),
        # function(a,b){var c=a[0];a[0]=a[b%a.length];a[b%a.length]=c}
        (
            r"{var\s\w=\w\[0\];\w\[0\]=\w\[\w\%\w.length\];\w\[\w\%\w.length\]=\w}",
            swap,
        ),
    )

    for pattern, fn in mapper:
        if re.search(pattern, js_func):
            return fn
    raise RegexMatchError(caller="map_functions", pattern="multiple")

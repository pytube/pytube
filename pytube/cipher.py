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

from pytube.exceptions import ExtractError, RegexMatchError
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

        self.calculated_n = None

    def calculate_n(self, initial_n: list):
        """Converts n to the correct value to prevent throttling."""
        if self.calculated_n:
            return self.calculated_n

        # First, update all instances of 'b' with the list(initial_n)
        for i in range(len(self.throttling_array)):
            if self.throttling_array[i] == 'b':
                self.throttling_array[i] = initial_n

        for step in self.throttling_plan:
            curr_func = self.throttling_array[int(step[0])]
            if not callable(curr_func):
                logger.debug(f'{curr_func} is not callable.')
                logger.debug(f'Throttling array:\n{self.throttling_array}\n')
                raise ExtractError(f'{curr_func} is not callable.')

            first_arg = self.throttling_array[int(step[1])]

            if len(step) == 2:
                curr_func(first_arg)
            elif len(step) == 3:
                second_arg = self.throttling_array[int(step[2])]
                curr_func(first_arg, second_arg)

        self.calculated_n = ''.join(initial_n)
        return self.calculated_n

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
        # https://github.com/yt-dlp/yt-dlp/commit/48416bc4a8f1d5ff07d5977659cb8ece7640dcd8
        # var Bpa = [iha];
        # ...
        # a.C && (b = a.get("n")) && (b = Bpa[0](b), a.set("n", b),
        # Bpa.length || iha("")) }};
        # In the above case, `iha` is the relevant function name
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
    ]
    logger.debug('Finding throttling function name')
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            logger.debug("finished regex search, matched: %s", pattern)
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                        nfunc=re.escape(function_match.group(1))),
                    js
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]

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

    array_raw = find_object_from_startpoint(raw_code, match.span()[1] - 1)
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

        if el.startswith('"') and el.endswith('"'):
            # Convert e.g. '"abcdef"' to string without quotation marks, 'abcdef'
            converted_array.append(el[1:-1])
            continue

        if el.startswith('function'):
            mapper = (
                (r"{for\(\w=\(\w%\w\.length\+\w\.length\)%\w\.length;\w--;\)\w\.unshift\(\w.pop\(\)\)}", throttling_unshift),  # noqa:E501
                (r"{\w\.reverse\(\)}", throttling_reverse),
                (r"{\w\.push\(\w\)}", throttling_push),
                (r";var\s\w=\w\[0\];\w\[0\]=\w\[\w\];\w\[\w\]=\w}", throttling_swap),
                (r"case\s\d+", throttling_cipher_function),
                (r"\w\.splice\(0,1,\w\.splice\(\w,1,\w\[0\]\)\[0\]\)", throttling_nested_splice),  # noqa:E501
                (r";\w\.splice\(\w,1\)}", js_splice),
                (r"\w\.splice\(-\w\)\.reverse\(\)\.forEach\(function\(\w\){\w\.unshift\(\w\)}\)", throttling_prepend),  # noqa:E501
                (r"for\(var \w=\w\.length;\w;\)\w\.push\(\w\.splice\(--\w,1\)\[0\]\)}", throttling_reverse),  # noqa:E501
            )

            found = False
            for pattern, fn in mapper:
                if re.search(pattern, el):
                    converted_array.append(fn)
                    found = True
            if found:
                continue

        converted_array.append(el)

    # Replace null elements with array itself
    for i in range(len(converted_array)):
        if converted_array[i] is None:
            converted_array[i] = converted_array

    return converted_array


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

    transform_plan_raw = find_object_from_startpoint(raw_code, match.span()[1] - 1)

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


def throttling_reverse(arr: list):
    """Reverses the input list.

    Needs to do an in-place reversal so that the passed list gets changed.
    To accomplish this, we create a reversed copy, and then change each
    indvidual element.
    """
    reverse_copy = arr.copy()[::-1]
    for i in range(len(reverse_copy)):
        arr[i] = reverse_copy[i]


def throttling_push(d: list, e: Any):
    """Pushes an element onto a list."""
    d.append(e)


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
    new_arr = d[-e:] + d[:-e]
    d.clear()
    for el in new_arr:
        d.append(el)


def throttling_cipher_function(d: list, e: str):
    """This ciphers d with e to generate a new list.

    In the javascript, the operation is as follows:
    var h = [A-Za-z0-9-_], f = 96;  // simplified from switch-case loop
    d.forEach(
        function(l,m,n){
            this.push(
                n[m]=h[
                    (h.indexOf(l)-h.indexOf(this[m])+m-32+f--)%h.length
                ]
            )
        },
        e.split("")
    )
    """
    h = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')
    f = 96
    # by naming it "this" we can more closely reflect the js
    this = list(e)

    # This is so we don't run into weirdness with enumerate while
    #  we change the input list
    copied_list = d.copy()

    for m, l in enumerate(copied_list):
        bracket_val = (h.index(l) - h.index(this[m]) + m - 32 + f) % len(h)
        this.append(
            h[bracket_val]
        )
        d[m] = h[bracket_val]
        f -= 1


def throttling_nested_splice(d: list, e: int):
    """Nested splice function in throttling js.

    In the javascript, the operation is as follows:
    function(d,e){
        e=(e%d.length+d.length)%d.length;
        d.splice(
            0,
            1,
            d.splice(
                e,
                1,
                d[0]
            )[0]
        )
    }

    While testing, all this seemed to do is swap element 0 and e,
    but the actual process is preserved in case there was an edge
    case that was not considered.
    """
    e = throttling_mod_func(d, e)
    inner_splice = js_splice(
        d,
        e,
        1,
        d[0]
    )
    js_splice(
        d,
        0,
        1,
        inner_splice[0]
    )


def throttling_prepend(d: list, e: int):
    """

    In the javascript, the operation is as follows:
    function(d,e){
        e=(e%d.length+d.length)%d.length;
        d.splice(-e).reverse().forEach(
            function(f){
                d.unshift(f)
            }
        )
    }

    Effectively, this moves the last e elements of d to the beginning.
    """
    start_len = len(d)
    # First, calculate e
    e = throttling_mod_func(d, e)

    # Then do the prepending
    new_arr = d[-e:] + d[:-e]

    # And update the input list
    d.clear()
    for el in new_arr:
        d.append(el)

    end_len = len(d)
    assert start_len == end_len


def throttling_swap(d: list, e: int):
    """Swap positions of the 0'th and e'th elements in-place."""
    e = throttling_mod_func(d, e)
    f = d[0]
    d[0] = d[e]
    d[e] = f


def js_splice(arr: list, start: int, delete_count=None, *items):
    """Implementation of javascript's splice function.

    :param list arr:
        Array to splice
    :param int start:
        Index at which to start changing the array
    :param int delete_count:
        Number of elements to delete from the array
    :param *items:
        Items to add to the array

    Reference: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/splice  # noqa:E501
    """
    # Special conditions for start value
    try:
        if start > len(arr):
            start = len(arr)
        # If start is negative, count backwards from end
        if start < 0:
            start = len(arr) - start
    except TypeError:
        # Non-integer start values are treated as 0 in js
        start = 0

    # Special condition when delete_count is greater than remaining elements
    if not delete_count or delete_count >= len(arr) - start:
        delete_count = len(arr) - start  # noqa: N806

    deleted_elements = arr[start:start + delete_count]

    # Splice appropriately.
    new_arr = arr[:start] + list(items) + arr[start + delete_count:]

    # Replace contents of input array
    arr.clear()
    for el in new_arr:
        arr.append(el)

    return deleted_elements


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

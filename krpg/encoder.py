import base64
from enum import Enum
from typing import Any, Callable
import zlib

import msgpack  # type: ignore


class AvailableEncodings(Enum):
    BASE871 = "base871"
    BASE161 = "base161"
    BASE93 = "base93"
    BRAILLE = "Braille"

    BASE64 = "base64"
    BASE32 = "base32"
    BASE85 = "base85"


DEFAULT = AvailableEncodings.BASE64

CUSTOM_ENCODINGS = {
    AvailableEncodings.BASE871: (
        "ƸƨǽƩҩΫеÙʘčΝϾĩ0Ê'=ңwǻSīǅҚҡǢəcƵΜʡŹǟǭÁĆɻЇ3Аǔɿ²ȅчɔщȳÖΟĳɲōǵ[ҥXɖʓɭƎŽƏɘҝɨ"
        "ƥtțśѩбҘЕșăhőáѸɫґäϧíBÅK&ŕƌ§нǩҠʫQфƲǒŜιD>ǦРΑϚЀǍΦш1ǨěϳǝѮȺÉêǊňϰϲģʞ;ЬȆХОяĉ"
        "ŦɾϟÏҎťĤŇɊsû#ëƀAѤϮŻ/ŮǶʑ¨¶ǲҞΛʍиmЄµǧUĪΪ¼ƮǛʒ]ЎϻåǼġЉδҜƃšƭβĄѧυкЖжџgƚŐʪэ`ȇ@"
        "{¿ВɤĻҒȵЧȏΨª÷ǏǑJ,ŪƕɚîóΒýΖüȑÑĐȩŀЊФѪ7ǂΰƣŬάĊİќǴЙКėǮǳϯϿǱŔȶèǤȚ£æǿȈɏɮɄҌÆϫƇŌ"
        "ʊТѦȀĖ\u03a2ЦȤѓ.ϡҀʌŞЪùŶҕĢįƾБѭr<ʝѬʖƹɷƴϕŖȯĲȔʐŧĥјНŢÞůʕʄWÈìľϋЗρƤюņʗ®űõξҋF"
        "ɦÐéЭіńαɌǄũĹ)ѰЯɶ»ϏʇΘ҂ωơžʃϸϷôȴȾłƊǌђȂϜ6ËøǷğɍѨïnȎΓєÚʜуÝҢόϦɼκϢyēɴΕϠоѷѴĎöǎ"
        "ÌѾaȡȮȐʦЩßNŃĕǘʢH*ÍĀλГƘɕĵʉɐѺɛȿИЫŒѻǠϊѵǙųŁǞМĺÂ\\ƉΤҤϬØLư9ўȧϩ5iţɠɳѱДǣъȽ¾ɒЍ"
        "ŷдʂƗΞћьŉđpΏϥзΥŝϹҙuȰ+ʣ?ȨĠϱεрȍvĒɟ«ѐŰɆпɋЈШȪĜÛΧПѶʠɰĦϼҖÕ³ϤČȄĿ%ƆĘƓїϙқÇɗΔĂɃ"
        "ɹЂѼѕzҊѣÔɜϒ¹ÓŭѫҭąƖƪĬȞÃƱðĶ°úɂɀęϭƅřƝƠȁɝȱϺÀǜƔҨχȌŚϘыRÎàηkŅҫʤѿœνƙɵɞϓǉċĚȓǥƯ"
        "ƐϣʁѢŋοϨɽĭѡGцлΙвɇφҔɧjCμҐƜɺЌʩϑǐYήέ½ѹĴƿEþʛƬϐ©ȝ¡ǸҁғǪȼǹlϵϗЏΩɉƞΣĽǾǗʀЃЛҧqȻş"
        "ΎώūǺŸ!ǕѲҍǫǋķʬǬг·ҟҗŲљƟżfŨĝϛѽ8ɬЮτπтÄTòŠʨхŗʎҦʈ2ĈĨŎMСZѯâƳȬ^ÒĔɅPƑψȸȋħɸмȖŤ"
        'Ɓ±ȟɈ¦ƂÿΚ¥ϖѝb-϶ɱ$ǈѥƫʅ¤ÜŘȫƋxçɥʚɓďςƻāθOǖɎΗʆЅΐ"Ћźǡ¯Ё_ȷȊǆļйʥσʙγĞϽoƶѳǯñȃ¢ŏ'
        "ŴȠȲʟãȒ}ǓºǚƈʭёѠҏǰ(ȭњVĮȦίȉĸȕϪζсȹ~Ҫȥ:ŵІƢʧҬϔƒаǁϞćƺI4ȘdΡУΠɢ¬ȗŊǇϝeƛϴύ"
    ),
    AvailableEncodings.BASE161: (
        "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ["
        "\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ЁАБВГДЕЖЗИЙКЛМНОПРСТУФХЦ"
        "ЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюяё№"
    ),
    AvailableEncodings.BASE93: ("!#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~"),
    AvailableEncodings.BRAILLE: (
        "⠀⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫⠬⠭⠮⠯⠰⠱⠲⠳⠴⠵⠶⠷⠸⠹⠺⠻⠼⠽⠾⠿⡀⡁⡂⡃⡄⡅⡆⡇⡈⡉"
        "⡊⡋⡌⡍⡎⡏⡐⡑⡒⡓⡔⡕⡖⡗⡘⡙⡚⡛⡜⡝⡞⡟⡠⡡⡢⡣⡤⡥⡦⡧⡨⡩⡪⡫⡬⡭⡮⡯⡰⡱⡲⡳⡴⡵⡶⡷⡸⡹⡺⡻⡼⡽⡾⡿⢀⢁⢂⢃⢄⢅⢆⢇⢈⢉⢊⢋⢌⢍⢎⢏⢐⢑⢒⢓"
        "⢔⢕⢖⢗⢘⢙⢚⢛⢜⢝⢞⢟⢠⢡⢢⢣⢤⢥⢦⢧⢨⢩⢪⢫⢬⢭⢮⢯⢰⢱⢲⢳⢴⢵⢶⢷⢸⢹⢺⢻⢼⢽⢾⢿⣀⣁⣂⣃⣄⣅⣆⣇⣈⣉⣊⣋⣌⣍⣎⣏⣐⣑⣒⣓⣔⣕⣖⣗⣘⣙⣚⣛⣜⣝⣞"
        "⣟⣠⣡⣢⣣⣤⣥⣦⣧⣨⣩⣪⣫⣬⣭⣮⣯⣰⣱⣲⣳⣴⣵⣶⣷⣸⣹⣺⣻⣼⣽⣾⣿"
    ),
}

STD_ENCODINGS: dict[AvailableEncodings, tuple[Callable[[bytes], bytes], Callable[[bytes], bytes]]] = {
    AvailableEncodings.BASE64: (base64.b64encode, base64.b64decode),
    AvailableEncodings.BASE32: (base64.b32encode, base64.b32decode),
    AvailableEncodings.BASE85: (base64.b85encode, base64.b85decode),
}


def encode_base(data: bytes, alphabet: str) -> str:
    num = int.from_bytes(data, "big")
    base = len(alphabet)
    out: list[str] = []
    while num:
        num, rem = divmod(num, base)
        out.append(alphabet[rem])
    return "".join(reversed(out)) or alphabet[0]


def decode_base(encoded: str, alphabet: str) -> bytes:
    base = len(alphabet)
    num = 0
    for char in encoded:
        num = num * base + alphabet.index(char)
    return num.to_bytes((num.bit_length() + 7) // 8, "big")


def basic_encode(data: bytes, encode_type: AvailableEncodings = DEFAULT) -> str:
    if encode_type in STD_ENCODINGS:
        encode_func, _ = STD_ENCODINGS[encode_type]
        return encode_func(data).decode()
    if encode_type in CUSTOM_ENCODINGS:
        alphabet = CUSTOM_ENCODINGS[encode_type]
        return encode_base(data, alphabet)
    else:
        raise ValueError(f"Unsupported encoding type: {encode_type}")


def basic_decode(data: str, encode_type: AvailableEncodings = DEFAULT) -> bytes:
    if encode_type in STD_ENCODINGS:
        _, decode_func = STD_ENCODINGS[encode_type]
        return decode_func(data.encode())
    if encode_type in CUSTOM_ENCODINGS:
        alphabet = CUSTOM_ENCODINGS[encode_type]
        return decode_base(data, alphabet)
    else:
        raise ValueError(f"Unsupported encoding type: {encode_type}")


CHUNK_SIZE = 512  # размер чанка в байтах
LEN_FIELD_SIZE = 4  # hex-длина: 4 символа = до 65535 символов на чанк


def chunked_encode(data: bytes, encode_type: AvailableEncodings = DEFAULT) -> str:
    out: list[str] = []
    for i in range(0, len(data), CHUNK_SIZE):
        chunk = data[i : i + CHUNK_SIZE]
        encoded = basic_encode(chunk, encode_type)
        out.append(f"{len(encoded):0{LEN_FIELD_SIZE}x}{encoded}")
    return "".join(out)


def chunked_decode(data: str, encode_type: AvailableEncodings = DEFAULT) -> bytes:
    out = bytearray()
    i = 0
    while i < len(data):
        len_chunk = int(data[i : i + LEN_FIELD_SIZE], 16)
        i += LEN_FIELD_SIZE
        encoded_chunk = data[i : i + len_chunk]
        i += len_chunk
        out.extend(basic_decode(encoded_chunk, encode_type))
    return bytes(out)


def create_save(data: Any, encode_type: AvailableEncodings = DEFAULT) -> str:
    packed: bytes = msgpack.dumps(data)  # type: ignore
    compressed = zlib.compress(packed)
    return chunked_encode(compressed, encode_type)


def load_save(data: str, encode_type: AvailableEncodings = DEFAULT) -> Any:
    decoded = chunked_decode(data, encode_type)
    decompressed = zlib.decompress(decoded)
    return msgpack.loads(decompressed)  # type: ignore

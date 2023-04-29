from math import ceil


class Encoder:
    abc = {
        'base871': (
            'ƸƨǽƩҩΫеÙʘčΝϾĩ0Ê\'=ңwǻSīǅҚҡǢəcƵΜʡŹǟǭÁĆɻЇ3Аǔɿ²ȅчɔщȳÖΟĳɲōǵ[ҥXɖʓɭƎŽƏɘҝɨ'
            'ƥtțśѩбҘЕșăhőáѸɫґäϧíBÅK&ŕƌ§нǩҠʫQфƲǒŜιD>ǦРΑϚЀǍΦш1ǨěϳǝѮȺÉêǊňϰϲģʞ;ЬȆХОяĉ'
            'ŦɾϟÏҎťĤŇɊsû#ëƀAѤϮŻ/ŮǶʑ¨¶ǲҞΛʍиmЄµǧUĪΪ¼ƮǛʒ]ЎϻåǼġЉδҜƃšƭβĄѧυкЖжџgƚŐʪэ`ȇ@'
            '{¿ВɤĻҒȵЧȏΨª÷ǏǑJ,ŪƕɚîóΒýΖüȑÑĐȩŀЊФѪ7ǂΰƣŬάĊİќǴЙКėǮǳϯϿǱŔȶèǤȚ£æǿȈɏɮɄҌÆϫƇŌ'
            'ʊТѦȀĖ\u03a2ЦȤѓ.ϡҀʌŞЪùŶҕĢįƾБѭr<ʝѬʖƹɷƴϕŖȯĲȔʐŧĥјНŢÞůʕʄWÈìľϋЗρƤюņʗ®űõξҋF'
            'ɦÐéЭіńαɌǄũĹ)ѰЯɶ»ϏʇΘ҂ωơžʃϸϷôȴȾłƊǌђȂϜ6ËøǷğɍѨïnȎΓєÚʜуÝҢόϦɼκϢyēɴΕϠоѷѴĎöǎ'
            'ÌѾaȡȮȐʦЩßNŃĕǘʢH*ÍĀλГƘɕĵʉɐѺɛȿИЫŒѻǠϊѵǙųŁǞМĺÂ\\ƉΤҤϬØLư9ўȧϩ5iţɠɳѱДǣъȽ¾ɒЍ'
            'ŷдʂƗΞћьŉđpΏϥзΥŝϹҙuȰ+ʣ?ȨĠϱεрȍvĒɟ«ѐŰɆпɋЈШȪĜÛΧПѶʠɰĦϼҖÕ³ϤČȄĿ%ƆĘƓїϙқÇɗΔĂɃ'
            'ɹЂѼѕzҊѣÔɜϒ¹ÓŭѫҭąƖƪĬȞÃƱðĶ°úɂɀęϭƅřƝƠȁɝȱϺÀǜƔҨχȌŚϘыRÎàηkŅҫʤѿœνƙɵɞϓǉċĚȓǥƯ'
            'ƐϣʁѢŋοϨɽĭѡGцлΙвɇφҔɧjCμҐƜɺЌʩϑǐYήέ½ѹĴƿEþʛƬϐ©ȝ¡ǸҁғǪȼǹlϵϗЏΩɉƞΣĽǾǗʀЃЛҧqȻş'
            'ΎώūǺŸ!ǕѲҍǫǋķʬǬг·ҟҗŲљƟżfŨĝϛѽ8ɬЮτπтÄTòŠʨхŗʎҦʈ2ĈĨŎMСZѯâƳȬ^ÒĔɅPƑψȸȋħɸмȖŤ'
            'Ɓ±ȟɈ¦ƂÿΚ¥ϖѝb-϶ɱ$ǈѥƫʅ¤ÜŘȫƋxçɥʚɓďςƻāθOǖɎΗʆЅΐ"Ћźǡ¯Ё_ȷȊǆļйʥσʙγĞϽoƶѳǯñȃ¢ŏ'
            'ŴȠȲʟãȒ}ǓºǚƈʭёѠҏǰ(ȭњVĮȦίȉĸȕϪζсȹ~Ҫȥ:ŵІƢʧҬϔƒаǁϞćƺI4ȘdΡУΠɢ¬ȗŊǇϝeƛϴύ'
        ),
        'base161': (
            "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ["
            "\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ЁАБВГДЕЖЗИЙКЛМНОПРСТУФХЦ"
            "ЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюяё№"
        ),
        'base64': "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
        'base85': "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~",
        'base93': "!#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~",
        'Braille': (
            "⠀⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫⠬⠭⠮⠯⠰⠱⠲⠳⠴⠵⠶⠷⠸⠹⠺⠻⠼⠽⠾⠿⡀⡁⡂⡃⡄⡅⡆⡇⡈⡉"
            "⡊⡋⡌⡍⡎⡏⡐⡑⡒⡓⡔⡕⡖⡗⡘⡙⡚⡛⡜⡝⡞⡟⡠⡡⡢⡣⡤⡥⡦⡧⡨⡩⡪⡫⡬⡭⡮⡯⡰⡱⡲⡳⡴⡵⡶⡷⡸⡹⡺⡻⡼⡽⡾⡿⢀⢁⢂⢃⢄⢅⢆⢇⢈⢉⢊⢋⢌⢍⢎⢏⢐⢑⢒⢓"
            "⢔⢕⢖⢗⢘⢙⢚⢛⢜⢝⢞⢟⢠⢡⢢⢣⢤⢥⢦⢧⢨⢩⢪⢫⢬⢭⢮⢯⢰⢱⢲⢳⢴⢵⢶⢷⢸⢹⢺⢻⢼⢽⢾⢿⣀⣁⣂⣃⣄⣅⣆⣇⣈⣉⣊⣋⣌⣍⣎⣏⣐⣑⣒⣓⣔⣕⣖⣗⣘⣙⣚⣛⣜⣝⣞"
            "⣟⣠⣡⣢⣣⣤⣥⣦⣧⣨⣩⣪⣫⣬⣭⣮⣯⣰⣱⣲⣳⣴⣵⣶⣷⣸⣹⣺⣻⣼⣽⣾⣿"
        ), 
    }
         
    def encode(self, data, type=1, base=None):
        abc = self.abc[type]
        base = base if base else len(abc)
        out_data = []
        in_data = int.from_bytes(b"\x01" + data, "big")
        d, r = in_data % base, in_data // base
        out_data.append(abc[d])
        while r:
            d, r = r % base, r // base
            out_data.append(abc[d])
        return "".join(out_data)

    def decode(self, data, type=1, base=None):
        abc = self.abc[type]
        base = base if base else len(abc)
        out_data = 0
        for i, ch in enumerate(data):
            out_data = abc.index(ch) * (base**i) + out_data
        return out_data.to_bytes(ceil(out_data.bit_length() / 8), "big")[1:]

    def __repr__(self):
        return f"<Encoder codes={len(self.abc)}>"

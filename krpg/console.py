import datetime
import os
import random
import re
import shlex
import sys
import time


class Console:
    def __init__(self, color=True):

        os.system("")  # enable VT100
        self.color = color
        self.queue = []
        self.theme = "GitHub Dark"
        self.themes = """["'3024 Day' 090300 db2d20 01a252 fded02 01a0e4 a16a94 b5e4f4 a5a2a2 5c5855 e8bbd0 3a3432 4a4543 807d7c d6d5d4 cdab53 f7f7f7", "'3024 Night' 090300 db2d20 01a252 fded02 01a0e4 a16a94 b5e4f4 a5a2a2 5c5855 e8bbd0 3a3432 4a4543 807d7c d6d5d4 cdab53 f7f7f7", "'Abernathy' 000000 cd0000 00cd00 cdcd00 1093f5 cd00cd 00cdcd faebd7 404040 ff0000 00ff00 ffff00 11b5f6 ff00ff 00ffff ffffff", "'Adventure' 040404 d84a33 5da602 eebb6e 417ab3 e5c499 bdcfe5 dbded8 685656 d76b42 99b52c ffb670 97d7ef aa7900 bdcfe5 e4d5c7", "'AdventureTime' 050404 bd0013 4ab118 e7741e 0f4ac6 665993 70a598 f8dcc0 4e7cbf fc5f5a 9eff6e efc11a 1997c6 9b5953 c8faf4 f6f5fb", "'Afterglow' 151515 ac4142 7e8e50 e5b567 6c99bb 9f4e85 7dd6cf d0d0d0 505050 ac4142 7e8e50 e5b567 6c99bb 9f4e85 7dd6cf f5f5f5", "'Alabaster' 000000 aa3731 448c27 cb9000 325cc0 7a3e9d 0083b2 f7f7f7 777777 f05050 60cb00 ffbc5d 007acc e64ce6 00aacb f7f7f7", "'AlienBlood' 112616 7f2b27 2f7e25 717f24 2f6a7f 47587f 327f77 647d75 3c4812 e08009 18e000 bde000 00aae0 0058e0 00e0c4 73fa91", "'Andromeda' 000000 cd3131 05bc79 e5e512 2472c8 bc3fbc 0fa8cd e5e5e5 666666 cd3131 05bc79 e5e512 2472c8 bc3fbc 0fa8cd e5e5e5", "'arcoiris' 333333 da2700 12c258 ffc656 518bfc e37bd9 63fad5 bab2b2 777777 ffb9b9 e3f6aa ffddaa b3e8f3 cbbaf9 bcffc7 efefef", "'Argonaut' 232323 ff000f 8ce10b ffb900 008df8 6d43a6 00d8eb ffffff 444444 ff2740 abe15b ffd242 0092ff 9a5feb 67fff0 ffffff", "'Arthur' 3d352a cd5c5c 86af80 e8ae5b 6495ed deb887 b0c4de bbaa99 554444 cc5533 88aa22 ffa75d 87ceeb 996600 b0c4de ddccbb", "'AtelierSulphurpool' 202746 c94922 ac9739 c08b30 3d8fd1 6679cc 22a2c9 979db4 6b7394 c76b29 293256 5e6687 898ea4 dfe2f1 9c637a f5f7ff", "'Atom' 000000 fd5ff1 87c38a ffd7b1 85befd b9b6fc 85befd e0e0e0 000000 fd5ff1 94fa36 f5ffa8 96cbfe b9b6fc 85befd e0e0e0", "'AtomOneLight' 000000 de3e35 3f953a d2b67c 2f5af3 950095 3f953a bbbbbb 000000 de3e35 3f953a d2b67c 2f5af3 a00095 3f953a ffffff", "'Aurora' 23262e f0266f 8fd46d ffe66d 0321d7 ee5d43 03d6b8 c74ded 292e38 f92672 8fd46d ffe66d 03d6b8 ee5d43 03d6b8 c74ded", "'ayu' 000000 ff3333 b8cc52 e7c547 36a3d9 f07178 95e6cb ffffff 323232 ff6565 eafe84 fff779 68d5ff ffa3aa c7fffd ffffff", "'Ayu Mirage' 191e2a ed8274 a6cc70 fad07b 6dcbfa cfbafa 90e1c6 c7c7c7 686868 f28779 bae67e ffd580 73d0ff d4bfff 95e6cb ffffff", "'ayu_light' 000000 ff3333 86b300 f29718 41a6d9 f07178 4dbf99 ffffff 323232 ff6565 b8e532 ffc94a 73d8ff ffa3aa 7ff1cb ffffff", "'Banana Blueberry' 17141f ff6b7f 00bd9c e6c62f 22e8df dc396a 56b6c2 f1f1f1 495162 fe9ea1 98c379 f9e46b 91fff4 da70d6 bcf3ff ffffff", "'Batman' 1b1d1e e6dc44 c8be46 f4fd22 737174 747271 62605f c6c5bf 505354 fff78e fff27d feed6c 919495 9a9a9d a3a3a6 dadbd6", "'Belafonte Day' 20111b be100e 858162 eaa549 426a79 97522c 989a9c 968c83 5e5252 be100e 858162 eaa549 426a79 97522c 989a9c d5ccba", "'Belafonte Night' 20111b be100e 858162 eaa549 426a79 97522c 989a9c 968c83 5e5252 be100e 858162 eaa549 426a79 97522c 989a9c d5ccba", "'BirdsOfParadise' 573d26 be2d26 6ba18a e99d2a 5a86ad ac80a6 74a6ad e0dbb7 9b6c4a e84627 95d8ba d0d150 b8d3ed d19ecb 93cfd7 fff9d5", "'Blazer' 000000 b87a7a 7ab87a b8b87a 7a7ab8 b87ab8 7ab8b8 d9d9d9 262626 dbbdbd bddbbd dbdbbd bdbddb dbbddb bddbdb ffffff", "'Blue Matrix' 101116 ff5680 00ff9c fffc58 00b0ff d57bff 76c1ff c7c7c7 686868 ff6e67 5ffa68 fffc67 6871ff d682ec 60fdff ffffff", "'BlueBerryPie' 0a4c62 99246e 5cb1b3 eab9a8 90a5bd 9d54a7 7e83cc f0e8d6 201637 c87272 0a6c7e 7a3188 39173d bc94b7 5e6071 0a6c7e", "'BlueDolphin' 292d3e ff8288 b4e88d f4d69f 82aaff e9c1ff 89ebff d0d0d0 434758 ff8b92 ddffa7 ffe585 9cc4ff ddb0f6 a3f7ff ffffff", "'BlulocoDark' 41444d fc2f52 25a45c ff936a 3476ff 7a82da 4483aa cdd4e0 8f9aae ff6480 3fc56b f9c859 10b1fe ff78f8 5fb9bc ffffff", "'BlulocoLight' 373a41 d52753 23974a df631c 275fe4 823ff1 27618d babbc2 676a77 ff6480 3cbc66 c5a332 0099e1 ce33c0 6d93bb d3d3d3", "'Borland' 4f4f4f ff6c60 a8ff60 ffffb6 96cbfe ff73fd c6c5fe eeeeee 7c7c7c ffb6b0 ceffac ffffcc b5dcff ff9cfe dfdffe ffffff", "'Breeze' 31363b ed1515 11d116 f67400 1d99f3 9b59b6 1abc9c eff0f1 7f8c8d c0392b 1cdc9a fdbc4b 3daee9 8e44ad 16a085 fcfcfc", "'Bright Lights' 191919 ff355b b7e876 ffc251 76d4ff ba76e7 6cbfb5 c2c8d7 191919 ff355b b7e876 ffc251 76d5ff ba76e7 6cbfb5 c2c8d7", "'Broadcast' 000000 da4939 519f50 ffd24a 6d9cbe d0d0ff 6e9cbe ffffff 323232 ff7b6b 83d182 ffff7c 9fcef0 ffffff a0cef0 ffffff", "'Brogrammer' 1f1f1f f81118 2dc55e ecba0f 2a84d2 4e5ab7 1081d6 d6dbe5 d6dbe5 de352e 1dd361 f3bd09 1081d6 5350b9 0f7ddb ffffff", "'Bubbles' 000000 589DF6 1F9EE7 21B089 944D95 F9555F BBBBBB FEF02A 555555 589DF6 3979BC 35BB9A E75699 FA8C8F FFFFFF FFFF55", "'Builtin Dark' 000000 bb0000 00bb00 bbbb00 0000bb bb00bb 00bbbb bbbbbb 555555 ff5555 55ff55 ffff55 5555ff ff55ff 55ffff ffffff", "'Builtin Light' 000000 bb0000 00bb00 bbbb00 0000bb bb00bb 00bbbb bbbbbb 555555 ff5555 55ff55 ffff55 5555ff ff55ff 55ffff ffffff", "'Builtin Pastel Dark' 4f4f4f ff6c60 a8ff60 ffffb6 96cbfe ff73fd c6c5fe eeeeee 7c7c7c ffb6b0 ceffac ffffcc b5dcff ff9cfe dfdffe ffffff", "'Builtin Solarized Dark' 073642 dc322f 859900 b58900 268bd2 d33682 2aa198 eee8d5 002b36 cb4b16 586e75 657b83 839496 6c71c4 93a1a1 fdf6e3", "'Builtin Solarized Light' 073642 dc322f 859900 b58900 268bd2 d33682 2aa198 eee8d5 002b36 cb4b16 586e75 657b83 839496 6c71c4 93a1a1 fdf6e3", "'Builtin Tango Dark' 000000 cc0000 4e9a06 c4a000 3465a4 75507b 06989a d3d7cf 555753 ef2929 8ae234 fce94f 729fcf ad7fa8 34e2e2 eeeeec", "'Builtin Tango Light' 000000 cc0000 4e9a06 c4a000 3465a4 75507b 06989a d3d7cf 555753 ef2929 8ae234 fce94f 729fcf ad7fa8 34e2e2 eeeeec", "'C64' 090300 883932 55a049 bfce72 40318d 8b3f96 67b6bd ffffff 000000 883932 55a049 bfce72 40318d 8b3f96 67b6bd f7f7f7", "'Calamity' 2f2833 fc644d a5f69c e9d7a5 3b79c7 f92672 74d3de d5ced9 7e6c88 fc644d a5f69c e9d7a5 3b79c7 f92672 74d3de ffffff", "'Catppuccin Frappe' 51576d e78284 a6d189 e5c890 8caaee f4b8e4 81c8be b5bfe2 626880 e78284 a6d189 e5c890 8caaee f4b8e4 81c8be a5adce", "'Catppuccin Latte' 5c5f77 d20f39 40a02b df8e1d 1e66f5 ea76cb 179299 acb0be 6c6f85 d20f39 40a02b df8e1d 1e66f5 ea76cb 179299 bcc0cc", "'Catppuccin Macchiato' 494d64 ed8796 a6da95 eed49f 8aadf4 f5bde6 8bd5ca b8c0e0 5b6078 ed8796 a6da95 eed49f 8aadf4 f5bde6 8bd5ca b8c0e0", "'Catppuccin Mocha' 45475a f38ba8 a6e3a1 f9e2af 89b4fa f5c2e7 94e2d5 bac2de 585b70 f38ba8 a6e3a1 f9e2af 89b4fa f5c2e7 94e2d5 a6adc8", "'CGA' 000000 aa0000 00aa00 aa5500 0000aa aa00aa 00aaaa aaaaaa 555555 ff5555 55ff55 ffff55 5555ff ff55ff 55ffff ffffff", "'Chalk' 7d8b8f b23a52 789b6a b9ac4a 2a7fac bd4f5a 44a799 d2d8d9 888888 f24840 80c470 ffeb62 4196ff fc5275 53cdbd d2d8d9", "'Chalkboard' 000000 c37372 72c373 c2c372 7372c3 c372c2 72c2c3 d9d9d9 323232 dbaaaa aadbaa dadbaa aaaadb dbaada aadadb ffffff", "'ChallengerDeep' 141228 ff5458 62d196 ffb378 65b2ff 906cff 63f2f1 a6b3cc 565575 ff8080 95ffa4 ffe9aa 91ddff c991e1 aaffe4 cbe3e7", "'Chester' 080200 fa5e5b 16c98d ffc83f 288ad6 d34590 28ddde e7e7e7 6f6b68 fa5e5b 16c98d feef6d 278ad6 d34590 27dede ffffff", "'Ciapre' 181818 810009 48513b cc8b3f 576d8c 724d7c 5c4f4b aea47f 555555 ac3835 a6a75d dcdf7c 3097c6 d33061 f3dbb2 f4f4f4", "'CLRS' 000000 f8282a 328a5d fa701d 135cd0 9f00bd 33c3c1 b3b3b3 555753 fb0416 2cc631 fdd727 1670ff e900b0 3ad5ce eeeeec", "'Cobalt Neon' 142631 ff2320 3ba5ff e9e75c 8ff586 781aa0 8ff586 ba46b2 fff688 d4312e 8ff586 e9f06d 3c7dd2 8230a7 6cbc67 8ff586", "'Cobalt2' 000000 ff0000 38de21 ffe50a 1460d2 ff005d 00bbbb bbbbbb 555555 f40e17 3bd01d edc809 5555ff ff55ff 6ae3fa ffffff", "'coffee_theme' 000000 c91b00 00c200 c7c400 0225c7 ca30c7 00c5c7 c7c7c7 686868 ff6e67 5ffa68 fffc67 6871ff ff77ff 60fdff ffffff", "'Contrast Light' 2E1742 0D6BAD 41C2D0 77B01B 8700FF BF0000 E6E6E6 857E39 462366 008CCC 46D1E0 99C252 AF87FF FF0000 FFFFFF A39B46", "'CrayonPonyFish' 2b1b1d 91002b 579524 ab311b 8c87b0 692f50 e8a866 68525a 3d2b2e c5255d 8dff57 c8381d cfc9ff fc6cba ffceaf b0949d", "'Crystal Violet' 0A0A14 5050E6 2DB9E6 32CD87 6E14EB E63232 D2D2D2 EBA041 363B54 7AA2F7 7DCFFF 41A6B5 BB9AF7 F7768E ACB0D0 E0AF68", "'Cyber Cube' 141D2B 2E6CFF 2DE2B2 9FEF00 9F00FF FF3E3E D5E0FF FFAF00 767676 5CB2FF 5CECC6 C5F467 CF8DFB FF8484 D5DAFF FFCC5C", "'Cyberdyne' 080808 ff8373 00c172 d2a700 0071cf ff90fe 6bffdd f1f1f1 2e2e2e ffc4be d6fcba fffed5 c2e3ff ffb2fe e6e7fe ffffff", "'cyberpunk' 000000 ff7092 00fbac fffa6a 00bfff df95ff 86cbfe ffffff 000000 ff8aa4 21f6bc fff787 1bccfd e6aefe 99d6fc ffffff", "'CyberPunk2077' 272932 9381FF 00D0DB 1AC5B0 742D8B 710000 D1C5C0 FDF500 7b8097 37EBF3 37EBF3 40FFE9 CB1DCD C71515 C1DEFF fff955", "'Dark Pastel' 000000 ff5555 55ff55 ffff55 5555ff ff55ff 55ffff bbbbbb 555555 ff5555 55ff55 ffff55 5555ff ff55ff 55ffff ffffff", "'Dark+' 000000 cd3131 0dbc79 e5e510 2472c8 bc3fbc 11a8cd e5e5e5 666666 f14c4c 23d18b f5f543 3b8eea d670d6 29b8db e5e5e5", "'darkermatrix' 091013 002e18 6fa64c 595900 00cb6b 412a4d 125459 002e19 333333 00381d 90d762 e2e500 00ff87 412a4d 176c73 00381e", "'darkmatrix' 091013 006536 6fa64c 7e8000 2c9a84 452d53 114d53 006536 333333 00733d 90d762 e2e500 46d8b8 4a3059 12545a 006536", "'Darkside' 000000 e8341c 68c256 f2d42c 1c98e8 8e69c9 1c98e8 bababa 000000 e05a4f 77b869 efd64b 387cd3 957bbe 3d97e2 bababa", "'deep' 000000 d70005 1cd915 d9bd26 5665ff b052da 50d2da e0e0e0 535353 fb0007 22ff18 fedc2b 9fa9ff e09aff 8df9ff ffffff", "'Desert' 4d4d4d ff2b2b 98fb98 f0e68c cd853f ffdead ffa0a0 f5deb3 555555 ff5555 55ff55 ffff55 87ceff ff55ff ffd700 ffffff", "'DimmedMonokai' 3a3d43 be3f48 879a3b c5a635 4f76a1 855c8d 578fa4 b9bcba 888987 fb001f 0f722f c47033 186de3 fb0067 2e706d fdffb9", "'Django' 000000 fd6209 41a83e ffe862 245032 f8f8f8 9df39f ffffff 323232 ff943b 73da70 ffff94 568264 ffffff cfffd1 ffffff", "'DjangoRebornAgain' 000000 fd6209 41a83e ffe862 245032 f8f8f8 9df39f ffffff 323232 ff943b 73da70 ffff94 568264 ffffff cfffd1 ffffff", "'DjangoSmooth' 000000 fd6209 41a83e ffe862 989898 f8f8f8 9df39f e8e8e7 323232 ff943b 73da70 ffff94 cacaca ffffff cfffd1 ffffff", "'Doom Peacock' 1c1f24 cb4b16 26a6a6 bcd42a 2a6cc6 a9a1e1 5699af ede0ce 2b2a27 ff5d38 98be65 e6f972 51afef c678dd 46d9ff dfdfdf", "'DoomOne' 000000 ff6c6b 98be65 ecbe7b a9a1e1 c678dd 51afef bbc2cf 000000 ff6655 99bb66 ecbe7b a9a1e1 c678dd 51afef bfbfbf", "'DotGov' 191919 bf091d 3d9751 f6bb34 17b2e0 7830b0 8bd2ed ffffff 191919 bf091d 3d9751 f6bb34 17b2e0 7830b0 8bd2ed ffffff", "'Dracula' 000000 ff5555 50fa7b f1fa8c bd93f9 ff79c6 8be9fd bbbbbb 555555 ff5555 50fa7b f1fa8c bd93f9 ff79c6 8be9fd ffffff", "'Dracula+' 21222c ff5555 50fa7b ffcb6b 82aaff c792ea 8be9fd f8f8f2 545454 ff6e6e 69ff94 ffcb6b d6acff ff92df a4ffff f8f8f2", "'DraculaPlus' 21222C 82aaff 8BE9FD 50FA7B c792ea FF5555 F8F8F2 ffcb6b 545454 D6ACFF A4FFFF 69FF94 FF92DF FF6E6E F8F8F2 ffcb6b", "'duckbones' 0e101a e03600 5dcd97 e39500 00a3cb 795ccc 00a3cb ebefc0 2b2f46 ff4821 58db9e f6a100 00b4e0 b3a1e6 00b4e0 b3b692", "'Duotone Dark' 1f1d27 d9393e 2dcd73 d9b76e ffc284 de8d40 2488ff b7a1ff 353147 d9393e 2dcd73 d9b76e ffc284 de8d40 2488ff eae5ff", "'Earthsong' 121418 c94234 85c54c f5ae2e 1398b9 d0633d 509552 e5c6aa 675f54 ff645a 98e036 e0d561 5fdaff ff9269 84f088 f6f7ec", "'Elemental' 3c3c30 98290f 479a43 7f7111 497f7d 7f4e2f 387f58 807974 555445 e0502a 61e070 d69927 79d9d9 cd7c54 59d599 fff1e9", "'Elementary' 242424 d71c15 5aa513 fdb40c 063b8c e40038 2595e1 efefef 4b4b4b fc1c18 6bc219 fec80e 0955ff fb0050 3ea8fc 8c00ec", "'ENCOM' 000000 9f0000 008b00 ffd000 0081ff bc00ca 008b8b bbbbbb 555555 ff0000 00ee00 ffff00 0000ff ff00ff 00cdcd ffffff", "'Espresso' 353535 d25252 a5c261 ffc66d 6c99bb d197d9 bed6ff eeeeec 535353 f00c0c c2e075 e1e48b 8ab7d9 efb5f7 dcf4ff ffffff", "'Espresso Libre' 000000 cc0000 1a921c f0e53a 0066ff c5656b 06989a d3d7cf 555753 ef2929 9aff87 fffb5c 43a8ed ff818a 34e2e2 eeeeec", "'Fahrenheit' 1d1d1d cda074 9e744d fecf75 720102 734c4d 979797 ffffce 000000 fecea0 cc734d fd9f4d cb4a05 4e739f fed04d ffffff", "'Fairyfloss' 040303 f92672 c2ffdf e6c000 c2ffdf ffb8d1 c5a3ff f8f8f0 6090cb ff857f c2ffdf ffea00 c2ffdf ffb8d1 c5a3ff f8f8f0", "'Fideloper' 292f33 cb1e2d edb8ac b7ab9b 2e78c2 c0236f 309186 eae3ce 092028 d4605a d4605a a86671 7c85c4 5c5db2 819090 fcf4df", "'FirefoxDev' 002831 e63853 5eb83c a57706 359ddf d75cff 4b73a2 dcdcdc 001e27 e1003f 1d9000 cd9409 006fc0 a200da 005794 e2e2e2", "'Firewatch' 585f6d d95360 5ab977 dfb563 4d89c4 d55119 44a8b6 e6e5ff 585f6d d95360 5ab977 dfb563 4c89c5 d55119 44a8b6 e6e5ff", "'FishTank' 03073c c6004a acf157 fecd5e 525fb8 986f82 968763 ecf0fc 6c5b30 da4b8a dbffa9 fee6a9 b2befa fda5cd a5bd86 f6ffec", "'Flat' 222d3f a82320 32a548 e58d11 3167ac 781aa0 2c9370 b0b6ba 212c3c d4312e 2d9440 e5be0c 3c7dd2 8230a7 35b387 e7eced", "'Flatland' 1d1d19 f18339 9fd364 f4ef6d 5096be 695abc d63865 ffffff 1d1d19 d22a24 a7d42c ff8949 61b9d0 695abc d63865 ffffff", "'Floraverse' 08002e 64002c 5d731a cd751c 1d6da1 b7077e 42a38c f3e0b8 331e4d d02063 b4ce59 fac357 40a4cf f12aae 62caa8 fff5db", "'ForestBlue' 333333 f8818e 92d3a2 1a8e63 8ed0ce 5e468c 31658c e2d8cd 3d3d3d fb3d66 6bb48d 30c85a 39a7a2 7e62b3 6096bf e2d8cd", "'Framer' 141414 ff5555 98ec65 ffcc33 00aaff aa88ff 88ddff cccccc 414141 ff8888 b6f292 ffd966 33bbff cebbff bbecff ffffff", "'FrontEndDelight' 242526 f8511b 565747 fa771d 2c70b7 f02e4f 3ca1a6 adadad 5fac6d f74319 74ec4c fdc325 3393ca e75e4f 4fbce6 8c735b", "'FunForrest' 000000 d6262b 919c00 be8a13 4699a3 8d4331 da8213 ddc265 7f6a55 e55a1c bfc65a ffcb1b 7cc9cf d26349 e6a96b ffeaa3", "'Galaxy' 000000 f9555f 21b089 fef02a 589df6 944d95 1f9ee7 bbbbbb 555555 fa8c8f 35bb9a ffff55 589df6 e75699 3979bc ffffff", "'Galizur' 223344 aa1122 33aa11 ccaa22 2255cc 7755aa 22bbdd 8899aa 556677 ff1133 33ff11 ffdd33 3377ff aa77ff 33ddff bbccdd", "'Ganyu' 12061B 5256c3 2aadb3 c7e18d ddb2ff E06C75 ecebea f8b433 322a51 9aa8dd 7ce7d8 b4f42c 9681ed a5313d f3f3f3 f1d661", "'Github' 3e3e3e 970b16 07962a f8eec7 003e8a e94691 89d1ec ffffff 666666 de0000 87d5a2 f1d007 2e6cba ffa29f 1cfafe ffffff", "'GitHub Dark' 000000 f78166 56d364 e3b341 6ca4f8 db61a2 2b7489 ffffff 4d4d4d f78166 56d364 e3b341 6ca4f8 db61a2 2b7489 ffffff", "'Glacier' 2e343c bd0f2f 35a770 fb9435 1f5872 bd2523 778397 ffffff 404a55 bd0f2f 49e998 fddf6e 2a8bc1 ea4727 a0b6d3 ffffff", "'Glorious' 1e1e1e be0f17 868715 cc881a 16777a a04b73 578e57 978771 7f7061 f73028 d5d5d7 f7b125 4e917c c77089 7db669 e6d4a3", "'Grape' 2d283f ed2261 1fa91b 8ddc20 487df4 8d35c9 3bdeed 9e9ea0 59516a f0729a 53aa5e b2dc87 a9bcec ad81c2 9de3eb a288f7", "'Grass' 000000 bb0000 00bb00 e7b000 0000a3 950062 00bbbb bbbbbb 555555 bb0000 00bb00 e7b000 0000bb ff55ff 55ffff ffffff", "'Grey-green' 000000 fe1414 74ff00 f1ff01 00deff ff00f0 00ffbc ffffff 666666 ff3939 00ff44 ffd100 00afff ff008a 00ffd3 f5ecec", "'Gruvbox Light' fbf1c7 9d0006 79740e b57614 076678 8f3f71 427b58 3c3836 9d8374 cc241d 98971a d79921 458588 b16186 689d69 7c6f64", "'GruvboxDark' 282828 cc241d 98971a d79921 458588 b16286 689d6a ebdbb2 928374 cc241d 98971a d79921 458588 b16286 689d6a ebdbb2", "'GruvboxDarkHard' 1d2021 cc241d 98971a d79921 458588 b16286 689d6a ebdbb2 928374 cc241d 98971a d79921 458588 b16286 689d6a ebdbb2", "'Guezwhoz' 080808 ff5f5f 87d7af d7d787 5fafd7 afafff 5fd7d7 dadada 8a8a8a d75f5f afd7af d7d7af 87afd7 afafd7 87d7d7 dadada", "'h4rithd' 151507 839496 B0D1BA 849900 D33682 C94B16 FFFFFF B58900 1F1F1E 839496 93A1A1 586E75 6C71C4 CB4B16 FFFFFF 657B83", "'h4rithd.com' 010100 3464A5 06989A 4E9B07 75517A CC0000 D3D7CF C4A000 545752 729ECE 35E2E3 8BE235 AC7EA8 EE282B D3D7CF FDE94E", "'Hacktober' 191918 b34538 587744 d08949 206ec5 864651 ac9166 f1eee7 2c2b2a b33323 42824a c75a22 5389c5 e795a5 ebc587 ffffff", "'Hardcore' 1b1d1e f92672 a6e22e fd971f 66d9ef 9e6ffe 5e7175 ccccc6 505354 ff669d beed5f e6db74 66d9ef 9e6ffe a3babf f8f8f2", "'Harper' 010101 f8b63f 7fb5e1 d6da25 489e48 b296c6 f5bfd7 a8a49d 726e6a f8b63f 7fb5e1 d6da25 489e48 b296c6 f5bfd7 fefbea", "'HaX0R_BLUE' 010921 10b6ff 10b6ff 10b6ff 10b6ff 10b6ff 10b6ff fafafa 080117 00b3f7 00b3f7 00b3f7 00b3f7 00b3f7 00b3f7 fefefe", "'HaX0R_GR33N' 001f0b 15d00d 15d00d 15d00d 15d00d 15d00d 15d00d fafafa 001510 19e20e 19e20e 19e20e 19e20e 19e20e 19e20e fefefe", "'HaX0R_R3D' 1f0000 b00d0d b00d0d b00d0d b00d0d b00d0d b00d0d fafafa 150000 ff1111 ff1010 ff1010 ff1010 ff1010 ff1010 fefefe", "'Highway' 000000 d00e18 138034 ffcb3e 006bb3 6b2775 384564 ededed 5d504a f07e18 b1d130 fff120 4fc2fd de0071 5d504a ffffff", "'Hipster Green' 000000 b6214a 00a600 bfbf00 246eb2 b200b2 00a6b2 bfbfbf 666666 e50000 86a93e e5e500 0000ff e500e5 00e5e5 e5e5e5", "'Hivacruz' 202746 c94922 ac9739 c08b30 3d8fd1 6679cc 22a2c9 979db4 6b7394 c76b29 73ad43 5e6687 898ea4 dfe2f1 9c637a f5f7ff", "'Homebrew' 000000 990000 00a600 999900 0000b2 b200b2 00a6b2 bfbfbf 666666 e50000 00d900 e5e500 0000ff e500e5 00e5e5 e5e5e5", "'Hopscotch' 322931 dd464c 8fc13e fdcc59 1290bf c85e7c 149b93 b9b5b8 797379 fd8b19 433b42 5c545b 989498 d5d3d5 b33508 ffffff", "'Hopscotch.256' 322931 dd464c 8fc13e fdcc59 1290bf c85e7c 149b93 b9b5b8 797379 dd464c 8fc13e fdcc59 1290bf c85e7c 149b93 ffffff", "'Horizon' 0a0a0d E95678 29D398 FAB795 26BBD9 EE64AC 59E1E3 e5e5e5 848484 EC6A88 3FDAA4 FBC3A7 3FC4DE F075B5 6BE4E6 e5e5e5", "'Hurtado' 575757 ff1b00 a5e055 fbe74a 496487 fd5ff1 86e9fe cbcccb 262626 d51d00 a5df55 fbe84a 89beff c001c1 86eafe dbdbdb", "'Hybrid' 2a2e33 b84d51 b3bf5a e4b55e 6e90b0 a17eac 7fbfb4 b5b9b6 1d1f22 8d2e32 798431 e58a50 4b6b88 6e5079 4d7b74 5a626a", "'Hyper' 000000 0066FF 00FFFF 33FF00 CC00FF FE0100 D0D0D0 FEFF00 808080 0066FF 00FFFF 33FF00 CC00FF FE0100 FFFFFF FEFF00", "'iceberg-dark' 1e2132 e27878 b4be82 e2a478 84a0c6 a093c7 89b8c2 c6c8d1 6b7089 e98989 c0ca8e e9b189 91acd1 ada0d3 95c4ce d2d4de", "'iceberg-light' dcdfe7 cc517a 668e3d c57339 2d539e 7759b4 3f83a6 33374c 8389a3 cc3768 598030 b6662d 22478e 6845ad 327698 262a3f", "'IC_Green_PPL' 014401 ff2736 41a638 76a831 2ec3b9 50a096 3ca078 e6fef2 035c03 b4fa5c aefb86 dafa87 2efaeb 50fafa 3cfac8 e0f1dc", "'IC_Orange_PPL' 000000 c13900 a4a900 caaf00 bd6d00 fc5e00 f79500 ffc88a 6a4f2a ff8c68 f6ff40 ffe36e ffbe55 fc874f c69752 fafaff", "'idea' adadad fc5256 98b61c ccb444 437ee7 9d74b0 248887 181818 ffffff fc7072 98b61c ffff0b 6c9ced fc7eff 248887 181818", "'idleToes' 323232 d25252 7fe173 ffc66d 4099ff f680ff bed6ff eeeeec 535353 f07070 9dff91 ffe48b 5eb7f7 ff9dff dcf4ff ffffff", "'IR_Black' 4f4f4f fa6c60 a8ff60 fffeb7 96cafe fa73fd c6c5fe efedef 7b7b7b fcb6b0 cfffab ffffcc b5dcff fb9cfe e0e0fe ffffff", "'Jackie Brown' 2c1d16 ef5734 2baf2b bebf00 246eb2 d05ec1 00acee bfbfbf 666666 e50000 86a93e e5e500 0000ff e500e5 00e5e5 e5e5e5", "'Japanesque' 343935 cf3f61 7bb75b e9b32a 4c9ad4 a57fc4 389aad fafaf6 595b59 d18fa6 767f2c 78592f 135979 604291 76bbca b2b5ae", "'Jellybeans' 929292 e27373 94b979 ffba7b 97bedc e1c0fa 00988e dedede bdbdbd ffa1a1 bddeab ffdca0 b1d8f6 fbdaff 1ab2a8 ffffff", "'JetBrains Darcula' 000000 fa5355 126e00 c2c300 4581eb fa54ff 33c2c1 adadad 555555 fb7172 67ff4f ffff00 6d9df1 fb82ff 60d3d1 eeeeee", "'jubi' 3b3750 cf7b98 90a94b 6ebfc0 576ea6 bc4f68 75a7d2 c3d3de a874ce de90ab bcdd61 87e9ea 8c9fcd e16c87 b7c9ef d5e5f1", "'Juicy Colors' 292a24 209DE5 00D2FF 68D644 AF80FF FF6249 CCCCCC FCC223 808080 209DE5 00D2FF 68D644 AF80FF FF6249 F2F2F2 FCC223", "'kanagawabones' 1f1f28 e46a78 98bc6d e5c283 7eb3c9 957fb8 7eb3c9 ddd8bb 3c3c51 ec818c 9ec967 f1c982 7bc2df a98fd2 7bc2df a8a48d", "'Kibble' 4d4d4d c70031 29cf13 d8e30e 3449d1 8400ff 0798ab e2d1e3 5a5a5a f01578 6ce05c f3f79e 97a4f7 c495f0 68f2e0 ffffff", "'Kolorit' 1d1a1e ff5b82 47d7a1 e8e562 5db4ee da6cda 57e9eb ededed 1d1a1e ff5b82 47d7a1 e8e562 5db4ee da6cda 57e9eb ededed", "'Konsolas' 000000 aa1717 18b218 ebae1f 2323a5 ad1edc 42b0c8 c8c1c1 7b716e ff4141 5fff5f ffff55 4b4bff ff54ff 69ffff ffffff", "'Lab Fox' 2e2e2e fc6d26 3eb383 fca121 db3b21 380d75 6e49cb ffffff 464646 ff6517 53eaa8 fca013 db501f 441090 7d53e7 ffffff", "'Laser' 626262 ff8373 b4fb73 09b4bd fed300 ff90fe d1d1fe f1f1f1 8f8f8f ffc4be d6fcba fffed5 f92883 ffb2fe e6e7fe ffffff", "'Later This Evening' 2b2b2b d45a60 afba67 e5d289 a0bad6 c092d6 91bfb7 3c3d3d 454747 d3232f aabb39 e5be39 6699d6 ab53d6 5fc0ae c1c2c2", "'Lavandula' 230046 7d1625 337e6f 7f6f49 4f4a7f 5a3f7f 58777f 736e7d 372d46 e05167 52e0c4 e0c386 8e87e0 a776e0 9ad4e0 8c91fa", "'LiquidCarbon' 000000 ff3030 559a70 ccac00 0099cc cc69c8 7ac4cc bccccc 000000 ff3030 559a70 ccac00 0099cc cc69c8 7ac4cc bccccc", "'LiquidCarbonTransparent' 000000 ff3030 559a70 ccac00 0099cc cc69c8 7ac4cc bccccc 000000 ff3030 559a70 ccac00 0099cc cc69c8 7ac4cc bccccc", "'LiquidCarbonTransparentInverse' bccccd ff3030 559a70 ccac00 0099cc cc69c8 7ac4cc 000000 ffffff ff3030 559a70 ccac00 0099cc cc69c8 7ac4cc 000000", "'lovelace' 282a36 f37f97 5adecd f2a272 8897f4 c574dd 79e6f3 fdfdfd 414458 ff4971 18e3c8 ff8037 556fff b043d1 3fdcee bebec1", "'Man Page' 000000 cc0000 00a600 999900 0000b2 b200b2 00a6b2 cccccc 666666 e50000 00d900 e5e500 0000ff e500e5 00e5e5 e5e5e5", "'Mariana' 000000 ec5f66 99c794 f9ae58 6699cc c695c6 5fb4b4 f7f7f7 333333 f97b58 acd1a8 fac761 85add6 d8b6d8 82c4c4 ffffff", "'Material' 212121 b7141f 457b24 f6981e 134eb2 560088 0e717c efefef 424242 e83b3f 7aba3a ffea2e 54a4f3 aa4dbc 26bbd1 d9d9d9", "'MaterialDark' 212121 b7141f 457b24 f6981e 134eb2 560088 0e717c efefef 424242 e83b3f 7aba3a ffea2e 54a4f3 aa4dbc 26bbd1 d9d9d9", "'MaterialDarker' 000000 ff5370 c3e88d ffcb6b 82aaff c792ea 89ddff ffffff 545454 ff5370 c3e88d ffcb6b 82aaff c792ea 89ddff ffffff", "'MaterialDesignColors' 435b67 fc3841 5cf19e fed032 37b6ff fc226e 59ffd1 ffffff a1b0b8 fc746d adf7be fee16c 70cfff fc669b 9affe6 ffffff", "'MaterialOcean' 546e7a ff5370 c3e88d ffcb6b 82aaff c792ea 89ddff ffffff 546e7a ff5370 c3e88d ffcb6b 82aaff c792ea 89ddff ffffff", "'Mathias' 000000 e52222 a6e32d fc951e c48dff fa2573 67d9f0 f2f2f2 555555 ff5555 55ff55 ffff55 5555ff ff55ff 55ffff ffffff", "'matrix' 0f191c 23755a 82d967 ffd700 3f5242 409931 50b45a 507350 688060 2fc079 90d762 faff00 4f7e7e 11ff25 c1ff8a 678c61", "'Medallion' 000000 b64c00 7c8b16 d3bd26 616bb0 8c5a90 916c25 cac29a 5e5219 ff9149 b2ca3b ffe54a acb8ff ffa0ff ffbc51 fed698", "'midnight-in-mojave' 1e1e1e ff453a 32d74b ffd60a 0a84ff bf5af2 5ac8fa ffffff 1e1e1e ff453a 32d74b ffd60a 0a84ff bf5af2 5ac8fa ffffff", "'Mirage' 011627 ff9999 85cc95 ffd700 7fb5ff ddb3ff 21c7a8 ffffff 575656 ff9999 85cc95 ffd700 7fb5ff ddb3ff 85cc95 ffffff", "'Misterioso' 000000 ff4242 74af68 ffad29 338f86 9414e6 23d7d7 e1e1e0 555555 ff3242 74cd68 ffb929 23d7d7 ff37ff 00ede1 ffffff", "'Molokai' 121212 fa2573 98e123 dfd460 1080d0 8700ff 43a8d0 bbbbbb 555555 f6669d b1e05f fff26d 00afff af87ff 51ceff ffffff", "'MonaLisa' 351b0e 9b291c 636232 c36e28 515c5d 9b1d29 588056 f7d75c 874228 ff4331 b4b264 ff9566 9eb2b4 ff5b6a 8acd8f ffe598", "'Monokai Cmder' 272822 a70334 74aa04 b6b649 01549e 89569c 1a83a6 cacaca 7c7c7c f3044b 8dd006 cccc81 0383f5 a87db8 58c2e5 ffffff", "'Monokai Pro' 403e41 fc9867 78dce8 a9dc76 ab9df2 ff6188 fcfcfa ffd866 727072 fc9867 78dce8 a9dc76 ab9df2 ff6188 fcfcfa ffd866", "'Monokai Pro (Filter Octagon)' 000000 d81e00 5ea702 cfae00 427ab3 89658e 00a7aa dbded8 686a66 f54235 99e343 fdeb61 84b0d8 bc94b7 37e6e8 f1f1f0", "'Monokai Pro (Filter Ristretto)' 403838 F38D70 85DACC ADDA78 A8A9EB FD6883 FFF1F3 F9CC6C 72696A F38D70 85DACC ADDA78 A8A9EB FD6883 FFF1F3 F9CC6C", "'Monokai Remastered' 1a1a1a f4005f 98e024 fd971f 9d65ff f4005f 58d1eb c4c5b5 625e4c f4005f 98e024 e0d561 9d65ff f4005f 58d1eb f6f6ef", "'Monokai Soda' 1a1a1a f4005f 98e024 fa8419 9d65ff f4005f 58d1eb c4c5b5 625e4c f4005f 98e024 e0d561 9d65ff f4005f 58d1eb f6f6ef", "'Monokai Vivid' 121212 fa2934 98e123 fff30a 0443ff f800f8 01b6ed ffffff 838383 f6669d b1e05f fff26d 0443ff f200f6 51ceff ffffff", "'Moonlight II' 191a2a ff757f c3e88d ffc777 82aaff c099ff 86e1fc c8d3f5 828bb8 ff757f c3e88d ffc777 82aaff c099ff 86e1fc c8d3f5", "'N0tch2k' 383838 a95551 666666 a98051 657d3e 767676 c9c9c9 d0b8a3 474747 a97775 8c8c8c a99175 98bd5e a3a3a3 dcdcdc d8c8bb", "'neobones_dark' 0f191f de6e7c 90ff6b b77e64 8190d4 b279a7 66a5ad c6d5cf 263945 e8838f a0ff85 d68c67 92a0e2 cf86c1 65b8c1 98a39e", "'neobones_light' e5ede6 a8334c 567a30 944927 286486 88507d 3b8992 202e18 b3c6b6 94253e 3f5a22 803d1c 1d5573 7b3b70 2b747c 415934", "'Neon' 000000 ff3045 5ffa74 fffc7e 0208cb f924e7 00fffc c7c7c7 686868 ff5a5a 75ff88 fffd96 3c40cb f15be5 88fffe ffffff", "'Neopolitan' 000000 800000 61ce3c fbde2d 253b76 ff0080 8da6ce f8f8f8 000000 800000 61ce3c fbde2d 253b76 ff0080 8da6ce f8f8f8", "'Neutron' 23252b b54036 5ab977 deb566 6a7c93 a4799d 3f94a8 e6e8ef 23252b b54036 5ab977 deb566 6a7c93 a4799d 3f94a8 ebedf2", "'Night Owlish Light' 011627 d3423e 2aa298 daaa01 4876d6 403f53 08916a 7a8181 7a8181 f76e6e 49d0c5 dac26b 5ca7e4 697098 00c990 989fb1", "'NightLion v1' 4c4c4c bb0000 5fde8f f3f167 276bd8 bb00bb 00dadf bbbbbb 555555 ff5555 55ff55 ffff55 5555ff ff55ff 55ffff ffffff", "'NightLion v2' 4c4c4c bb0000 04f623 f3f167 64d0f0 ce6fdb 00dadf bbbbbb 555555 ff5555 7df71d ffff55 62cbe8 ff9bf5 00ccd8 ffffff", "'Nocturnal Winter' 4d4d4d f12d52 09cd7e f5f17a 3182e0 ff2b6d 09c87a fcfcfc 808080 f16d86 0ae78d fffc67 6096ff ff78a2 0ae78d ffffff", "'nord' 3b4252 bf616a a3be8c ebcb8b 81a1c1 b48ead 88c0d0 e5e9f0 4c566a bf616a a3be8c ebcb8b 81a1c1 b48ead 8fbcbb eceff4", "'nord-light' 3b4252 bf616a a3be8c ebcb8b 81a1c1 b48ead 88c0d0 d8dee9 4c566a bf616a a3be8c ebcb8b 81a1c1 b48ead 8fbcbb eceff4", "'Novel' 000000 cc0000 009600 d06b00 0000cc cc00cc 0087cc cccccc 808080 cc0000 009600 d06b00 0000cc cc00cc 0087cc ffffff", "'Obsidian' 000000 a60001 00bb00 fecd22 3a9bdb bb00bb 00bbbb bbbbbb 555555 ff0003 93c863 fef874 a1d7ff ff55ff 55ffff ffffff", "'Ocean' 000000 990000 00a600 999900 0000b2 b200b2 00a6b2 bfbfbf 666666 e50000 00d900 e5e500 0000ff e500e5 00e5e5 e5e5e5", "'Oceanic-Next' 121c21 e44754 89bd82 f7bd51 5486c0 b77eb8 50a5a4 ffffff 52606b e44754 89bd82 f7bd51 5486c0 b77eb8 50a5a4 ffffff", "'OceanicMaterial' 000000 ee2b2a 40a33f ffea2e 1e80f0 8800a0 16afca a4a4a4 777777 dc5c60 70be71 fff163 54a4f3 aa4dbc 42c7da ffffff", "'Ollie' 000000 ac2e31 31ac61 ac4300 2d57ac b08528 1fa6ac 8a8eac 5b3725 ff3d48 3bff99 ff5e1e 4488ff ffc21d 1ffaff 5b6ea7", "'OneDark' 1e2127 e06c75 98c379 d19a66 61afef c678dd 56b6c2 abb2bf 5c6370 e06c75 98c379 d19a66 61afef c678dd 56b6c2 ffffff", "'OneHalfDark' 282c34 e06c75 98c379 e5c07b 61afef c678dd 56b6c2 dcdfe4 282c34 e06c75 98c379 e5c07b 61afef c678dd 56b6c2 dcdfe4", "'OneHalfLight' 383a42 e45649 50a14f c18401 0184bc a626a4 0997b3 fafafa 4f525e e06c75 98c379 e5c07b 61afef c678dd 56b6c2 ffffff", "'OneStar' 000000 d13b3b 0dbc79 dfdf44 2472c8 c42cc4 33a0bb f1f1f1 666666 fa4b4b 23d18b fcfc5c 3b8eea d861d8 29b8db fafafa", "'Operator Mono Dark' 5a5a5a ca372d 4d7b3a d4d697 4387cf b86cb4 72d5c6 ced4cd 9a9b99 c37d62 83d0a2 fdfdc5 89d3f6 ff2c7a 82eada fdfdf6", "'Overnight Slumber' 0a1222 ffa7c4 85cc95 ffcb8b 8dabe1 c792eb 78ccf0 ffffff 575656 ffa7c4 85cc95 ffcb8b 8dabe1 c792eb ffa7c4 ffffff", "'PaleNightHC' 000000 f07178 c3e88d ffcb6b 82aaff c792ea 89ddff ffffff 666666 f6a9ae dbf1ba ffdfa6 b4ccff ddbdf2 b8eaff 999999", "'Pandora' 000000 ff4242 74af68 ffad29 338f86 9414e6 23d7d7 e2e2e2 3f5648 ff3242 74cd68 ffb929 23d7d7 ff37ff 00ede1 ffffff", "'Paraiso Dark' 2f1e2e ef6155 48b685 fec418 06b6ef 815ba4 5bc4bf a39e9b 776e71 ef6155 48b685 fec418 06b6ef 815ba4 5bc4bf e7e9db", "'PaulMillr' 2a2a2a ff0000 79ff0f e7bf00 396bd7 b449be 66ccff bbbbbb 666666 ff0080 66ff66 f3d64e 709aed db67e6 7adff2 ffffff", "'PencilDark' 212121 c30771 10a778 a89c14 008ec4 523c79 20a5ba d9d9d9 424242 fb007a 5fd7af f3e430 20bbfc 6855de 4fb8cc f1f1f1", "'PencilLight' 212121 c30771 10a778 a89c14 008ec4 523c79 20a5ba d9d9d9 424242 fb007a 5fd7af f3e430 20bbfc 6855de 4fb8cc f1f1f1", "'Peppermint' 353535 e74669 89d287 dab853 449fd0 da62dc 65aaaf b4b4b4 535353 e4859b a3cca2 e1e487 6fbce2 e586e7 96dcdb dfdfdf", "'Piatto Light' 414141 b23771 66781e cd6f34 3c5ea8 a454b2 66781e ffffff 3f3f3f db3365 829429 cd6f34 3c5ea8 a454b2 829429 f2f2f2", "'Pnevma' 2f2e2d a36666 90a57d d7af87 7fa5bd c79ec4 8adbb4 d0d0d0 4a4845 d78787 afbea2 e4c9af a1bdce d7beda b1e7dd efefef", "'Popping and Locking' 1d2021 cc241d 98971a d79921 458588 b16286 689d6a a89984 928374 f42c3e b8bb26 fabd2f 99c6ca d3869b 7ec16e ebdbb2", "'primary' 000000 db4437 0f9d58 f4b400 4285f4 db4437 4285f4 ffffff 000000 db4437 0f9d58 f4b400 4285f4 4285f4 0f9d58 ffffff", "'Primer' 000000 ea4a5a 34d058 ffdf5d 2188ff 8a63d2 15e2e2 ecf0f1 4f5861 fdaeb7 bef5cb fff5b1 c8e1ff d1bcf9 a2ecec ffffff", "'Pro' 000000 990000 00a600 999900 2009db b200b2 00a6b2 bfbfbf 666666 e50000 00d900 e5e500 0000ff e500e5 00e5e5 e5e5e5", "'Pro Light' 000000 e5492b 50d148 c6c440 3b75ff ed66e8 4ed2de dcdcdc 9f9f9f ff6640 61ef57 f2f156 0082ff ff7eff 61f7f8 f2f2f2", "'Purple Rain' 000000 ff260e 9be205 ffc400 00a2fa 815bb5 00deef ffffff 565656 ff4250 b8e36e ffd852 00a6ff ac7bf0 74fdf3 ffffff", "'purplepeter' 0a0520 ff796d 99b481 efdfac 66d9ef e78fcd ba8cff ffba81 100b23 f99f92 b4be8f f2e9bf 79daed ba91d4 a0a0d6 b9aed3", "'QB64 Super Dark Blue' 000000 054663 00485C 157E15 631563 98220E 989898 808000 626262 457693 00586C 55CE55 934593 D8624E D8D8D8 FFA700", "'Rapture' 000000 fc644d 7afde1 fff09b 6c9bf5 ff4fa1 64e0ff c0c9e5 304b66 fc644d 7afde1 fff09b 6c9bf5 ff4fa1 64e0ff ffffff", "'Raycast_Dark' 000000 ff5360 59d499 ffc531 56c2ff cf2f98 52eee5 ffffff 000000 ff6363 59d499 ffc531 56c2ff cf2f98 52eee5 ffffff", "'Raycast_Light' 000000 b12424 006b4f f8a300 138af2 9a1b6e 3eb8bf ffffff 000000 b12424 006b4f f8a300 138af2 9a1b6e 3eb8bf ffffff", "'rebecca' 12131e dd7755 04dbb5 f2e7b7 7aa5ff bf9cf9 56d3c2 e4e3e9 666699 ff92cd 01eac0 fffca8 69c0fa c17ff8 8bfde1 f4f2f9", "'Red Alert' 000000 d62e4e 71be6b beb86b 489bee e979d7 6bbeb8 d6d6d6 262626 e02553 aff08c dfddb7 65aaf1 ddb7df b7dfdd ffffff", "'Red Planet' 202020 8c3432 728271 e8bf6a 69819e 896492 5b8390 b9aa99 676767 b55242 869985 ebeb91 60827e de4974 38add8 d6bfb8", "'Red Sands' 000000 ff3f00 00bb00 e7b000 0072ff bb00bb 00bbbb bbbbbb 555555 bb0000 00bb00 e7b000 0072ae ff55ff 55ffff ffffff", "'Relaxed' 151515 bc5653 909d63 ebc17a 6a8799 b06698 c9dfff d9d9d9 636363 bc5653 a0ac77 ebc17a 7eaac7 b06698 acbbd0 f7f7f7", "'Retro' 13a10e 13a10e 13a10e 13a10e 13a10e 13a10e 13a10e 13a10e 16ba10 16ba10 16ba10 16ba10 16ba10 16ba10 16ba10 16ba10", "'Retrowave' df81fc 929292 46BDFF FF92DF FF16B0 FFFFFF 181A1F fcee54 ffffff FF16B0 fcee54 f85353 ffffff 46BDFF ff901f FF92DF", "'Rippedcasts' 000000 cdaf95 a8ff60 bfbb1f 75a5b0 ff73fd 5a647e bfbfbf 666666 eecbad bcee68 e5e500 86bdc9 e500e5 8c9bc4 e5e5e5", "'Rose Pine' 706e86 eb6f92 9ccfd8 f6c177 31748f c4a7e7 ebbcba e0def4 706e86 eb6f92 9ccfd8 f6c177 31748f c4a7e7 ebbcba e0def4", "'Rouge 2' 5d5d6b c6797e 969e92 dbcdab 6e94b9 4c4e78 8ab6c1 e8e8ea 616274 c6797e e6dcc4 e6dcc4 98b3cd 8283a1 abcbd3 e8e8ea", "'Royal' 241f2b 91284c 23801c b49d27 6580b0 674d96 8aaabe 524966 312d3d d5356c 2cd946 fde83b 90baf9 a479e3 acd4eb 9e8cbd", "'Ryuuko' 2c3941 865f5b 66907d b1a990 6a8e95 b18a73 88b2ac ececec 5d7079 865f5b 66907d b1a990 6a8e95 b18a73 88b2ac ececec", "'Sakura' 000000 d52370 41af1a bc7053 6964ab c71fbf 939393 998eac 786d69 f41d99 22e529 f59574 9892f1 e90cdd eeeeee cbb6ff", "'Scarlet Protocol' 101116 ff0051 00dc84 faf945 0271b6 ca30c7 00c5c7 c7c7c7 686868 ff6e67 5ffa68 fffc67 6871ff bd35ec 60fdff ffffff", "'Seafoam Pastel' 757575 825d4d 728c62 ada16d 4d7b82 8a7267 729494 e0e0e0 8a8a8a cf937a 98d9aa fae79d 7ac3cf d6b2a1 ade0e0 e0e0e0", "'SeaShells' 17384c d15123 027c9b fca02f 1e4950 68d4f1 50a3b5 deb88d 434b53 d48678 628d98 fdd39f 1bbcdd bbe3ee 87acb4 fee4ce", "'seoulbones_dark' 4b4b4b e388a3 98bd99 ffdf9b 97bdde a5a6c5 6fbdbe dddddd 6c6465 eb99b1 8fcd92 ffe5b3 a2c8e9 b2b3da 6bcacb a8a8a8", "'seoulbones_light' e2e2e2 dc5284 628562 c48562 0084a3 896788 008586 555555 bfbabb be3c6d 487249 a76b48 006f89 7f4c7e 006f70 777777", "'Serendipity Midnight' 232534 5BA2D0 94B8FF A78BFA DEE0EF 9CCFD8 EE8679 F8D2C9 8D8F9E 5BA2D0 94B8FF A78BFA DEE0EF 9CCFD8 EE8679 F8D2C9", "'Serendipity Morning' F2E9DE 3788BE 7397DE 886CDB 575279 77AAB3 D26A5D C8A299 6E6A86 3788BE 7397DE 886CDB 575279 77AAB3 D26A5D C8A299", "'Serendipity Sunset' 363847 709BBD A0B6E8 A392DC DEE0EF AAC9D4 D1918F EDD5D6 6B6D7C 709BBD A0B6E8 A392DC DEE0EF AAC9D4 D1918F EDD5D6", "'Seti' 323232 c22832 8ec43d e0c64f 43a5d5 8b57b5 8ec43d eeeeee 323232 c22832 8ec43d e0c64f 43a5d5 8b57b5 8ec43d ffffff", "'shades-of-purple' 000000 d90429 3ad900 ffe700 6943ff ff2c70 00c5c7 c7c7c7 686868 f92a1c 43d426 f1d000 6871ff ff77ff 79e8fb ffffff", "'Shaman' 012026 b2302d 00a941 5e8baa 449a86 00599d 5d7e19 405555 384451 ff4242 2aea5e 8ed4fd 61d5ba 1298ff 98d028 58fbd6", "'Slate' 222222 e2a8bf 81d778 c4c9c0 264b49 a481d3 15ab9c 02c5e0 ffffff ffcdd9 beffa8 d0ccca 7ab0d2 c5a7d9 8cdfe0 e0e0e0", "'SleepyHollow' 572100 ba3934 91773f b55600 5f63b4 a17c7b 8faea9 af9a91 4e4b61 d9443f d6b04e f66813 8086ef e2c2bb a4dce7 d2c7a9", "'Smyck' 000000 b84131 7da900 c4a500 62a3c4 ba8acc 207383 a1a1a1 7a7a7a d6837c c4f137 fee14d 8dcff0 f79aff 6ad9cf f7f7f7", "'Snazzy' 000000 fc4346 50fb7c f0fb8c 49baff fc4cb4 8be9fe ededec 555555 fc4346 50fb7c f0fb8c 49baff fc4cb4 8be9fe ededec", "'SoftServer' 000000 a2686a 9aa56a a3906a 6b8fa3 6a71a3 6ba58f 99a3a2 666c6c dd5c60 bfdf55 deb360 62b1df 606edf 64e39c d2e0de", "'Solarized Darcula' 25292a f24840 629655 b68800 2075c7 797fd4 15968d d2d8d9 25292a f24840 629655 b68800 2075c7 797fd4 15968d d2d8d9", "'Solarized Dark - Patched' 002831 d11c24 738a05 a57706 2176c7 c61c6f 259286 eae3cb 475b62 bd3613 475b62 536870 708284 5956ba 819090 fcf4dc", "'Solarized Dark Higher Contrast' 002831 d11c24 6cbe6c a57706 2176c7 c61c6f 259286 eae3cb 006488 f5163b 51ef84 b27e28 178ec8 e24d8e 00b39e fcf4dc", "'Sonoran Gothic' 867F6E EB6f6f 669C50 F2D696 227B4d A5ABDA E18F62 EAF4DE 867F6E EB6f6f 669C50 F2D696 227B4D A5ABDA E18F62 EAF4DE", "'Sonoran Sunrise' F9FAE3 EB6f6f 669C50 F2C55C 227B4D 7189D9 E07941 665E4B F9FAE3 EB6f6f 669C50 F2C55C 227B4D 7189D9 E07941 665E4B", "'Spacedust' 6e5346 e35b00 5cab96 e3cd7b 0f548b e35b00 06afc7 f0f1ce 684c31 ff8a3a aecab8 ffc878 67a0ce ff8a3a 83a7b4 fefff1", "'SpaceGray' 000000 b04b57 87b379 e5c179 7d8fa4 a47996 85a7a5 b3b8c3 000000 b04b57 87b379 e5c179 7d8fa4 a47996 85a7a5 ffffff", "'SpaceGray Eighties' 15171c ec5f67 81a764 fec254 5486c0 bf83c1 57c2c1 efece7 555555 ff6973 93d493 ffd256 4d84d1 ff55ff 83e9e4 ffffff", "'SpaceGray Eighties Dull' 15171c b24a56 92b477 c6735a 7c8fa5 a5789e 80cdcb b3b8c3 555555 ec5f67 89e986 fec254 5486c0 bf83c1 58c2c1 ffffff", "'Spiderman' 1b1d1e e60813 e22928 e24756 2c3fff 2435db 3256ff fffef6 505354 ff0325 ff3338 fe3a35 1d50ff 747cff 6184ff fffff9", "'Spring' 000000 ff4d83 1f8c3b 1fc95b 1dd3ee 8959a8 3e999f ffffff 000000 ff0021 1fc231 d5b807 15a9fd 8959a8 3e999f ffffff", "'Square' 050505 e9897c b6377d ecebbe a9cdeb 75507b c9caec f2f2f2 141414 f99286 c3f786 fcfbcc b6defb ad7fa8 d7d9fc e2e2e2", "'Sublette' 253045 ee5577 55ee77 ffdd88 5588ff ff77cc 44eeee f5f5da 405570 ee6655 99ee77 ffff77 77bbff aa88ff 55ffbb ffffee", "'Subliminal' 7f7f7f e15a60 a9cfa4 ffe2a9 6699cc f1a5ab 5fb3b3 d4d4d4 7f7f7f e15a60 a9cfa4 ffe2a9 6699cc f1a5ab 5fb3b3 d4d4d4", "'Sundried' 302b2a a7463d 587744 9d602a 485b98 864651 9c814f c9c9c9 4d4e48 aa000c 128c21 fc6a21 7999f7 fd8aa1 fad484 ffffff", "'Symfonic' 000000 dc322f 56db3a ff8400 0084d4 b729d9 ccccff ffffff 1b1d21 dc322f 56db3a ff8400 0084d4 b729d9 ccccff ffffff", "'synthwave' 000000 f6188f 1ebb2b fdf834 2186ec f85a21 12c3e2 ffffff 000000 f841a0 25c141 fdf454 2f9ded f97137 19cde6 ffffff", "'synthwave-everything' fefefe f97e72 72f1b8 fede5d 6d77b3 c792ea f772e0 fefefe fefefe f88414 72f1b8 fff951 36f9f6 e1acff f92aad fefefe", "'SynthwaveAlpha' 241b30 e60a70 00986c adad3e 6e29ad b300ad 00b0b1 b9b1bc 7f7094 e60a70 0ae4a4 f9f972 aa54f9 ff00f6 00fbfd f2f2e3", "'Tango Adapted' 000000 ff0000 59d600 f0cb00 00a2ff c17ecc 00d0d6 e6ebe1 8f928b ff0013 93ff00 fff121 88c9ff e9a7e1 00feff f6f6f4", "'Tango Half Adapted' 000000 ff0000 4cc300 e2c000 008ef6 a96cb3 00bdc3 e0e5db 797d76 ff0013 8af600 ffec00 76bfff d898d1 00f6fa f4f4f2", "'Teerb' 1c1c1c d68686 aed686 d7af87 86aed6 d6aed6 8adbb4 d0d0d0 1c1c1c d68686 aed686 e4c9af 86aed6 d6aed6 b1e7dd efefef", "'Terminal Basic' 000000 990000 00a600 999900 0000b2 b200b2 00a6b2 bfbfbf 666666 e50000 00d900 e5e500 0000ff e500e5 00e5e5 e5e5e5", "'Thayer Bright' 1b1d1e f92672 4df840 f4fd22 2757d6 8c54fe 38c8b5 ccccc6 505354 ff5995 b6e354 feed6c 3f78ff 9e6ffe 23cfd5 f8f8f2", "'The Hulk' 1b1d1e 269d1b 13ce30 63e457 2525f5 641f74 378ca9 d9d8d1 505354 8dff2a 48ff77 3afe16 506b95 72589d 4085a6 e5e6e1", "'Tinacious Design (Dark)' 1d1d26 ff3399 00d364 ffcc66 00cbff cc66ff 00ceca cbcbf0 636667 ff2f92 00d364 ffd479 00cbff d783ff 00d5d4 d5d6f3", "'Tinacious Design (Light)' 1d1d26 ff3399 00d364 ffcc66 00cbff cc66ff 00ceca cbcbf0 636667 ff2f92 00d364 ffd479 00cbff d783ff 00d5d4 d5d6f3", "'TokyoNight' 363b54 f7768e 41a6b5 e0af68 7aa2f7 bb9af7 7dcfff 787c99 363b54 f7768e 41a6b5 e0af68 7aa2f7 bb9af7 7dcfff acb0d0", "'tokyonight' 15161e f7768e 9ece6a e0af68 7aa2f7 bb9af7 7dcfff a9b1d6 414868 f7768e 9ece6a e0af68 7aa2f7 bb9af7 7dcfff c0caf5", "'tokyonight-day' e9e9ed f52a65 587539 8c6c3e 2e7de9 9854f1 007197 6172b0 a1a6c5 f52a65 587539 8c6c3e 2e7de9 9854f1 007197 3760bf", "'tokyonight-storm' 1d202f f7768e 9ece6a e0af68 7aa2f7 bb9af7 7dcfff a9b1d6 414868 f7768e 9ece6a e0af68 7aa2f7 bb9af7 7dcfff c0caf5", "'TokyoNightLight' 0f0f14 8c4351 33635c 8f5e15 34548a 5a4a78 0f4b6e 828594 0f0f14 8c4351 33635c 8f5e15 34548a 5a4a78 0f4b6e 828594", "'TokyoNightStorm' 3b4261 f7768e 73daca e0af68 7aa2f7 bb9af7 7dcfff 7982a9 3b4261 f7768e 73daca e0af68 7aa2f7 bb9af7 7dcfff a9b1d6", "'Tomorrow' 000000 c82829 718c00 eab700 4271ae 8959a8 3e999f ffffff 000000 c82829 718c00 eab700 4271ae 8959a8 3e999f ffffff", "'Tomorrow Night' 000000 cc6666 b5bd68 f0c674 81a2be b294bb 8abeb7 ffffff 000000 cc6666 b5bd68 f0c674 81a2be b294bb 8abeb7 ffffff", "'Tomorrow Night Blue' 000000 ff9da4 d1f1a9 ffeead bbdaff ebbbff 99ffff ffffff 000000 ff9da4 d1f1a9 ffeead bbdaff ebbbff 99ffff ffffff", "'Tomorrow Night Bright' 000000 d54e53 b9ca4a e7c547 7aa6da c397d8 70c0b1 ffffff 000000 d54e53 b9ca4a e7c547 7aa6da c397d8 70c0b1 ffffff", "'Tomorrow Night Burns' 252525 832e31 a63c40 d3494e fc595f df9395 ba8586 f5f5f5 5d6f71 832e31 a63c40 d2494e fc595f df9395 ba8586 f5f5f5", "'Tomorrow Night Eighties' 000000 f2777a 99cc99 ffcc66 6699cc cc99cc 66cccc ffffff 000000 f2777a 99cc99 ffcc66 6699cc cc99cc 66cccc ffffff", "'ToyChest' 2c3f58 be2d26 1a9172 db8e27 325d96 8a5edc 35a08f 23d183 336889 dd5944 31d07b e7d84b 34a6da ae6bdc 42c3ae d5d5d5", "'Treehouse' 321300 b2270e 44a900 aa820c 58859a 97363d b25a1e 786b53 433626 ed5d20 55f238 f2b732 85cfed e14c5a f07d14 ffc800", "'Twilight' 141414 c06d44 afb97a c2a86c 44474a b4be7c 778385 ffffd4 262626 de7c4c ccd88c e2c47e 5a5e62 d0dc8e 8a989b ffffd4", "'Ubuntu' 2e3436 cc0000 4e9a06 c4a000 3465a4 75507b 06989a d3d7cf 555753 ef2929 8ae234 fce94f 729fcf ad7fa8 34e2e2 eeeeec", "'UltraDark' 000000 f07178 c3e88d ffcb6b 82aaff c792ea 89ddff cccccc 333333 f6a9ae dbf1ba ffdfa6 b4ccff ddbdf2 b8eaff ffffff", "'UltraViolent' 242728 ff0090 b6ff00 fff727 47e0fb d731ff 0effbb e1e1e1 636667 fb58b4 deff8c ebe087 7fecff e681ff 69fcd3 f9f9f5", "'UnderTheSea' 022026 b2302d 00a941 59819c 459a86 00599d 5d7e19 405555 384451 ff4242 2aea5e 8ed4fd 61d5ba 1298ff 98d028 58fbd6", "'Unholy' 808080 65AEF7 9CDCFE 608B4E AE81FF D16969 FFFFFF FDD877 808080 569CD6 9CDCFE B5CEA8 AE81FF D16969 FFFFFF DCDCAA", "'Unikitty' 0c0c0c a80f20 bafc8b eedf4b 145fcd ff36a2 6bd1bc e2d7e1 434343 d91329 d3ffaf ffef50 0075ea fdd5e5 79ecd5 fff3fe", "'Urple' 000000 b0425b 37a415 ad5c42 564d9b 6c3ca1 808080 87799c 5d3225 ff6388 29e620 f08161 867aed a05eee eaeaea bfa3ff", "'Vaughn' 25234f 705050 60b48a dfaf8f 5555ff f08cc3 8cd0d3 709080 709080 dca3a3 60b48a f0dfaf 5555ff ec93d3 93e0e3 ffffff", "'VibrantInk' 878787 ff6600 ccff04 ffcc00 44b4cc 9933cc 44b4cc f5f5f5 555555 ff0000 00ff00 ffff00 0000ff ff00ff 00ffff e5e5e5", "'vimbones' f0f0ca a8334c 4f6c31 944927 286486 88507d 3b8992 353535 c6c6a3 94253e 3f5a22 803d1c 1d5573 7b3b70 2b747c 5c5c5c", "'Violet Dark' 56595c c94c22 85981c b4881d 2e8bce d13a82 32a198 c9c6bd 45484b bd3613 738a04 a57705 2176c7 c61c6f 259286 c9c6bd", "'Violet Light' 56595c c94c22 85981c b4881d 2e8bce d13a82 32a198 d3d0c9 45484b bd3613 738a04 a57705 2176c7 c61c6f 259286 c9c6bd", "'WarmNeon' 000000 e24346 39b13a dae145 4261c5 f920fb 2abbd4 d0b8a3 fefcfc e97071 9cc090 ddda7a 7b91d6 f674ba 5ed1e5 d8c8bb", "'Wez' 000000 cc5555 55cc55 cdcd55 5555cc cc55cc 7acaca cccccc 555555 ff5555 55ff55 ffff55 5555ff ff55ff 55ffff ffffff", "'Whimsy' 535178 ef6487 5eca89 fdd877 65aef7 aa7ff0 43c1be ffffff 535178 ef6487 5eca89 fdd877 65aef7 aa7ff0 43c1be ffffff", "'WildCherry' 000507 d94085 2ab250 ffd16f 883cdc ececec c1b8b7 fff8de 009cc9 da6bac f4dca5 eac066 308cba ae636b ff919d e4838d", "'wilmersdorf' 34373e e06383 7ebebd cccccc a6c1e0 e1c1ee 5b94ab ababab 434750 fa7193 8fd7d6 d1dfff b2cff0 efccfd 69abc5 d3d3d3", "'Wombat' 000000 ff615a b1e969 ebd99c 5da9f6 e86aff 82fff7 dedacf 313131 f58c80 ddf88f eee5b2 a5c7ff ddaaff b7fff9 ffffff", "'Wryan' 333333 8c4665 287373 7c7c99 395573 5e468c 31658c 899ca1 3d3d3d bf4d80 53a6a6 9e9ecb 477ab3 7e62b3 6096bf c0c0c0", "'zenbones' f0edec a8334c 4f6c31 944927 286486 88507d 3b8992 2c363c cfc1ba 94253e 3f5a22 803d1c 1d5573 7b3b70 2b747c 4f5e68", "'zenbones_dark' 1c1917 de6e7c 819b69 b77e64 6099c0 b279a7 66a5ad b4bdc3 403833 e8838f 8bae68 d68c67 61abda cf86c1 65b8c1 888f94", "'zenbones_light' f0edec a8334c 4f6c31 944927 286486 88507d 3b8992 2c363c cfc1ba 94253e 3f5a22 803d1c 1d5573 7b3b70 2b747c 4f5e68", "'Zenburn' 4d4d4d 705050 60b48a f0dfaf 506070 dc8cc3 8cd0d3 dcdccc 709080 dca3a3 c3bf9f e0cf9f 94bff3 ec93d3 93e0e3 ffffff", "'zenburned' 404040 e3716e 819b69 b77e64 6099c0 b279a7 66a5ad f0e4cf 625a5b ec8685 8bae68 d68c67 61abda cf86c1 65b8c1 c0ab86", "'zenwritten_dark' 191919 de6e7c 819b69 b77e64 6099c0 b279a7 66a5ad bbbbbb 3d3839 e8838f 8bae68 d68c67 61abda cf86c1 65b8c1 8e8e8e", "'zenwritten_light' eeeeee a8334c 4f6c31 944927 286486 88507d 3b8992 353535 c6c3c3 94253e 3f5a22 803d1c 1d5573 7b3b70 2b747c 5c5c5c"]"""
        self.themes = [shlex.split(i) for i in eval(self.themes)]

        self.keys = (
            "black",
            "red",
            "green",
            "yellow",
            "blue",
            "magenta",
            "cyan",
            "white",
            "Bblack",
            "Bred",
            "Bgreen",
            "Byellow",
            "Bblue",
            "Bmagenta",
            "Bcyan",
            "Bwhite",
        )

        self.levels = {
            1: "[bold red]> [/]",
            2: "[bold yellow]>> [/]",
            3: "[bold green]>>> [/]",
            4: "[bold blue]>>>> [/]",
            5: "[bold magenta]>>>>> [/]",
        }
        self.history = []
        self.allow_min = True
        self.allow_wait = True

        self.panels: list[callable] = []

    def find_theme(self, name):
        for i in self.themes:
            if i[0] == name:
                return i

    def wait(self, text=""):
        if not self.allow_wait:
            return
        if sys.platform == "linux":
            r = os.system(f"read -p '{text}' -n1 -s")
            if r == 2:
                raise KeyboardInterrupt
        elif sys.platform == "win32":
            os.system(f"echo|set /p={text}&& pause >nul")

        # move cursor left *len(text) and print space to overwrite the prompt
        count = len(text)
        self.print(f"\033[{count}D{' '*count}\033[{count}D", end="")

    @property
    def csi(self):
        if self.theme:
            data = dict(zip(self.keys, self.find_theme(self.theme)[1:]))
            data |= dict(
                zip(["b-" + i for i in self.keys], self.find_theme(self.theme)[1:])
            )

            def hex_to_csi(hex, type="fg"):
                # # - fg
                # $ - bg
                if type == "fg":
                    return f"\033[38;2;{int(hex[:2], 16)};{int(hex[2:4], 16)};{int(hex[4:], 16)}m"
                else:
                    return f"\033[48;2;{int(hex[:2], 16)};{int(hex[2:4], 16)};{int(hex[4:], 16)}m"

            data = {
                k: hex_to_csi(v, "bg" if "-" in k else "fg") for k, v in data.items()
            }
        else:
            data = {
                "black": "\033[30m",
                "red": "\033[31m",
                "green": "\033[32m",
                "yellow": "\033[33m",
                "blue": "\033[34m",
                "magenta": "\033[35m",
                "cyan": "\033[36m",
                "white": "\033[37m",
                "Bblack": "\033[90m",
                "Bred": "\033[91m",
                "Bgreen": "\033[92m",
                "Byellow": "\033[93m",
                "Bblue": "\033[94m",
                "Bmagenta": "\033[95m",
                "Bcyan": "\033[96m",
                "Bwhite": "\033[97m",
                "b-black": "\033[40m",
                "b-red": "\033[41m",
                "b-green": "\033[42m",
                "b-yellow": "\033[43m",
                "b-blue": "\033[44m",
                "b-magenta": "\033[45m",
                "b-cyan": "\033[46m",
                "b-white": "\033[47m",
                "b-Bblack": "\033[100m",
                "b-Bred": "\033[101m",
                "b-Bgreen": "\033[102m",
                "b-Byellow": "\033[103m",
                "b-Bblue": "\033[104m",
                "b-Bmagenta": "\033[105m",
                "b-Bcyan": "\033[106m",
                "b-Bwhite": "\033[107m",
            }
        return data | {
            "bold": "\033[1m",
            "underline": "\033[4m",
            "blink": "\033[5m",
            "reverse": "\033[7m",
            "conceal": "\033[8m",
            "strike": "\033[9m",
            "overline": "\033[53m",
        }

    def show_history(self):
        self.print(
            "[bold red]Ваша история:",
            " ".join(self.history),
            "[/]",
        )

    def number_menu(self, prompt, variants, exit_cmd=None):
        def checker(text):
            if text.isdigit():
                if int(text) in range(1, variants + 1):
                    return True
                else:
                    return False
            elif exit_cmd and text == exit_cmd:
                return True
            return False

        def factory(text):
            if text.isdigit():
                return int(text) - 1
            elif exit_cmd and text == exit_cmd:
                return "e"

        return self.prompt(prompt, checker, factory)

    def confirm(self, prompt, exit_cmd=None):
        def checker(text):
            if text in "10tfyn":
                return True
            elif exit_cmd and text == exit_cmd:
                return True
            return False

        def factory(text):
            if text in "1ty":
                return True
            elif text in "0fn":
                return False
            elif exit_cmd and text == exit_cmd:
                return "e"

        return self.prompt(prompt, checker, factory)

    def draw_panel(self):
        # save cursor position
        reset = "\033[100;97m"
        sys.stdout.write("\033[s")
        for i in self.panels:
            # make white bg
            sys.stdout.write("\033E" + reset)
            # move cursor 1 down at start
            sys.stdout.write("\033[1G")
            # print panel
            text = self.format(i(), clear=reset)
            sys.stdout.write(text)

            # print spaces
            width, _ = os.get_terminal_size()
            spaces = " " * (width - self.len_no_ansi(text))
            sys.stdout.write(spaces)
        sys.stdout.write("\033[0m")

    def clear_down(self):
        # clear all after cursor
        sys.stdout.write("\033[u")
        sys.stdout.write("\033[J")

    @staticmethod
    def len_no_ansi(string):
        return len(
            re.sub(
                r"[\u001B\u009B][\[\]()#;?]*((([a-zA-Z\d]*(;[-a-zA-Z\d\/#&.:=?%@~_]*)*)?\u0007)|((\d{1,4}(?:;\d{0,4})*)?[\dA-PR-TZcf-ntqry=><~]))",
                "",
                string,
            )
        )
        
    
        

    def prompt(self, prompt=1, checker=None, factory=None):
        checker = checker or (lambda x: True)
        factory = factory or (lambda x: x)
        while True:
            if not self.queue:
                self.draw_panel()
                try:
                    data = input(self.format(self.levels.get(prompt, prompt)))
                finally:
                    self.clear_down()
                if not data:
                    continue
                data, *self.queue = shlex.split(data)
            else:
                data = self.queue.pop(0)
                self.print(
                    f"[blue][AUTO] {self.levels.get(prompt, prompt)} [bold blue underline]{data}[/]"
                )
            if data == ".?":
                self.print(
                    "[green bold]Список макросов:[/]\n"
                    "  [green].? [/] - показать список макросов\n"
                    "  [green].h [/] - показать историю\n"
                    "  [green].. [/] - повторить последнюю команду\n"
                    "  [green].!N[/] - повторить последние N команд\n"
                    "  [green].x [/] - изменить цветной вывод\n"
                    "  [green].t?[/] - управление темами\n"
                    "  [green].f [/] - отключить все задержки\n"
                    "  [green].w [/] - отключить нажатие для продолжения"
                )
            elif data == ".h":
                self.show_history()

            elif data == "..":
                self.queue.append(self.history[-1])
            elif data.startswith(".!"):
                self.queue = self.history[-int(data[2:] or "1") :] + self.queue
                continue
            elif data == ".x":
                self.color = not self.color
            elif data.startswith(".t"):
                arg = data[2:]
                if not arg:
                    self.print("[red bold]Текущая тема[/]")
                    for i in self.csi.values():
                        self.print(f"{i}X\033[0m", end=" ")
                    self.print("")
                elif arg == "?":
                    self.print(
                        "[green].t?[/]      - справка\n"
                        "[green].t[/]       - текущая тема\n"
                        "[green].t![/]      - список тем\n"
                        "[green].t_THEME[/] - установить\n"
                        "[green].t0[/]      - сбросить на стандартную\n"
                        "[green][/]           (по умолчанию GitHub Dark)\n"
                        "[green][/]           (замените пробелы ':'-ом)"
                    )
                elif arg == "!":
                    self.print("[green bold]Список тем:", end=" ")
                    for i, t in enumerate(self.themes):
                        self.print(
                            f"[{'green' if i % 2 else 'white'}]{t[0]}\033[0m", end=" "
                        )
                elif arg.startswith("_"):
                    sel = arg[1:].replace(":", " ")
                    if self.find_theme(sel):
                        self.theme = sel
                    else:
                        self.print(f"[red bold]Тема {sel} не найдена[/]")
                elif arg == "0":
                    self.theme = None
            elif data == ".f":
                self.allow_min = not self.allow_min
            elif data == ".w":
                self.allow_wait = not self.allow_wait

            elif checker(data):
                self.history.append(data)
                return factory(data)

    def format(self, text, clear="\033[0m"):

        if self.color:
            # replace [red reverse] with \033[31m\033[7m
            text = re.sub(
                r"\[([a-zB0-9 -]+)\]",
                lambda m: "".join(self.csi.get(i, "") for i in m.group(1).split()),
                text,
            )
            # replace [/] with \033[0m
            text = re.sub(r"\[\/\]", clear, text)
            # replace [#123456] with \033[38;2;18;52;86m
            text = re.sub(
                r"\[#([0-9a-fA-F]{6})\]",
                lambda m: f"\033[38;2;{int(m.group(1)[:2], 16)};{int(m.group(1)[2:4], 16)};{int(m.group(1)[4:], 16)}m",
                text,
            )
        else:
            text = re.sub(r"\[([a-z0-9 -]+)\]", "", text)
            text = re.sub(r"\[\/\]", "", text)
            text = re.sub(r"\[#([0-9a-fA-F]{6})\]", "", text)
        return text

    def print(
        self,
        *text,
        sep=" ",
        end="\n",
        min=0,
        max=None,
        format=True,
        convert_float=True,
        line_delay=True,
    ):
        # min+=0.0000001
        min = min if self.allow_min else 0
        text = [
            f"{i:.2f}" if convert_float and isinstance(i, float) else str(i)
            for i in text
        ]
        if format:
            text = [self.format(str(i)) for i in text]
        if min != 0:
            text = sep.join(text) + end
            text = text.splitlines()
            for line in text:
                for i in line:
                    delay = random.uniform(min, max or min)
                    sys.stdout.write(i)
                    sys.stdout.flush()
                    time.sleep(delay)
                time.sleep(delay * 30 * line_delay)
                sys.stdout.write("\n")
        else:
            text = sep.join(text) + end
            sys.stdout.write(text)

    def presense(self, e, minimal=False):
        def bar(value, maximum, color="green", width=15):
            symlen = int(value / maximum * width) if maximum else 0
            return f"[white][[{color}]{'|'*symlen}{' '*(width-symlen)}[white]][/]"

        if minimal:
            self.print(
                f"[bold white]{e.name}[0 white]:"
                f" [red]A={e.attack:.2f} [blue]D={e.defense:.2f}[/] "
                f"{bar(e.hp, e.max_hp)} [cyan]HP={e.hp:.2f}/{e.max_hp:.2f}\n"
            )
        else:
            sp = " " * 4
            self.print(
                f"[bold white]{e.name}[/]\n"
                f"{sp}[cyan]HP={e.hp:.2f}/{e.max_hp:.2f} {bar(e.hp, e.max_hp, 'green')}\n"
                f"{sp}[cyan]MP={e.mp:.2f}/{e.max_mp:.2f} {bar(e.mp, e.max_mp, 'blue')}\n"
                f"{sp}[red]A={e.attack:.2f} [blue]D={e.defense:.2f}\n"
                f"{sp}[bold red]S={e.strength} [bold blue]D={e.dexterity}"
                f" [bold yellow]W={e.wisdom} [bold green]E={e.endurance}"
                f" [bold white]F={e.free_points}[/]"
            )

    def log(self, text, level=1):
        if not level:
            return
        # 1 - debug, 2 - info, 3 - warning, 4 - error, 5 - critical
        color = ["[magenta]", "[blue]", "[green]", "[yellow]", "[red]"][level - 1]
        level = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"][level - 1]
        ts = f"[{datetime.datetime.now().strftime('%H:%M:%S')}]"
        self.print(f"{color}{ts}[/] | {color}[bold]{level}[/] | {color}{text}[/]")

    def __repr__(self):
        return "<Console>"

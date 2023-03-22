import json
from bs4 import BeautifulSoup

html = """
<table class="table p1" align="center" style="text-align:center; margin:auto;">
<tbody><tr>
<th>Number
</th>
<th>Arcana
</th>
<th>P1 Race Equivalent
</th>
<th>P1 Equivalent User
</th>
<th>P2 Equivalent User
</th>
<th>P3 S. Link
</th>
<th>P4 S. Link
</th>
<th>P5 Confidant
</th></tr>
<tr>
<td colspan="1" rowspan="2">0
</td>
<td><a href="/wiki/Fool_Arcana" title="Fool Arcana">Fool</a>
</td>
<td>National Spirit (民霊, <i>Minrei</i>)<sup><a href="/wiki/Help:Japanese" title="Help:Japanese"><span class="t_nihongo_icon" style="font:bold 70% sans-serif;">?</span></a></sup>
</td>
<td>-
</td>
<td>-
</td>
<td><a href="/wiki/Specialized_Extracurricular_Execution_Squad" title="Specialized Extracurricular Execution Squad">SEES</a>
</td>
<td><a href="/wiki/Investigation_Team" title="Investigation Team">Investigation Team</a>
</td>
<td><a href="/wiki/Igor" title="Igor">Igor</a>
</td></tr>
<tr>
<td style="font-weight:normal; background-color:#222"><a href="/wiki/Hunger_Arcana" title="Hunger Arcana">Jester</a><sup>3</sup>
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td><a href="/wiki/Tohru_Adachi" title="Tohru Adachi">Tohru Adachi</a>
</td>
<td>-
</td></tr>
<tr>
<td colspan="1" rowspan="2">I
</td>
<td><a href="/wiki/Magician_Arcana" title="Magician Arcana">Magician</a>
</td>
<td><a href="/wiki/Genma" title="Genma">Genma</a>
</td>
<td><a href="/wiki/Yuka_Ayase" title="Yuka Ayase">Yuka Ayase</a>
</td>
<td>-
</td>
<td><a href="/wiki/Kenji_Tomochika" title="Kenji Tomochika">Kenji Tomochika</a><br><a href="/wiki/Junpei_Iori" title="Junpei Iori">Junpei Iori</a><sup>1</sup>
</td>
<td><a href="/wiki/Yosuke_Hanamura" title="Yosuke Hanamura">Yosuke Hanamura</a>
</td>
<td><a href="/wiki/Morgana" title="Morgana">Morgana</a>
</td></tr>
<tr>
<td style="font-weight:normal; background-color:#222222;"><a href="/wiki/Councillor_Arcana" title="Councillor Arcana">Councillor</a><sup>7</sup>
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td><a href="/wiki/Takuto_Maruki" title="Takuto Maruki">Takuto Maruki</a>
</td></tr>
<tr>
<td>II
</td>
<td><a href="/wiki/Priestess_Arcana" title="Priestess Arcana">Priestess</a>
</td>
<td><a href="/wiki/Megami" title="Megami">Megami</a>
</td>
<td><a href="/wiki/Maki_Sonomura" title="Maki Sonomura">Maki Sonomura</a>
</td>
<td>-
</td>
<td><a href="/wiki/Fuuka_Yamagishi" title="Fuuka Yamagishi">Fuuka Yamagishi</a>
</td>
<td><a href="/wiki/Yukiko_Amagi" title="Yukiko Amagi">Yukiko Amagi</a>
</td>
<td><a href="/wiki/Makoto_Niijima" title="Makoto Niijima">Makoto Niijima</a>
</td></tr>
<tr>
<td>III
</td>
<td><a href="/wiki/Empress_Arcana" title="Empress Arcana">Empress</a>
</td>
<td><a href="/wiki/Lady" title="Lady">Lady</a>
</td>
<td><a href="/wiki/Yukino_Mayuzumi" title="Yukino Mayuzumi">Yukino Mayuzumi</a>
</td>
<td><a href="/wiki/Yukino_Mayuzumi" title="Yukino Mayuzumi">Yukino Mayuzumi</a>
</td>
<td><a href="/wiki/Mitsuru_Kirijo" title="Mitsuru Kirijo">Mitsuru Kirijo</a>
</td>
<td><a href="/wiki/Margaret" title="Margaret">Margaret</a>
</td>
<td><a href="/wiki/Haru_Okumura" title="Haru Okumura">Haru Okumura</a>
</td></tr>
<tr>
<td>IV
</td>
<td><a href="/wiki/Emperor_Arcana" title="Emperor Arcana">Emperor</a>
</td>
<td><a href="/wiki/Deity" title="Deity">Deity</a>
</td>
<td><a href="/wiki/Boy_with_Earring" title="Boy with Earring">Protagonist</a>
</td>
<td>-
</td>
<td><a href="/wiki/Hidetoshi_Odagiri" title="Hidetoshi Odagiri">Hidetoshi Odagiri</a>
</td>
<td><a href="/wiki/Kanji_Tatsumi" title="Kanji Tatsumi">Kanji Tatsumi</a>
</td>
<td><a href="/wiki/Yusuke_Kitagawa" title="Yusuke Kitagawa">Yusuke Kitagawa</a>
</td></tr>
<tr>
<td colspan="1" rowspan="2">V
</td>
<td><a href="/wiki/Hierophant_Arcana" title="Hierophant Arcana">Hierophant</a>
</td>
<td><a href="/wiki/Kishin" title="Kishin">Kishin</a>
</td>
<td><a href="/wiki/Kei_Nanjo" title="Kei Nanjo">Kei Nanjo</a>
</td>
<td><a href="/wiki/Kei_Nanjo" title="Kei Nanjo">Kei Nanjo</a>
</td>
<td><a href="/wiki/Bunkichi_and_Mitsuko" title="Bunkichi and Mitsuko">Bunkichi and Mitsuko</a>
</td>
<td><a href="/wiki/Ryotaro_Dojima" title="Ryotaro Dojima">Ryotaro Dojima</a>
</td>
<td><a href="/wiki/Sojiro_Sakura" title="Sojiro Sakura">Sojiro Sakura</a>
</td></tr>
<tr>
<td style="font-weight:normal; background-color:#222"><a href="/wiki/Apostle_Arcana" title="Apostle Arcana">Apostle</a><sup>8</sup>
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td><a href="/wiki/Zenkichi_Hasegawa" title="Zenkichi Hasegawa">Zenkichi Hasegawa</a>
</td></tr>
<tr>
<td>VI
</td>
<td><a href="/wiki/Lovers_Arcana" title="Lovers Arcana">Lovers</a>
</td>
<td><a href="/wiki/Fairy" title="Fairy">Fairy</a>
</td>
<td>-
</td>
<td><a href="/wiki/Lisa_Silverman" title="Lisa Silverman">Lisa Silverman</a>
</td>
<td><a href="/wiki/Yukari_Takeba" title="Yukari Takeba">Yukari Takeba</a>
</td>
<td><a href="/wiki/Rise_Kujikawa" title="Rise Kujikawa">Rise Kujikawa</a>
</td>
<td><a href="/wiki/Ann_Takamaki" title="Ann Takamaki">Ann Takamaki</a>
</td></tr>
<tr>
<td>VII
</td>
<td><a href="/wiki/Chariot_Arcana" title="Chariot Arcana">Chariot</a>
</td>
<td><a href="/wiki/Fury_(race)" title="Fury (race)">Fury</a>
</td>
<td><a href="/wiki/Masao_Inaba" title="Masao Inaba">Masao Inaba</a>
</td>
<td>-
</td>
<td><a href="/wiki/Kazushi_Miyamoto" title="Kazushi Miyamoto">Kazushi Miyamoto</a><br><a href="/wiki/Rio_Iwasaki" title="Rio Iwasaki">Rio Iwasaki</a><sup>1</sup>
</td>
<td><a href="/wiki/Chie_Satonaka" title="Chie Satonaka">Chie Satonaka</a>
</td>
<td><a href="/wiki/Ryuji_Sakamoto" title="Ryuji Sakamoto">Ryuji Sakamoto</a>
</td></tr>
<tr>
<td>VIII<sup>2</sup>
</td>
<td><a href="/wiki/Justice_Arcana" title="Justice Arcana">Justice</a>
</td>
<td><a href="/wiki/Wargod" title="Wargod">Wargod</a>
</td>
<td><a href="/wiki/Hidehiko_Uesugi" title="Hidehiko Uesugi">Hidehiko Uesugi</a>
</td>
<td><a href="/wiki/Katsuya_Suou" title="Katsuya Suou">Katsuya Suou</a>
</td>
<td><a href="/wiki/Chihiro_Fushimi" title="Chihiro Fushimi">Chihiro Fushimi</a><br><a href="/wiki/Ken_Amada" title="Ken Amada">Ken Amada</a><sup>1</sup>
</td>
<td><a href="/wiki/Nanako_Dojima" title="Nanako Dojima">Nanako Dojima</a>
</td>
<td><a href="/wiki/Goro_Akechi" title="Goro Akechi">Goro Akechi</a>
</td></tr>
<tr>
<td>IX
</td>
<td><a href="/wiki/Hermit_Arcana" title="Hermit Arcana">Hermit</a>
</td>
<td><a href="/wiki/Holy" title="Holy">Holy</a>
</td>
<td>-
</td>
<td>-
</td>
<td><a href="/wiki/Isako_Toriumi" title="Isako Toriumi">"Maya"</a><br><a href="/wiki/Saori_Hasegawa" title="Saori Hasegawa">Saori Hasegawa</a><sup>1</sup>
</td>
<td><a href="/wiki/Fox" title="Fox">Fox</a>
</td>
<td><a href="/wiki/Futaba_Sakura" title="Futaba Sakura">Futaba Sakura</a>
</td></tr>
<tr>
<td>X
</td>
<td><a href="/wiki/Fortune_Arcana" title="Fortune Arcana">Fortune</a>
</td>
<td><a href="/wiki/Beast_(race)" title="Beast (race)">Beast</a>
</td>
<td>-
</td>
<td><a href="/wiki/Jun_Kurosu" title="Jun Kurosu">Jun Kurosu</a>
</td>
<td><a href="/wiki/Keisuke_Hiraga" title="Keisuke Hiraga">Keisuke Hiraga</a><br><a href="/wiki/Ryoji_Mochizuki" title="Ryoji Mochizuki">Ryoji Mochizuki</a><sup>1</sup>
</td>
<td><a href="/wiki/Naoto_Shirogane" title="Naoto Shirogane">Naoto Shirogane</a>
</td>
<td><a href="/wiki/Chihaya_Mifune" title="Chihaya Mifune">Chihaya Mifune</a>
</td></tr>
<tr>
<td rowspan="2">XI<sup>2</sup>
</td>
<td><a href="/wiki/Strength_Arcana" title="Strength Arcana">Strength</a>
</td>
<td><a href="/wiki/Snake" title="Snake">Snake</a>
</td>
<td>-
</td>
<td>-
</td>
<td><a href="/wiki/Yuko_Nishiwaki" title="Yuko Nishiwaki">Yuko Nishiwaki</a><br><a href="/wiki/Koromaru" title="Koromaru">Koromaru</a><sup>1</sup>
</td>
<td><a href="/wiki/Kou_Ichijo" title="Kou Ichijo">Kou Ichijo</a> or<br><a href="/wiki/Daisuke_Nagase" title="Daisuke Nagase">Daisuke Nagase</a>
</td>
<td><a href="/wiki/Caroline_and_Justine" class="mw-redirect" title="Caroline and Justine">Caroline and Justine</a>
</td></tr>
<tr>
<td style="font-weight:normal; background-color:#222"><a href="/wiki/Hunger_Arcana" title="Hunger Arcana">Hunger</a><sup>3</sup>
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td><a href="/wiki/Tohru_Adachi" title="Tohru Adachi">Tohru Adachi</a>
</td>
<td>-
</td></tr>
<tr>
<td>XII
</td>
<td><a href="/wiki/Hanged_Man_Arcana" title="Hanged Man Arcana">Hanged Man</a>
</td>
<td><a href="/wiki/Fallen" title="Fallen">Fallen</a>
</td>
<td>-
</td>
<td><a href="/wiki/Baofu" title="Baofu">Baofu</a>
</td>
<td><a href="/wiki/Maiko_Oohashi" title="Maiko Oohashi">Maiko Oohashi</a>
</td>
<td><a href="/wiki/Naoki_Konishi" title="Naoki Konishi">Naoki Konishi</a>
</td>
<td><a href="/wiki/Munehisa_Iwai" title="Munehisa Iwai">Munehisa Iwai</a>
</td></tr>
<tr>
<td>XIII
</td>
<td><a href="/wiki/Death_Arcana" title="Death Arcana">Death</a>
</td>
<td><a href="/wiki/Reaper_(race)" title="Reaper (race)">Reaper</a>
</td>
<td>-
</td>
<td><a href="/wiki/Eikichi_Mishina" title="Eikichi Mishina">Eikichi Mishina</a>
</td>
<td><a href="/wiki/Pharos" title="Pharos">Pharos</a>
</td>
<td><a href="/wiki/Hisano_Kuroda" title="Hisano Kuroda">Hisano Kuroda</a>
</td>
<td><a href="/wiki/Tae_Takemi" title="Tae Takemi">Tae Takemi</a>
</td></tr>
<tr>
<td>XIV
</td>
<td><a href="/wiki/Temperance_Arcana" title="Temperance Arcana">Temperance</a>
</td>
<td><a href="/wiki/Avatar" title="Avatar">Avatar</a>
</td>
<td>-
</td>
<td>-
</td>
<td><a href="/wiki/Andre_Laurent_Jean_Geraux" title="Andre Laurent Jean Geraux">Andre Laurent Jean Geraux</a>
</td>
<td><a href="/wiki/Eri_Minami" title="Eri Minami">Eri Minami</a>
</td>
<td><a href="/wiki/Sadayo_Kawakami" title="Sadayo Kawakami">Sadayo Kawakami</a>
</td></tr>
<tr>
<td>XV
</td>
<td><a href="/wiki/Devil_Arcana" title="Devil Arcana">Devil</a>
</td>
<td><a href="/wiki/Tyrant" title="Tyrant">Tyrant</a>
</td>
<td><a href="/wiki/Reiji_Kido" title="Reiji Kido">Reiji Kido</a>
</td>
<td>-
</td>
<td><a href="/wiki/President_Tanaka" title="President Tanaka">President Tanaka</a>
</td>
<td><a href="/wiki/Sayoko_Uehara" title="Sayoko Uehara">Sayoko Uehara</a>
</td>
<td><a href="/wiki/Ichiko_Ohya" title="Ichiko Ohya">Ichiko Ohya</a>
</td></tr>
<tr>
<td>XVI
</td>
<td><a href="/wiki/Tower_Arcana" title="Tower Arcana">Tower</a>
</td>
<td><a href="/wiki/Vile" title="Vile">Vile</a>
</td>
<td>-
</td>
<td>-
</td>
<td><a href="/wiki/Mutatsu" title="Mutatsu">Mutatsu</a>
</td>
<td><a href="/wiki/Shu_Nakajima" title="Shu Nakajima">Shu Nakajima</a>
</td>
<td><a href="/wiki/Shinya_Oda" title="Shinya Oda">Shinya Oda</a>
</td></tr>
<tr>
<td>XVII
</td>
<td><a href="/wiki/Star_Arcana" title="Star Arcana">Star</a>
</td>
<td><a href="/wiki/Yoma" title="Yoma">Yoma</a>
</td>
<td>-
</td>
<td><a href="/wiki/Ulala_Serizawa" title="Ulala Serizawa">Ulala Serizawa</a>
</td>
<td><a href="/wiki/Mamoru_Hayase" title="Mamoru Hayase">Mamoru Hayase</a><br><a href="/wiki/Akihiko_Sanada" title="Akihiko Sanada">Akihiko Sanada</a><sup>1</sup>
</td>
<td><a href="/wiki/Teddie" title="Teddie">Teddie</a>
</td>
<td><a href="/wiki/Hifumi_Togo" title="Hifumi Togo">Hifumi Togo</a>
</td></tr>
<tr>
<td>XVIII
</td>
<td><a href="/wiki/Moon_Arcana" title="Moon Arcana">Moon</a>
</td>
<td><a href="/wiki/Night" title="Night">Night</a>
</td>
<td>-
</td>
<td><a href="/wiki/Maya_Amano" title="Maya Amano">Maya Amano</a>
</td>
<td><a href="/wiki/Nozomi_Suemitsu" title="Nozomi Suemitsu">Nozomi Suemitsu</a><br><a href="/wiki/Shinjiro_Aragaki" title="Shinjiro Aragaki">Shinjiro Aragaki</a><sup>1</sup>
</td>
<td><a href="/wiki/Ai_Ebihara" title="Ai Ebihara">Ai Ebihara</a>
</td>
<td><a href="/wiki/Yuuki_Mishima" title="Yuuki Mishima">Yuuki Mishima</a>
</td></tr>
<tr>
<td>XIX
</td>
<td><a href="/wiki/Sun_Arcana" title="Sun Arcana">Sun</a>
</td>
<td><a href="/wiki/Avian" title="Avian">Avian</a>
</td>
<td>-
</td>
<td><a href="/wiki/Tatsuya_Suou" title="Tatsuya Suou">Tatsuya Suou</a>
</td>
<td><a href="/wiki/Akinari_Kamiki" title="Akinari Kamiki">Akinari Kamiki</a>
</td>
<td><a href="/wiki/Yumi_Ozawa" title="Yumi Ozawa">Yumi Ozawa</a> or<br><a href="/wiki/Ayane_Matsunaga" title="Ayane Matsunaga">Ayane Matsunaga</a>
</td>
<td><a href="/wiki/Toranosuke_Yoshida" title="Toranosuke Yoshida">Toranosuke Yoshida</a>
</td></tr>
<tr>
<td rowspan="2">XX
</td>
<td><a href="/wiki/Judgement_Arcana" title="Judgement Arcana">Judgement</a>
</td>
<td><a href="/wiki/Herald" title="Herald">Herald</a>
</td>
<td><a href="/wiki/Eriko_Kirishima" title="Eriko Kirishima">Eriko Kirishima</a>
</td>
<td><a href="/wiki/Eriko_Kirishima" title="Eriko Kirishima">Eriko Kirishima</a>
</td>
<td><a href="/wiki/Specialized_Extracurricular_Execution_Squad" title="Specialized Extracurricular Execution Squad">Nyx Annihilation Team</a>
</td>
<td><a href="/wiki/Investigation_Team" title="Investigation Team">Seekers of Truth</a>
</td>
<td><a href="/wiki/Sae_Niijima" title="Sae Niijima">Sae Niijima</a>
</td></tr>
<tr>
<td style="font-weight:normal; background-color:#222"><a href="/wiki/Aeon_Arcana" title="Aeon Arcana">Aeon</a>
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td><a href="/wiki/Aigis" title="Aigis">Aigis</a><sup>4</sup>
</td>
<td><a href="/wiki/Marie" title="Marie">Marie</a><sup>5</sup>
</td>
<td>-
</td></tr>
<tr>
<td rowspan="2">XXI
</td>
<td><a href="/wiki/World_Arcana" title="World Arcana">World</a>
</td>
<td><a href="/wiki/Dragon" title="Dragon">Dragon</a>
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td></tr>
<tr title="Persona 3 only">
<td style="font-weight:normal; background-color:#222"><a href="/wiki/Universe_Arcana" title="Universe Arcana">Universe</a><sup>6</sup>
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td></tr>
<tr>
<td rowspan="2">Unnumbered
</td>
<td><a href="/wiki/Faith_Arcana" title="Faith Arcana">Faith</a><sup>7</sup> <sup>9</sup>
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td><a href="/wiki/Sumire_Yoshizawa" title="Sumire Yoshizawa">Sumire Yoshizawa</a>
</td></tr>
<tr>
<td style="font-weight:normal; background-color:#222"><a href="/wiki/Hope_Arcana" title="Hope Arcana">Hope</a><sup>8</sup> <sup>9</sup>
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td>-
</td>
<td><a href="/wiki/Sophia_(Persona_5_Strikers)" title="Sophia (Persona 5 Strikers)">Sophia</a>
</td></tr></tbody></table> 
"""  # noqa

images = {
    "Fool": "https://static.wikia.nocookie.net/megamitensei/images/5/53/Fool-0.png/revision/latest/scale-to-width-down/130?cb=20160404201043",  # noqa
    "Magician": "https://static.wikia.nocookie.net/megamitensei/images/c/cb/Magician-0.png/revision/latest/scale-to-width-down/130?cb=20160404201629",  # noqa
    "Priestess": "https://static.wikia.nocookie.net/megamitensei/images/a/ad/Priestess-0.png/revision/latest/scale-to-width-down/130?cb=20160404201724",  # noqa
    "Empress": "https://static.wikia.nocookie.net/megamitensei/images/6/63/Empress-0.png/revision/latest/scale-to-width-down/130?cb=20160404201807",  # noqa
    "Emperor": "https://static.wikia.nocookie.net/megamitensei/images/e/e6/Emperor-0.png/revision/latest/scale-to-width-down/130?cb=20160404201848",  # noqa
    "Hierophant": "https://static.wikia.nocookie.net/megamitensei/images/f/f6/Hierophant-0.png/revision/latest/scale-to-width-down/130?cb=20160404201947",  # noqa
    "Lovers": "https://static.wikia.nocookie.net/megamitensei/images/a/a5/Lovers-0.png/revision/latest/scale-to-width-down/130?cb=20160404202019",  # noqa
    "Chariot": "https://static.wikia.nocookie.net/megamitensei/images/1/15/Chariot-0.png/revision/latest/scale-to-width-down/130?cb=20160404202048",  # noqa
    "Justice": "https://static.wikia.nocookie.net/megamitensei/images/8/83/Justice-0.png/revision/latest/scale-to-width-down/130?cb=20160404202153",  # noqa
    "Hermit": "https://static.wikia.nocookie.net/megamitensei/images/a/ab/Hermit-0.png/revision/latest/scale-to-width-down/130?cb=20160404202218",  # noqa
    "Fortune": "https://static.wikia.nocookie.net/megamitensei/images/f/f3/Fortune-0.png/revision/latest/scale-to-width-down/130?cb=20160404202245",  # noqa
    "Strength": "https://static.wikia.nocookie.net/megamitensei/images/b/b0/Strength-0.png/revision/latest/scale-to-width-down/130?cb=20160404202121",  # noqa
    "Hanged_Man": "https://static.wikia.nocookie.net/megamitensei/images/2/2f/Hanged_Man.png/revision/latest/scale-to-width-down/130?cb=20160404202318",  # noqa
    "Death": "https://static.wikia.nocookie.net/megamitensei/images/d/df/Death-0.png/revision/latest/scale-to-width-down/130?cb=20160404202413",  # noqa
    "Temperance": "https://static.wikia.nocookie.net/megamitensei/images/2/2d/Temperance-0.png/revision/latest/scale-to-width-down/130?cb=20160404202449",  # noqa
    "Devil": "https://static.wikia.nocookie.net/megamitensei/images/4/4b/Devil-0.png/revision/latest/scale-to-width-down/130?cb=20160404202521",  # noqa
    "Tower": "https://static.wikia.nocookie.net/megamitensei/images/1/1f/Tower-0.png/revision/latest/scale-to-width-down/130?cb=20160404202557",  # noqa
    "Star": "https://static.wikia.nocookie.net/megamitensei/images/1/15/Star-0.png/revision/latest/scale-to-width-down/130?cb=20160404202628",  # noqa
    "Moon": "https://static.wikia.nocookie.net/megamitensei/images/c/ce/Moon-0.png/revision/latest/scale-to-width-down/130?cb=20160404202708",  # noqa
    "Sun": "https://static.wikia.nocookie.net/megamitensei/images/f/ff/Sun-0.png/revision/latest/scale-to-width-down/130?cb=20160404202738",  # noqa
    "Judgement": "https://static.wikia.nocookie.net/megamitensei/images/b/b0/Judgement.png/revision/latest/scale-to-width-down/130?cb=20160404202809",  # noqa
    "World": "https://static.wikia.nocookie.net/megamitensei/images/a/a9/World-0.png/revision/latest/scale-to-width-down/130?cb=20160404202908",  # noqa
}

# load the html into a BeautifulSoup object
soup = BeautifulSoup(html, "html.parser")

# find the table
table = soup.find("table")

# find all the rows in the table
rows = table.find_all("tr")

base_url = "https://megamitensei.fandom.com"


def find_infos(col):
    if col:
        names = [x.text for x in col.find_all("a")]
        urls = [f'{base_url}{x["href"]}' for x in col.find_all("a")]
        return list(zip(names, urls))
    return []


# loop through the rows
arcanas = {}
for row in rows:
    # find all the columns in the row
    cols = row.find_all("td")

    # skip invalid rows
    if len(cols) == 0:
        continue

    # get info (index is used to skip category column on some rows)
    index = 0
    if len(cols) == 8:
        # <td rowspan="2">XI<sup>2</sup> -> XI
        category = cols[0].text.split("<")[0].strip()
    else:
        index = -1

    # category must be only letters unless it's 0
    if category != "0" and not category.isalpha():
        category = "".join([x for x in category if x.isalpha()])

    # <td><a href="/wiki/Judgement_Arcana" title="Judgement Arcana">Judgement</a> -> Judgement # noqa
    arcana_name = cols[index + 1].find("a").text
    arcana_url = f'{base_url}{cols[index + 1].find("a")["href"]}'

    # get characters
    games = {}
    games["Persona 3"] = find_infos(cols[index + 5])
    games["Persona 4"] = find_infos(cols[index + 6])
    games["Persona 5"] = find_infos(cols[index + 7])

    # format info
    if category not in arcanas:
        arcanas[category] = {}

    arcanas[category][arcana_name] = {
        "category": category,
        "name": arcana_name,
        "url": arcana_url,
        "characters": [],
    }

    # add characters (expand the list to match the number of games)
    for game, characters in games.items():
        for name, url in characters:
            arcanas[category][arcana_name]["characters"].append(
                {"name": name, "url": url, "game": game}
            )

# manually add the protagonists
arcanas["XXI"]["Universe"]["characters"].append(
    {
        "name": "Makoto Yuki",
        "url": "https://megamitensei.fandom.com/wiki/Makoto_Yuki",
        "game": "Persona 3",
    }
)
arcanas["XXI"]["World"]["characters"].append(
    {
        "name": "Yu Narukami",
        "url": "https://megamitensei.fandom.com/wiki/Yu_Narukami",
        "game": "Persona 4",
    }
)
arcanas["XXI"]["Universe"]["characters"].append(
    {
        "name": "Ren Amamiya",
        "url": "https://megamitensei.fandom.com/wiki/Ren_Amamiya",
        "game": "Persona 5",
    }
)

# save to json
with open("arcanas.json", "wb") as f:
    f.write(json.dumps(arcanas, indent=4).encode("utf-8"))

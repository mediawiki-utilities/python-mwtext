from mwtext.content_transformers import Wikitext2Words


def test_preprocessing_english():
    forbidden_link_prefixes = ['category', 'image', 'file']

    wtpp = Wikitext2Words(forbidden_link_prefixes, CJK=True)
    text = """
{{Infobox thing
 | derp = herp
 | image = file.jpg}}
[[Image:Animage.jpg]]
; This is a term
== Here's a header ==
This is some text.  It should [[show]] up [[pretty:naturally]].{{fact}}
== Another header ==
Here is another paragraph.  Nothing [[inane|special]] here.<ref name="wut"/>
[[Category:foobar]]"""
    assert list(wtpp.transform(text)) == \
        ["this", "is", "some", "text", "it", "should", "show", "up", "pretty",
         "naturally", "here", "is", "another", "paragraph", "nothing",
         "special", "here"]


def test_preprocessing_vietnamese():
    forbidden_link_prefixes = [
        'category', 'image', 'file',
        'tập tin', 'thể loại']

    wtpp = Wikitext2Words(forbidden_link_prefixes, CJK=True)
    text = """
{{Infobox actor
|name = George Lucas
|image = George Lucas, Pasadena.jpg
|birthdate = {{birth date and age|1944|5|14}}
|birthplace = [[Modesto]], [[California]], <br />[[Hoa Kỳ]]
|birthname = George Walton Lucas, Jr.
|yearsactive = 1965-nay
|spouse = [[Marcia Lucas]] (1969–1983)
|domesticpartner = [[Mellody Hobson]] (2007—)
}}
'''George Walton Lucas, Jr.''' (sinh ngày 14 tháng 5 năm 1944) là một nhà sản xuất phim, đạo diễn, diễn viên, tác giả kịch bản người Mỹ và là chủ tịch của hãng [[Lucasfilm]]. Ông được biết đến nhiều nhất với vai trò tác giả của loạt phim khoa học viễn tưởng ''[[Chiến tranh giữa các vì sao]]'' và bộ phim phiêu lưu ''[[Indiana Jones (loạt phim)|Indiana Jones]]''. George Lucas cũng là một tỷ phú với tài sản 3,9 tỷ đô la Mỹ (thống kê năm 2007).<ref>{{chú thích web|url=http://www.forbes.com/lists/2007/10/07billionaires_George-Lucas_PNOV.html| title=George Lucas ranks 243 on The World's Billionaires 2007 |work=[[Forbes]] |accessdate = ngày 1 tháng 5 năm 2007 |date = ngày 1 tháng 5 năm 2007}}</ref>


{{George Lucas}}
{{Lucasfilm}}
{{sơ khai diễn viên Mỹ}}

{{DEFAULTSORT:Lucas, George}}
[[Thể loại:Tỷ phú Hoa Kỳ]]
[[Thể loại:Nam tiểu thuyết gia Mỹ]]
""" # Noqa
    assert list(wtpp.transform(text)) == \
        ['george', 'walton', 'lucas', 'jr', 'sinh', 'ngày', 'anumber', 'tháng',
         'anumber', 'năm', 'anumber', 'là', 'một', 'nhà', 'sản', 'xuất',
         'phim', 'đạo', 'diễn', 'diễn', 'viên', 'tác', 'giả', 'kịch', 'bản',
         'người', 'mỹ', 'và', 'là', 'chủ', 'tịch', 'của', 'hãng', 'lucasfilm',
         'ông', 'được', 'biết', 'đến', 'nhiều', 'nhất', 'với', 'vai', 'trò',
         'tác', 'giả', 'của', 'loạt', 'phim', 'khoa', 'học', 'viễn', 'tưởng',
         'chiến', 'tranh', 'giữa', 'các', 'vì', 'sao', 'và', 'bộ', 'phim',
         'phiêu', 'lưu', 'indiana', 'jones', 'george', 'lucas', 'cũng', 'là',
         'một', 'tỷ', 'phú', 'với', 'tài', 'sản', 'anumber', 'tỷ', 'đô', 'la',
         'mỹ', 'thống', 'kê', 'năm', 'anumber']


def test_preprocessing_korean():
    forbidden_link_prefixes = [
        'category', 'image', 'file',
        '파일', '분류', '그림']

    wtpp = Wikitext2Words(forbidden_link_prefixes, CJK=True)
    text = """
{{영화인 정보
|이름       = 조지 루카스
|원어명   = George Lucas
|사진   = Time 100 George Lucas.jpg|섬네일|300px
|기타       =
}}
'''조지 월턴 루카스 주니어'''(George Walton Lucas, Jr.<ref>{{서적 인용 |성=White |이름=Dana |날짜=2000년 |제목=George Lucas |번역제목= |url= |언어= |쪽=12 |출판사=Twenty-First Century Books |isbn=0822549751 |확인날짜= }}</ref>, [[1944년]] [[5월 14일]] ~ )는 [[미국]]의 영화 제작자이자 기업가이다. 《[[스타워즈]]》와 《[[인디아나 존스]]》 프랜차이즈의 창작자로 가장 유명하며, [[루카스필름]]과 [[인더스트리얼 라이트 & 매직]] 그리고 [[스카이워커 사운드]]등의 설립자이기도 하다. 2012년 루카스필름을 [[월트 디즈니 컴퍼니]]에 매각하기 전까지는 루카스필름의 회장 겸 최고경영자(CEO)였다<ref>{{뉴스 인용 |저자= |제목=‘스타워즈’ 제작 루카스필름, 월트디즈니에 팔린다 |url=http://news.khan.co.kr/kh_news/khan_art_view.html?artid=201210312200155 |뉴스=경향신문 |출판사= |위치= |날짜=2012-10-31 |확인날짜= }}</ref>.

== 상세 ==
《[[인디아나 존스]]》의 세 번째 시리즈인 《[[인디아나 존스와 최후의 성전]]》을 제작한 뒤 그 속편을 제작하지 않고 영화에서 손을 떼겠다고 발표하기도 했다. 당시 《인디아나 존스》 시리즈는 영화와 게임으로 발표하였는데, 네 번째 시리즈는 게임만 발표하였다. 그 뒤 영화계에 복귀한 뒤 네 번째 시리즈를 제작하여 2008년 개봉하였다. 그래서 《인디아나 존스》 시리즈의 세 번째 작품까지는 영화가 원작이지만, 네 번째 작품인 《[[인디아나 존스: 크리스탈 해골의 왕국]]》은 어느 것이 원작인지 불분명하다. 당시 그 영화를 제작하다가 중단하고 게임을 제작했으며, 이런 관점에서는 영화가 원작이다. 그러나 2008년 개봉된 영화는 게임 내용을 바탕으로 처음부터 다시 제작했으며, 이런 관점에서 게임이 원작이기 때문이다.



{{스타 워즈}}
{{루카스필름}}
{{전거 통제}}
{{기본정렬:루카스, 조지}}
[[분류:머데스토 출신]]
""" # Noqa
    assert list(wtpp.transform(text)) == \
        ['조지', '월턴', '루카스', '주니어', 'george', 'walton', 'lucas', 'jr',
         'anumber', '년', 'anumber', '월', 'anumber', '일', '는', '미국', '의',
         '영화', '제작자', '이자', '기업가', '이다', '스타워즈', '와', '인디아나',
         '존스', '프랜차이즈', '의', '창작', '자', '로', '가장', '유명하며',
         '루카스필름', '과', '인더스트리얼', '라이트', '매직', '그리고', '스카이워커',
         '사운드', '등', '의', '설립', '자', '이기도', '하다', 'anumber', '년',
         '루카스필름', '을', '월트', '디즈니', '컴퍼니', '에', '매각', '하기', '전',
         '까지는', '루카스필름', '의', '회장', '겸', '최고경영자', 'ceo', '였다',
         '인디아나', '존스', '의', '세', '번째', '시리즈', '인', '인디아나', '존스',
         '와', '최후', '의', '성전', '을', '제작', '한', '뒤', '그', '속편', '을',
         '제작', '하지', '않고', '영화', '에서', '손', '을', '떼겠다고', '발표',
         '하기도', '했다', '당시', '인디아나', '존스', '시리즈', '는', '영화', '와',
         '게임', '으로', '발표', '하였는데', '네', '번째', '시리즈', '는', '게임', '만',
         '발표', '하였다', '그', '뒤', '영화계', '에', '복귀', '한', '뒤', '네', '번째',
         '시리즈', '를', '제작', '하여', 'anumber', '년', '개봉', '하였다', '그래서',
         '인디아나', '존스', '시리즈', '의', '세', '번째', '작품', '까지는', '영화',
         '가', '원작', '이지만', '네', '번째', '작품', '인', '인디아나', '존스',
         '크리스탈', '해골', '의', '왕국', '은', '어느', '것', '이', '원작', '인지',
         '불분명', '하다', '당시', '그', '영화', '를', '제작', '하다가', '중단', '하고',
         '게임', '을', '제작', '했으며', '이런', '관점', '에서는', '영화', '가', '원작',
         '이다', '그러나', 'anumber', '년', '개봉', '된', '영화', '는', '게임', '내용',
         '을', '바탕', '으로', '처음', '부터', '다시', '제작', '했으며', '이런', '관점',
         '에서', '게임', '이', '원작', '이기', '때문', '이다']


def test_preprocessing_arabic():
    forbidden_link_prefixes = [
        'category', 'image', 'file',
        'تصنيف', 'ملف', 'صورة']

    wtpp = Wikitext2Words(forbidden_link_prefixes, CJK=True)
    text = """
{{معلومات ممثل
| الاسم              = جورج لوكاس
| صورة              = George Lucas cropped 2009.jpg
| قياس_الصورة       =
| اسم_الولادة        =
| تاريخ_الولادة      = {{تاريخ الميلاد والعمر|1944|5|14}}
| مكان_الولادة       =
}}
'''جورج لوكاس''' ([[14 مايو]] [[1944]] ،[[موديستو، كاليفورنيا|موديستو]]، [[كاليفورنيا]])، [[مخرج]] و[[سيناريو (فن)|سيناريست]] و[[منتج]] اشتهر بإخراجه وإنتاجه لفيلم '''[[حرب النجوم (فيلم)|حرب النجوم]]'''.

== الترشيحات لجائزة الأوسكار ==
جوائز
* أفضل نص مقتبس عام 1974 عن فيلم American Graffiti
* أفضل مخرج عام 1974 عن فيلم American Graffiti
* أفضل نص أصلي عام 1978 عن فيلم [[حرب النجوم (فيلم)|Star Wars]]
* أفضل مخرج عام 1978 عن فيلم [[حرب النجوم (فيلم)|Star Wars]]

== الترشيحات لجائزة الجولدن جلوب ==
أفضل مخرج عام 1999

أفضل مخرج عام 1974 عن فيلم American Graffiti

أفضل مخرج عام 1978 عن فيلم [[حرب النجوم (فيلم)|Star Wars]]

== وصلات خارجية ==
* {{روابط فنية}}
* {{Isfdb name}}
== مراجع ==
{{مراجع}}

{{تصنيف كومنز|George Lucas}}
{{أفلام من إخراج جورج لوكاس}}
{{مواقع التواصل الاجتماعي}}
{{مكرمون مركز كينيدي الثقافي (عقد 2010)}}
{{جائزة بافتا بريتانيا لوس أنجلوس}}
[[تصنيف:مواليد 1944]]
[[تصنيف:مواليد في موديستو (كاليفورنيا)]]
[[تصنيف:ميثوديون أمريكيون]]

[[تصنيف:فاعلو خير في القرن 21]]
""" # Noqa
    assert list(wtpp.transform(text)) == \
        ['جورج', 'لوكاس', 'anumber', 'مايو', 'anumber',
         '،موديستو،', 'كاليفورنيا', '،', 'مخرج', 'وسيناريست', 'ومنتج',
         'اشتهر', 'بإخراجه', 'وإنتاجه', 'لفيلم',
         'حرب', 'النجوم',
         'جوائز', 'أفضل', 'نص', 'مقتبس', 'عام', 'anumber', 'عن', 'فيلم',
         'american', 'graffiti', 'أفضل', 'مخرج', 'عام', 'anumber', 'عن',
         'فيلم', 'american', 'graffiti', 'أفضل', 'نص', 'أصلي', 'عام',
         'anumber', 'عن', 'فيلم', 'star', 'wars', 'أفضل', 'مخرج', 'عام',
         'anumber', 'عن', 'فيلم', 'star', 'wars',
         'أفضل', 'مخرج', 'عام', 'anumber',
         'أفضل', 'مخرج', 'عام', 'anumber', 'عن', 'فيلم', 'american',
         'graffiti',
         'أفضل', 'مخرج', 'عام', 'anumber', 'عن', 'فيلم', 'star', 'wars']


def test_preprocessing_japanese():
    forbidden_link_prefixes = [
        'category', 'image', 'file']

    wtpp = Wikitext2Words(forbidden_link_prefixes, CJK=True)
    text = """
{{Vertical_images_list
|寄せ=
|幅=160px
|枠幅=
| 1=Matsuyama castle(Iyo) Nohara-Yagura &amp; Inui-Yagura.JPG
| 2=搦手の守りの要である野原櫓と乾櫓
| 3=MATSUYAMA_CASTLE(IYO),TENJIN_YAGURA.JPG
| 4=天神櫓（[[菅原道真]]を本壇で祀る）
| 5=Matsuyama castle(Iyo) Hommaru-Ido(Well).JPG
| 6=本丸の深さ約40メートルの井戸
}}
'''松山城'''（まつやまじょう）は、[[愛媛県]][[松山市]]にあった[[日本の城]]。別名 金亀城（きんきじょう）、勝山城（かつやまじょう）。各地の[[松山城]]と区別するため「伊予松山城」と呼ばれることもあるが、一般的に「松山城」は本城を指すことが多い{{efn|[[現存12天守]]と'''所在地が同じ名の「松山」市'''という2つの点で、同じく現存12天守で岡山県高梁市にある松山城とはこちらが優勢する形となり、一方は「[[備中松山城]]」で一歩後退して譲る形となっている。}}。たびたび放火（不審火）
や失火により往時の建造物を焼失している。

現在は、城跡の主要部分が公園として整備され、[[天守|大天守]]（[[現存天守|現存12天守]]の1つ）を含む21棟の現存建造物が国の[[重要文化財]]に、[[城郭]]遺構が国の[[史跡]]に指定されている。そのほか、連立式天守群の小天守以下5棟をはじめとする22棟（塀を含む）が木造で復元されている。

また、[[現存天守|現存十二天守]]としては、最も新しい城である。

== 概要 ==
松山市の中心部、[[城山 (松山市)|勝山]]（城山）山頂に[[本丸]]、西南麓に二之丸と三之丸を構える[[平山城]]である。[[日本三大一覧#城|日本三大平山城]]にも数えられる。山頂の本壇にある天守（大天守）は、日本の12箇所に現存する天守の一つである。この中では、[[姫路城]]と同じく、[[天守#縄張り|連立式]]で、[[日本三大一覧#城|日本三大連立式平山城]]の1つにも数えられる。1933年ごろまでは、本丸部分には40棟の建造物が現存していたが、1949年までに19棟が火災により失われ、現存建築は21棟にまで減少した。建造物の現存数は[[二条城]]（京都府）の28棟に次ぐものである。

[[幕末]]に再建された大天守ほか、日本で現存数の少ない[[天守#型式|望楼型]][[櫓 (城郭)|二重櫓]]である野原櫓（騎馬櫓）や、深さ44メートルにおよぶ[[本丸]]の[[井戸]]などが保存されている。

== 構造 ==
山頂に本丸、南西麓に二之丸、続いて三之丸。北麓には北曲輪、南東麓に東曲輪がある。三之丸は比高6メートルほどの[[土塁]]で囲み、北と東に[[石垣]]造の[[虎口]]を開く。本丸から二之丸にかけて[[登り石垣]]を築いて囲み、丘陵斜面からの大手城道への侵入を防ぐ構造としている。山頂の本丸北部には本壇という天守曲輪を持ち、大天守と小天守・南隅櫓・北隅櫓を3棟の渡櫓（廊下）で連結し[[天守#連立式|連立式]]天守をなしている。松山城の中枢は二の丸で、藩主の生活の場である御殿や庭園、茶室などがあった。三の丸には身分の高い家来の屋敷が建ち並んでいた。本丸は主に倉庫として使われていた。

== 歴史・沿革 ==
=== 江戸時代 ===
* [[1602年]]（[[慶長]]7年）、[[伊予国]][[松前城 (伊予国)|正木城]]（[[松前町 (愛媛県)|松前]]）城主10万石の[[大名]]であった[[加藤嘉明]]{{efn|[[賤ヶ岳の戦い#賤ヶ岳の七本槍|賤ヶ岳の七本槍]]の一人で、[[文禄・慶長の役|朝鮮出兵]]における[[水軍]]の将。}}が、[[関ヶ原の戦い]]での戦功により20万石に加増され、[[足立重信]]を普請[[奉行]]に任じ、麓に二之丸（二之丸史跡庭園）と三之丸（堀之内）を有する[[平山城]]の築城に着手した{{efn|[[倭城]]の防御手法であるといわれる二之丸と[[本丸]]間を結ぶ[[登り石垣]]（竪石垣）を築いている。}}。
"""# Noqa
    assert list(wtpp.transform(text)) == \
        ['松山', '城', 'まつ', 'やま', 'じょう', 'は', '愛媛県', '松山市', 'に', 'あっ',
         'た', '日本', 'の', '城', '別名', '金亀', '城', 'きん', 'きじょう', '勝山', '城',
         'かつ', 'やま', 'じょう', '各地', 'の', '松山', '城', 'と', '区別', 'する', 'ため',
         '伊予', '松山', '城', 'と', '呼ば', 'れる', 'こと', 'も', 'ある', 'が', '一般的',
         'に', '松山', '城', 'は', '本城', 'を', '指す', 'こと', 'が', '多い', 'たびたび',
         '放火', '不審火', 'や', '失火', 'に', 'より', '往時', 'の', '建造物', 'を', '焼失',
         'し', 'て', 'いる', '現在', 'は', '城跡', 'の', '主要', '部分', 'が', '公園', 'と',
         'し', 'て', '整備', 'さ', 'れ', '大天', '守', '現存', 'anumber', '天守', 'の',
         'anumber', 'つ', 'を', '含む', 'anumber', '棟', 'の', '現存', '建造物', 'が',
         '国', 'の', '重要', '文化財', 'に', '城郭', '遺構', 'が', '国', 'の', '史跡', 'に',
         '指定', 'さ', 'れ', 'て', 'いる', 'その', 'ほか', '連立', '式', '天守', '群', 'の',
         '小', '天守', '以下', 'anumber', '棟', 'を', 'はじめ', 'と', 'する', 'anumber',
         '棟', '塀', 'を', '含む', 'が', '木造', 'で', '復元', 'さ', 'れ', 'て', 'いる',
         'また', '現存', '十二', '天守', 'と', 'し', 'て', 'は', '最も', '新しい', '城',
         'で', 'ある', '松山市', 'の', '中心', '部', '勝山', '城山', '山頂', 'に', '本丸',
         '西南', '麓', 'に', '二之丸', 'と', '三之丸', 'を', '構える', '平山', '城', 'で',
         'ある', '日本', '三', '大', '平山', '城', 'に', 'も', '数え', 'られる', '山頂',
         'の', '本', '壇', 'に', 'ある', '天守', '大天', '守', 'は', '日本', 'の', 'anumber',
         '箇所', 'に', '現存', 'する', '天守', 'の', '一', 'つ', 'で', 'ある', 'この', '中',
         'で', 'は', '姫路', '城', 'と', '同じく', '連立', '式', 'で', '日本', '三', '大',
         '連立', '式', '平', '山城', 'の', 'anumber', 'つ', 'に', 'も', '数え', 'られる',
         'anumber', '年ごろ', 'まで', 'は', '本丸', '部分', 'に', 'は', 'anumber', '棟',
         'の', '建造物', 'が', '現存', 'し', 'て', 'い', 'た', 'が', 'anumber', '年', 'まで',
         'に', 'anumber', '棟', 'が', '火災', 'に', 'より', '失わ', 'れ', '現存', '建築',
         'は', 'anumber', '棟', 'に', 'まで', '減少', 'し', 'た', '建造物', 'の', '現存',
         '数', 'は', '二', '条', '城', '京都府', 'の', 'anumber', '棟', 'に', '次ぐ', 'もの',
         'で', 'ある', '幕末', 'に', '再建', 'さ', 'れ', 'た', '大天', '守', 'ほか', '日本',
         'で', '現存', '数', 'の', '少ない', '望楼', '型', '二', '重', '櫓', 'で', 'ある',
         '野原', '櫓', '騎馬', '櫓', 'や', '深', 'さ', 'anumber', 'メートル', 'に', 'およぶ',
         '本丸', 'の', '井戸', 'など', 'が', '保存', 'さ', 'れ', 'て', 'いる', '山頂', 'に',
         '本丸', '南西', '麓', 'に', '二之丸', '続い', 'て', '三之丸', '北麓', 'に', 'は',
         '北曲輪', '南東', '麓', 'に', '東', '曲輪', 'が', 'ある', '三之丸', 'は', '比高',
         'anumber', 'メートル', 'ほど', 'の', '土塁', 'で', '囲み', '北', 'と', '東', 'に',
         '石垣', '造', 'の', '虎口', 'を', '開く', '本丸', 'から', '二之丸', 'に', 'かけ',
         'て', '登り', '石垣', 'を', '築い', 'て', '囲み', '丘陵', '斜面', 'から', 'の',
         '大手', '城', '道', 'へ', 'の', '侵入', 'を', '防ぐ', '構造', 'と', 'し', 'て',
         'いる', '山頂', 'の', '本丸', '北部', 'に', 'は', '本', '壇', 'と', 'いう', '天守',
         '曲輪', 'を', '持ち', '大天', '守', 'と', '小天', '守', '・', '南', '隅櫓', '・',
         '北', '隅櫓', 'を', 'anumber', '棟', 'の', '渡櫓', '廊下', 'で', '連結', 'し',
         '連立', '式', '天守', 'を', 'なし', 'て', 'いる', '松山', '城', 'の', '中枢', 'は',
         '二の丸', 'で', '藩主', 'の', '生活', 'の', '場', 'で', 'ある', '御殿', 'や', '庭園',
         '茶室', 'など', 'が', 'あっ', 'た', '三の丸', 'に', 'は', '身分', 'の', '高い',
         '家来', 'の', '屋敷', 'が', '建ち並ん', 'で', 'い', 'た', '本丸', 'は', '主に',
         '倉庫', 'と', 'し', 'て', '使わ', 'れ', 'て', 'い', 'た', 'anumber', '年', '慶長',
         'anumber', '年', '伊予', '国', '正木', '城', '松前', '城主', 'anumber', '万', '石',
         'の', '大名', 'で', 'あっ', 'た', '加藤', '嘉明', 'が', '関ヶ原', 'の', '戦い',
         'で', 'の', '戦功', 'に', 'より', 'anumber', '万', '石', 'に', '加増', 'さ', 'れ',
         '足立', '重信', 'を', '普請', '奉行', 'に', '任じ', '麓', 'に', '二之丸', '二之丸',
         '史跡', '庭園', 'と', '三之丸', '堀之内', 'を', '有する', '平山', '城', 'の', '築城',
         'に', '着手', 'し', 'た']


def test_preprocessing_chinese():
    forbidden_link_prefixes = [
        'category', 'image', 'file']

    wtpp = Wikitext2Words(forbidden_link_prefixes, CJK=True)
    text = """
'''西沟村'''，山西省[[平顺县]][[西沟乡]]的一个行政村。西沟全村面积30500亩，耕地1080亩，辖9个自然庄，660户，1932口人<ref>{{cite news |title=传承新时代纪兰精神——记平顺县西沟乡西沟村党总支书记郭雪岗 |url=https://www.sohu.com/a/339506060_99958012 |accessdate=2020-06-28 |work=搜狐_长治日报 |date=2019-09-08}}</ref>。[[中华人民共和国]]成立后很长时间内，西沟村是全国地图上唯一标出的行政村<ref name=&quot;fbfz&quot;>{{Cite web |url=http://news.ifeng.com/mainland/special/2013lianghui/yanlun/detail_2013_03/02/22662614_0.shtml |title=申纪兰：我觉得共产党还是好的 腐败分子都是混进来的，凤凰网，2013年03月02日 |access-date=2013年3月2日 |archive-url=https://web.archive.org/web/20130302163509/http://news.ifeng.com/mainland/special/2013lianghui/yanlun/detail_2013_03/02/22662614_0.shtml |archive-date=2013年3月2日 |dead-url=no }}</ref>。

==早期==
1943年2月6日，[[李顺达]]联络其他六户农民，在西沟村创办了太行山第一个互助组，发展生产，支援抗战<ref name=平顺县>{{cite web |title=平顺历史 |url=http://www.pingshun.gov.cn/zjps/psgk/lsyg/ |website=平顺县人民政府 |accessdate=2020-06-28}}</ref>。

1951年12月10日，李顺达组织26户农民在西沟办起初级农业生产合作社，并定名为“西沟农林牧生产合作社”。李顺达当选社长、[[申纪兰]]担任副社长<ref>{{Cite book|title=平顺历史与文化 卷3 人物春秋|last=赵小平著|first=|publisher=太原：[[山西教育出版社]]|year=2015.01|isbn=7-5440-7545-9|location=|pages=80-81}}</ref>。1952年3月，李顺达获得农业部“爱国丰产金星奖”(1954年颁发“爱国丰产金星奖章”，全国仅4人获此荣誉，其中一人为临近西沟村的川底村的[[郭玉恩]]）<ref name=平顺县/>。此后，李顺达把社名改为“西沟金星农林牧生产合作社”。

1955年，毛泽东主持编辑《[[中国农村的社会主义高潮]]》一书（1956年出版）时，收入了中共平顺县委书记李琳、新华社驻山西分社记者马明撰写的介绍该社事迹的《勤俭办社，建设山区》一文，毛泽东为此文撰写按语。西沟村名扬全中国。

==组成==
西沟村由池底、刘家底、东峪、辉沟、南赛、东峪沟等9个自然庄组成。

==景点==
西沟村现有西沟展览馆、李顺达故居、李顺达纪念亭、金星峰等红色旅游景点。

;西沟展览馆
始建于1968年，1971年开馆。现展馆系统地展示了全国著名劳模李顺达、申纪兰带领西沟人民艰苦奋斗的历史。

;李顺达故居
2013年7月1日揭牌并对外开放，陈列了许多珍贵照片、文献资料和他用过的劳动工具<ref>{{cite news |title=李顺达故居在山西平顺县对外开放 |url=http://www.chinanews.com/sh/2013/07-02/4993924.shtml |accessdate=2020-06-28 |work=中国新闻网 |agency=山西日报 |date=2013年07月02日}}</ref>。

==发展==
;西沟铁合金厂
西沟村当地有丰富的硅矿资源，1987年11月8日，一座电炉容量1800千伏安的铁合金厂正式点火生产。2003年因环保问题关停。
"""# Noqa
    assert list(wtpp.transform(text)) == \
        ['西沟村', '山西省', '平顺县', '西沟', '乡', '的', '一个', '行政村', '西沟', '全村',
         '面积', 'anumber', '亩', '耕地', 'anumber', '亩', '辖', 'anumber', '个', '自然',
         '庄', 'anumber', '户', 'anumber', '口人', '中华人民共和国', '成立', '后', '很',
         '长时间', '内', '西沟村', '是', '全国', '地图', '上', '唯一', '标出', '的', '行政村',
         'anumber', '年', 'anumber', '月', 'anumber', '日', '李顺达', '联络', '其他',
         '六户', '农民', '在', '西沟村', '创办', '了', '太行山', '第一个', '互助组', '发展', '生产',
         '支援', '抗战', 'anumber', '年', 'anumber', '月', 'anumber', '日', '李顺达',
         '组织', 'anumber', '户', '农民', '在', '西沟', '办起', '初级', '农业', '生产', '合作社',
         '并', '定名', '为', '西沟', '农林牧', '生产', '合作社', '李顺达', '当选', '社长', '申纪兰',
         '担任', '副社长', 'anumber', '年', 'anumber', '月', '李顺达', '获得', '农业部', '爱国',
         '丰产', '金星奖', 'anumber', '年', '颁发', '爱国', '丰产', '金星', '奖章', '全国',
         '仅', 'anumber', '人', '获此', '荣誉', '其中', '一', '人为', '临近', '西沟村', '的',
         '川底', '村', '的', '郭玉恩', '此后', '李顺达', '把', '社名', '改为', '西沟', '金星',
         '农林牧', '生产', '合作社', 'anumber', '年', '毛泽东', '主持', '编辑', '中国', '农村',
         '的', '社会主义', '高潮', '一书', 'anumber', '年', '出版', '时', '收入', '了', '中共',
         '平顺', '县委书记', '李琳', '新华社', '驻', '山西', '分社', '记者', '马明', '撰写',
         '的', '介绍', '该社', '事迹', '的', '勤俭', '办社', '建设', '山区', '一文', '毛泽东',
         '为', '此文', '撰写', '按语', '西沟村', '名扬', '全', '中国', '西沟村', '由', '池底',
         '刘家', '底', '东峪', '辉沟', '南赛', '东峪沟', '等', 'anumber', '个', '自然', '庄',
         '组成', '西沟村', '现有', '西沟', '展览馆', '李顺达', '故居', '李顺达', '纪念亭', '金星',
         '峰', '等', '红色', '旅游景点', '始建', '于', 'anumber', '年', 'anumber', '年',
         '开馆', '现', '展馆', '系统地', '展示', '了', '全国', '著名', '劳模', '李顺达', '申纪兰',
         '带领', '西沟', '人民', '艰苦奋斗', '的', '历史', 'anumber', '年', 'anumber', '月',
         'anumber', '日', '揭牌', '并', '对外开放', '陈列', '了', '许多', '珍贵', '照片',
         '文献资料', '和', '他', '用', '过', '的', '劳动工具', '西沟村', '当地', '有', '丰富',
         '的', '硅矿', '资源', 'anumber', '年', 'anumber', '月', 'anumber', '日', '一座',
         '电炉', '容量', 'anumber', '千伏安', '的', '铁合金厂', '正式', '点火', '生产',
         'anumber', '年', '因', '环保', '问题', '关停']
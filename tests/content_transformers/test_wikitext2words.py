from mwtext.content_transformers import Wikitext2Words


def test_preprocessing_english():
    forbidden_link_prefixes = ['category', 'image', 'file']

    wtpp = Wikitext2Words(forbidden_link_prefixes)
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

    wtpp = Wikitext2Words(forbidden_link_prefixes)
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
    print(list(wtpp.transform(text)))
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

    wtpp = Wikitext2Words(forbidden_link_prefixes)
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
    print(list(wtpp.transform(text)))
    assert list(wtpp.transform(text)) == \
        ['조지', '월턴', '루카스', '주니어', 'george', 'walton', 'lucas', 'jr',
         '년', '월', '일', '는', '미국의', '영화', '제작자이자', '기업가이다', '스타워즈',
         '와', '인디아나', '존스', '프랜차이즈의', '창작자로', '가장', '유명하며',
         '루카스필름과', '인더스트리얼', '라이트', '매직', '그리고', '스카이워커',
         '사운드등의', '설립자이기도', '하다', '년', '루카스필름을', '월트', '디즈니',
         '컴퍼니에', '매각하기', '전까지는', '루카스필름의', '회장', '겸', '최고경영자',
         'ceo', '였다',
         '인디아나', '존스', '의', '세', '번째', '시리즈인', '인디아나', '존스와',
         '최후의', '성전', '을', '제작한', '뒤', '그', '속편을', '제작하지', '않고',
         '영화에서', '손을', '떼겠다고', '발표하기도', '했다', '당시', '인디아나', '존스',
         '시리즈는', '영화와', '게임으로', '발표하였는데', '네', '번째', '시리즈는',
         '게임만', '발표하였다', '그', '뒤', '영화계에', '복귀한', '뒤', '네', '번째',
         '시리즈를', '제작하여', '년', '개봉하였다', '그래서', '인디아나', '존스',
         '시리즈의', '세', '번째', '작품까지는', '영화가', '원작이지만', '네', '번째',
         '작품인', '인디아나', '존스', '크리스탈', '해골의', '왕국', '은', '어느', '것이',
         '원작인지', '불분명하다', '당시', '그', '영화를', '제작하다가', '중단하고',
         '게임을', '제작했으며', '이런', '관점에서는', '영화가', '원작이다', '그러나',
         '년', '개봉된', '영화는', '게임', '내용을', '바탕으로', '처음부터', '다시',
         '제작했으며', '이런', '관점에서', '게임이', '원작이기', '때문이다']


def test_preprocessing_arabic():
    forbidden_link_prefixes = [
        'category', 'image', 'file',
        'تصنيف', 'ملف', 'صورة']

    wtpp = Wikitext2Words(forbidden_link_prefixes)
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
    print(list(wtpp.transform(text)))
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

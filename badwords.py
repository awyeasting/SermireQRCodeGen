replacementPairs = [
('-',''),
('_',''),
('0','o'),
('1','i'),
('2','z'),
('3','e'),
('4','a'),
('5','s'),
('6','g'),
('7','t'),
('8','b'),
('9','q')
]

# From noswearing.com
words = [
'anus'
'arse'
'ass'
'axwound'
'bampot'
'bastard'
'beaner'
'bitch'
'blowjob'
'bollocks'
'bollox'
'boner'
'butt'
'cameltoe'
'carpetmuncher'
'chinc'
'chink'
'choad'
'chode'
'clit'
'cock'
'coochie'
'coochy'
'coon'
'cooter'
'cracker'
'cum'
'cunt'
'cunnie'
'cunnilingus'
'dago'
'damn'
'deggo'
'dick'
'dike'
'dildo'
'doochbag'
'dookie'
'douche'
'dyke'
'fag'
'fellatio'
'feltch'
'flamer'
'fuck'
'fudgepacker'
'gay'
'goddamn'
'gooch'
'gook'
'gringo'
'guido'
'handjob'
'hardon'
'heeb'
'hell'
'ho'
'hoe'
'homo'
'honkey'
'humping'
'jagoff'
'jap'
'jerkoff'
'jigaboo'
'jizz'
'junglebunny'
'junglebunni'
'junglebuni'
'kike'
'kooch'
'kootch'
'kraut'
'kunt'
'kyke'
'lesbian'
'lesbo'
'lezzie'
'mick'
'minge'
'muff'
'munging'
'negro'
'niga'
'nigga'
'nigger'
'nig'
'nutsack'
'paki'
'panooch'
'pecker'
'penis'
'piss'
'polesmoker'
'pollock'
'poon'
'porchmonkey'
'porchmonki'
'prick'
'punanny'
'punta'
'pussies'
'pussy'
'puto'
'queef'
'queer'
'renob'
'rimjob'
'ruski'
'schlong'
'scrote'
'shit'
'shiz'
'skank'
'skeet'
'slut'
'smeg'
'snatch'
'spic'
'spick'
'splooge'
'spook'
'tard'
'testicle'
'tit'
'twat'
'vajj'
'vag'
'vajayjay'
'vjayjay'
'wank'
'wetback'
'whore'
'wop'
]

def check(s):
	s = s.lower()

	for pair in replacementPairs:
		s = s.replace(pair[0], pair[1])

	return any(x in s for x in words)

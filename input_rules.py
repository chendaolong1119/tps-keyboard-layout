"""Section 5.1: what each rule of the input logic saves and how many syllables it touches.
Usage: python input_rules.py"""
import model

ENTERING = 'ㆴㆵㆻㆷ'            # typed with ㄅㄉㄍㄏ by position
ALLOPHONE = 'ㄐㄑㄒㆢ'           # shown for ㄗㄘㄙㆡ before ㄧ
NASAL = 'ㆩㆪㆫㆥㆧㆮㆯ'          # precomposed nasal vowels, replaced by vowel + nasal key
TONES = 'ˋ˪ˊ˫˙ˇˆ'

if __name__ == '__main__':
    n = ent = allo = nas = 0
    for seq in model.unit_stream():
        syl = []
        for u in seq + ['␣']:
            if u == '␣' or u in TONES:
                if syl:
                    n += 1
                    ent += any(x in ENTERING for x in syl)
                    allo += any(a in 'ㄗㄘㄙㆡ' and b == 'ㄧ' for a, b in zip(syl, syl[1:]))
                    nas += 'N' in syl
                syl = []
            else:
                syl.append(u)
    saved = {'entering finals by position': len(ENTERING), 'allophone merging': len(ALLOPHONE),
             'nasal combination': len(NASAL) - 1}
    share = {'entering finals by position': ent, 'allophone merging': allo, 'nasal combination': nas}
    print(f'{n} syllables')
    for k in saved:
        print(f'{k:30s} keys saved {saved[k]:2d}   syllables {100 * share[k] / n:4.1f}%')
    print(f'main layer without the rules: {39 + sum(saved.values())} units for 41 keys')

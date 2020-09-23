import re
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
from collections import namedtuple
import io


all_hgs = []

hg_index = {}
# creates a dictionary of tuples that show what Unicode replaces what ASCII character
# the ASCII to Unicode list copied from github, see read me for credits
def fill_homoglyphs():

    Hgs = namedtuple('Hgs', ('ascii', 'fwd', 'rev'))

    hg_index.update({Hgs(*t).ascii: Hgs(*t) for t in (
        (' ', u'\u00A0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u202F\u205F', u'\u3000'),
        ('2', u'\u14BF', u'\u00B2\u2082\u2461\uFF12'),
        ('3', u'\u01B7\u2128', u'\u00B3\u2083\u2462\uFF13\u1883\u2CC4\u2CCC\u2CCD'),
        ('4', u'\u13CE', u'\u2074\u2084\u2463\uFF14'),
        ('6', u'\u13EE', u'\u2076\u2086\u2465\uFF16'),
        ('9', u'\u13ED', u'\u2079\u2089\u2468\uFF19'),
        ('A', u'\u0391\u0410\u13AA', u'\u1D2C\u24B6\uFF21'),
        ('B', u'\u0392\u0412\u13F4\u15F7\u2C82', u'\u1D2E\u212C\u24B7\uFF22'),
        ('C', u'\u03F9\u0421\u13DF\u216D\u2CA4', u'\u2102\u212D\u24B8\uFF23'),
        ('D', u'\u13A0\u15EA\u216E', u'\u1D30\u2145\u24B9\uFF24'),
        ('E', u'\u0395\u0415\u13AC', u'\u1D31\u2130\u24BA\uFF25'),
        ('F', u'\u15B4', u'\u2131\u24BB\uFF26'),
        ('G', u'\u050C\u13C0', u'\u1D33\u24BC\uFF27'),
        ('H', u'\u0397\u041D\u12D8\u13BB\u157C\u2C8E', u'\u1D34\u210B\u210C\u210D\u24BD\uFF28'),
        ('I', u'\u0399\u0406\u2160', u'\u1D35\u2110\u2111\u24BE\uFF29'),
        ('J', u'\u0408\u13AB\u148D', u'\u1D36\u24BF\uFF2A'),
        ('K', u'\u039A\u13E6\u16D5\u212A\u2C94', u'\u1D37\u24C0\uFF2B'),
        ('L', u'\u13DE\u14AA\u216C', u'\u1D38\u2112\u24C1\uFF2C\u2CD0\u31C4'),
        ('M', u'\u039C\u03FA\u041C\u13B7\u216F', u'\u1D39\u2133\u24C2\uFF2D'),
        ('N', u'\u039D\u2C9A', u'\u1D3A\u2115\u24C3\uFF2E'),
        ('O', u'\u039F\u041E\u2C9E', u'\u1D3C\u24C4\uFF2F\u1C5B'),
        ('P', u'\u03A1\u0420\u13E2\u2CA2', u'\u1D3E\u2119\u24C5\uFF30'),
        ('Q', u'\u051A\u2D55', u'\u211A\u24C6\uFF31\u10B3'),
        ('R', u'\u13A1\u13D2\u1587', u'\u1D3F\u211B\u211C\u211D\u24C7\uFF32'),
        ('S', u'\u0405\u13DA', u'\u24C8\uFF33\u10BD'),
        ('T', u'\u03A4\u0422\u13A2', u'\u1D40\u24C9\uFF34'),
        ('V', u'\u13D9\u2164', u'\u24CB\uFF36'),
        ('W', u'\u13B3\u13D4', u'\u1D42\u24CC\uFF37'),
        ('X', u'\u03A7\u0425\u2169\u2CAC', u'\u24CD\uFF38'),
        ('Y', u'\u03A5\u2CA8', u'\u03D2\u24CE\uFF39'),
        ('Z', u'\u0396\u13C3', u'\u2124\u24CF\uFF3A'),
        ('a', u'\u0430', u'\u00AA\u1D43\u1D45\u2090\u24D0\uFF41'),
        ('c', u'\u03F2\u0441\u217D', u'\u1D9C\u24D2\uFF43'),
        ('d', u'\u0501\u217E', u'\u1D48\u2146\u24D3\uFF44'),
        ('e', u'\u0435\u1971', u'\u1D49\u2091\u212F\u2147\u24D4\uFF45\u19C9'),
        ('g', u'\u0261', u'\u1D4D\u1DA2\u210A\u24D6\uFF47'),
        ('h', u'\u04BB', u'\u02B0\u210E\u24D7\uFF48'),
        ('i', u'\u0456\u2170', u'\u1D62\u2071\u2139\u2148\u24D8\uFF49'),
        ('j', u'\u03F3\u0458', u'\u02B2\u2149\u24D9\u2C7C\uFF4A'),
        ('l', u'\u217C', u'\u02E1\u2113\u24DB\uFF4C'),
        ('m', u'\u217F', u'\u1D50\u24DC\uFF4D'),
        ('n', u'\u1952', u'\u207F\u24DD\uFF4E'),
        ('o', u'\u03BF\u043E\u0D20\u2C9F', u'\u00BA\u1D52\u2092\u2134\u24DE\uFF4F\u0CE6\u0D66\u199E\u19D0'),
        ('p', u'\u0440\u2CA3', u'\u1D56\u24DF\uFF50'),
        ('s', u'\u0455', u'\u02E2\u24E2\uFF53'),
        ('u', u'\u1959\u222A', u'\u1D58\u1D64\u24E4\uFF55'),
        ('v', u'\u1D20\u2174\u2228\u22C1', u'\u1D5B\u1D65\u24E5\u2C7D\uFF56'),
        ('w', u'\u1D21', u'\u02B7\u24E6\uFF57'),
        ('x', u'\u0445\u2179\u2CAD', u'\u02E3\u2093\u24E7\uFF58'),
        ('y', u'\u0443\u1EFF', u'\u02B8\u24E8\uFF59'),
        ('z', u'\u1D22', u'\u1DBB\u24E9\uFF5A\u1901')
    )})
    hg_index.update({c: hgs for hgs in all_hgs for c in hgs.ascii})
# calls the function
fill_homoglyphs()
# checks if the ascii character has a matching unicode in hg_index.
# if it does it returns the Unicode if it doesnt it returns the ASCII
def uni(letter):
    if letter in hg_index:
        uni = hg_index[letter].fwd[0]
        return(uni)
    else:
        return(letter)
# replaces a specific character
def replace(filepath, letter):
    UNICODE = uni(letter)
    newfilepath = "fixed_"+filepath
    with io.open(newfilepath, "w+", encoding="utf-8") as new:
        with io.open(filepath, encoding="utf-8") as old:
            # replaces the char using regex
            for line in old:
                if letter in line:
                    new.write(re.sub(letter, UNICODE, line))
                else:
                    new.write(re.sub(UNICODE, letter, line))
# replaces everything that can be replaced
def replaceall(filepath):
    newfilepath = "fixed_"+filepath
    fixed = ""
    with io.open(newfilepath, "w+", encoding="utf-8") as new:
        with io.open(filepath, encoding="utf-8") as old:
            for line in old:
                fixed = line
                for entry in hg_index:
                    fixed = overwrite(entry, uni(entry), fixed)
                new.write(fixed)

def overwrite(letter, unicode, line):
    if letter in line:
        return re.sub(str(letter), unicode, line)
    else:
        return re.sub(unicode, str(letter), line)


filename = str(input("input the name of the file you want to fix "))
english = str(input("input the letter or 'all' to replace as many things as possible "))
if english == "all":
    replaceall(filename)
elif len(english) == 1:
    replace(filename, english)
else:
    print("invalid input")
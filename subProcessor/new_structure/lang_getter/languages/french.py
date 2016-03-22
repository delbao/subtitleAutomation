#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#    Copyright (C) 2007  Universidad de las Ciencias Informáticas
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# Autores:
#    Manuel Vázquez Acosta
#    Roberto Oscar Labrada
#    Miguel Yuniesqui Godales

# $Id: french.py 527 2008-02-26 22:31:09Z mygodales@UCI.CU $

"""
Frecuencia de los textos en francés
"""

ISO_639_1_LANGUAGE_CODE = "fr"
iso = ISO_639_1_LANGUAGE_CODE  # Backwards compatibility

FOOTPRINT_VECTOR = {u'a': 0.074482502189366778,
                    u'aa': 6.4129284637829867e-06,
                    u'ab': 0.0017571423990765383,
                    u'ac': 0.0024369128162375349,
                    u'ad': 0.0015070381889890018,
                    u'ae': 1.2825856927565973e-05,
                    u'af': 0.00035912399397184725,
                    u'ag': 0.0025523455285856285,
                    u'ah': 0.00083368070029178826,
                    u'ai': 0.014390611472729022,
                    u'aj': 0.00010901978388431077,
                    u'ak': 4.4890499246480906e-05,
                    u'al': 0.0034822201558341618,
                    u'am': 0.0025972360278321096,
                    u'an': 0.017058389713662744,
                    u'ao': 6.4129284637829867e-06,
                    u'ap': 0.0017507294706127553,
                    u'aq': 0.00021803956776862154,
                    u'ar': 0.012934876711450284,
                    u'as': 0.0050982781287074739,
                    u'at': 0.0035271106550806425,
                    u'au': 0.0074903004456985285,
                    u'av': 0.0032834193734568892,
                    u'aw': 8.3368070029178818e-05,
                    u'ax': 7.0542213101612857e-05,
                    u'ay': 0.00069900920255234556,
                    u'az': 0.00073107384487126046,
                    u'a\xe7': 7.0542213101612857e-05,
                    u'a\xee': 0.00064129284637829862,
                    u'a\xef': 8.3368070029178818e-05,
                    u'a\xf4': 6.4129284637829867e-06,
                    u'b': 0.011511910644481083,
                    u'ba': 0.0028088626671369482,
                    u'bb': 2.5651713855131947e-05,
                    u'be': 0.0019687690383813771,
                    u'bi': 0.0031102703049347485,
                    u'bj': 4.4890499246480906e-05,
                    u'bl': 0.0025972360278321096,
                    u'bn': 3.2064642318914931e-05,
                    u'bo': 0.0015455157597716997,
                    u'br': 0.0015326899028441337,
                    u'bs': 0.00020521371084105558,
                    u'bt': 0.00010260685542052779,
                    u'bu': 0.0005450989194215538,
                    u'by': 0.00018597492544970661,
                    u'b\xe2': 6.4129284637829867e-06,
                    u'b\xe9': 0.00016032321159457466,
                    u'b\xea': 0.00010901978388431077,
                    u'c': 0.033522996912870542,
                    u'ca': 0.0017635553275403212,
                    u'cc': 0.00063487991791451564,
                    u'ce': 0.01011318818738577,
                    u'ch': 0.0063487991791451566,
                    u'ci': 0.0016930131144387084,
                    u'ck': 3.8477570782697919e-05,
                    u'cl': 0.00062846698945073266,
                    u'co': 0.011960111584955271,
                    u'cq': 2.5651713855131947e-05,
                    u'cr': 0.0018148587552505851,
                    u'cs': 3.2064642318914931e-05,
                    u'ct': 0.0021739827492224324,
                    u'cu': 0.00082726777182800528,
                    u'c\xe6': 1.2825856927565973e-05,
                    u'c\xe8': 0.00086574534261070317,
                    u'c\xe9': 0.00050020842017507294,
                    u'c\xee': 6.4129284637829867e-06,
                    u'c\xf4': 0.00017314906852214064,
                    u'd': 0.030156998390387334,
                    u'da': 0.00382210536441466,
                    u'dd': 5.7716356174046881e-05,
                    u'de': 0.014275178760380928,
                    u'dh': 6.4129284637829867e-06,
                    u'di': 0.0039824285760092348,
                    u'dl': 6.4129284637829867e-06,
                    u'dm': 1.2825856927565973e-05,
                    u'do': 0.0033283098727033699,
                    u'dp': 1.2825856927565973e-05,
                    u'dr': 0.001981594895308943,
                    u'ds': 0.00062846698945073266,
                    u'du': 0.0026485394555423735,
                    u'dv': 6.4129284637829867e-06,
                    u'dy': 6.4129284637829867e-06,
                    u'd\xe0': 6.4129284637829867e-06,
                    u'd\xe8': 0.00012184564081187674,
                    u'd\xe9': 0.0018405104691057172,
                    u'd\xee': 1.2825856927565973e-05,
                    u'd\xf4': 6.4129284637829867e-06,
                    u'd\xfb': 2.5651713855131947e-05,
                    u'e': 0.14657260135911976,
                    u'ea': 0.0014621476897425209,
                    u'eb': 0.00017956199698592363,
                    u'ec': 0.0029371212364126078,
                    u'ed': 0.0013018244781479462,
                    u'ee': 0.00046814377785615803,
                    u'ef': 0.00070542213101612854,
                    u'eg': 0.00039760156475454519,
                    u'eh': 0.00026934299547888541,
                    u'ei': 0.0017635553275403212,
                    u'ej': 1.9238785391348959e-05,
                    u'el': 0.0064321672491743356,
                    u'em': 0.0047583929201269757,
                    u'en': 0.020713758938019047,
                    u'eo': 5.1303427710263894e-05,
                    u'ep': 0.00084650655721935422,
                    u'eq': 0.00014749735466700869,
                    u'er': 0.013640298842466413,
                    u'es': 0.022669702119472859,
                    u'et': 0.010177317472023599,
                    u'eu': 0.0096322185526020454,
                    u'ev': 0.0013338891204668611,
                    u'ew': 5.7716356174046881e-05,
                    u'ex': 0.00098117805495879693,
                    u'ey': 7.0542213101612857e-05,
                    u'ez': 0.0033860262288774169,
                    u'e\xe7': 0.00015391028313079167,
                    u'e\xfb': 0.00014108442620322571,
                    u'f': 0.014325063479405275,
                    u'fa': 0.0035335235835444257,
                    u'fe': 0.0020777888222656875,
                    u'ff': 0.0012376951935101164,
                    u'fi': 0.005329143553403662,
                    u'fl': 0.00049379549171128996,
                    u'fo': 0.002398435245454837,
                    u'fr': 0.0011158495526982397,
                    u'fs': 3.2064642318914931e-05,
                    u'ft': 6.4129284637829867e-06,
                    u'fu': 0.00076313848719017537,
                    u'fy': 1.2825856927565973e-05,
                    u'f\xe2': 9.6193926956744793e-05,
                    u'f\xe8': 1.2825856927565973e-05,
                    u'f\xe9': 0.00014108442620322571,
                    u'f\xea': 8.9780998492961813e-05,
                    u'f\xee': 1.2825856927565973e-05,
                    u'f\xfb': 3.2064642318914931e-05,
                    u'g': 0.013013889636344957,
                    u'ga': 0.0047583929201269757,
                    u'gb': 6.4129284637829867e-06,
                    u'gd': 1.9238785391348959e-05,
                    u'ge': 0.0036361304389649534,
                    u'gg': 6.4129284637829867e-06,
                    u'gh': 0.00013467149773944271,
                    u'gi': 0.00044249206400102605,
                    u'gl': 0.00055151184788533689,
                    u'gm': 1.9238785391348959e-05,
                    u'gn': 0.0017892070413954532,
                    u'go': 0.00033988520858049831,
                    u'gr': 0.0017507294706127553,
                    u'gs': 5.7716356174046881e-05,
                    u'gt': 0.00016673614005835764,
                    u'gu': 0.0013916054766409081,
                    u'gy': 6.4129284637829867e-06,
                    u'g\xe2': 1.9238785391348959e-05,
                    u'g\xe8': 0.00011543271234809376,
                    u'g\xe9': 0.00042966620707346009,
                    u'g\xea': 2.5651713855131947e-05,
                    u'g\xee': 6.4129284637829867e-06,
                    u'h': 0.011727177991849195,
                    u'ha': 0.0026549523840061562,
                    u'hb': 6.4129284637829867e-06,
                    u'he': 0.0045788309231410522,
                    u'hi': 0.00091704877032096712,
                    u'ho': 0.0026100618847596756,
                    u'hr': 0.00010901978388431077,
                    u'hs': 1.9238785391348959e-05,
                    u'ht': 0.00019238785391348959,
                    u'hu': 0.00035271106550806427,
                    u'hy': 9.6193926956744793e-05,
                    u'h\xe2': 0.00021803956776862154,
                    u'h\xe8': 0.00010260685542052779,
                    u'h\xe9': 0.0016930131144387084,
                    u'h\xf4': 6.4129284637829867e-06,
                    u'h\xfb': 6.4129284637829867e-06,
                    u'i': 0.068459908902772551,
                    u'ia': 0.0011863917657998525,
                    u'ib': 0.00084009362875557124,
                    u'ic': 0.0018982268252797641,
                    u'id': 0.001436495975887389,
                    u'ie': 0.0095360246256453018,
                    u'if': 0.00067977041716099662,
                    u'ig': 0.0055407701927085006,
                    u'ii': 0.00046814377785615803,
                    u'ij': 6.4129284637829867e-06,
                    u'il': 0.0097604771218777059,
                    u'im': 0.0016352967582646616,
                    u'in': 0.010645461249879758,
                    u'io': 0.0027383204540353352,
                    u'ip': 0.00043607913553724307,
                    u'iq': 0.0006861833456247796,
                    u'ir': 0.0049764324878955974,
                    u'is': 0.011883156443389874,
                    u'it': 0.0099336261903998462,
                    u'iu': 3.2064642318914931e-05,
                    u'iv': 0.0012697598358290313,
                    u'ix': 0.00031423349472536633,
                    u'iz': 4.4890499246480906e-05,
                    u'i\xe8': 0.0010132426972777118,
                    u'i\xe9': 0.00046814377785615803,
                    u'j': 0.0077985489023811505,
                    u'ja': 0.00056433770481290285,
                    u'je': 0.0055920736204187645,
                    u'jo': 0.0016866001859749255,
                    u'ju': 0.00085933241414692019,
                    u'j\xe0': 0.00010260685542052779,
                    u'k': 0.00067515668038180602,
                    u'ke': 8.9780998492961813e-05,
                    u'ki': 1.2825856927565973e-05,
                    u'kn': 6.4129284637829867e-06,
                    u'ks': 0.00028858178087023441,
                    u'l': 0.052305072970738317,
                    u'la': 0.010940455959213774,
                    u'lb': 1.2825856927565973e-05,
                    u'lc': 7.6955141565395837e-05,
                    u'ld': 0.00011543271234809376,
                    u'le': 0.02377272581524353,
                    u'lg': 0.00011543271234809376,
                    u'lh': 0.00017314906852214064,
                    u'li': 0.0044185077115464775,
                    u'lk': 6.4129284637829867e-06,
                    u'll': 0.00616282425369545,
                    u'lm': 7.0542213101612857e-05,
                    u'lo': 0.0026228877416872415,
                    u'lp': 2.5651713855131947e-05,
                    u'lq': 0.00041684035014589413,
                    u'lr': 6.4129284637829867e-06,
                    u'ls': 0.00076313848719017537,
                    u'lt': 0.00025010421008753647,
                    u'lu': 0.0037130855805303491,
                    u'lv': 6.4129284637829867e-06,
                    u'ly': 0.00023727835315997051,
                    u'l\xe0': 0.00091063584185718403,
                    u'l\xe2': 0.00017956199698592363,
                    u'l\xe8': 0.00044890499246480904,
                    u'l\xe9': 0.00077596434411774133,
                    u'l\xf4': 6.4129284637829867e-06,
                    u'l\xfb': 6.4129284637829867e-06,
                    u'm': 0.033038645381292288,
                    u'ma': 0.0088241895661653903,
                    u'mb': 0.00093628755571231606,
                    u'me': 0.010183730400487383,
                    u'mi': 0.0023727835315997051,
                    u'ml': 4.4890499246480906e-05,
                    u'mm': 0.002885817808702344,
                    u'mn': 7.6955141565395837e-05,
                    u'mo': 0.0064321672491743356,
                    u'mp': 0.0018405104691057172,
                    u'ms': 0.00016032321159457466,
                    u'mt': 0.00504697470099721,
                    u'mu': 0.00042325327860967711,
                    u'my': 2.5651713855131947e-05,
                    u'm\xe8': 0.00041042742168211115,
                    u'm\xe9': 0.00093628755571231606,
                    u'm\xea': 0.0005130342771026389,
                    u'm\xee': 6.4129284637829867e-06,
                    u'n': 0.07218794796401122,
                    u'na': 0.0018982268252797641,
                    u'nb': 0.00060281527559560074,
                    u'nc': 0.0040465578606470641,
                    u'nd': 0.0055728348350274149,
                    u'ne': 0.014249527046525797,
                    u'nf': 0.0010901978388431076,
                    u'ng': 0.0018918138968159811,
                    u'nh': 8.9780998492961813e-05,
                    u'ni': 0.0026036489562958924,
                    u'nj': 8.9780998492961813e-05,
                    u'nk': 3.8477570782697919e-05,
                    u'nl': 0.00015391028313079167,
                    u'nn': 0.0054509891942155385,
                    u'no': 0.0038798217205887066,
                    u'np': 6.4129284637829867e-06,
                    u'nq': 0.00038477570782697917,
                    u'nr': 5.1303427710263894e-05,
                    u'ns': 0.0090422291339340103,
                    u'nt': 0.015686023022413186,
                    u'nu': 0.00063487991791451564,
                    u'nv': 0.00037836277936319619,
                    u'ny': 0.00033988520858049831,
                    u'nz': 3.2064642318914931e-05,
                    u'n\xe2': 6.4129284637829867e-06,
                    u'n\xe7': 0.00012825856927565972,
                    u'n\xe8': 1.2825856927565973e-05,
                    u'n\xe9': 0.00096193926956744799,
                    u'n\xea': 0.00024369128162375349,
                    u'n\xee': 6.4129284637829867e-06,
                    u'n\xf4': 1.9238785391348959e-05,
                    u'o': 0.063870800452061435,
                    u'oa': 1.9238785391348959e-05,
                    u'ob': 0.00069259627408856258,
                    u'oc': 0.0011158495526982397,
                    u'od': 0.00046814377785615803,
                    u'oe': 3.8477570782697919e-05,
                    u'of': 0.0010645461249879757,
                    u'og': 0.00016673614005835764,
                    u'oh': 0.00021162663930483856,
                    u'oi': 0.0080482252220476485,
                    u'oj': 0.00065411870330586458,
                    u'ok': 0.00011543271234809376,
                    u'ol': 0.0025331067431942798,
                    u'om': 0.0091255972039631893,
                    u'on': 0.020463654727931511,
                    u'oo': 0.00015391028313079167,
                    u'op': 0.00097476512649501395,
                    u'oq': 0.00024369128162375349,
                    u'or': 0.0058742424728252156,
                    u'os': 0.0018661621829608491,
                    u'ot': 0.0020457241799467728,
                    u'ou': 0.020470067656395294,
                    u'ov': 0.00022445249623240452,
                    u'ow': 0.00014749735466700869,
                    u'ox': 6.4129284637829867e-06,
                    u'oy': 0.00069259627408856258,
                    u'o\xeb': 1.9238785391348959e-05,
                    u'o\xee': 1.9238785391348959e-05,
                    u'o\xf9': 0.00053227306249398784,
                    u'o\xfb': 0.00016673614005835764,
                    u'p': 0.02530369819517899,
                    u'pa': 0.007727578798858499,
                    u'pd': 6.4129284637829867e-06,
                    u'pe': 0.0043351396415172985,
                    u'pg': 7.0542213101612857e-05,
                    u'ph': 0.00032064642318914931,
                    u'pi': 0.0014172571904960401,
                    u'pl': 0.003418090871196332,
                    u'pm': 1.9238785391348959e-05,
                    u'po': 0.0056113124058101132,
                    u'pp': 0.0011671529804085036,
                    u'pr': 0.0053996857665052746,
                    u'ps': 0.00035912399397184725,
                    u'pt': 0.00045531792092859202,
                    u'pu': 0.0012120434796549845,
                    u'pv': 6.4129284637829867e-06,
                    u'py': 0.00019238785391348959,
                    u'p\xe2': 1.2825856927565973e-05,
                    u'p\xe7': 7.6955141565395837e-05,
                    u'p\xe8': 0.00015391028313079167,
                    u'p\xe9': 0.00044249206400102605,
                    u'p\xea': 7.6955141565395837e-05,
                    u'p\xee': 6.4129284637829867e-06,
                    u'p\xfb': 1.2825856927565973e-05,
                    u'q': 0.011458093807639055,
                    u'qu': 0.014987013819860839,
                    u'r': 0.065475520677896443,
                    u'ra': 0.0087792990669189087,
                    u'rb': 0.00023727835315997051,
                    u'rc': 0.0020970276076570367,
                    u'rd': 0.0018020328983230191,
                    u're': 0.017904896270882098,
                    u'rf': 9.6193926956744793e-05,
                    u'rg': 0.0011415012665533717,
                    u'rh': 1.9238785391348959e-05,
                    u'ri': 0.0070157437393785875,
                    u'rk': 0.00058998941866803478,
                    u'rl': 0.00055151184788533689,
                    u'rm': 0.0012954115496841632,
                    u'rn': 0.00083368070029178826,
                    u'ro': 0.0091512489178183221,
                    u'rp': 0.00020521371084105558,
                    u'rq': 0.00030782056626158335,
                    u'rr': 0.0018340975406419342,
                    u'rs': 0.0031808125180363615,
                    u'rt': 0.0045531792092859203,
                    u'ru': 0.0016096450444095297,
                    u'rv': 0.00028858178087023441,
                    u'rw': 6.4129284637829867e-06,
                    u'ry': 0.00014749735466700869,
                    u'r\xe2': 4.4890499246480906e-05,
                    u'r\xe7': 0.00012184564081187674,
                    u'r\xe8': 0.00060281527559560074,
                    u'r\xe9': 0.0021996344630775644,
                    u'r\xea': 0.00051944720556642188,
                    u'r\xee': 6.4129284637829867e-06,
                    u'r\xf4': 0.00015391028313079167,
                    u'r\xfb': 3.8477570782697919e-05,
                    u's': 0.075221260586016428,
                    u'sa': 0.0048481739186199378,
                    u'sb': 6.4129284637829867e-06,
                    u'sc': 0.0011415012665533717,
                    u'sd': 1.2825856927565973e-05,
                    u'se': 0.012575752717478437,
                    u'sf': 3.8477570782697919e-05,
                    u'sg': 1.9238785391348959e-05,
                    u'sh': 7.6955141565395837e-05,
                    u'si': 0.0052201237695193511,
                    u'sk': 6.4129284637829867e-06,
                    u'sl': 2.5651713855131947e-05,
                    u'sm': 5.1303427710263894e-05,
                    u'so': 0.0058678295443614324,
                    u'sp': 0.00094270048417609905,
                    u'sq': 0.0005450989194215538,
                    u'ss': 0.0070349825247699362,
                    u'st': 0.0074325840895244815,
                    u'su': 0.0058806554012889988,
                    u'sw': 6.4129284637829867e-06,
                    u'sy': 5.7716356174046881e-05,
                    u's\xe8': 3.8477570782697919e-05,
                    u's\xe9': 0.0010260685542052778,
                    u's\xfb': 5.7716356174046881e-05,
                    u't': 0.068366952548227222,
                    u'ta': 0.0036425433674287361,
                    u'tc': 6.4129284637829867e-06,
                    u'td': 6.4129284637829867e-06,
                    u'te': 0.018001090197838843,
                    u'tf': 6.4129284637829867e-06,
                    u'th': 0.0033283098727033699,
                    u'ti': 0.0055728348350274149,
                    u'tl': 3.2064642318914931e-05,
                    u'tm': 0.00037194985089941321,
                    u'tn': 6.4129284637829867e-06,
                    u'to': 0.0051367556994901722,
                    u'tp': 8.3368070029178818e-05,
                    u'tr': 0.0076121460865104049,
                    u'ts': 0.0013595408343219932,
                    u'tt': 0.0024753903870202328,
                    u'tu': 0.0021034405361208194,
                    u'tw': 6.4129284637829867e-06,
                    u'tx': 6.4129284637829867e-06,
                    u'ty': 0.00020521371084105558,
                    u't\xe2': 5.7716356174046881e-05,
                    u't\xe8': 0.00016032321159457466,
                    u't\xe9': 0.0024112611023824029,
                    u't\xea': 0.00018597492544970661,
                    u't\xee': 6.4129284637829867e-06,
                    u't\xf4': 0.00021803956776862154,
                    u'u': 0.063171181573115062,
                    u'ua': 0.00094911341263988203,
                    u'ub': 0.0016609484721197935,
                    u'uc': 0.00091063584185718403,
                    u'ud': 0.00076955141565395835,
                    u'ue': 0.0085099560714400231,
                    u'uf': 0.00033347228011671527,
                    u'ug': 0.00058357649020425179,
                    u'uh': 1.2825856927565973e-05,
                    u'ui': 0.0073812806618142176,
                    u'uj': 0.00056433770481290285,
                    u'ul': 0.0017507294706127553,
                    u'um': 0.00044890499246480904,
                    u'un': 0.0073299772341039538,
                    u'uo': 0.00055151184788533689,
                    u'up': 0.0011350883380895887,
                    u'uq': 0.00011543271234809376,
                    u'ur': 0.013165742136146472,
                    u'us': 0.010305576041299259,
                    u'ut': 0.0066886843877256548,
                    u'uv': 0.0016352967582646616,
                    u'ux': 0.002956360021803957,
                    u'uy': 7.0542213101612857e-05,
                    u'uz': 0.0029948375925866549,
                    u'u\xe8': 7.0542213101612857e-05,
                    u'u\xe9': 0.00027575592394266845,
                    u'u\xea': 1.9238785391348959e-05,
                    u'u\xef': 1.9238785391348959e-05,
                    u'v': 0.015460109492800776,
                    u'va': 0.0028281014525282969,
                    u've': 0.0054060986949690578,
                    u'vi': 0.0026228877416872415,
                    u'vo': 0.0070991118094077665,
                    u'vr': 0.00080802898643665634,
                    u'vu': 0.00025010421008753647,
                    u'v\xe8': 8.3368070029178818e-05,
                    u'v\xe9': 0.00063487991791451564,
                    u'v\xea': 0.00010260685542052779,
                    u'v\xee': 0.00021803956776862154,
                    u'v\xf4': 3.8477570782697919e-05,
                    u'w': 0.001350313360763612,
                    u'wa': 0.00010260685542052779,
                    u'wb': 1.2825856927565973e-05,
                    u'we': 0.00012184564081187674,
                    u'wh': 0.00014108442620322571,
                    u'wi': 0.00047455670631994101,
                    u'wn': 5.1303427710263894e-05,
                    u'wo': 0.0005130342771026389,
                    u'wr': 3.8477570782697919e-05,
                    u'ws': 5.7716356174046881e-05,
                    u'ww': 0.00010260685542052779,
                    u'x': 0.0035910507492771422,
                    u'xa': 0.00015391028313079167,
                    u'xc': 0.00027575592394266845,
                    u'xe': 0.00017314906852214064,
                    u'xi': 0.00030782056626158335,
                    u'xo': 6.4129284637829867e-06,
                    u'xp': 0.00022445249623240452,
                    u'xq': 1.2825856927565973e-05,
                    u'xt': 7.6955141565395837e-05,
                    u'xv': 0.00010260685542052779,
                    u'xx': 5.1303427710263894e-05,
                    u'x\xe9': 1.2825856927565973e-05,
                    u'y': 0.0038748122526260169,
                    u'ya': 0.00026934299547888541,
                    u'ye': 0.00083368070029178826,
                    u'yi': 8.3368070029178818e-05,
                    u'yl': 3.2064642318914931e-05,
                    u'ym': 9.6193926956744793e-05,
                    u'yn': 1.9238785391348959e-05,
                    u'yo': 0.00060281527559560074,
                    u'yp': 7.0542213101612857e-05,
                    u'yr': 0.00011543271234809376,
                    u'ys': 0.00023086542469618753,
                    u'yt': 1.2825856927565973e-05,
                    u'yw': 1.2825856927565973e-05,
                    u'y\xe9': 8.3368070029178818e-05,
                    u'z': 0.0056311981095612945,
                    u'za': 0.0027383204540353352,
                    u'ze': 8.9780998492961813e-05,
                    u'zi': 0.00071183505947991152,
                    u'zo': 0.00043607913553724307,
                    u'z\xe8': 6.4129284637829867e-06,
                    u'z\xe9': 1.2825856927565973e-05,
                    u'\xe0': 0.0049462565497536658,
                    u'\xe2': 0.0007925752334916853,
                    u'\xe2c': 0.00023086542469618753,
                    u'\xe2g': 3.2064642318914931e-05,
                    u'\xe2l': 6.4129284637829867e-06,
                    u'\xe2m': 0.00011543271234809376,
                    u'\xe2t': 0.0006477057748420816,
                    u'\xe6': 9.7848794258232757e-06,
                    u'\xe6t': 1.2825856927565973e-05,
                    u'\xe7': 0.00050881373014281036,
                    u'\xe7a': 0.00018597492544970661,
                    u'\xe7i': 6.4129284637829867e-06,
                    u'\xe7o': 0.00034629813704428129,
                    u'\xe7u': 6.4129284637829862e-05,
                    u'\xe7\xe0': 5.7716356174046881e-05,
                    u'\xe8': 0.0032339026502345926,
                    u'\xe8b': 6.4129284637829867e-06,
                    u'\xe8c': 0.00039118863629076215,
                    u'\xe8d': 2.5651713855131947e-05,
                    u'\xe8g': 9.6193926956744793e-05,
                    u'\xe8l': 5.7716356174046881e-05,
                    u'\xe8m': 0.00012184564081187674,
                    u'\xe8n': 0.00085933241414692019,
                    u'\xe8q': 1.2825856927565973e-05,
                    u'\xe8r': 0.0015839933305543976,
                    u'\xe8s': 0.00073748677333504344,
                    u'\xe8t': 7.0542213101612857e-05,
                    u'\xe8v': 0.00023727835315997051,
                    u'\xe9': 0.013899421224381963,
                    u'\xe9a': 5.1303427710263894e-05,
                    u'\xe9b': 8.9780998492961813e-05,
                    u'\xe9c': 0.0012954115496841632,
                    u'\xe9d': 0.00066053163176964756,
                    u'\xe9e': 0.0018084458267868021,
                    u'\xe9f': 0.00044890499246480904,
                    u'\xe9g': 0.00057075063327668583,
                    u'\xe9h': 6.4129284637829867e-06,
                    u'\xe9i': 4.4890499246480906e-05,
                    u'\xe9j': 0.00010901978388431077,
                    u'\xe9l': 0.00050020842017507294,
                    u'\xe9m': 0.00032064642318914931,
                    u'\xe9n': 0.00037194985089941321,
                    u'\xe9o': 1.2825856927565973e-05,
                    u'\xe9p': 0.0013916054766409081,
                    u'\xe9q': 8.9780998492961813e-05,
                    u'\xe9r': 0.0020970276076570367,
                    u'\xe9s': 0.0011863917657998525,
                    u'\xe9t': 0.0016801872575111425,
                    u'\xe9u': 1.9238785391348959e-05,
                    u'\xe9v': 0.00048096963478372399,
                    u'\xe9\xe2': 0.00033988520858049831,
                    u'\xe9\xe7': 6.4129284637829867e-06,
                    u'\xe9\xe9': 2.5651713855131947e-05,
                    u'\xe9\xef': 6.4129284637829867e-06,
                    u'\xea': 0.0018738044100451573,
                    u'\xeac': 7.0542213101612857e-05,
                    u'\xeal': 4.4890499246480906e-05,
                    u'\xeam': 0.00049379549171128996,
                    u'\xean': 3.2064642318914931e-05,
                    u'\xeat': 0.0017379036136851893,
                    u'\xeav': 6.4129284637829862e-05,
                    u'\xeb': 1.4677319138734913e-05,
                    u'\xebt': 1.9238785391348959e-05,
                    u'\xee': 0.00072408107751092239,
                    u'\xeem': 6.4129284637829867e-06,
                    u'\xeen': 0.00010260685542052779,
                    u'\xeet': 0.00084009362875557124,
                    u'\xef': 8.3171475119497843e-05,
                    u'\xefe': 1.9238785391348959e-05,
                    u'\xeff': 2.5651713855131947e-05,
                    u'\xefr': 1.9238785391348959e-05,
                    u'\xefs': 1.2825856927565973e-05,
                    u'\xefv': 1.9238785391348959e-05,
                    u'\xf4': 0.00058220032583648491,
                    u'\xf4d': 1.2825856927565973e-05,
                    u'\xf4l': 0.00012825856927565972,
                    u'\xf4m': 3.2064642318914931e-05,
                    u'\xf4n': 1.9238785391348959e-05,
                    u'\xf4t': 0.00049379549171128996,
                    u'\xf4v': 1.9238785391348959e-05,
                    u'\xf9': 0.00040607249617166593,
                    u'\xfb': 0.00037182541818128447,
                    u'\xfbl': 3.2064642318914931e-05,
                    u'\xfbr': 5.7716356174046881e-05,
                    u'\xfbt': 0.00038477570782697917}

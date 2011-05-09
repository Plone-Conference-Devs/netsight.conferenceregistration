from decimal import Decimal
from time import time
from zope.interface import alsoProvides, implements
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory
from zope.component.hooks import getSite
from plone.memoize import ram
from getpaid.brownpapertickets.interfaces import IBPTOptions
from getpaid.brownpapertickets.bpt import BrownPaperTicketsClient


class to_vocab(object):
    ''' takes a list of (value, token, title) tuples '''

    implements(IVocabularyFactory)

    def __init__(self, tuples):
        self.tuples = tuples

    def __call__(self, context):
        terms = [SimpleTerm(*values) for values in self.tuples]
        return SimpleVocabulary(terms)



countries = [
    'Afghanistan', 'Albania', 'Algeria',
    'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina',
    'Armenia','Australia', 'Austria', 'Azerbaijan', 'Bahamas',
    'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium',
    'Belize', 'Benin', 'Bhutan', 'Bolivia',
    'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria',
    'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada',
    'Cape Verde', 'Central African Republic', 'Chad', 'Chile',
    'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica',
    "C&ocirc;te d'Ivoire", 'Croatia', 'Cuba', 'Cyprus',
    'Czech Republic', 'Denmark', 'Djibouti', 'Dominica',
    'Dominican Republic', 'East Timor', 'Ecuador', 'Egypt', 'El Salvador',
    'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Fiji',
    'Finland', 'France', 'Gabon', 'Gambia', 'Georgia', 'Germany',
    'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea',
    'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 'Hong Kong',
    'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq',
    'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan',
    'Kazakhstan','Kenya', 'Kiribati', 'North Korea','South Korea',
    'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon',
    'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania',
    'Luxembourg', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia',
    'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania',
    'Mauritius', 'Mexico', 'Micronesia', 'Moldova', 'Monaco',
    'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar',
    'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Zealand',
    'Nicaragua', 'Niger', 'Nigeria', 'Norway', 'Oman', 'Pakistan',
    'Palau', 'Palestine', 'Panama', 'Papua New Guinea',
    'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal',
    'Puerto Rico', 'Qatar', 'Romania', 'Russia', 'Rwanda',
    'Saint Kitts and Nevis', 'Saint Lucia',
    'Saint Vincent and the Grenadines', 'Samoa', 'San Marino',
    'Sao Tome and Principe',
    'Saudi Arabia', 'Senegal', 'Serbia and Montenegro',
    'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia',
    'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa',
    'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Swaziland',
    'Sweden', 'Switzerland', 'Syria', 'Taiwan',
    'Tajikistan','Tanzania', 'Thailand', 'Togo', 'Tonga',
    'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan',
    'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates',
    'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City',
    'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe']

def countries_vocab(context):
    return SimpleVocabulary.fromValues(countries)
alsoProvides(countries_vocab, IVocabularyFactory)

def badgetypes_vocab(context):
    badgetypes = ['Gold Sponsor', 'Silver Sponsor', 'Bronze Sponsor', 'Supporting Sponsor', 'Staff']
    return SimpleVocabulary.fromValues(badgetypes)
alsoProvides(badgetypes_vocab, IVocabularyFactory)


@ram.cache(lambda *args: time() // 86400)
def fetch_prices():
    prices = {}
    
    options = IBPTOptions(getSite())
    client = BrownPaperTicketsClient()
    res = client('pricelist',
        id = options.developer_id,
        # hardcoded to the Plone Conf 2011 event & date
        event_id = '176269',
        date_id = '512529',
        )
    if res.find('resultcode').text == '000000': # success
        for node in res.findall('price'):
            price_id = node.find('price_id').text
            name = node.find('name').text
            value = Decimal(node.find('value').text)
            service_fee = Decimal(node.find('service_fee').text)
            total_price = value + service_fee
            prices[price_id] = {
                'name': name,
                'value': value,
                'service_fee': service_fee,
                'total_price': total_price,
                'title': u'USD %s - %s' % (total_price, name),
                }
    return prices

def prices_vocab(context):
    terms = []
    for price_id, price_info in fetch_prices().items():
        terms.append(SimpleTerm(value=price_id, token=price_id, title=price_info['title']))
    return SimpleVocabulary(terms)
alsoProvides(prices_vocab, IVocabularyFactory)


shirts = [
    ("Men/Small", None, 'Mens Small (36-38" / 91-96cm)'),
    ("Men/Medium", None, 'Mens Medium (38-40" / 96-102cm)'),
    ("Men/Large", None, 'Mens Large (40-42" / 102-107cm)'),
    ("Men/XL", None, 'Mens XL (42-44" / 107-112cm)'),
    ("Men/XXL", None, 'Mens XXL (44-46" / 112-117cm)'),
    ("Women/Small", None, 'Womens Small (UK 8-10 / US 6-8 / Euro 36-38)'),
    ("Women/Medium", None, 'Womens Medium (UK 10-12 / US 8-10 / Euro 38-40)'),
    ("Women/Large", None, 'Womens Large (UK 14 / US 12 / Euro 42)'),
    ("Women/XL", None, 'Womens Large (UK 16 / US 14 / Euro 44)'),
    ]
shirts_vocab = to_vocab(shirts)

food = [
    ('normal',),
    ('vegetarian',),
    ('vegan',),
    ('other',),
    ]
food_vocab = to_vocab(food)

sprints = [
    ('unsure',  None, 'Unsure'),
    ( 'no',  None, 'No'),
    ( 'one',  None, 'One Day'),
    ( 'two',  None, 'Two Days'),
    ]
sprints_vocab = to_vocab(sprints)

INSERT INTO trend.l_language (short, lang)
VALUES('DE', 'German');
INSERT INTO trend.l_language (short, lang)
VALUES('EN', 'English');
INSERT INTO trend.l_language (short, lang)
VALUES('PL', 'Polish');
INSERT INTO trend.l_language (short, lang)
VALUES('CS', 'Czech');
INSERT INTO trend.l_language (short, lang)
VALUES('SK', 'Slovak');
INSERT INTO trend.l_language (short, lang)
VALUES('BG', 'Bulgarian');
INSERT INTO trend.l_language (short, lang)
VALUES('DA', 'Danish');
INSERT INTO trend.l_language (short, lang)
VALUES('ET', 'Estonian');
INSERT INTO trend.l_language (short, lang)
VALUES('FI', 'Finnish');
INSERT INTO trend.l_language (short, lang)
VALUES('FR', 'French');
INSERT INTO trend.l_language (short, lang)
VALUES('EL', 'Greek, Modern');
INSERT INTO trend.l_language (short, lang)
VALUES('HR', 'Croatian');
INSERT INTO trend.l_language (short, lang)
VALUES('HU', 'Hungarian');
INSERT INTO trend.l_language (short, lang)
VALUES('IT', 'Italian');
INSERT INTO trend.l_language (short, lang)
VALUES('LV', 'Latvian');
INSERT INTO trend.l_language (short, lang)
VALUES('LI', 'Limburgan');
INSERT INTO trend.l_language (short, lang)
VALUES('PT', 'Portuguese');
INSERT INTO trend.l_language (short, lang)
VALUES('RO', 'Romanian');
INSERT INTO trend.l_language (short, lang)
VALUES('SL', 'Slovenian');
INSERT INTO trend.l_language (short, lang)
VALUES('ES', 'Spanish');
INSERT INTO trend.l_language (short, lang)
VALUES('SV', 'Swedish');
INSERT INTO trend.l_language (short, lang)
VALUES('NL', 'Dutch');
INSERT INTO trend.l_country (short, country)
VALUES('FR', 'France');
INSERT INTO trend.l_country (short, country)
VALUES('GB', 'Great Britain');
INSERT INTO trend.l_country (short, country)
VALUES('IT', 'Italy');
INSERT INTO trend.l_country (short, country)
VALUES('ES', 'Spain');
INSERT INTO trend.l_country (short, country)
VALUES('PL', 'Poland');
INSERT INTO trend.l_country (short, country)
VALUES('RO', 'Romania');
INSERT INTO trend.l_country (short, country)
VALUES('NL', 'Netherlands');
INSERT INTO trend.l_country (short, country)
VALUES('BE', 'Belgium');
INSERT INTO trend.l_country (short, country)
VALUES('GR', 'Greece');
INSERT INTO trend.l_country (short, country)
VALUES('CZ', 'Czechia');
INSERT INTO trend.l_country (short, country)
VALUES('PT', 'Portugal');
INSERT INTO trend.l_country (short, country)
VALUES('SE', 'Sweden');
INSERT INTO trend.l_country (short, country)
VALUES('HU', 'Hungary');
INSERT INTO trend.l_country (short, country)
VALUES('AT', 'Austria');
INSERT INTO trend.l_country (short, country)
VALUES('CH', 'Switzerland');
INSERT INTO trend.l_country (short, country)
VALUES('BG', 'Bulgaria');
INSERT INTO trend.l_country (short, country)
VALUES('DK', 'Denmark');
INSERT INTO trend.l_country (short, country)
VALUES('FI', 'Finland');
INSERT INTO trend.l_country (short, country)
VALUES('SK', 'Slovakia');
INSERT INTO trend.l_country (short, country)
VALUES('IE', 'Ireland');
INSERT INTO trend.l_country (short, country)
VALUES('HR', 'Croatia');
INSERT INTO trend.l_country (short, country)
VALUES('LT', 'Lithuania');
INSERT INTO trend.l_country (short, country)
VALUES('SI', 'Slovenia');
INSERT INTO trend.l_country (short, country)
VALUES('LV', 'Latvia');
INSERT INTO trend.l_country (short, country)
VALUES('EE', 'Estonia');
INSERT INTO trend.l_country (short, country)
VALUES('CY', 'Cyprus');
INSERT INTO trend.l_country (short, country)
VALUES('LU', 'Luxembourg');
INSERT INTO trend.l_version (version)
VALUES('21-04-22')
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'FR'
    and l.short IN ('FR', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'GB'
    and l.short IN ('DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'IT'
    and l.short IN ('IT', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'ES'
    and l.short IN ('ES', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'PL'
    and l.short IN ('PL', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'RO'
    and l.short IN ('RO', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'NL'
    and l.short IN ('NL', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'BE'
    and l.short IN ('FR', 'NL', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'GR'
    and l.short IN ('EL', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'CZ'
    and l.short IN ('CS', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'PT'
    and l.short IN ('PT', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'SE'
    and l.short IN ('SV', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'HU'
    and l.short IN ('HU', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'AT'
    and l.short IN ('DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'CH'
    and l.short IN ('FR', 'IT', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'BG'
    and l.short IN ('BG', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'DK'
    and l.short IN ('DA', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'FI'
    and l.short IN ('FI', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'SK'
    and l.short IN ('SK', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'IE'
    and l.short IN ('DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'HR'
    and l.short IN ('HR', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'LT'
    and l.short IN ('LI', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'SI'
    and l.short IN ('SL', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'LV'
    and l.short IN ('LV', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'EE'
    and l.short IN ('ET', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'CY'
    and l.short IN ('EL', 'DE', 'EN');
INSERT INTO trend.a_country_language (country_id, language_id)
SELECT c.id,
    l.id
FROM trend.l_country AS c
    INNER JOIN trend.l_language AS l ON c.short = 'LU'
    and l.short IN ('FR', 'DE', 'EN');
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Deutschland'
FROM trend.l_language
WHERE short = 'DE';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Germany'
FROM trend.l_language
WHERE short = 'EN';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Niemcy'
FROM trend.l_language
WHERE short = 'PL';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Německo'
FROM trend.l_language
WHERE short = 'CS';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Nemecko'
FROM trend.l_language
WHERE short = 'SK';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Германия'
FROM trend.l_language
WHERE short = 'BG';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Tyskland'
FROM trend.l_language
WHERE short = 'DA';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Saksamaa'
FROM trend.l_language
WHERE short = 'ET';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Saksa'
FROM trend.l_language
WHERE short = 'FI';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Allemagne'
FROM trend.l_language
WHERE short = 'FR';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Γερμανία'
FROM trend.l_language
WHERE short = 'EL';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Njemačka'
FROM trend.l_language
WHERE short = 'HR';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Németország'
FROM trend.l_language
WHERE short = 'HU';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Germania'
FROM trend.l_language
WHERE short = 'IT';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Vācija'
FROM trend.l_language
WHERE short = 'LV';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Vokietija'
FROM trend.l_language
WHERE short = 'LI';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Alemanha'
FROM trend.l_language
WHERE short = 'PT';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Germania'
FROM trend.l_language
WHERE short = 'RO';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Nemčija'
FROM trend.l_language
WHERE short = 'SL';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Alemania'
FROM trend.l_language
WHERE short = 'ES';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Tyskland'
FROM trend.l_language
WHERE short = 'SV';
INSERT INTO trend.l_germany_language (language_id, germany)
SELECT id,
    'Duitsland'
FROM trend.l_language
WHERE short = 'NL';
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('DE', 'German', FALSE, 'Deutschland');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('EN', 'English', FALSE, 'Germany');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('PL', 'Polish', TRUE, 'Niemcy');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('CS', 'Czech', TRUE, 'Německo');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('SK', 'Slovak', TRUE, 'Nemecko');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('BG', 'Bulgarian', FALSE, 'Германия');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('DA', 'Danish', FALSE, 'Tyskland');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('ET', 'Estonian', FALSE, 'Saksamaa');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('FI', 'Finnish', FALSE, 'Saksa');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('FR', 'French', TRUE, 'Allemagne');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('EL', 'Greek, Modern', TRUE, 'Γερμανία');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('HR', 'Croatian', TRUE, 'Njemačka');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('HU', 'Hungarian', FALSE, 'Németország');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('IT', 'Italian', TRUE, 'Germania');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('LV', 'Latvian', TRUE, 'Vācija');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('LI', 'Limburgan', TRUE, 'Vokietija');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('PT', 'Portuguese', TRUE, 'Alemanha');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('RO', 'Romanian', FALSE, 'Germania');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('SL', 'Slovenian', FALSE, 'Nemčija');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('ES', 'Spanish', TRUE, 'Alemania');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('SV', 'Swedish', FALSE, 'Tyskland');
INSERT INTO trend.l_language (short, lang, remove_diacritics, germany)
VALUES('NL', 'Dutch', FALSE, 'Duitsland');
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
VALUES('21-04-22');
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
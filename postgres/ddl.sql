DROP TABLE trend.l_language CASCADE;
DROP TABLE trend.l_keyword CASCADE;
DROP TABLE trend.l_version CASCADE;
DROP TABLE trend.l_country CASCADE;
DROP TABLE trend.a_country_language CASCADE;
DROP TABLE trend.d_searchword CASCADE;
DROP TABLE trend.d_trends CASCADE;
CREATE TABLE trend.l_language (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    short CHAR(2),
    lang VARCHAR(20),
    remove_diacritics BOOLEAN,
    germany VARCHAR(20)
);
CREATE TABLE trend.l_version (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    version VARCHAR(20)
);
CREATE TABLE trend.l_keyword (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    keyword_id INT,
    language_id INT,
    version_id INT,
    without_germany BOOLEAN,
    keyword VARCHAR(200),
    CONSTRAINT fk_language FOREIGN KEY(language_id) REFERENCES trend.l_language(id),
    CONSTRAINT fk_version FOREIGN KEY(version_id) REFERENCES trend.l_version(id)
);
CREATE TABLE trend.l_country (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    short CHAR(2),
    country VARCHAR(20)
);
CREATE TABLE trend.a_country_language (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country_id INT,
    language_id INT,
    CONSTRAINT fk_language FOREIGN KEY(language_id) REFERENCES trend.l_language(id),
    CONSTRAINT fk_country FOREIGN KEY(country_id) REFERENCES trend.l_country(id)
);
CREATE TABLE trend.d_searchword (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country_id INT,
    version_id INT,
    keyword_id INT,
    searchword VARCHAR(4000),
    CONSTRAINT fk_version FOREIGN KEY(version_id) REFERENCES trend.l_version(id),
    CONSTRAINT fk_country FOREIGN KEY(country_id) REFERENCES trend.l_country(id)
);
CREATE TABLE trend.d_trends (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    searchword_id INT,
    iteration INT,
    date DATE,
    value INT,
    date_of_retrieval TIMESTAMP,
    CONSTRAINT fk_searchword FOREIGN KEY(searchword_id) REFERENCES trend.d_searchword(id)
);
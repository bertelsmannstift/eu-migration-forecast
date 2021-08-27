CREATE TABLE trend.l_language (
    id INT GENERATED ALWAYS AS IDENTITY,
    short CHAR(2),
    lang VARCHAR(20)
);
CREATE TABLE trend.l_keyword (
    id INT GENERATED ALWAYS AS IDENTITY,
    keyword_id INT,
    language_id INT,
    version_id INT,
    without_germany BOOLEAN,
    keyword VARCHAR(200)
);
CREATE TABLE trend.l_version (
    id INT GENERATED ALWAYS AS IDENTITY,
    version VARCHAR(20)
);
CREATE TABLE trend.l_country (
    id INT GENERATED ALWAYS AS IDENTITY,
    short CHAR(2),
    country VARCHAR(20)
);
CREATE TABLE trend.l_germany_language (
    id INT GENERATED ALWAYS AS IDENTITY,
    language_id INT,
    germany VARCHAR(20)
);
CREATE TABLE trend.a_country_language (
    id INT GENERATED ALWAYS AS IDENTITY,
    country_id INT,
    language_id INT
);
CREATE TABLE trend.d_searchword (
    id INT GENERATED ALWAYS AS IDENTITY,
    country_id INT,
    language_id INT,
    version_id INT,
    keyword_id INT,
    searchword VARCHAR(400)
);
CREATE TABLE trend.d_trends (
    id INT GENERATED ALWAYS AS IDENTITY,
    searchword_id INT,
    iteration INT,
    date DATE,
    value INT,
    date_of_retrieval TIMESTAMP
);
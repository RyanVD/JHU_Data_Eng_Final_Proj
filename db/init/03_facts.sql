-- Fact: CDC PLACES mental health / sleep outcomes
CREATE TABLE Fact_Mental_Health (
    id                    SERIAL PRIMARY KEY,
    county_fips           CHAR(5) NOT NULL REFERENCES Dim_County(county_fips),
    year                  INTEGER NOT NULL REFERENCES Dim_Year(year),
    poor_mental_health_pct NUMERIC(5,2),
    poor_sleep_pct        NUMERIC(5,2),
    data_value_type       VARCHAR(30),  -- crude vs age-adjusted
    UNIQUE (county_fips, year)
);

-- Fact: FRED/FHFA housing costs
CREATE TABLE Fact_Housing (
    id                    SERIAL PRIMARY KEY,
    county_fips           CHAR(5) REFERENCES Dim_County(county_fips),  -- NULL for national/state rows
    year                  INTEGER NOT NULL REFERENCES Dim_Year(year),
    rate_geography_level  VARCHAR(10) NOT NULL,  -- 'county', 'state', or 'national'
    housing_price_index   NUMERIC(10,2),
    mortgage_rate_30yr    NUMERIC(5,2),
    average_rent          NUMERIC(10,2)
);

-- Fact: HUD Point-in-Time homelessness counts
CREATE TABLE Fact_Homelessness (
    id                    SERIAL PRIMARY KEY,
    coc_code              VARCHAR(10) NOT NULL REFERENCES Dim_CoC(coc_code),
    year                  INTEGER NOT NULL REFERENCES Dim_Year(year),
    total_homeless_count  INTEGER,
    sheltered_count       INTEGER,
    UNIQUE (coc_code, year)
);

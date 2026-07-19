-- Dimension: County
CREATE TABLE Dim_County (
    county_fips   CHAR(5) PRIMARY KEY,
    county_name   VARCHAR(100) NOT NULL,
    state_abbr    CHAR(2) NOT NULL
);

-- Dimension: Year
CREATE TABLE Dim_Year (
    year          INTEGER PRIMARY KEY
);

-- Dimension: Continuum of Care (HUD region)
CREATE TABLE Dim_CoC (
    coc_code      VARCHAR(10) PRIMARY KEY,
    coc_name      VARCHAR(150) NOT NULL
);

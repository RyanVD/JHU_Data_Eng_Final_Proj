-- Bridge: resolves CoC-to-county many-to-many relationship
CREATE TABLE Bridge_CoC_County (
    coc_code      VARCHAR(10) NOT NULL REFERENCES Dim_CoC(coc_code),
    county_fips   CHAR(5) NOT NULL REFERENCES Dim_County(county_fips),
    overlap_ratio NUMERIC(5,4) NOT NULL,  -- fraction of CoC's population/area within this county
    PRIMARY KEY (coc_code, county_fips)
);

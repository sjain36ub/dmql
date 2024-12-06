CREATE TABLE results (
    date DATE,
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    home_score INT,
    away_score INT,
    tournament VARCHAR(100),
    city VARCHAR(100),
    country VARCHAR(100),
    neutral BOOLEAN,
    PRIMARY KEY (date, home_team, away_team)
);

CREATE TABLE shootouts (
    date DATE,
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    winner VARCHAR(100),
    first_shooter VARCHAR(100),
    PRIMARY KEY (date, home_team, away_team),
    FOREIGN KEY (date, home_team, away_team) REFERENCES results (date, home_team, away_team)
);

CREATE TABLE goalscorers (
    date DATE,
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    team VARCHAR(100),
    scorer VARCHAR(100), -- Removed NOT NULL constraint
    minute INT,
    own_goal BOOLEAN,
    penalty BOOLEAN,
    PRIMARY KEY (date, home_team, away_team, scorer),
    FOREIGN KEY (date, home_team, away_team) REFERENCES results (date, home_team, away_team)
);


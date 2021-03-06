#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn= psycopg2.connect("dbname=tournament")
    cur= conn.cursor()
    cur.execute("delete from matches;");
    cur.execute("alter sequence matches_id_seq restart with 1;")
    conn.commit()
    conn.close()

def deletePlayers():
    """Remove all the player records from the database."""
    conn= psycopg2.connect("dbname=tournament")
    cur= conn.cursor()
    cur.execute("delete from players;");
    cur.execute("alter sequence players_id_seq restart with 1;")
    conn.commit()
    conn.close()

def countPlayers():
    """Returns the number of players currently registered."""
    conn= psycopg2.connect("dbname=tournament")
    cur= conn.cursor()
    cur.execute("select count(*) as num from players;")
    numPlayers= cur.fetchall()
    print numPlayers
    conn.close()
    return numPlayers[0][0]

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn= psycopg2.connect("dbname=tournament")
    cur= conn.cursor()
    cur.execute("insert into players (name) values (%s);", (name,))
    conn.commit()
    conn.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn= psycopg2.connect("dbname=tournament")
    cur= conn.cursor()
    cur.execute("CREATE TABLE totMatchesTbl AS SELECT players.id, name, COUNT(matches.id) as totMatches FROM players LEFT JOIN matches ON (players.id= matches.winner OR players.id= matches.loser) GROUP BY players.id ORDER BY players.id;")
    cur.execute("SELECT totmatchestbl.id, name, COUNT(matches.id) as totWins, totmatches FROM totmatchestbl LEFT JOIN matches ON (totmatchestbl.id= matches.winner) GROUP BY totmatchestbl.id, totmatchestbl.name, totmatchestbl.totmatches ORDER BY totWins desc;")
    standings= cur.fetchall()
    conn.close()

    return standings



def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn= psycopg2.connect("dbname=tournament")
    cur= conn.cursor()
    cur.execute("insert into matches (winner, loser) values (%s, %s);", (winner, loser))
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings= playerStandings()

    pairings=[]

    for i in range(0, len(standings), 2):
        tup= (standings[i][0], standings[i][1], standings[i+1][0], standings[i+1][1])
        pairings.append(tup)

    return pairings



'''Python tool utilizing Smash.GG API to access tournament stats and compile a single player's winrate overall'''
import requests
import json
import pandas as pd

winIndex = 0
totalIndex = 1
lossIndex = 1

def getTourneyInfo(tournament):
        entrantsAndSets = []
        
        get = requests.get("https://api.smash.gg/tournament/%s/event/wii-u-singles?expand[]=phase&expand[]=groups" % tournament)
        JSON = json.loads(get.text)
        phase_id = JSON['entities']['groups'][0]["id"]
        
        entrantsJSON = requests.get("https://api.smash.gg/phase_group/%d?expand[]=entrants" % phase_id)
        setsJSON = requests.get("https://api.smash.gg/phase_group/%d?expand[]=sets" % phase_id)
        
        entrantsAndSets.append(json.loads(entrantsJSON.text)['entities']['entrants'])
        entrantsAndSets.append(json.loads(setsJSON.text)['entities']['sets'])
        return entrantsAndSets
        

def findPlayerID(name, entrants):
    for player in entrants:
        if(player['name'] == name):
            return player['id']
    return -1 #If we return -1, we couldn't find the player with given name

def playerSetScore(id, set):
    scores = [0, 0]
    if set['entrant1Id'] == id:
        scores[winIndex] += set['entrant1Score']
        scores[lossIndex] += set['entrant2Score']
    elif set['entrant2Id'] == id:
        scores[winIndex] += set['entrant2Score']
        scores[lossIndex] += set['entrant1Score']
    return scores

def main():
    #We inport all the tournament names through a csv file
    df = pd.read_csv("tournaments.csv")
    tournaments = df["Tournaments"]
    totalGameStats = [0, 0]
    totalSetStats = [0, 0]

    playerName = raw_input("Player name?\n")
    
    for tournament in tournaments:
        print tournament

        #Utilize get requests to get the entrants and sets of a tournament
        entrants = getTourneyInfo(tournament)[0]
        sets = getTourneyInfo(tournament)[1]

        #Using the user provided name, we search for the numerical id for the player
        playerId = findPlayerID(playerName, entrants)
        
        #We can skip this entire tournament if the player was not found in entrants
        if not playerId == -1:
            
            #The way we tally games and sets are different because we can directly get wins and losses for games, but it's easier for us 
            #to keep track of wins and total for sets.
            scores = [0,0]
            totalSets = 0
            wonSets = 0
            for games in sets:
                #For each game in the set, we check if it's a valid game that provides legitimate scores.
                if (games['entrant1Score'] == 0 or games['entrant1Score'] == 1 or games['entrant1Score'] == 2 or games['entrant1Score'] == 3
                ) and (games['entrant2Score'] == 0 or games['entrant2Score'] == 1 or games['entrant2Score'] == 2 or games['entrant2Score'] == 3
                ):
                    #Tmp is just the single game's score count, but we are interested in the total number of games won/lost in tournament
                    tmp = playerSetScore(playerId, games)
                    #Check if it's a legitimate game and not just a 0-0 game
                    if  not(tmp[winIndex] == 0 and tmp[lossIndex] == 0):
                        totalSets += 1
                        totalSetStats[totalIndex] += 1
                        
                        #We can tell if the player won the set by looking at the comparison of wins vs losses
                        if tmp[0] > tmp[1]:
                            wonSets += 1
                            totalSetStats[winIndex] += 1
                    scores[winIndex] += tmp[winIndex] #Number of wins
                    scores[lossIndex] += tmp[lossIndex] #Number of losses
            
            wins = float(scores[winIndex])
            losses = float(scores[winIndex])
            totalGames = wins + losses

            totalGameStats[winIndex] += wins
            totalGameStats[totalIndex] += totalGames
            
            gameWinPercent = wins/totalGames * 100
            setWinPercent = float(wonSets)/float(totalSets) * 100

            print ("Game Winrate for %s: %5.2f %%" % (playerName, gameWinPercent))
            print ("Set Winrate for %s: %5.2f %%" % (playerName, setWinPercent))
            print ("Games Won: %d" % wins)
            print ("Games Lost: %d" % losses)
            print ("Sets Won: %d" % wonSets)
            print ("Sets Lost: %d" % (totalSets - wonSets))

    print ("Total Games Winrate: %5.2f %%" % (float(totalGameStats[winIndex]/float(totalGameStats[totalIndex])) * 100))
    print ("Total Set Winrate: %5.2f %%" % (float(totalSetStats[winIndex]/float(totalSetStats[totalIndex])) * 100))

        

    #Given a tournament name and event, we can get the necessary information to get the player information
    

if __name__ == "__main__":
    main()
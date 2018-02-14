import requests
import json
import time
import datetime
import math
import threading


# Make a get request to get the latest position of the international space station from the opennotify api.
MILLION = 1000000
BILLION = 1000000000
mainCoinsSymbols = ["BTC", "ETH", "NAS", "QASH", "PROC", "USDT", "CRPT", "EOS", "XRP", "XMR"]

currFloor = 0
currCeiling = 0
isFirstCall = True
interval = 10 * BILLION
lastTotMarketCap = 0;
lastChangeDate = datetime.datetime.now()

def stringToFloat(str):
	try:
		return float(str)
	except:
		return 0

def setFloorAndCeiling(totmarketcap, interval):
	return math.floor(totmarketcap / (interval)) * interval, math.ceil(totmarketcap / (interval)) * interval
	
def getTotMarketCap(data):
		totmarketcap = 0
		for coin in data:
			coinmc = stringToFloat(coin["market_cap_usd"])
			price = stringToFloat(coin["price_usd"])
			totmarketcap = totmarketcap + coinmc
		return totmarketcap

def getMainCoinsInfo(data, mainCoinsSymbols):
	mainCoins = []
	
	for coin in data:
		for mainCoinSymbol in mainCoinsSymbols:
			if mainCoinSymbol == coin["symbol"]:
				mainCoins.append(coin)
	return mainCoins

def printMarketCap(string, totmarketcap):
	print(string, "{:,}".format(totmarketcap), "$")


def printMainCoins(mainCoins):
	for coin in mainCoins:
		strCoinSym =  coin["symbol"] + ":"
		coinPriceUSD = stringToFloat(coin["price_usd"])
		strCoinUSD = "{:,}".format(coinPriceUSD) + "$"
		coinMarketCapUSD = stringToFloat(coin["market_cap_usd"])
		strMarketCap = "{:,}".format(coinMarketCapUSD) + "$"
		strCoinBTC = coin["price_btc"] + " BTC"
		strPerChg1H = coin["percent_change_1h"] + "%"
		strPerChg24H = coin["percent_change_24h"] + "%"
		strPerChg7D = coin["percent_change_7d"] + "%"
		print('{:>5}  {:>10}  {:>18} {:>20} {:>10} {:>10} {:>10}'.format(strCoinSym, strCoinUSD, strMarketCap, strCoinBTC, strPerChg1H, strPerChg24H, strPerChg7D))
		
		#print(coin["symbol"], ":", "{:,}".format(coinPriceUSD),  "$,", coin["price_btc"],"BTC, 1h:", coin["percent_change_1h"], "%")

def printTimeStamp():
	print("TIME: ",datetime.datetime.now())

def apiCall(url):

	try:
		response = requests.get(url)
		return json.loads(response.content.decode('utf-8'))
	except :#ConnectionError as e:
		#print(e)
		print("NO INTERNET CONNECTION!")
		return 0
	

def resolver(isManual):
	global lastTotMarketCap
	global lastChangeDate
	data = apiCall("https://api.coinmarketcap.com/v1/ticker/?limit=1500")
	if(data != 0):
		totmarketcap = getTotMarketCap(data)

		if (totmarketcap != lastTotMarketCap) or (isManual == True):
			print("----------------------------------------------------------------")
			changeDate = datetime.datetime.now()
			mainCoins = getMainCoinsInfo(data, mainCoinsSymbols)
			mainCoinsMarketCap = getTotMarketCap(mainCoins)
			print(mainCoinsMarketCap)
			printTimeStamp()
			print()
			print("Main Coins:")
			printMainCoins(mainCoins)
			print()
			printMarketCap("TotMarketcap: ", totmarketcap)
			printMarketCap("MainMarketcap: ", mainCoinsMarketCap)
			checkBoundaries(totmarketcap)
		
			lastTotMarketCap = totmarketcap
			if(isManual == False):
				print("Time passed Since last update:", changeDate - lastChangeDate)
				lastChangeDate = changeDate
			print("----------------------------------------------------------------")
			print()
	
def checkBoundaries(totmarketcap):
	global isFirstCall
	global currFloor
	global currCeiling
	if isFirstCall == True:
		currFloor, currCeiling = setFloorAndCeiling(totmarketcap, interval)
		isFirstCall = False

	#print("currFloor:", currFloor, ", currCeiling:", currCeiling)
	if totmarketcap > currCeiling:
		print("Broke", "{:,}".format(currCeiling), "point!!! :)")
		currFloor, currCeiling = setFloorAndCeiling(totmarketcap, interval) 
		i = 0
		while i < 4:
			print("\a", ":)")
			i += 1
			time.sleep(1)
	if totmarketcap < currFloor:
		print("Broke", "{:,}".format(currFloor), "point... :(")
		i = 0
		while i < 8:
			print("\a", ":(")
			i += 1
			time.sleep(0.25)
		currFloor, currCeiling = setFloorAndCeiling(totmarketcap, interval)
	
def checkEnter():
	while True:
		text = input()
		if text == "":
			print ("---MANUAL---")
			resolver(True)

t1 = threading.Thread(target=checkEnter)
t1.setDaemon(True)
t1.start()

while True: 
	resolver(False)
	time.sleep(5)


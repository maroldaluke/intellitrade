# lmarolda - term project
# intellitrade

# this is the main file for this project. it pulls stock data from the stockData.py
# file and then uses that data within this file. to run, simple command + B on this file! 

import math, copy, random
from cmu_112_graphics import *
from stockData import *

# MODEL

def appStarted(app):
    # stock info
    app.apple = [ aapl_2008, aapl_2011, aapl_2015, aapl_2018 ]
    app.disney = [ dis_2008, dis_2011, dis_2015, dis_2018 ]
    app.generalElectric = [ ge_2008, ge_2011, ge_2015, ge_2018 ] 
    app.stockCompany = app.apple
    app.index = 0
    app.stock = app.stockCompany[app.index]
    (app.graphX0, app.graphY0) = (app.width / 8, app.height / 8)
    app.indicatorLine = app.height * 2/3
    app.lineWidth = 5
    # game states
    app.startingScreen = True
    app.paused = False
    app.gameover = False
    app.sma1On = True
    app.sma2On = True
    app.ema1On = False
    app.ema2On = False
    app.macdOn = True
    app.rsiOn = False
    app.aiModeOn = False
    app.gameInfoScreen = False
    # account info
    app.startingAccountValue = 100000
    app.shares = 0
    app.profitLoss = 100
    app.cash = 100000
    app.currentPosition = 0
    app.accountValue = app.cash + app.currentPosition
    # marked lines
    app.markedLines = []
    app.isDrawing = False
    # zoom in and out
    app.graphPeriod = 60
    (app.minPeriod, app.maxPeriod) = (30, 100)
    app.startIndex = 0
    # speed of the price action
    app.timerDelay = 800
    (app.minSpeed, app.maxSpeed) = (1200,400)
    # all stocks are same length lists
    app.stockLength = 250
    # colors
    (app.sma1Color, app.sma2Color) = ("red", "blue")
    (app.ema1Color, app.ema2Color) = ("green", "orange")
    (app.drawColor, app.eraseColor) = ("#0AAD00", "#E7A2FF")
    (app.macdColor, app.macdSignalColor) = ("purple", "dark blue")
    app.rsiColor = "dark red"
    app.aiModeColor = "#FF8CFD"
    app.whiteButton = "white"
    # images
    app.logo = app.loadImage('intellitrade_logo.png')
    app.scaledLogo = app.scaleImage(app.logo, 1/2)
    app.gameinfo = app.loadImage('gameinfo.png')
    app.scaledGameInfo = app.scaleImage(app.gameinfo, .99)
    # ai mode
    app.aiHasPosition = False
    app.aiStartingAccountValue = 100000
    app.aiShares = 0
    app.aiProfitLoss = 100
    app.aiCash = 100000
    app.aiCurrentPosition = 0
    app.aiAccountValue = app.aiCash + app.aiCurrentPosition

# TECHNICAL INDICATOR FUNCTIONS

# function returns list of floats of a specific period SMA, for a given stock
def simpleMovingAverage(stock, period):
    # formula for SMA:
    # SMA at period N = (A1 + A2 + A3 + AN) / N 
    # where N is the total number of periods
    sma = []
    startingDay = period
    totalDays = len(stock)
    closePriceIndex = 3
    for day in range(startingDay, totalDays):
        sumOfCloses = 0
        for previousDay in range(period, 0, -1):
            close = stock[day - previousDay][closePriceIndex]
            sumOfCloses += close
        smaValue = sumOfCloses / period
        sma.append(smaValue)
    # to make up for the lost days at beginning of the SMA, make a line
    # connecting the first day close with the beginning of SMA
    firstClose = stock[0][closePriceIndex]
    difference = sma[0] - firstClose
    valueIncrement = difference / period
    for day in range(startingDay):
        smaValue = firstClose + (day * valueIncrement)
        sma.insert(0, smaValue)
    return sma

# function returns list of floats of a specific period EMA, for a given stock
def exponentialMovingAverage(stock, period):
    # formula for EMA:
    # EMA(today) = (Price(today) * K) + (EMA(yesterday) * (1 - K))
    # where N = period and K = 2 / (N + 1)
    totalDays = len(stock)
    closePriceIndex = 3
    baseEma = stock[0][closePriceIndex]
    # have to start somewhere, so first EMA value is the first closing price
    ema = [baseEma]
    weight = 2 / (period + 1)
    for day in range(1, totalDays):
        close = stock[day][closePriceIndex]
        emaValue = (close * weight) + (ema[day - 1] * (1 - weight))
        ema.append(emaValue)
    return ema

# function returns list of floats of MACD for a given stock
def macd(stock):
    macd = []
    totalDays = len(stock)
    twelvePeriod = exponentialMovingAverage(stock, 12)
    twentySixPeriod = exponentialMovingAverage(stock, 26)
    for day in range(totalDays):
        macdValue = twelvePeriod[day] - twentySixPeriod[day]
        macd.append(macdValue)
    return macd

def macdSignalLine(macd):
    totalDays = len(macd)
    period = 9
    baseEma = macd[0]
    # have to start somewhere, so first EMA value is the first closing price
    signal = [baseEma]
    weight = 2 / (period + 1)
    for day in range(1, totalDays):
        close = macd[day]
        emaValue = (close * weight) + (signal[day - 1] * (1 - weight))
        signal.append(emaValue)
    return signal

# function returns list of floats of RSI indicator for a given stock
def relativeStrengthIndex(stock):
    # uses a 14 day period to calculate the average gain
    rsi = []
    period = 14
    totalDays = len(stock)
    initialTotalGain = 0
    initialTotalLoss = 0
    # calculate first part of the rsi
    for row in range(period + 1):
        currentDay = stock[row]
        (dayOpen, dayClose) = (currentDay[0], currentDay[3])
        if dayOpen < dayClose:
            dayGain = ((dayClose - dayOpen) / dayOpen) * 100
            initialTotalGain += dayGain
        else:
            dayLoss = ((dayOpen - dayClose) / dayOpen) * 100
            initialTotalLoss += dayLoss
    initialAverageGain = initialTotalGain / period
    initialAverageLoss = initialTotalLoss / period
    # from the rsi formula
    rsiStepOne = 100 - (100 / (1 + initialAverageGain / initialAverageLoss))
    # add the first rsi value to the list
    rsi.append(rsiStepOne)
    # now calculate the rest of the rsi
    for row in range(period + 1, totalDays):
        currentDay = stock[row]
        (dayOpen, dayClose) = (currentDay[0], currentDay[3])
        (currentGain, currentLoss) = (0, 0)
        if dayOpen < dayClose: 
            currentGain = ((dayClose - dayOpen) / dayOpen) * 100
        else:
            currentLoss = ((dayOpen - dayClose) / dayOpen) * 100
        prevTotalGain = 0
        prevTotalLoss = 0
        for index in range(1, period):
            prevDay = stock[row - index]
            (dayOpen, dayClose) = (prevDay[0], prevDay[3])
            if dayOpen < dayClose:
                dayGain = ((dayClose - dayOpen) / dayOpen) * 100
                prevTotalGain += dayGain
            else:
                dayLoss = ((dayOpen - dayClose) / dayOpen) * 100
                prevTotalLoss += dayLoss
        prevAverageGain = prevTotalGain / period
        prevAverageLoss = prevTotalLoss / period
        denom = (prevAverageGain * 13 + currentGain) / (prevAverageLoss*13 + currentLoss)
        rsiStepTwo = 100 - (100 / (1 + denom))
        rsi.append(rsiStepTwo)
    # now bridge the starting point to the first value of RSI
    firstValue = 50
    difference = rsi[0] - firstValue
    valueIncrement = difference / period
    for day in range(period, 0, -1):
        rsiValue = firstValue + (day * valueIncrement)
        rsi.insert(0, rsiValue)
    return rsi

# GRAPH SCALING FUNCTIONS

def graphScaler(app, stock, maxY, minY):
    rawData = []
    dataMargin = 10
    (openPriceIndex, closePriceIndex) = (0, 3)
    for day in range(app.startIndex, app.graphPeriod + app.startIndex):
        currentDay = stock[day]
        dayData = [currentDay[0], currentDay[3]]
        rawData.extend(dayData)
    maxValue = max(rawData)
    minValue = min(rawData)
    # now lets convert to the scaled data
    scaledData = []
    rawRange = maxValue - minValue
    graphMax = maxY + dataMargin
    graphMin = minY - dataMargin
    graphRange = graphMax - graphMin
    # take care of the even spacing between data points
    (startingX, endingX) = (app.graphX0, app.width)
    xRange = endingX - startingX
    xIncrement = xRange / app.graphPeriod
    # find each scaled data point
    currentX = startingX
    for value in rawData:
        currentDifference = maxValue - value
        rangePercentage = currentDifference / rawRange
        graphIncrement = rangePercentage * graphRange
        graphHeight = graphMax - graphIncrement
        dataCoordinate = (currentX, graphHeight)
        scaledData.append(dataCoordinate)
        currentX += xIncrement
    return scaledData

def indicatorScaler(app, indicator, maxY, minY):
    rawData = []
    dataMargin = 10
    for day in range(app.startIndex, app.graphPeriod + app.startIndex):
        currentDay = indicator[day]
        rawData.append(currentDay)
    maxValue = max(rawData)
    minValue = min(rawData)
    # now lets convert to the scaled data
    scaledData = []
    rawRange = maxValue - minValue
    graphMax = maxY + dataMargin
    graphMin = minY - dataMargin
    graphRange = graphMax - graphMin
    # take care of the even spacing between data points
    (startingX, endingX) = (app.graphX0, app.width)
    xRange = endingX - startingX
    xIncrement = xRange / (app.graphPeriod / 2)
    # find each scaled data point
    currentX = startingX
    for value in rawData:
        currentDifference = maxValue - value
        rangePercentage = currentDifference / rawRange
        graphIncrement = rangePercentage * graphRange
        graphHeight = graphMax - graphIncrement
        dataCoordinate = (currentX, graphHeight)
        scaledData.append(dataCoordinate)
        currentX += xIncrement
    return scaledData

# CONTROLLER

def gameOver(app):
    if (app.stockLength <= app.graphPeriod + app.startIndex) or (app.accountValue <= 0):
        app.gameover = True

def timerFired(app):
    gameOver(app)
    calculateAccountInfo(app)
    if app.paused == False and app.gameover == False and app.startingScreen == False:
        takeStep(app)

def takeStep(app):
    app.startIndex += 1
    if app.aiModeOn:
        aiBuySellStock(app)
        calculateAiMode(app)

def keyPressed(app, event):
    key = event.key
    if app.gameover == False:
        if key == "p":
            if app.paused:
                app.markedLines = []
            app.paused = not app.paused
            app.gameInfoScreen = False
        elif key == "s" and app.paused:
            takeStep(app)

def mousePressed(app, event):
    (x, y) = (event.x, event.y)
    if app.gameover == False:
        if app.startingScreen:
            if clickedAppleButton(app, x, y):
                app.stockCompany = app.apple
                app.stock = app.stockCompany[app.index]
            elif clickedDisneyButton(app, x, y):
                app.stockCompany = app.disney
                app.stock = app.stockCompany[app.index]
            elif clickedGEButton(app, x, y):
                app.stockCompany = app.generalElectric
                app.stock = app.stockCompany[app.index]
            if app.stockCompany != None:
                if clicked2008Button(app, x, y):
                    app.index = 0
                    app.stock = app.stockCompany[app.index]
                elif clicked2011Button(app, x, y):
                    app.index = 1
                    app.stock = app.stockCompany[app.index]
                elif clicked2015Button(app, x, y):
                    app.index = 2    
                    app.stock = app.stockCompany[app.index]
                elif clicked2018Button(app, x, y):
                    app.index = 3
                    app.stock = app.stockCompany[app.index]         
            if app.stock != None and clickedStartButton(app, x, y):
                app.startingScreen = False
            if clickedAiMode(app, x, y):
                app.aiModeOn = not app.aiModeOn
        elif clickedBuyStock(app, x, y):
            buyStock(app)
        elif clickedSellStock(app, x, y):
            sellStock(app)
        elif clickedZoomPlus(app, x, y):
            app.graphPeriod -= 4
            # recalculate the current price
            calculateAccountInfo(app)
        elif clickedZoomMinus(app, x, y):
            app.graphPeriod += 4
            # recalculate the current price
            calculateAccountInfo(app)
        elif clickedSpeedPlus(app, x, y):
            app.timerDelay -= 50
        elif clickedSpeedMinus(app, x, y):
            app.timerDelay += 50
        elif clickedSma1(app, x, y):
            app.sma1On = not app.sma1On
        elif clickedSma2(app, x, y):
            app.sma2On = not app.sma2On
        elif clickedEma1(app, x, y):
            app.ema1On = not app.ema1On
        elif clickedEma2(app, x, y):
            app.ema2On = not app.ema2On
        elif clickedMacd(app, x, y):
            app.macdOn = not app.macdOn
            app.rsiOn = not app.rsiOn
        elif clickedRsi(app, x, y):
            app.macdOn = not app.macdOn
            app.rsiOn = not app.rsiOn
        elif clickedGameInfo(app, x, y):
            app.paused = True
            app.gameInfoScreen = True
        elif app.paused and clickedDrawLine(app, x, y):
            app.isDrawing = True
        elif app.isDrawing:
            drawingLines(app, x, y)
    else:
        if clickedRestart(app, x, y):
            appStarted(app)        

# ai mode
def calculateAiMode(app):
    if app.aiShares > 0: app.aiHasPosition = True
    else: app.aiHasPosition = False
    endOfScreen = int(app.graphPeriod / 2)
    currentPrice = app.stock[endOfScreen + app.startIndex][0]
    app.currentAiPosition = currentPrice * app.aiShares
    app.aiAccountValue = app.aiCash + app.currentAiPosition
    app.aiProfitLoss = app.aiAccountValue - app.aiStartingAccountValue

def aiBuySellStock(app):
    endOfScreen = int(app.graphPeriod / 2)
    shares = 2000
    currentPrice = app.stock[endOfScreen + app.startIndex][0]
    currentIndex = endOfScreen + app.startIndex
    # sma cross
    sma1 = simpleMovingAverage(app.stock, 3)
    sma2 = simpleMovingAverage(app.stock, 8)
    mac = macd(app.stock)
    signal = macdSignalLine(mac)
    # continuously check 
    if sma2[currentIndex - 1] > sma1[currentIndex - 1]: 
        (wasDowntrend, wasUptrend) = (True, False)
    else: 
        (wasDowntrend, wasUptrend) = (False, True)
    if (sma1[currentIndex] > sma2[currentIndex]) and (mac[currentIndex] > signal[currentIndex]): 
        (isUptrend, isDowntrend) = (True, False)
    else: 
        (isUptrend, isDowntrend) = (False, True)
    # when to buy
    if wasDowntrend and isUptrend:
        app.aiShares += shares
        app.aiCash -= (currentPrice * shares)
    # when to sell
    if app.aiHasPosition and wasUptrend and isDowntrend:
        app.aiShares -= shares
        app.aiCash += (currentPrice * shares) 

def calculateAccountInfo(app):
    endOfScreen = int(app.graphPeriod / 2)
    currentPrice = app.stock[endOfScreen + app.startIndex][0]
    app.currentPosition = currentPrice * app.shares
    app.accountValue = app.cash + app.currentPosition
    app.profitLoss = app.accountValue - app.startingAccountValue
    
def buyStock(app):
    app.paused = True
    endOfScreen = int(app.graphPeriod / 2)
    currentPrice = app.stock[endOfScreen + app.startIndex][0]
    shares = 500
    app.shares += shares
    cashValue = app.cash - (currentPrice * shares)
    app.cash = cashValue
    app.paused = False

def sellStock(app):
    if app.shares > 0:
        app.paused = True
        endOfScreen = int(app.graphPeriod / 2)
        currentPrice = app.stock[endOfScreen + app.startIndex][0]
        shares = 500
        app.shares -= shares
        cashValue = app.cash + (currentPrice * shares)
        app.cash = cashValue
        app.paused = False

def drawingLines(app, x, y):
    (minX, minY) = (app.graphX0, app.graphY0)
    (maxX, maxY) = (app.width, app.indicatorLine)
    if (minX <= x <= maxX) and (minY <= y <= maxY):
        app.markedLines.append((x, y))
    elif clickedEraseLine(app, x, y):
        numPoints = len(app.markedLines)
        if numPoints > 1:
            if numPoints % 2 == 0:
                app.markedLines.pop()
                app.markedLines.pop()   
            else:
                # takes care of extra points not connected to lines
                app.markedLines.pop()
                app.markedLines.pop() 
                app.markedLines.pop()  

def clickedBuyStock(app, x, y):
    margin = 15
    centerY = app.graphY0 / 2
    buttonWidth = 110
    (buyX1, buyX2) = (app.graphX0, app.graphX0 + buttonWidth)
    (buyY1, buyY2) = (margin, app.graphY0 - margin)
    if (buyX1 <= x <= buyX2) and (buyY1 <= y <= buyY2):
        return True
    return False

def clickedSellStock(app, x, y):
    margin = 15
    centerY = app.graphY0 / 2
    buttonWidth = 110
    length = app.graphX0 + buttonWidth
    (sellX1, sellX2) = (length + margin, length + margin + buttonWidth)
    (sellY1, sellY2) = (margin, app.graphY0 - margin)
    if (sellX1 <= x <= sellX2) and (sellY1 <= y <= sellY2):
        return True
    return False

def clickedDrawLine(app, x, y):
    margin = 15
    centerY = app.graphY0 / 2
    buttonWidth = 110
    length = app.width / 2 + (buttonWidth * 4)+ (margin * 4)
    (dlX1, dlX2) = (length, app.width - margin)
    (dlY1, dlY2) = (margin, centerY - margin / 4)
    if (dlX1 <= x <= dlX2) and (dlY1 <= y <= dlY2):
        return True
    return False

def clickedEraseLine(app, x, y):
    margin = 15
    centerY = app.graphY0 / 2
    buttonWidth = 110
    length = app.width / 2 + (buttonWidth * 4)+ (margin * 4)
    (elX1, elX2) = (length, app.width - margin)
    (elY1, elY2) = (centerY + margin / 4,  app.graphY0 - margin)
    if (elX1 <= x <= elX2) and (elY1 <= y <= elY2):
        return True
    return False

def clickedAppleButton(app, x, y):
    betweenButtons = 20
    centerLine = app.width * 3/4
    startingY = app.height * 4/13
    (buttonWidth, buttonHeight) = (100, 60)
    (appleX1, appleX2) = (centerLine - buttonWidth / 2, centerLine + buttonWidth / 2)
    (appleY1, appleY2) = (startingY, startingY + buttonHeight)
    if (appleX1 <= x <= appleX2) and (appleY1 <= y <= appleY2):
        return True
    return False

def clickedDisneyButton(app, x, y):
    betweenButtons = 20
    centerLine = app.width * 3/4
    startingY = app.height * 4/13
    (buttonWidth, buttonHeight) = (100, 60)
    (compX1, compX2) = (centerLine - buttonWidth / 2, centerLine + buttonWidth / 2)
    (buttonWidth, buttonHeight) = (100, 60)
    (disneyX1, disneyX2) = (compX1 - betweenButtons - buttonWidth, compX1 - betweenButtons)
    (disneyY1, disneyY2) = (startingY, startingY + buttonHeight)
    if (disneyX1 <= x <= disneyX2) and (disneyY1 <= y <= disneyY2):
        return True
    return False

def clickedGEButton(app, x, y):
    betweenButtons = 20
    centerLine = app.width * 3/4
    startingY = app.height * 4/13
    (buttonWidth, buttonHeight) = (100, 60)
    (compX1, compX2) = (centerLine - buttonWidth / 2, centerLine + buttonWidth / 2)
    (buttonWidth, buttonHeight) = (100, 60)
    (geX1, geX2) = (compX2 + betweenButtons, compX2 + buttonWidth + betweenButtons)
    (geY1, geY2) = (startingY, startingY + buttonHeight)
    if (geX1 <= x <= geX2) and (geY1 <= y <= geY2):
        return True
    return False

def clicked2008Button(app, x, y):
    betweenButtons = 20
    centerLine = app.width * 3/4
    distanceBetween2 = 50
    (buttonWidth, buttonHeight) = (100, 60)
    startingY2 = app.height / 2 - betweenButtons 
    (yearX1, yearX2) = (centerLine - betweenButtons / 2, centerLine + betweenButtons / 2)
    (X1_2008, X2_2008) = (yearX1 - buttonWidth * 2 - betweenButtons, yearX1 - buttonWidth - betweenButtons)
    (Y1_2008, Y2_2008) = (startingY2 + distanceBetween2, startingY2 + distanceBetween2 + buttonHeight)    
    if (X1_2008 <= x <= X2_2008) and (Y1_2008 <= y <= Y2_2008):
        return True
    return False

def clicked2011Button(app, x, y):
    betweenButtons = 20
    centerLine = app.width * 3/4
    distanceBetween2 = 50
    (buttonWidth, buttonHeight) = (100, 60)
    startingY2 = app.height / 2 - betweenButtons 
    (yearX1, yearX2) = (centerLine - betweenButtons / 2, centerLine + betweenButtons / 2)
    (X1_2011, X2_2011) = (yearX1 - buttonWidth, yearX1)
    (Y1_2011, Y2_2011) = (startingY2 + distanceBetween2, startingY2 + distanceBetween2 + buttonHeight)    
    if (X1_2011 <= x <= X2_2011) and (Y1_2011 <= y <= Y2_2011):
        return True
    return False
    
def clicked2015Button(app, x, y):
    betweenButtons = 20
    centerLine = app.width * 3/4
    distanceBetween2 = 50
    (buttonWidth, buttonHeight) = (100, 60)
    startingY2 = app.height / 2 - betweenButtons 
    (yearX1, yearX2) = (centerLine - betweenButtons / 2, centerLine + betweenButtons / 2)
    (X1_2015, X2_2015) = (yearX2, yearX2 + buttonWidth)
    (Y1_2015, Y2_2015) = (startingY2 + distanceBetween2, startingY2 + distanceBetween2 + buttonHeight)    
    if (X1_2015 <= x <= X2_2015) and (Y1_2015 <= y <= Y2_2015):
        return True
    return False

def clicked2018Button(app, x, y):
    betweenButtons = 20
    centerLine = app.width * 3/4
    distanceBetween2 = 50
    (buttonWidth, buttonHeight) = (100, 60)
    startingY2 = app.height / 2 - betweenButtons 
    (yearX1, yearX2) = (centerLine - betweenButtons / 2, centerLine + betweenButtons / 2)
    (X1_2018, X2_2018) = (yearX2 + buttonWidth + betweenButtons, yearX2 + buttonWidth * 2 + betweenButtons)
    (Y1_2018, Y2_2018) = (startingY2 + distanceBetween2, startingY2 + distanceBetween2 + buttonHeight)    
    if (X1_2018 <= x <= X2_2018) and (Y1_2018 <= y <= Y2_2018):
        return True
    return False

def clickedStartButton(app, x, y):
    centerLine = app.width * 3/4
    startButtonWidth = 80
    offset = 80
    (startX1, startX2) = (centerLine - startButtonWidth - offset, centerLine + startButtonWidth - offset)
    (startY1, startY2) = (app.height * 5/6 - startButtonWidth, app.height * 5/6)
    if (startX1 <= x <= startX2) and (startY1 <= y <= startY2):
        return True
    return False

def clickedAiMode(app, x, y):
    centerLine = app.width * 3/4
    startButtonWidth = 80
    offset = 80
    (aiX1, aiX2) = (centerLine + offset / 2, centerLine + startButtonWidth + offset)
    (aiY1, aiY2) = (app.height * 5/6 - startButtonWidth, app.height * 5/6)
    if (aiX1 <= x <= aiX2) and (aiY1 <= y <= aiY2):
        return True
    return False    

def clickedZoomPlus(app, x, y):
    margin = 15
    centerY = app.graphY0 / 2
    smallButtonWidth = 50
    (zoomPlusX1, zoomPlusY1) = (app.width * 2/5, margin)
    (zoomPlusX2, zoomPlusY2) = (app.width * 2/5 + smallButtonWidth, centerY - margin / 4)
    # if zoom plus button is pressed
    if (zoomPlusX1 <= x <= zoomPlusX2) and (zoomPlusY1 <= y <= zoomPlusY2):
        if (app.minPeriod <= app.graphPeriod):
            return True
    return False

def clickedZoomMinus(app, x, y):
    margin = 15
    centerY = app.graphY0 / 2
    smallButtonWidth = 50
    (zoomMinusX1, zoomMinusY1) = (app.width * 2/5 + smallButtonWidth + margin / 2, margin)
    (zoomMinusX2, zoomMinusY2) = (zoomMinusX1 + margin / 2 + smallButtonWidth, centerY - margin / 4)
    if (zoomMinusX1 <= x <= zoomMinusX2) and (zoomMinusY1 <= y <= zoomMinusY2):
        if (app.graphPeriod <= app.maxPeriod):
            return True
    return False

def clickedSpeedPlus(app, x, y):
    margin = 15
    centerY = app.graphY0 / 2
    smallButtonWidth = 50
    (speedPlusX1, speedPlusY1) = (app.width * 2/5, centerY + margin / 4)
    (speedPlusX2, speedPlusY2) = (speedPlusX1 + smallButtonWidth, app.graphY0 - margin)
    if (speedPlusX1 <= x <= speedPlusX2) and (speedPlusY1 <= y <= speedPlusY2):
        if (app.maxSpeed <= app.timerDelay):
            return True
    return False

def clickedSpeedMinus(app, x, y):
    margin = 15
    centerY = app.graphY0 / 2
    smallButtonWidth = 50
    length = app.width * 2/5 + smallButtonWidth
    (speedMinusX1, speedMinusY1) = (length + margin / 2, centerY + margin / 4)
    (speedMinusX2, speedMinusY2) = (margin / 2 + smallButtonWidth + length, app.graphY0 - margin)
    if (speedMinusX1 <= x <= speedMinusX2) and (speedMinusY1 <= y <= speedMinusY2):
        if (app.timerDelay <= app.minSpeed):
            return True
    return False

def clickedSma1(app, x, y):
    margin = 15
    centerY = app.graphY0 / 2
    buttonWidth = 110
    (sma1X1, sma1X2) = (app.width / 2 , app.width / 2 + buttonWidth)
    (sma1Y1, sma1Y2) = (margin, app.graphY0 - margin)
    if (sma1X1 <= x <= sma1X2) and (sma1Y1 <= y <= sma1Y2):
        return True
    return False

def clickedSma2(app, x, y):
    margin = 15
    centerY = app.graphY0 / 2
    buttonWidth = 110
    length = app.width / 2 + buttonWidth
    (sma2X1, sma2X2) = (length + margin, length + margin + buttonWidth)
    (sma2Y1, sma2Y2) = (margin, app.graphY0 - margin)
    if (sma2X1 <= x <= sma2X2) and (sma2Y1 <= y <= sma2Y2):
        return True
    return False

def clickedEma1(app, x, y):
    margin = 15
    centerY = app.graphY0 / 2
    buttonWidth = 110
    length = (app.width / 2) + (2 * margin) + (2 * buttonWidth)
    (ema1X1, ema1X2) = (length, length + buttonWidth)
    (ema1Y1, ema1Y2) = (margin, app.graphY0 - margin)
    if (ema1X1 <= x <= ema1X2) and (ema1Y1 <= y <= ema1Y2):
        return True
    return False

def clickedEma2(app, x, y):
    margin = 15
    centerY = app.graphY0 / 2
    buttonWidth = 110
    length = (app.width / 2) + (2 * margin) + (3 * buttonWidth)
    (ema2X1, ema2X2) = (length + margin, length + margin + buttonWidth)
    (ema2Y1, ema2Y2) = (margin, app.graphY0 - margin)
    if (ema2X1 <= x <= ema2X2) and (ema2Y1 <= y <= ema2Y2):
        return True
    return False

def clickedMacd(app, x, y):
    margin = 15
    buttonHeight = 60
    (x0, x1) = (margin, app.graphX0 - margin)
    (macdY1, macdY2) = (app.indicatorLine, app.indicatorLine + buttonHeight)
    if (x0 <= x <= x1) and (macdY1 <= y <= macdY2):
        return True
    return False

def clickedRsi(app, x, y):
    margin = 15
    buttonHeight = 60
    (x0, x1) = (margin, app.graphX0 - margin)
    length = app.indicatorLine + buttonHeight
    (rsiY1, rsiY2) = (length + margin, length + margin + buttonHeight)
    if (x0 <= x <= x1) and (rsiY1 <= y <= rsiY2):
        return True
    return False  

def clickedGameInfo(app, x, y):
    buttonHeight = 60
    margin = 15
    length = app.indicatorLine + 2 * buttonHeight + margin
    (giX1, giX2) = (margin, app.graphX0 - margin)
    (giY1, giY2) = (length + margin, length + margin + buttonHeight)
    if (giX1 <= x <= giX2) and (giY1 <= y <= giY2):
        return True
    return False  

def clickedRestart(app, x, y):
    margin = buttonHeight = 40
    (buttonX1, buttonX2) = (app.width / 2 - 2 * margin, app.width / 2 + 2 * margin)
    (buttonY1, buttonY2) = (app.height * 3/4 + buttonHeight, app.height * 3/4 + 3 * buttonHeight)
    if (buttonX1 <= x <= buttonX2) and (buttonY1 <= y <= buttonY2):
        return True
    return False

# VIEW

def drawInterface(app, canvas):
    # create background color
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "#B5FFFE")
    # draw the two graph charts
    (x0, y0) = (app.graphX0, app.graphY0)
    (x1, y1) = (app.width, app.height)
    canvas.create_rectangle(x0, y0, x1, y1, width = app.lineWidth, fill = "white")
    canvas.create_line(x0, app.indicatorLine, x1, app.indicatorLine, width = app.lineWidth)
    # indicators
    if app.sma1On:
        drawSma(app, canvas, app.stock, 3, app.sma1Color)
    if app.sma2On:
        drawSma(app, canvas, app.stock, 8, app.sma2Color)
    if app.ema1On:
        drawEma(app, canvas, app.stock, 5, app.ema1Color)
    if app.ema2On:
        drawEma(app, canvas, app.stock, 9, app.ema2Color)
    # bottom chart
    if app.macdOn:
        drawMacdChart(app, canvas, app.stock)
    else:
        drawRsiChart(app, canvas, app.stock)
    # draw the buttons and text
    drawLeftSideButtons(app, canvas)
    drawTopSideButtons(app, canvas)

def drawMarkedLines(app, canvas):
    lines = app.markedLines
    numOfPoints = len(app.markedLines)
    for index in range(1, numOfPoints, 2):
        (x0, y0) = lines[index]
        (x1, y1) = lines[index - 1]
        canvas.create_line(x0, y0, x1, y1)
        
def drawTopSideButtons(app, canvas):
    margin = 15
    buttonWidth = 110
    centerY = app.graphY0 / 2
    (y0, y1) = (margin, app.graphY0 - margin)
    defaultColor = "white"
    # buy button
    (buyX1, buyX2) = (app.graphX0, app.graphX0 + buttonWidth)
    buyTextX = (buyX1 + buyX2) / 2
    canvas.create_rectangle(buyX1, y0, buyX2, y1, fill = "#90FF7C", width = app.lineWidth)
    canvas.create_text(buyTextX, centerY, text= "Buy", font= "Proxima 24 bold")
    # sell button
    (sellX1, sellX2) = (buyX2 + margin, buyX2 + margin + buttonWidth)
    sellTextX = (sellX1 + sellX2) / 2
    canvas.create_rectangle(sellX1, y0, sellX2, y1, fill = "#FF7C7C", width = app.lineWidth)
    canvas.create_text(sellTextX, centerY, text= "Sell", font= "Proxima 24 bold")
    # zoom buttons
    smallButtonWidth = 50
    zoomTextY = (y0 + centerY - margin / 4) // 2
    (zs1X1, zs1X2) = (app.width * 2/5, app.width * 2/5 + smallButtonWidth)
    (zs2X1, zs2X2) = (zs1X2 + margin / 2, zs1X2 + margin / 2 + smallButtonWidth)
    zsPlusX1 = (zs1X1 + zs1X2) / 2
    zsMinusX2 = (zs2X1 + zs2X2) / 2
    zsTextX = (sellX2 + zs1X1) / 2
    canvas.create_rectangle(zs1X1, y0, zs1X2, centerY - margin / 4, fill = app.whiteButton, 
                            width = app.lineWidth)
    canvas.create_text(zsTextX, zoomTextY, text= "Zoom:", font= "Proxima 22 bold")
    canvas.create_text(zsPlusX1, zoomTextY, text= "+", font= "Proxima 24 bold")
    canvas.create_rectangle(zs2X1, y0, zs2X2, centerY - margin / 4, fill = app.whiteButton, 
                            width = app.lineWidth)
    canvas.create_text(zsMinusX2, zoomTextY, text= "-", font= "Proxima 24 bold")
    # speed buttons
    speedTextY = (centerY + margin / 4 + y1) // 2
    canvas.create_rectangle(zs1X1, centerY + margin / 4, zs1X2, y1, fill = app.whiteButton, 
                            width = app.lineWidth)
    canvas.create_text(zsTextX, speedTextY, text= "Speed:", font= "Proxima 22 bold")
    canvas.create_text(zsPlusX1, speedTextY, text= "+", font= "Proxima 24 bold")
    canvas.create_rectangle(zs2X1, centerY + margin / 4, zs2X2, y1, fill = app.whiteButton, 
                            width = app.lineWidth)
    canvas.create_text(zsMinusX2, speedTextY, text= "-", font= "Proxima 24 bold")
    # sma1 button
    (sma1X1, sma1X2) = (app.width / 2 , app.width / 2 + buttonWidth)
    sma1TextX = (sma1X1 + sma1X2) / 2
    if app.sma1On: sma1Color = app.sma1Color 
    else: sma1Color = defaultColor
    canvas.create_rectangle(sma1X1, y0, sma1X2, y1, fill = sma1Color, width = app.lineWidth)
    canvas.create_text(sma1TextX, centerY, text= "SMA1", font= "Proxima 24 bold")
    # sma2 button
    (sma2X1, sma2X2) = (sma1X2 + margin, sma1X2 + margin + buttonWidth)
    sma2TextX = (sma2X1 + sma2X2) / 2
    if app.sma2On: sma2Color = app.sma2Color 
    else: sma2Color = defaultColor
    canvas.create_rectangle(sma2X1, y0, sma2X2, y1, fill = sma2Color, width = app.lineWidth)
    canvas.create_text(sma2TextX, centerY, text= "SMA2", font= "Proxima 24 bold")
    # ema1 button
    (ema1X1, ema1X2) = (sma2X2 + margin, sma2X2 + margin + buttonWidth)
    ema1TextX = (ema1X1 + ema1X2) / 2
    if app.ema1On: ema1Color = app.ema1Color 
    else: ema1Color = defaultColor
    canvas.create_rectangle(ema1X1, y0, ema1X2, y1, fill = ema1Color, width = app.lineWidth)
    canvas.create_text(ema1TextX, centerY, text= "EMA1", font= "Proxima 24 bold")
    # ema2 button
    (ema2X1, ema2X2) = (ema1X2 + margin, ema1X2 + margin + buttonWidth)
    ema2TextX = (ema2X1 + ema2X2) / 2
    if app.ema2On: ema2Color = app.ema2Color 
    else: ema2Color = defaultColor
    canvas.create_rectangle(ema2X1, y0, ema2X2, y1, fill = ema2Color, width = app.lineWidth)
    canvas.create_text(ema2TextX, centerY, text= "EMA2", font= "Proxima 24 bold")
    # draw line button
    (dlX1, dlX2) = (ema2X2 + margin, app.width - margin)
    lineTextX = (dlX1 + dlX2) / 2
    if app.paused: (drawColor, eraseColor) = (app.drawColor, app.eraseColor)
    else: drawColor = eraseColor = defaultColor
    canvas.create_rectangle(dlX1, y0, dlX2, centerY - margin / 4, fill = drawColor, width = app.lineWidth)
    canvas.create_rectangle(dlX1, centerY + margin / 4, dlX2, app.graphY0 - margin, 
                            fill = eraseColor, width = app.lineWidth)
    canvas.create_text(lineTextX, zoomTextY, text= "Draw Line", font= "Proxima 14 bold")
    canvas.create_text(lineTextX, speedTextY, text= "Erase Line", font= "Proxima 14 bold")

def drawLeftSideButtons(app, canvas):
    margin = 15
    defaultColor = "white"
    # logo
    canvas.create_image(75, 45, image = ImageTk.PhotoImage(app.scaledLogo))
    # account info box
    accountBoxHeight = 250
    (x0, x1) = (margin, app.graphX0 - margin)
    cx = (x0 + x1) // 2
    (accountY1, accountY2) = (app.graphY0, app.graphY0 + accountBoxHeight)
    canvas.create_rectangle(x0, accountY1, x1, accountY2, fill = app.whiteButton, width = app.lineWidth)
    (accTextY1, accTextY2) = (accountY1 + margin, accountY1 + margin * 2.3)
    canvas.create_text(cx, accTextY1, text= "Account", font= "Proxima 18 bold")
    canvas.create_text(cx, accTextY2, text= "Information", font= "Proxima 18 bold")
    canvas.create_line(x0 + margin, accTextY2 + margin, x1 - margin, accTextY2 + margin, width = 4)
    # ai versus mode button
    buttonHeight = 60
    (aiY1, aiY2) = (app.height / 2, app.height / 2 + buttonHeight)
    aiTextY = (aiY1 + aiY2) / 2
    if app.aiModeOn: aiModeColor = app.aiModeColor 
    else: aiModeColor = defaultColor
    canvas.create_rectangle(x0, aiY1, x1, aiY2, fill = aiModeColor, width = app.lineWidth)
    canvas.create_text(cx, aiTextY, text= "AI Mode", font= "Proxima 22 bold")
    # lower chart text
    lowChartTextY = app.indicatorLine - 2 * margin
    canvas.create_text(cx, lowChartTextY, text= "Lower Chart:", font= "Proxima 20 bold")
    # macd button
    if app.macdOn: macdColor = app.macdColor
    else: macdColor = defaultColor
    (macdY1, macdY2) = (app.indicatorLine, app.indicatorLine + buttonHeight)
    macdTextY = (macdY1 + macdY2) / 2
    canvas.create_rectangle(x0, macdY1, x1, macdY2, fill = macdColor, width = app.lineWidth)
    canvas.create_text(cx, macdTextY, text= "MACD", font= "Proxima 22 bold")
    # rsi button
    if app.rsiOn: rsiColor = app.rsiColor
    else: rsiColor = defaultColor
    (rsiY1, rsiY2) = (macdY2 + margin, macdY2 + margin + buttonHeight)
    rsiTextY = (rsiY1 + rsiY2) / 2
    canvas.create_rectangle(x0, rsiY1, x1, rsiY2, fill = rsiColor, width = app.lineWidth)
    canvas.create_text(cx, rsiTextY, text= "RSI", font= "Proxima 22 bold")
    # game info button
    (giY1, giY2) = (rsiY2 + margin, rsiY2 + margin + buttonHeight)
    giTextY = (giY1 + giY2) / 2
    canvas.create_rectangle(x0, giY1, x1, giY2, fill = "white", width = app.lineWidth)
    canvas.create_text(cx, giTextY - 10, text= "Game", font= "Proxima 19 bold")
    canvas.create_text(cx, giTextY + 10, text= "Information", font= "Proxima 19 bold")
    # finance info text
    startingDist = 30
    drawAccountInfoText(app, canvas, cx, accTextY2 + startingDist)
    
def drawAccountInfoText(app, canvas, xPosition, startingY):
    distanceBetween = 21
    # profit loss
    plText = "Profit/Loss:"
    canvas.create_text(xPosition, startingY, text= plText, font= "Proxima 14 bold")
    if app.profitLoss > 0: plColor = "dark green"
    elif app.profitLoss < 0: plColor = "red"
    else: plColor = "black"
    canvas.create_text(xPosition, startingY + distanceBetween, text = format(app.profitLoss, '.2f'), 
                       fill = plColor, font= "Proxima 16 bold")
    # cash
    cashText= "Cash:"
    canvas.create_text(xPosition, startingY + 2 * distanceBetween, text= cashText, font= "Proxima 14 bold")
    canvas.create_text(xPosition, startingY + 3 * distanceBetween, text= format(app.cash, '.2f'), 
                       font= "Proxima 16 bold")
    # position
    positionText = "Position($):"
    canvas.create_text(xPosition, startingY + 4 * distanceBetween, text= positionText, font= "Proxima 14 bold")
    canvas.create_text(xPosition, startingY + 5 * distanceBetween, text= format(app.currentPosition, '.2f'), 
                       font= "Proxima 16 bold")
    sharesText = f'Shares: {app.shares}'
    canvas.create_text(xPosition, startingY + 6 * distanceBetween, text= sharesText, font= "Proxima 14 bold")
    # account value
    accountValText = "Account Value:"
    canvas.create_text(xPosition, startingY + 7 * distanceBetween, text= accountValText, font= "Proxima 14 bold")
    canvas.create_text(xPosition, startingY + 8 * distanceBetween, text= format(app.accountValue, '.2f'), fill= plColor, 
                       font= "Proxima 16 bold")

def drawStockChart(app, canvas, stock):
    data = graphScaler(app, stock, app.graphY0, app.indicatorLine)
    for day in range(1, len(data)):
        currentDay = data[day]
        previousDay = data[day - 1]
        (cx, cy) = (currentDay[0], currentDay[1])
        (px, py) = (previousDay[0], previousDay[1])
        canvas.create_line(px, py, cx, cy, width = 2)
    """
    increment = 0
    for day in range(1, len(data), 2):
        #debug
        currentDay = data[day]
        previousDay = data[day - 1]
        (cx, cy) = (currentDay[0], currentDay[1])
        (px, py) = (previousDay[0], previousDay[1])
        canvas.create_text(cx,cy, text= f"{stock[app.start + increment][3]}")
        canvas.create_text(px,py, text= f"{stock[app.start + increment][0]}")
        increment += 1
    """

def drawMacdChart(app, canvas, stock):
    mac = macd(stock)
    data = indicatorScaler(app, mac, app.indicatorLine, app.height)
    for day in range(1, len(data)):
        currentDay = data[day]
        previousDay = data[day - 1]
        (cx, cy) = (currentDay[0], currentDay[1])
        (px, py) = (previousDay[0], previousDay[1])
        canvas.create_line(px, py, cx, cy, fill = app.macdColor, width = 2)
    signal = macdSignalLine(mac)
    data = indicatorScaler(app, signal, app.indicatorLine, app.height)
    for day in range(1, len(data)):
        currentDay = data[day]
        previousDay = data[day - 1]
        (cx, cy) = (currentDay[0], currentDay[1])
        (px, py) = (previousDay[0], previousDay[1])
        canvas.create_line(px, py, cx, cy, fill = app.macdSignalColor)

def drawRsiChart(app, canvas, stock):
    rsi = relativeStrengthIndex(stock)
    data = indicatorScaler(app, rsi, app.indicatorLine, app.height)
    for day in range(1, len(data)):
        currentDay = data[day]
        previousDay = data[day - 1]
        (cx, cy) = (currentDay[0], currentDay[1])
        (px, py) = (previousDay[0], previousDay[1])
        canvas.create_line(px, py, cx, cy, fill = app.rsiColor, width = 2)
    # draw the 20 and 80 value lines
    distance = (app.height - app.indicatorLine) * 0.2
    (x0, x1) = (app.graphX0, app.width)
    (y0, y1) = (app.indicatorLine + distance, app.height - distance)
    canvas.create_line(x0, y0, x1, y0, width = 1, fill = app.macdSignalColor)
    canvas.create_line(x0, y1, x1, y1, width = 1, fill = app.macdSignalColor)

def drawSma(app, canvas, stock, period, color):
    sma = simpleMovingAverage(stock, period)
    data = indicatorScaler(app, sma, app.graphY0, app.indicatorLine)
    for day in range(1, len(data)):
        currentDay = data[day]
        previousDay = data[day - 1]
        (cx, cy) = (currentDay[0], currentDay[1])
        (px, py) = (previousDay[0], previousDay[1])
        canvas.create_line(px, py, cx, cy, fill= color)

def drawEma(app, canvas, stock, period, color):
    sma = exponentialMovingAverage(stock, period)
    data = indicatorScaler(app, sma, app.graphY0, app.indicatorLine)
    for day in range(1, len(data)):
        currentDay = data[day]
        previousDay = data[day - 1]
        (cx, cy) = (currentDay[0], currentDay[1])
        (px, py) = (previousDay[0], previousDay[1])
        canvas.create_line(px, py, cx, cy, fill= color)

def drawStartingScreen(app, canvas):
    # background
    canvas.create_rectangle(0, 0, app.width, app.height, fill= "#8DFFBD")
    # game info box
    margin = 40
    (infoX1, infoX2) = (app.width / 8, app.width / 2)
    (infoY1, infoY2) = (app.height * 1/6, app.height * 5/6)
    canvas.create_rectangle(infoX1, infoY1, infoX2, infoY2, fill = "white",
                            width = app.lineWidth)
    infoTextX = (infoX1 + infoX2) / 2
    canvas.create_text(infoTextX, app.height * 1/6 + margin, text = "GAME INFORMATION",
                       font = "Proxima 32 bold")
    gameDescription = """
      Hello and welcome to Intellitrade, the 
      ultimate stock trading game. The goal 
   of the game is simple, make as much money 
    as possible. Choose the stock and year of 
     which you would like to trade, and click 
    start! In the game, you will see the price 
      action of the stock over time, with the 
    choice of a variety of different indicators. 
    You can speed it up, slow it down, zoom in 
     and out, and mark up the charts while the 
      game is paused. To learn more about the 
    indicators and modes of the game, click the 
      Game Info button when you start playing. 
    """
    canvas.create_text(infoTextX, app.height / 2, text = gameDescription, font = "Proxima 21")
    canvas.create_text(infoTextX, infoY2 - margin, text = "GOOD LUCK", font = "Proxima 26 bold")
    # choose stock text
    centerLine = app.width * 3/4
    (buttonWidth, buttonHeight) = (100, 60)
    distanceBetween = 60
    betweenButtons = 20
    canvas.create_text(centerLine, infoY1, text = "CHOOSE YOUR STOCK!", anchor = "n",
                       font = "Proxima 30 bold")
    canvas.create_text(centerLine, infoY1 + distanceBetween, text = "Company:", font = "Proxima 24")
    # company buttons
    (color, defaultColor) = ("green", "white")
    startingY = app.height * 4/13
    compTextY = (startingY + startingY + buttonHeight) / 2
    (compX1, compX2) = (centerLine - buttonWidth / 2, centerLine + buttonWidth / 2)
    # apple
    if app.stockCompany == app.apple: appleColor = color
    else: appleColor = defaultColor
    appleX = (compX1 + compX2) / 2
    canvas.create_rectangle(compX1, startingY, compX2, startingY + buttonHeight, 
                            fill = appleColor, width = app.lineWidth)
    canvas.create_text(appleX, compTextY, text = "Apple", font = "Proxima 22")
    # disney
    if app.stockCompany == app.disney: disColor = color
    else: disColor = defaultColor
    disneyX = (compX1 - betweenButtons - buttonWidth + compX1 - betweenButtons) / 2
    canvas.create_rectangle(compX1 - betweenButtons - buttonWidth, startingY, compX1 - betweenButtons,
                            startingY + buttonHeight, fill = disColor, width = app.lineWidth)
    canvas.create_text(disneyX, compTextY, text = "Disney", font = "Proxima 22")
    # general electric
    if app.stockCompany == app.generalElectric: geColor = color
    else: geColor = defaultColor
    geX = (compX2 + betweenButtons + compX2 + buttonWidth + betweenButtons) / 2
    canvas.create_rectangle(compX2 + betweenButtons, startingY, compX2 + buttonWidth + betweenButtons,
                            startingY + buttonHeight, fill = geColor, width = app.lineWidth)
    canvas.create_text(geX, compTextY, text = "GE", font = "Proxima 22")
    # year buttons
    distanceBetween2 = 50
    startingY2 = app.height / 2 - betweenButtons 
    canvas.create_text(centerLine, startingY2, text = "Trading Year:", font = "Proxima 24")
    (yearX1, yearX2) = (centerLine - betweenButtons / 2, centerLine + betweenButtons / 2)
    yearTextY = (startingY2 + distanceBetween2 + startingY2 + distanceBetween2 + buttonHeight) / 2
    # 2011
    if app.index == 1: year2Color = color
    else: year2Color = defaultColor
    text2011X = (yearX1 - buttonWidth + yearX1) / 2
    canvas.create_rectangle(yearX1 - buttonWidth, startingY2 + distanceBetween2, yearX1, 
                            startingY2 + distanceBetween2 + buttonHeight, fill = year2Color, width = app.lineWidth)
    canvas.create_text(text2011X, yearTextY, text = "2011", font = "Proxima 22")
    # 2015
    if app.index == 2: year3Color = color
    else: year3Color = defaultColor
    text2015X = (yearX2 + yearX2 + buttonWidth) / 2
    canvas.create_rectangle(yearX2, startingY2 + distanceBetween2, yearX2 + buttonWidth, 
                            startingY2 + distanceBetween2 + buttonHeight, fill = year3Color, width = app.lineWidth)
    canvas.create_text(text2015X, yearTextY, text = "2015", font = "Proxima 22")
    # 2008
    if app.index == 0: year1Color = color
    else: year1Color = defaultColor
    text2008X = (yearX1 - buttonWidth * 2 - betweenButtons + yearX1 - buttonWidth - betweenButtons) / 2
    canvas.create_rectangle(yearX1 - buttonWidth * 2 - betweenButtons, startingY2 + distanceBetween2, 
                            yearX1 - buttonWidth - betweenButtons, startingY2 + distanceBetween2 + buttonHeight, 
                            fill = year1Color, width = app.lineWidth)
    canvas.create_text(text2008X, yearTextY, text = "2008", font = "Proxima 22")
    # 2018
    if app.index == 3: year4Color = color
    else: year4Color = defaultColor
    text2018X = (yearX2 + buttonWidth + betweenButtons + yearX2 + buttonWidth * 2 + betweenButtons) / 2
    canvas.create_rectangle(yearX2 + buttonWidth + betweenButtons, startingY2 + distanceBetween2, 
                            yearX2 + buttonWidth * 2 + betweenButtons, startingY2 + distanceBetween2 + buttonHeight, 
                            fill = year4Color, width = app.lineWidth)
    canvas.create_text(text2018X, yearTextY, text = "2018", font = "Proxima 22")
    # start button
    startButtonWidth = 80
    offset = 80
    (startX1, startX2) = (centerLine - startButtonWidth - offset, centerLine + startButtonWidth - offset)
    canvas.create_rectangle(startX1, infoY2 - startButtonWidth, startX2, infoY2, fill = "white", 
                            width = app.lineWidth)
    startTextY = (infoY2 + infoY2 - startButtonWidth) / 2
    canvas.create_text(centerLine - offset, startTextY, text = "START!", font = "Proxima 32 bold")
    # ai mode
    if app.aiModeOn: aiColor = app.aiModeColor
    else: aiColor = app.whiteButton
    (aiX1, aiX2) = (centerLine + offset / 2, centerLine + startButtonWidth + offset)
    canvas.create_rectangle(aiX1, infoY2 - startButtonWidth, aiX2, infoY2, fill = aiColor, 
                            width = app.lineWidth)
    aiTextX = (aiX1 + aiX2) / 2
    canvas.create_text(aiTextX, startTextY, text = "AI MODE", font = "Proxima 24 bold") 
    # logo
    canvas.create_image(app.width - 70, 40, image = ImageTk.PhotoImage(app.scaledLogo))

def drawGameInfoScreen(app, canvas):
    if app.paused and app.gameInfoScreen:
        canvas.create_image(app.width / 2, app.height / 2, image = ImageTk.PhotoImage(app.scaledGameInfo))

def drawGameOverScreen(app, canvas):
    if app.gameover:
        if app.profitLoss > 0: 
            color = "dark green"
            summaryText = f"You profited a total of ${format(app.profitLoss, '.2f')}... Nice!"
        elif app.profitLoss == 0: 
            color = "black"
            summaryText = f"You broke even... not bad!"
        else: 
            color = "red"
            summaryText = f"You lost a total of ${format(app.profitLoss, '.2f')}... Oh no!"
        margin = 40
        (cx, cy) = (app.width // 2, app.height // 2)
        canvas.create_rectangle(0, 0, app.width, app.height, fill = "purple")
        canvas.create_text(cx, app.height * 1/6 - margin, text = "GAME OVER!", fill = "white",
                           font = "Proxima 54 bold")
        canvas.create_line(app.width * 1/3, app.height * 1/6, app.width * 2/3, app.height * 1/6, width = 10)
        startingY = app.height * 1/4
        canvas.create_rectangle(app.width * 1/4, startingY, app.width * 3/4, 
                                startingY * 3, fill = "white", width = app.lineWidth)
        canvas.create_text(cx, startingY + margin, text = "GAME SUMMARY", font = "Proxima 32 bold")
        # account value
        canvas.create_text(cx, startingY + 2 * margin, text = f"Final Account Value: {format(app.accountValue, '.2f')}",
                           font = "Proxima 28", fill = color)
        # remaining cash
        canvas.create_text(cx, startingY + 3 * margin, text = f"Remaining Cash: {format(app.cash, '.2f')}",
                           font = "Proxima 28")        
        # profit loss
        canvas.create_text(cx, startingY + 4 * margin, text = f"Profit/Loss: {format(app.profitLoss, '.2f')}",
                           font = "Proxima 28", fill = color)       
        canvas.create_line(cx - 2 * margin, app.height / 2 + margin / 4, cx + 2 * margin, 
                           app.height / 2 + margin / 4, width = 4)
        # ai score
        if app.aiModeOn == True: aiText = f"AI Profit/Loss: {format(app.aiProfitLoss, '.2f')}"
        else: aiText = "AI Profit/Loss: NA"
        canvas.create_text(cx, startingY + 6 * margin, text = aiText, font = "Proxima 26")
        # summary text
        canvas.create_text(cx, startingY * 3 - margin * 1.5, text = summaryText, font = "Proxima 27 bold",
                           fill = color)
        # restart button
        buttonHeight = 40
        (buttonX1, buttonX2) = (app.width / 2 - 2 * margin, app.width / 2 + 2 * margin)
        (buttonY1, buttonY2) = (app.height * 3/4 + buttonHeight, app.height * 3/4 + 3 * buttonHeight)
        canvas.create_rectangle(buttonX1, buttonY1, buttonX2, buttonY2, fill = "white", width = 5)
        textY = (app.height * 3/4 + buttonHeight + app.height * 3/4 + 3 * buttonHeight) / 2
        canvas.create_text(cx, textY, text = "RESTART", font = "Proxima 28 bold")

def redrawAll(app, canvas):
    if app.startingScreen:
        drawStartingScreen(app, canvas)
    else:
        drawInterface(app, canvas)
        drawStockChart(app, canvas, app.stock)
        drawGameInfoScreen(app, canvas)
        drawMarkedLines(app, canvas)
        drawGameOverScreen(app, canvas)

# MAIN

def runStockGame():
    width = 1200
    height = 700
    runApp(width = width, height = height)

runStockGame()
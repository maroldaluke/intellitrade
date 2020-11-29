# lmarolda - term project
# stock trader v0
# intellitrade

import math, copy, random
from cmu_112_graphics import *
from stockData import *

def appStarted(app):
    app.stocks = [  aapl_2008, aapl_2011, aapl_2015, aapl_2018,
                        ge_2008, ge_2011, ge_2015, ge_2018,
                      dis_2008, dis_2011, dis_2015, dis_2018  ]
    
    (app.graphX0, app.graphY0) = (app.width / 8, app.height / 8)
    app.indicatorLine = app.height * 2/3
    app.paused = False
    app.gameover = False
    app.graphPeriod = 50
    app.startIndex = 0
    app.timerDelay = 400
    # all stocks are same length lists
    app.stockLength = len(app.stocks[0])

def gameOver(app):
    if (app.stockLength <= app.graphPeriod + app.startIndex):
        app.gameover = True

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

aapl_sma = simpleMovingAverage(aapl_2008, 10)

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

# (not fully working RSI yet, but very close)
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
            dayGain = (dayClose - dayOpen) / dayOpen
            initialTotalGain += dayGain
        else:
            dayLoss = (dayOpen - dayClose) / dayOpen
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
            (prevDay[0], prevDay[3]) = (dayOpen, dayClose)
            if dayOpen < dayClose:
                dayGain = ((dayClose - dayOpen) / dayOpen) * 100
                prevTotalGain += dayGain
            else:
                dayLoss = ((dayOpen - dayClose) / dayOpen) * 100
                prevTotalLoss += dayLoss
        prevAverageGain = prevTotalGain / period
        prevAverageLoss = prevTotalLoss / period
        # problem is right here
        denom = (prevAverageGain*13 + currentGain) / (prevAverageLoss*13 + currentLoss)
        rsiStepTwo = 100 - (100 / (1 + denom))
        rsi.append(rsiStepTwo)
    return rsi

def timerFired(app):
    gameOver(app)
    if app.paused == False and app.gameover == False:
        app.startIndex += 1

def keyPressed(app, event):
    if event.key == "p":
        app.paused = not app.paused

def drawInterface(app, canvas):
    (x0, y0) = (app.graphX0, app.graphY0)
    (x1, y1) = (app.width, app.height)
    lineWidth = 5
    canvas.create_rectangle(x0, y0, x1, y1, width = lineWidth)
    canvas.create_line(x0, app.indicatorLine, x1, app.indicatorLine, width = lineWidth)

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

def drawStockChart(app, canvas, stock):
    data = graphScaler(app, stock, app.graphY0, app.indicatorLine)
    for day in range(1, len(data)):
        currentDay = data[day]
        previousDay = data[day - 1]
        (cx, cy) = (currentDay[0], currentDay[1])
        (px, py) = (previousDay[0], previousDay[1])
        canvas.create_line(px, py, cx, cy, width = 2)

def drawIndicatorChart(app, canvas, stock):
    mac = macd(stock)
    data = indicatorScaler(app, mac, app.indicatorLine, app.height)
    for day in range(1, len(data)):
        currentDay = data[day]
        previousDay = data[day - 1]
        (cx, cy) = (currentDay[0], currentDay[1])
        (px, py) = (previousDay[0], previousDay[1])
        canvas.create_line(px, py, cx, cy, fill = "purple", width = 2)
    signal = macdSignalLine(mac)
    data = indicatorScaler(app, signal, app.indicatorLine, app.height)
    for day in range(1, len(data)):
        currentDay = data[day]
        previousDay = data[day - 1]
        (cx, cy) = (currentDay[0], currentDay[1])
        (px, py) = (previousDay[0], previousDay[1])
        canvas.create_line(px, py, cx, cy, fill = "cyan")

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

def drawGameOverScreen(app, canvas):
    if app.gameover:
        (cx, cy) = (app.width // 2, app.height // 2)
        canvas.create_rectangle(0, 0, app.width, app.height, fill = "red")
        canvas.create_text(cx, cy, text = "Game Over!", fill = "black",
                           font = "Times 28 bold")

def redrawAll(app, canvas):
    drawInterface(app, canvas)
    drawStockChart(app, canvas, aapl_2008)
    drawIndicatorChart(app, canvas, aapl_2008)
    drawSma(app, canvas, aapl_2008, 3, "red")
    drawSma(app, canvas, aapl_2008, 8, "blue")
    drawEma(app, canvas, aapl_2008, 5, "green")
    drawGameOverScreen(app, canvas)

def runStockGame():
    width = 1200
    height = 700
    runApp(width = width, height = height)

runStockGame()

            

    
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
    app.lineWidth = 5
    app.paused = False
    app.gameover = False
    # zoom in and out
    app.graphPeriod = 60
    (app.minPeriod, app.maxPeriod) = (30, 100)
    app.startIndex = 0
    # speed of the price action
    app.timerDelay = 600
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

def mousePressed(app, event):
    (x, y) = (event.x, event.y)
    if app.gameover == False:
        if clickedZoomPlus(app, x, y):
            if (app.minPeriod <= app.graphPeriod):
                app.graphPeriod -= 5
        elif clickedZoomMinus(app, x, y):
            if (app.graphPeriod <= app.maxPeriod):
                app.graphPeriod += 5

def clickedZoomPlus(app, x, y):
    margin = 15
    centerY = app.graphY0 / 2
    smallButtonWidth = 50
    (zoomPlusX1, zoomPlusY1) = (app.width * 2/5, margin)
    (zoomPlusX2, zoomPlusY2) = (app.width * 2/5 + smallButtonWidth, centerY - margin / 4)
    # if zoom plus button is pressed
    if (zoomPlusX1 <= x <= zoomPlusX2) and (zoomPlusY1 <= y <= zoomPlusY2):
        return True
    return False

def clickedZoomMinus(app, x, y):
    margin = 15
    centerY = app.graphY0 / 2
    smallButtonWidth = 50
    (zoomMinusX1, zoomMinusY1) = (app.width * 2/5 + smallButtonWidth + margin / 2, margin)
    (zoomMinusX2, zoomMinusY2) = (zoomMinusX1 + margin / 2 + smallButtonWidth, centerY - margin / 4)
    if (zoomMinusX1 <= x <= zoomMinusX2) and (zoomMinusY1 <= y <= zoomMinusY2):
        return True
    return False

def drawInterface(app, canvas):
    # create background color
    canvas.create_rectangle(0, 0, app.width, app.height, fill = "#B5FFFE")
    # draw the two graph charts
    (x0, y0) = (app.graphX0, app.graphY0)
    (x1, y1) = (app.width, app.height)
    canvas.create_rectangle(x0, y0, x1, y1, width = app.lineWidth, fill = "white")
    canvas.create_line(x0, app.indicatorLine, x1, app.indicatorLine, width = app.lineWidth)
    # draw the buttons and text
    drawLeftSideButtons(app, canvas)
    drawTopSideButtons(app, canvas)

def drawTopSideButtons(app, canvas):
    margin = 15
    buttonWidth = 110
    centerY = app.graphY0 / 2
    (y0, y1) = (margin, app.graphY0 - margin)
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
    canvas.create_rectangle(zs1X1, y0, zs1X2, centerY - margin / 4, fill = "white", 
                            width = app.lineWidth)
    canvas.create_text(zsTextX, zoomTextY, text= "Zoom:", font= "Proxima 22 bold")
    canvas.create_text(zsPlusX1, zoomTextY, text= "+", font= "Proxima 24 bold")
    canvas.create_rectangle(zs2X1, y0, zs2X2, centerY - margin / 4, fill = "white", 
                            width = app.lineWidth)
    canvas.create_text(zsMinusX2, zoomTextY, text= "-", font= "Proxima 24 bold")
    # speed buttons
    speedTextY = (centerY + margin / 4 + y1) // 2
    canvas.create_rectangle(zs1X1, centerY + margin / 4, zs1X2, y1, fill = "white", 
                            width = app.lineWidth)
    canvas.create_text(zsTextX, speedTextY, text= "Speed:", font= "Proxima 22 bold")
    canvas.create_text(zsPlusX1, speedTextY, text= "+", font= "Proxima 24 bold")
    canvas.create_rectangle(zs2X1, centerY + margin / 4, zs2X2, y1, fill = "white", 
                            width = app.lineWidth)
    canvas.create_text(zsMinusX2, speedTextY, text= "-", font= "Proxima 24 bold")
    # sma1 button
    (sma1X1, sma1X2) = (app.width / 2 , app.width / 2 + buttonWidth)
    sma1TextX = (sma1X1 + sma1X2) / 2
    canvas.create_rectangle(sma1X1, y0, sma1X2, y1, fill = "white", width = app.lineWidth)
    canvas.create_text(sma1TextX, centerY, text= "SMA1", font= "Proxima 24 bold")
    # sma2 button
    (sma2X1, sma2X2) = (sma1X2 + margin, sma1X2 + margin + buttonWidth)
    sma2TextX = (sma2X1 + sma2X2) / 2
    canvas.create_rectangle(sma2X1, y0, sma2X2, y1, fill = "white", width = app.lineWidth)
    canvas.create_text(sma2TextX, centerY, text= "SMA2", font= "Proxima 24 bold")
    # ema1 button
    (ema1X1, ema1X2) = (sma2X2 + margin, sma2X2 + margin + buttonWidth)
    ema1TextX = (ema1X1 + ema1X2) / 2
    canvas.create_rectangle(ema1X1, y0, ema1X2, y1, fill = "white", width = app.lineWidth)
    canvas.create_text(ema1TextX, centerY, text= "EMA1", font= "Proxima 24 bold")
    # ema2 button
    (ema2X1, ema2X2) = (ema1X2 + margin, ema1X2 + margin + buttonWidth)
    ema2TextX = (ema2X1 + ema2X2) / 2
    canvas.create_rectangle(ema2X1, y0, ema2X2, y1, fill = "white", width = app.lineWidth)
    canvas.create_text(ema2TextX, centerY, text= "EMA2", font= "Proxima 24 bold")
    # draw line button
    (dlX1, dlX2) = (ema2X2 + margin, app.width - margin)
    lineTextX = (dlX1 + dlX2) / 2
    canvas.create_rectangle(dlX1, y0, dlX2, centerY - margin / 4, fill = "white", width = app.lineWidth)
    canvas.create_rectangle(dlX1, centerY + margin / 4, dlX2, app.graphY0 - margin, 
                            fill = "white", width = app.lineWidth)
    canvas.create_text(lineTextX, zoomTextY, text= "Draw Line", font= "Proxima 14 bold")
    canvas.create_text(lineTextX, speedTextY, text= "Erase Line", font= "Proxima 14 bold")

def drawLeftSideButtons(app, canvas):
    margin = 15
    # account info box
    accountBoxHeight = 250
    (x0, x1) = (margin, app.graphX0 - margin)
    cx = (x0 + x1) // 2
    (accountY1, accountY2) = (app.graphY0, app.graphY0 + accountBoxHeight)
    canvas.create_rectangle(x0, accountY1, x1, accountY2, fill = "white", width = app.lineWidth)
    (accTextY1, accTextY2) = (accountY1 + margin, accountY1 + margin * 2.3)
    canvas.create_text(cx, accTextY1, text= "Account", font= "Proxima 18 bold")
    canvas.create_text(cx, accTextY2, text= "Information", font= "Proxima 18 bold")
    canvas.create_line(x0 + margin, accTextY2 + margin, x1 - margin, accTextY2 + margin, width = 4)
    # ai versus mode button
    buttonHeight = 60
    (aiY1, aiY2) = (app.height / 2, app.height / 2 + buttonHeight)
    aiTextY = (aiY1 + aiY2) / 2
    canvas.create_rectangle(x0, aiY1, x1, aiY2, fill = "white", width = app.lineWidth)
    canvas.create_text(cx, aiTextY, text= "AI Mode", font= "Proxima 22 bold")
    # lower chart text
    lowChartTextY = app.indicatorLine - 2 * margin
    canvas.create_text(cx, lowChartTextY, text= "Lower Chart:", font= "Proxima 20 bold")
    # macd button
    (macdY1, macdY2) = (app.indicatorLine, app.indicatorLine + buttonHeight)
    macdTextY = (macdY1 + macdY2) / 2
    canvas.create_rectangle(x0, macdY1, x1, macdY2, fill = "white", width = app.lineWidth)
    canvas.create_text(cx, macdTextY, text= "MACD", font= "Proxima 22 bold")
    # rsi button
    (rsiY1, rsiY2) = (macdY2 + margin, macdY2 + margin + buttonHeight)
    rsiTextY = (rsiY1 + rsiY2) / 2
    canvas.create_rectangle(x0, rsiY1, x1, rsiY2, fill = "white", width = app.lineWidth)
    canvas.create_text(cx, rsiTextY, text= "RSI", font= "Proxima 22 bold")
    # game info button
    (giY1, giY2) = (rsiY2 + margin, rsiY2 + margin + buttonHeight)
    giTextY = (giY1 + giY2) / 2
    canvas.create_rectangle(x0, giY1, x1, giY2, fill = "white", width = app.lineWidth)
    canvas.create_text(cx, giTextY - 10, text= "Game", font= "Proxima 19 bold")
    canvas.create_text(cx, giTextY + 10, text= "Information", font= "Proxima 19 bold")
    
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

            

    
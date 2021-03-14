# Currency Name => Asset
# Purchase Date => Timestamp of row with transactionType === Buy || null
# Cost Basis    => USD Spot Price at Transaction
# Date Sold     => Timestamp of row when transactionType === Sell || null
# Proceeds      => USD Total (inclusive of fees)
# Timestamp	| Transaction Type	| Asset	| Quantity Transacted | USD Spot Price at Transaction | USD Subtotal |	USD Total (inclusive of fees) |	USD Fees |	Notes
import csv
import tkinter as tk
from tkinter import filedialog as fd
from datetime import datetime
import tkinter.messagebox
import glob
import os
import webbrowser
import operator
import uuid
from dateutil import relativedelta

def getCurrentRowAsDict(row):
    # Skip if its not a Buy or Sell transaction or if this is the header row
    if row[1] not in ['Buy', 'Sell'] or row[0] == 'Timestamp':
        return None
    return {
        'id': str(uuid.uuid4()),
        'Timestamp': row[0],
        'Transaction Type': row[1],
        'Asset': row[2],
        'Quantity Transacted': float(row[3]),
        'USD Spot Price at Transaction': float(row[4]),
        'USD Subtotal': float(row[5]),
        'USD Total (inclusive of fees)': float(row[6]),
        'USD Fees': float(row[7]),
        'Notes': row[8]
    }


def createNewRow(assetAmount, asset, receivedDate, dateSold, proceeds, costBasis, gain, shortTermOrLongTerm):
    updatedRow = {
        'Asset Amount': assetAmount,
        'Asset Name': asset,
        'Received Date': receivedDate,
        'Date Sold': dateSold,
        'Proceeds (USD)': proceeds,    
        'Cost Basis (USD)': costBasis,
        'Gain (USD)': gain,
        'Type': shortTermOrLongTerm
    }
    return updatedRow

def groupCryptoAssets(sourcefile):
    groupedCryptoAssets = {}
    with open(sourcefile, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            currentRow = getCurrentRowAsDict(row)
            if currentRow is None:
                continue
            if currentRow['Asset'] not in groupedCryptoAssets.keys():
                groupedCryptoAssets[currentRow['Asset']] = []

            groupedCryptoAssets[currentRow['Asset']].append(currentRow)
    return groupedCryptoAssets

def getMDYTimestamp(timestamp):
    return datetime.fromisoformat(timestamp[:-1]).strftime('%m/%d/%Y')

def groupTransactions(transactions):
    # group by transaction type (buy or sell)
    buys = []
    sells = []
    for transaction in transactions:
        if  transaction['Transaction Type'] in ['Buy', 'Receive']:
            buys.append(transaction)
        elif transaction['Transaction Type'] == 'Sell':
            sells.append(transaction)
    
    # Sort the buy and sells so we can traverse in order descending
    sells.sort(key = lambda x: datetime.fromisoformat(x['Timestamp'][:-1]).strftime('%Y-%m-%d %H:%M:%S'))
    buys.sort(key = lambda x: datetime.fromisoformat(x['Timestamp'][:-1]).strftime('%Y-%m-%d %H:%M:%S'))
    return buys, sells

def isShortTermOrLongTerm(receivedDate, dateSold):
    m1, d1, y1 = [int(value) for value in receivedDate.split('/')]
    m2, d2, y2 = [int(value) for value in dateSold.split('/')]
    print(relativedelta.relativedelta(datetime(y2, m2, d2), datetime(y1, m1, d1)).years)
    if relativedelta.relativedelta(datetime(y2, m2, d2), datetime(y1, m1, d1)).years < 1:
        return 'Short Term'
    return 'Long Term'

def processAsset(asset):
    # For each asset (BTC, LTC etc.)
    ignoreList = []
    rowsForAsset = []
    buys, sells = groupTransactions(asset)

    # If there were no sells then we can skip this asset
    if len(sells) == 0:
        return

    # Find the earliest sell in sells and start iterating from there
    for sell in sells:
        dateSold = getMDYTimestamp(sell['Timestamp'])

        # We dont care about 2021 sales
        yearSold = int(dateSold.split('/')[2])
        if yearSold > 2020 or yearSold < 2017:
            continue
        applicableBuys = [buy for buy in buys if getMDYTimestamp(buy['Timestamp']) < dateSold]
        sellValue = sell["USD Total (inclusive of fees)"]
        receivedDate = getMDYTimestamp(applicableBuys[0]['Timestamp'])

        # print('\nSell Date:\t\t', dateSold)
        # print('Applicable Buys:\t', [ getMDYTimestamp(buy['Timestamp']) for buy in applicableBuys ])
        
        for i in range(0, len(applicableBuys)-1):
            buy = applicableBuys[i]
            if buy['id'] in ignoreList:
                continue
            purchaseValue = buy["USD Spot Price at Transaction"]
            sellValue = sellValue - purchaseValue

            # If this is true then we would then create a new row for the csv
            if sellValue < 0:
                buy["USD Spot Price at Transaction"] = purchaseValue + sellValue
                # Asset Amount	Asset Name	Received Date	Date Sold	Proceeds (USD)	Cost Basis (USD)	Gain (USD)	Type
                costBasis = sell["USD Total (inclusive of fees)"]
                proceeds = None # ??? which field is this
                gain = None     # ??? which field is this
                assetAmount = sell['Quantity Transacted']
                assetName = sell['Asset']
                rowsForAsset.append(createNewRow(assetAmount, assetName, receivedDate, dateSold, proceeds, costBasis, gain, isShortTermOrLongTerm(receivedDate, dateSold)))
                break
            else:
                # We remove any "used up" buys from the buy list
                ignoreList.append(buy['id'])
                # print(ignoreList)
                # buys[:] = [d for d in buys if d['id'] != buy['id']]
                # print(len([buy['Timestamp'] for buy in buys]))
    return rowsForAsset
        # Here for each buy in applicableBuys, we take the "USD Total (inclusive of fees)" from the sell and continually subtract each subsequent buys "USD Spot Price at Transaction" value
        # print(applicableBuys)

def convertToNewFormat(sourcefile):
    newRows = []
    groupedAssets = groupCryptoAssets(sourcefile)
    for asset in groupedAssets:
        rowsForAsset = processAsset(groupedAssets[asset])
        if rowsForAsset:
            newRows = newRows + rowsForAsset
    return newRows


def saveToNewFormat(newRows):
    csv_columns = newRows[0].keys()
    today = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    csv_file = "coinbase_converted_{}.csv".format(today)
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in newRows:
                writer.writerow(data)
        return csv_file
    except IOError as e:
        print("I/O error", e)

def selectCSV():
    name = fd.askopenfilename()
    if '.csv' not in name:
        tkinter.messagebox.showinfo(
            'ERROR', 'ERROR: File must be of .csv format')
        raise Exception("Must be a csv file")
    newRows = convertToNewFormat(name)
    newFilename = saveToNewFormat(newRows)
    tkinter.messagebox.showinfo('Success', f'Success! File was saved to {newFilename}')

def googleHowTo():
    webbrowser.open('https://www.google.com/search?q=coinbase+how+to+download+csv')

def main():
    # convertToNewFormat('./test.csv')
    # return
    root = tkinter.Tk()
    root.title('Coinbase CSV Converter')
    root.geometry('500x200')
    root.resizable(False, False)   
    tkinter.Button(root, text='Select CSV file to open', command=selectCSV).pack()
    tkinter.Button(root, text='How to retrieve your CSV from Coinbase', command=googleHowTo).pack()
    tkinter.Button(root, text='Exit', command=exit).pack()
    tk.mainloop()
   


main()

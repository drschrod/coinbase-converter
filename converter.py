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


def getCurrentRowAsDict(row):
    # Skip if its not a Buy or Sell transaction or if this is the header row
    if row[1] not in ['Buy', 'Sell'] or row[0] == 'Timestamp':
        return None
    return {
        'Timestamp': row[0],
        'Transaction Type': row[1],
        'Asset': row[2],
        # 'Quantity Transacted': row[3],
        'USD Spot Price at Transaction': row[4],
        # 'USD Subtotal': row[5],
        'USD Total': row[6],
        # 'USD Fees': row[7],
        # 'Notes': row[8]
    }


def createNewRow(transactionType, assetName, usdPriceAtTransaction, proceeds, year, month, day):
    updatedRow = {
        'Purchase Date': "{}/{}/20".format(month, day) if transactionType == 'Buy' else '',
        'Date Sold': "{}/{}/20".format(month, day) if transactionType == 'Sell' else '',
        'Currency Name': assetName,
        'Cost Basis': usdPriceAtTransaction,
        'Proceeds': proceeds,
    }
    print(updatedRow)
    return updatedRow


def convertToNewFormat(sourcefile):
    newRows = []
    with open(sourcefile, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            currentRow = getCurrentRowAsDict(row)
            if currentRow is None:
                continue
            transactionType = currentRow['Transaction Type']
            assetName = currentRow['Asset']
            usdPriceAtTransaction = currentRow['USD Spot Price at Transaction']
            proceeds = currentRow['USD Total']
            timestamp = currentRow['Timestamp'].split('T')[0].split('-')

            # Get year month day from timestamp
            year = 20  # Abbreviated. NOTE: If this is used in the future for 2021 you must update this line
            month = timestamp[1]
            day = timestamp[2]
            newRows.append(createNewRow(transactionType, assetName,
                                        usdPriceAtTransaction, proceeds, year, month, day))
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
    print(name)
    newRows = convertToNewFormat(name)
    newFilename = saveToNewFormat(newRows)
    tkinter.messagebox.showinfo('Success', f'Success! File was saved to {newFilename}')

def googleHowTo():
    webbrowser.open('https://www.google.com/search?q=coinbase+how+to+download+csv')

def main():
    root = tkinter.Tk()
    root.title('Coinbase CSV Converter')
    root.geometry('500x200')
    root.resizable(False, False)   
    tkinter.Button(root, text='Select CSV file to open', command=selectCSV).pack()
    tkinter.Button(root, text='How to retrieve your CSV from Coinbase', command=googleHowTo).pack()
    tkinter.Button(root, text='Exit', command=exit).pack()
    tk.mainloop()
   


main()

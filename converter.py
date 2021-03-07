# Currency Name => Asset
# Purchase Date => Timestamp of row with transactionType === Buy || null
# Cost Basis    => USD Spot Price at Transaction
# Date Sold     => Timestamp of row when transactionType === Sell || null
# Proceeds      => USD Total (inclusive of fees)
# Timestamp	| Transaction Type	| Asset	| Quantity Transacted | USD Spot Price at Transaction | USD Subtotal |	USD Total (inclusive of fees) |	USD Fees |	Notes
import csv
from datetime import datetime


    
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
    updatedRow={}
    # Column Interpretations go here
    updatedRow['Currency Name'] = assetName
    updatedRow['Cost Basis'] = usdPriceAtTransaction
    updatedRow['Proceeds'] = proceeds
    if transactionType == 'Buy':
        updatedRow['Purchase Date'] = "{}/{}/20".format(month, day)
        updatedRow['Date Sold'] = ''
    elif transactionType == 'Sell':
        updatedRow['Purchase Date'] = ''
        updatedRow['Date Sold'] = "{}/{}/20".format(month, day)
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
            year = 20 # Abbreviated. NOTE: If this is used in the future for 2021 you must update this line
            month = timestamp[1]
            day = timestamp[2]
            newRows.append(createNewRow(transactionType, assetName, usdPriceAtTransaction, proceeds, year, month, day))
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
    except IOError as e:
        print("I/O error", e)
def main():
    newRows = convertToNewFormat('coinbase.csv')
    saveToNewFormat(newRows)

main()
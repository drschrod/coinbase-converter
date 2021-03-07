# Coinbase CSV Converter for Turbotax
## _Disclaimer/Warning: I am not guaranteeing the conversion is 100% accurate. It is up to you the user to review the converted document and discern whether or not it is valid._

## For Use in Tax Year 2020

I thought it was shady that Coinbase was pushing its users to a thirdparty source that requires you to _pay additional fees_ to get your own cryptocurrency transactions exported for use in Turbotax. I decided to make this script that _should_ convert the current CSV being exported by Coinbase.com to the format that is accepted by Turbotax.

### Current (stupid) headers provided by coinbase
| Timestamp	| Transaction Type	| Asset	| Quantity Transacted | USD Spot Price at Transaction | USD Subtotal |	USD Total (inclusive of fees) |	USD Fees |	Notes |
| ----------| ----------------- | ----- | ------------------- | ----------------------------- | ------------ | ------------------------------ | -------- | ------ |
---

### The headers the (TurboTax) csv parser requires are:
|Currency Name | Purchase Date | Cost Basis | Date Sold | Proceeds |
| ------------ | ------------- | ---------- | --------- | -------- |
---

### Assumed Conversions
```
Currency Name => Asset
Purchase Date => Timestamp of row with transactionType === Buy || null
Cost Basis    => USD Spot Price at Transaction
Date Sold     => Timestamp of row when transactionType === Sell || null
Proceeds      => USD Total (inclusive of fees)
```

## Requirements:
- Access to Python3
- Access to Unix terminal or Powershell

## How to use:
1. Download/Clone this Repo
2. From the root directory of this project run `python3 converter.py` or `python converter.py` ( depending on how you have it aliased. MacOS defaults to python to version 2)
3. From the GUI select the file you want converted.
4. When conversion is complete, the newly created file will be created in the same directory as the script.

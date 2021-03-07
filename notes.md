Current (stupid) headers provided by coinbase
Timestamp	Transaction Type	Asset	Quantity Transacted	USD Spot Price at Transaction	USD Subtotal	USD Total (inclusive of fees)	USD Fees	Notes

The headers your (TurboTax) csv parser requires are:
Currency Name	Purchase Date	Cost Basis	Date Sold	Proceeds

Currency Name => Asset
Purchase Date => Timestamp of row with transactionType === Buy || null
Cost Basis    => USD Spot Price at Transaction
Date Sold     => Timestamp of row when transactionType === Sell || null


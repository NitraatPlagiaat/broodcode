# BroodCode

Generate unique price-based codes for ordering for large groups at broodbode.nl. Allows people to order by transferring the code in cents to the order-master's bank account (using Tikkie for instance).

After the order are in, the script helps the order-master to place the order, by converting codes back to sandwich names in the same sort-order as the form.

## Usage

Run `python broodcode.py` to download sandwich info from broodbode.nl and create the order list. This list can be spread through any channel. If one person wants to order multiple things, multiple payments need to be made.

When the ordering deadline has been reached, create a file named `order.txt` in this directory, which contains the amounts you received in cents, one line per order. Like this:

```
651
738
551
```

After creating the file, run `python broodcode.py` again for it to translate the codes back to sandwich names (in order-form-order). Place the order, pay from the money you received, done.

Afterwards, perform a `rm order.txt data.pickle` to reset for the next order.

## Profit!

In order to make unique codes, prices have a margin on top of about 10 cents each on average. The order-master's profit!

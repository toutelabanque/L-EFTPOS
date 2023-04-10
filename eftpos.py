from gpiozero import Button
from requests import request
from tkinter import Tk, StringVar
from tkinter.ttk import Entry, Label
from os import environ

# Get business's account ID from environment variable else user input.
if environ.get('BUSINESS_ID'):
    business_id = environ['BUSINESS_ID']
else:
    business_id = input("What is your business's account ID at La Banque?")
    environ['BUSINESS_ID'] = business_id

root = Tk()

entry_contents = StringVar()
Entry(root, textvariable=entry_contents).pack()

label_contents = StringVar()
label_contents.set("Enter the amount due below.")
Label(root, textvariable=label_contents).pack()

mode = 'amount'


def type_(num: int):
    # Delete last `num` characters
    if num < 0:
        entry_contents.set(entry_contents.get()[0:num])
    # Append `num` to the `Entry`'s content (AKA type `num`)
    else:
        entry_contents.set(entry_contents.get() + str(num))


def clear():
    entry_contents.set("")


def submit():
    if mode == 'amount':
        global amount
        amount = entry_contents
        mode = 'payer-id'
        clear()
    else:
        response = request('POST', '127.0.0.1', json={
            "payer-id": business_id,
            "recipient-id": entry_contents,
            "amount": amount,
            "taxable": True
        })

        label_contents.set({200: 'Paid $' + response.content, 403: 'Failed; Must register EFTPOS', 404: 'Nonexistent user'}.get(response.status_code, 'Something went wrong'))

        mode = 'amount'
        clear()


numpad = [
    Button(17),  # 0
    Button(27),  # 1
    Button(22),  # 2
    Button(2),  # 3
    Button(3),  # 4
    Button(26),  # 5
    Button(23),  # 6
    Button(24),  # 7
    Button(25),  # 8
    Button(16),  # 9
]

for key in numpad:
    key.when_pressed = lambda: type_(numpad.index(key))

ok = Button(5)
ok.when_pressed = submit

backspace = Button(6)
backspace.when_pressed = lambda: type_(-1)

cancel = Button(4)
cancel.when_pressed = clear

root.mainloop()

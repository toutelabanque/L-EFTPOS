from gpiozero import Button
from requests import request
from tkinter import Tk, StringVar
from tkinter.ttk import Entry, Label
from os import environ

# Get business's account ID from environment variable else user input.
if environ.get('BUSINESS_ID'):
    business_id = environ['BUSINESS_ID']
else:
    business_id = input("What is your business's account ID at La Banque? ")
    environ['BUSINESS_ID'] = business_id

root = Tk()

entry_contents = StringVar()
Entry(root, textvariable=entry_contents).pack()

label_contents = StringVar()
label_contents.set("Please enter the amount due below.")
Label(root, textvariable=label_contents).pack()

mode = 'amount'


def type_(num: int):
    print(num)
    # Delete last `num` characters
    if num < 0:
        entry_contents.set(entry_contents.get()[0:num])
    # Append `num` to the `Entry`'s content (AKA type `num`)
    else:
        entry_contents.set(entry_contents.get() + str(num))
    return num


def clear():
    entry_contents.set("")


def submit():
    global mode
    if mode == 'amount':
        global amount
        amount = entry_contents
        mode = 'payer-id'
        clear()
        label_contents.set("Please enter your account ID at La Banque.")
    elif mode == 'payer-id':
        global payer_id
        payer_id = entry_contents
        mode = 'password'
        clear()
        label_contents.set("Please enter your password.")
    elif mode == 'password':
        response = request('POST', 'https://hpspectre.local/charge/', json={
            "payer-id": business_id,
            "recipient-id": entry_contents.get(),
            "amount": amount,
            "password": entry_contents,
            "taxable": True
        })
        label_contents.set({200: 'Paid $' + response.content, 401: 'Incorrect Password', 403: 'Failed; Must register EFTPOS',
                           404: 'Nonexistent user'}.get(response.status_code, 'Something went wrong'))  # Display response
        clear()
        mode = 'amount'
    else:
        raise ValueError


# Numpad
zero = Button(17)
zero.when_pressed = lambda: type_(0)
one = Button(27)
one.when_pressed = lambda: type_(1)
two = Button(22)
two.when_pressed = lambda: type_(2)
three = Button(2)
three.when_pressed = lambda: type_(3)
four = Button(3)
four.when_pressed = lambda: type_(4)
five = Button(26)
five.when_pressed = lambda: type_(5)
six = Button(23)
six.when_pressed = lambda: type_(6)
seven = Button(24)
seven.when_pressed = lambda: type_(7)
eight = Button(25)
eight.when_pressed = lambda: type_(8)
nine = Button(16)
nine.when_pressed = lambda: type_(9)

ok = Button(5)
ok.when_pressed = submit

backspace = Button(6)
backspace.when_pressed = lambda: type_(-1)

x = Button(4)
x.when_pressed = clear

root.mainloop()

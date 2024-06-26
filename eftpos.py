from gpiozero import Button
from requests import request, Response
from requests.exceptions import ConnectionError, JSONDecodeError, ReadTimeout
from tkinter import Tk, StringVar
from tkinter.ttk import Entry, Label
from socket import gaierror

# Get business's account ID from file else user input.
with open('config.txt', 'a+') as config:
    config.seek(0)
    if config.read():
        config.seek(0)
        business_id = config.read()
    else:
        business_id = input("What is your business's account ID at La Banque? ")
        config.write(business_id)

root = Tk()

entry_contents = StringVar()
entry = Entry(root, textvariable=entry_contents)
entry.pack()
entry.focus_set()

label_contents = StringVar()
label_contents.set('Credit[1] or Debit[2]?')
Label(root, textvariable=label_contents).pack()

mode = 'type'


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
    # Save the transaction type
    if mode == 'type':
        try:
            global transaction_type
            if int(entry_contents.get()) < 1:
                raise ValueError
            transaction_type = ('credit', 'debit')[int(entry_contents.get()) - 1]
            mode = 'amount'
            clear()
            label_contents.set("Please enter the amount due.")
        except (ValueError, IndexError):
            label_contents.set("Please choose either Credit[1] or Debit[2].")
    # Save the amount due (from cashier) and switch to getting customer's ID
    elif mode == 'amount':
        global amount
        try:
            amount = float(entry_contents.get())
            mode = 'payer-id'
            clear()
            label_contents.set("Please enter your account ID at La Banque.")
        except ValueError:
            label_contents.set("Invalid amount. Please try again.")
    # Save customer's ID and switch to getting their PIN
    elif mode == 'payer-id':
        global payer_id
        payer_id = entry_contents.get()
        mode = 'pin'
        clear()
        label_contents.set("Please enter your PIN.")
    elif mode == 'pin':
        label_contents.set("Authorizing...")
        # Make request and get response. Craft placeholder response on failure to connect.
        try:
            response = request('POST', 'https://hpspectre.local/charge/', json={
                "type": transaction_type,
                "payer-id": payer_id,
                "recipient-id": business_id,
                "amount": amount * 100,
                "pin": entry_contents.get(),
                "taxable": True
            }, verify=False, timeout=30.0)
        except (gaierror, ConnectionError, ReadTimeout):
            response = Response()
            response.status_code = 503
        try:
            content = response.json()
        except JSONDecodeError:
            content = "000"
        # Display response
        label_contents.set({201: 'Successfully paid $' + str(round((float(content[0]) + float(content[2]))/100, 2)), 205: 'Insufficient Funds', 401: 'Incorrect PIN', 403: 'Failed; Must register EFTPOS',
                        404: 'Nonexistent debit-enabled checking account', 503: 'La Banque is down at the moment'}.get(response.status_code, 'Something went wrong'))
        
    # Reset
        clear()
        mode = 'reset'
    else:
        label_contents.set("Please enter the amount due below.")
        mode = 'amount'


# Numpad
zero = Button(17, hold_repeat=True, hold_time=0.5, bounce_time=0.5)
zero.when_pressed = lambda: type_(0)
zero.when_held = lambda: type_(0)
one = Button(27, hold_repeat=True, hold_time=0.5, bounce_time=0.5)
one.when_pressed = lambda: type_(1)
one.when_held = lambda: type_(1)
two = Button(22, hold_repeat=True, hold_time=0.5, bounce_time=0.5)
two.when_pressed = lambda: type_(2)
two.when_held = lambda: type_(2)
three = Button(2, hold_repeat=True, hold_time=0.5, bounce_time=0.5)
three.when_pressed = lambda: type_(3)
three.when_held = lambda: type_(3)
four = Button(3, hold_repeat=True, hold_time=0.5, bounce_time=0.5)
four.when_pressed = lambda: type_(4)
four.when_held = lambda: type_(4)
five = Button(26, hold_repeat=True, hold_time=0.5, bounce_time=0.5)
five.when_pressed = lambda: type_(5)
five.when_held = lambda: type_(5)
six = Button(23, hold_repeat=True, hold_time=0.5, bounce_time=0.5)
six.when_pressed = lambda: type_(6)
six.when_held = lambda: type_(6)
seven = Button(24, hold_repeat=True, hold_time=0.5, bounce_time=0.5)
seven.when_pressed = lambda: type_(7)
seven.when_held = lambda: type_(7)
eight = Button(25, hold_repeat=True, hold_time=0.5, bounce_time=0.5)
eight.when_pressed = lambda: type_(8)
eight.when_held = lambda: type_(8)
nine = Button(16, hold_repeat=True, hold_time=0.5, bounce_time=0.5)
nine.when_pressed = lambda: type_(9)
nine.when_held = lambda: type_(9)

ok = Button(5, bounce_time=0.5)
ok.when_pressed = submit

backspace = Button(6, bounce_time=0.5)
backspace.when_pressed = lambda: type_(-1)

x = Button(4, bounce_time=0.5)
x.when_pressed = clear

root.mainloop()

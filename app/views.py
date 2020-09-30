from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from .models import Profile, saleOrder, purchaseOrder
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
import random

def registrationR(request):
    if request.method == 'POST':
        form = request.POST
        if form:
            username = form['username']
            email = form['email']
            password = form['password']
            user = User.objects.create_user(username=username, email=email, password=password)
            newUser = Profile(user=user)
            newUser.btcAmount = random.uniform(1, 10)
            newUser.save()
            form = LoginForm()
            return render(request, 'app/login.html', {})
        else:
            print('utente gia registrato')
    else:
        form = RegisterForm()
        return render(request, 'app/registration.html', {'form':form})

def loginR(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            #Accesso utente
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
    else:
        form = LoginForm()
        return render(request, 'app/login.html', {'form':form})

def home(request):
    if request.method == 'POST':
        values = request.POST
        thisUser = Profile.objects.get(user=request.user)
        if values:
            #Verfico se l'ordine in questione, è di acquisto o di vendita
            if "purchasePrice" in values:
                try:
                    price = values["purchasePrice"]
                    quantity = values['quantity']
                except:
                    HttpResponse('Invalid data entered!')
                else:
                    userBalance = thisUser.btcBalance #recupero il bilancio dell'utente
                    if float(price) < userBalance : #verifico se l'utente dispone del saldo minimo per effettuare l'acquisto
                        newPurchase = purchaseOrder(profile=thisUser, price=price, quantity=quantity)
                        newPurchase.save()

                        #filtro gli ordini di vendita con prezzo minore dell'ordine di acquisto,  recuperando il primo della lista
                        saleOrders = saleOrder.objects.filter(price__lt=newPurchase.price)[0]
                        
                        if saleOrders:
                            #registro i due ordini
                            purchaseOrder.objects.filter(_id=newPurchase._id).update(active=False)
                            thisUser.btcAmount += float(newPurchase.quantity)
                            thisUser.btcBalance -= float(newPurchase.price)
                            thisUser.save()
                            
                            saleOrder.objects.filter(_id=saleOrders._id).update(active=False)
                            saleProfile = saleOrders.profile

                            oldBalance = saleProfile.btcBalance                                
                            
                            saleProfile.btcAmount -= float(saleOrders.quantity)
                            saleProfile.btcBalance += float(saleOrders.price)
                            
                            profit = saleProfile.btcBalance - oldBalance #calcolo il profitto in btc
                            saleProfile.profit = profit
                            saleProfile.save()
                            HttpResponse('Registered order')
                        else:
                            HttpResponse("Impossible to perfom the operation!")

            else:
                try:
                    price = values["salePrice"]
                    quantity = values['quantity']
                except:
                    HttpResponse('Invalid data entered!')
                else:
                    userBtc = thisUser.btcAmount #recupero il numero di bitcoin che lutente possiede
                    if float(quantity) < userBtc:
                        newSale = saleOrder(profile=thisUser, price=price, quantity=quantity)
                        newSale.save()

        
        btcVal = thisUser.btcAmount
        return render(request, 'app/home.html', {'btcVal': btcVal})
    else:
        thisUser = Profile.objects.get(user=request.user)
        btcVal = thisUser.btcAmount
        return render(request, 'app/home.html', {'btcVal': btcVal})

    

def checkActiveOrders(request):
    response = []
    
    #Recupero gli ordini d'acquisto
    activePurOrders = purchaseOrder.objects.filter(active=True)
    for order in activePurOrders:
        response.append( {
            'id': str(order._id),
            'tipology': 'purchase',
            'datetime': order.datetime,
            'price': order.price,
            'quantity': order.quantity
        })
    
    #Recupero gli ordini di venditas
    activeSaleOrders = saleOrder.objects.filter(active=True)
    for order2 in activeSaleOrders:
        response.append( {
            'id': str(order2._id),
            'tipology': 'sale',
            'datetime': order2.datetime,
            'price': order2.price,
            'quantity': order2.quantity
        })
    
    return JsonResponse(response, safe=False)


def checkProfit(request):
    response = []
    userProfits = Profile.objects.all()
    for user in userProfits:
        if user.profit >= 0:
            response.append({
                'user': str(user._id),
                'balance': user.btcBalance,
                'btcAmount': user.btcAmount,
                'profit': f"+{user.profit}"
            })
        else:
            response.append({
                'user': str(user._id),
                'balance': user.btcBalance,
                'btcAmount': user.btcAmount,
                'profit': f"-{user.profit}"
            })
    return JsonResponse(response, safe=False)
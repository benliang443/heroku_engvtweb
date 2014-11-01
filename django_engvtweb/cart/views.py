from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from forms import *
from django_engvtweb.team_order.models import QbpPart
from changuito import CartProxy

#map of models to strings used in forms to reference
#each model.  Doing this just to avoid having to do an "eval(str)"
#in order to get the model class.

#Convention will be to just use the lowercased model name as a string when
#referencing it.

PRODUCT_MODELS = {
    QbpPart.get_slug_name(): QbpPart,
}

def add_item_to_shopping_cart(request):
    """
    Handles addition of items to the shopping cart. Call from any product page
    as POST from an AddToCart form.

    :param request:
    :return: HttpResponseRedirect to cart
    """

    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = int(form.cleaned_data['quantity'])
            object_type = form.cleaned_data['object_type']
            obj_id = form.cleaned_data['object_id']
            model = PRODUCT_MODELS[object_type]
            product = model.objects.get(id=obj_id)
            cart = request.cart
            cart.add(product, product.unit_price, quantity)
            return HttpResponseRedirect(reverse('cart:cart'))
    else:
        return Http404()

def render_shopping_cart(request):
    """
    Renders shopping cart index, and also handles updating of totals through formset rendered on page.
    """
    cart = request.cart
    if request.method == 'POST':
        formset = CartFormset(request.POST)
        #validate formset
        if formset.is_valid():
            #loop through each item to see if quantity has changed
            #if so, update quantity
            for form in formset:
                new_quantity = form.cleaned_data['quantity']
                item_id = form.cleaned_data['item_id']
                item = cart.get_item(item_id)
                if item.quantity != new_quantity:
                    if new_quantity == 0:
                        cart.remove_item(item_id)
                    item.update_quantity(new_quantity)
             #want to reload page if POST successful, so no need to redirect here

    #get initial data from cart
    initial_data = [{'item_id': item.id,
                     'quantity': int(item.quantity)} for item in cart]
    formset = CartFormset(initial=initial_data)
    return render(request, 'cart/index.html',
                  dict(cart=CartProxy(request), formset=formset))

def remove_item(request, item_id=None):

    if item_id is None:
        return Http404('No item ID given, cannot remove item.')

    cart = request.cart
    cart.remove_item(int(item_id))
    return HttpResponseRedirect(reverse('cart:cart'))




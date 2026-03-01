from django.db import transaction
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from mainapp.models import ProductMaster,PurchaseHistory,PurchaseItem,Denomination

from django.shortcuts import render

def billing_page(request):
    return render(request, "billing.html")


class ProductMasterAPI(APIView):

    def get(self, request):
        try:
            products_data = []
            product_obj = ProductMaster.objects.filter(is_active=True)

            for product in product_obj:
                products_data.append({
                    "product_id": product.id,
                    "name": product.name,
                    "stock": product.stock,
                    "purchase_price": product.purchase_price,
                    "tax_percentage": product.tax_percentage,
                    "created_at": product.created_at
                })

            return Response({"status": "success", "message": "Details fetched successfully", "data": products_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        try:
            data = request.data
            name = data.get('name')
            stock = data.get('stock')
            purchase_price = data.get('purchase_price')
            tax_percentage = data.get('tax_percentage')

            if not name:
                return Response({"status": "error", "message": "Product name is required"}, status=status.HTTP_400_BAD_REQUEST)

            if ProductMaster.objects.filter(name__iexact=name, is_active=True).exists():
                return Response({"status": "error", "message": "Product already exists", "is_valid": True}, status=status.HTTP_200_OK)

            transaction.set_autocommit(False)

            product = ProductMaster(
                name=name,
                stock=stock if stock else 0,
                purchase_price=purchase_price,
                tax_percentage=tax_percentage
            )
            product.save()

            transaction.commit()

            return Response({"status": "success", "message": "Product created successfully", "product_id": product.id, "is_valid": False}, status=status.HTTP_201_CREATED)

        except Exception as e:
            transaction.rollback()
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            data = request.data
            product_id = data.get("product_id")

            if not product_id:
                return Response({"status": "error", "message": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            product_obj = ProductMaster.objects.filter(id=product_id, is_active=True).first()
            if not product_obj:
                return Response({"status": "error", "message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

            transaction.set_autocommit(False)

            product_obj.name = data.get('name', product_obj.name)
            product_obj.stock = data.get('stock', product_obj.stock)
            product_obj.purchase_price = data.get('purchase_price', product_obj.purchase_price)
            product_obj.tax_percentage = data.get('tax_percentage', product_obj.tax_percentage)
            product_obj.save()

            transaction.commit()

            return Response({"status": "success", "message": "Product updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            transaction.rollback()
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request):
        try:
            data = request.data
            product_id = data.get("product_id")

            if not product_id:
                return Response({"status": "error", "message": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            product_obj = ProductMaster.objects.filter(id=product_id, is_active=True).first()
            if not product_obj:
                return Response({"status": "error", "message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

            product_obj.is_active = False
            product_obj.save()

            return Response({"status": "success", "message": "Product deleted successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class GenerateBillAPI(APIView):


    def calculate_change_from_db(self, balance):

        change = {}
        remaining = balance

        denominations = Denomination.objects.filter(available_count__gt=0).order_by("-value")

        for denom in denominations:

            if remaining <= 0:
                break

            max_needed = remaining // denom.value
            if max_needed > 0:

                usable_count = min(max_needed, denom.available_count)

                if usable_count > 0:
                    change[denom.value] = int(usable_count)

                    remaining -= denom.value * usable_count
                    denom.available_count -= usable_count
                    denom.save()

        if remaining != 0:
            raise Exception("Cannot provide exact change. Insufficient denominations.")

        return change

    def post(self, request):
        try:
            data = request.data
            customer_email = data.get("customer_email")
            products = data.get("products")
            amount_paid = Decimal(data.get("amount_paid"))
            paid_denomination = data.get("paid_denomination") 
            print("amount_paid",amount_paid) 
           
            for value, count in paid_denomination.items():
                print("value",value)
                print("count",count)
                denom = Denomination.objects.get(value=int(value))
                print("d",denom)
                denom.available_count += int(count)
                print("denom.available_count",denom.available_count)
                denom.save()

            
            total_without_tax = Decimal(0)
            total_tax = Decimal(0)

            purchase = PurchaseHistory.objects.create(
                customer_email=customer_email,
                amount_paid=amount_paid
            )

            for item in products:
                product = ProductMaster.objects.get(id=item["product_id"])

                if product.stock < item["quantity"]:
                    raise Exception("Insufficient stock")

                quantity = item["quantity"]
                print("quatity",quantity)
                price = product.purchase_price
                print("price",price)
                tax = price * (product.tax_percentage / 100)
                print("tax",tax)
                total_price = (price + tax) * quantity
                print("total_price",total_price)

                total_without_tax += price * quantity
                total_tax += tax * quantity

                PurchaseItem.objects.create(
                    purchase=purchase,
                    product=product,
                    quantity=quantity,
                    unit_price=price,
                    tax_amount=tax,
                    total_price=total_price
                )

                product.stock -= quantity
                product.save()

            net_total = total_without_tax + total_tax
            rounded_total = round(net_total)
            print("round_total",rounded_total)
            balance = amount_paid - Decimal(rounded_total)

            balance = amount_paid - Decimal(rounded_total)
            print("balance",balance)

            # If exact amount
            if balance == 0:
                change_given = {}

            # If extra amount
            elif balance > 0:
                change_given = self.calculate_change_from_db(balance)

            # Safety case (optional, just in case)
            else:
                return Response({"status": "error", "message": "Payment is less than bill amount"},status=400)
           

            # Save totals
            purchase.total_without_tax = total_without_tax
            purchase.total_tax = total_tax
            purchase.net_total = net_total
            purchase.rounded_total = rounded_total
            purchase.balance = balance
            purchase.change_given = change_given
            purchase.save()

            return Response({"status": "success","purchase_id": purchase.id,"net_total": rounded_total,"balance": balance,"change_given": change_given}, status=201)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=400)


    def get(self, request, purchase_id):
        try:
            purchase = PurchaseHistory.objects.get(id=purchase_id)
            items = purchase.items.all()

            items_data = []

            for item in items:
                items_data.append({
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "purchase_price": item.unit_price,
                    "quantity": item.quantity,
                    "tax_percentage": item.product.tax_percentage,
                    "tax_amount": item.tax_amount,
                    "total_price": item.total_price
                })

            bill_data = {
                "purchase_id": purchase.id,
                "customer_email": purchase.customer_email,
                "created_at": purchase.created_at,
                "items": items_data,
                "summary": {
                    "total_without_tax": purchase.total_without_tax,
                    "total_tax": purchase.total_tax,
                    "net_total": purchase.net_total,
                    "rounded_total": purchase.rounded_total,
                    "amount_paid": purchase.amount_paid,
                    "balance": purchase.balance
                },
                "change_given": purchase.change_given
            }

            return Response({
                "status": "success",
                "message": "Bill details fetched successfully",
                "data": bill_data
            }, status=status.HTTP_200_OK)

        except PurchaseHistory.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Purchase not found"
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)




class PurchaseHistoryListAPI(APIView):

    def get(self, request):
        try:
            email = request.GET.get("email")

            purchases = PurchaseHistory.objects.filter(customer_email=email)

            data = [{
                "purchase_id": p.id,
                "net_total": p.rounded_total,
                "date": p.created_at
            } for p in purchases]

            return Response({"status": "success", "data": data}, status=200)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=400)

class DenominationAPI(APIView):

    def get(self, request):
        try:
            denoms = Denomination.objects.all()
            data = [{"value": d.value, "available_count": d.available_count} for d in denoms]
            return Response({"status": "success", "data": data}, status=200)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=400)


    def post(self, request):
        try:
            data = request.data
            denom = Denomination.objects.create(
                value=data.get("value"),
                available_count=data.get("available_count", 0)
            )
            return Response({"status": "success", "id": denom.id}, status=201)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=400)
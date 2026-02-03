from django.shortcuts import render, redirect
from .models import FoodItem, FoodOrder
from accounts.models import Student
from django.db.models import Count


# ✅ Food Menu + Ordering Page
def food_menu(request):

    items = FoodItem.objects.all()
    students = Student.objects.all()

    # ✅ If form submitted
    if request.method == "POST":

        student_id = request.POST.get("student")
        item_id = request.POST.get("item")
        slot = request.POST.get("time_slot")

        # ✅ Safety Check: Food Item Missing
        if not item_id:
            return render(request, "food/menu.html", {
                "items": items,
                "students": students,
                "error": "⚠ Please select a food item before ordering!"
            })

        # ✅ Fetch student and food item
        student = Student.objects.get(id=student_id)

        try:
            item = FoodItem.objects.get(id=item_id)
        except FoodItem.DoesNotExist:
            return render(request, "food/menu.html", {
                "items": items,
                "students": students,
                "error": "⚠ Selected food item does not exist!"
            })

        # ✅ Create Food Order
        FoodOrder.objects.create(
            student=student,
            item=item,
            time_slot=slot
        )

        return redirect("order_success")

    # ✅ Show menu page
    return render(request, "food/menu.html", {
        "items": items,
        "students": students
    })


# ✅ Order Success Page
def order_success(request):
    return render(request, "food/success.html")


# ✅ Peak Rush Time Demand Tracking
def peak_times(request):

    demand = FoodOrder.objects.values("time_slot").annotate(total=Count("id"))
    
    # Calculate additional statistics for the enhanced template
    total_orders = sum(d['total'] for d in demand)
    busiest_slot = max(demand, key=lambda x: x['total'], default={'time_slot': 'No data', 'total': 0})
    max_orders = max([d['total'] for d in demand], default=1)

    return render(request, "food/peak.html", {
        "demand": demand,
        "total_orders": total_orders,
        "busiest_slot": busiest_slot,
        "max_orders": max_orders
    })

from django.shortcuts import render , redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import jwt
from .models import *
from .manager import *
from django.contrib.auth.models import User
from .forms import *
from .decorators import *
from  django.template.loader import get_template
from django.contrib.auth import login
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import admin
from django.contrib.admin import AdminSite
import datetime

def home(request):
    return render(request,'accounts/home.html')

@login_required(login_url='login')
@allowed_users(allowed_roles = ['admin','hr'])
def dashboard(request):
    return render(request,'accounts/dashboard.html')

@login_required(login_url='login')
@allowed_users(allowed_roles = ['employee'])
def user(request):
    employee = Employee.objects.filter(user=request.user).first()
    context = {'employee':employee}
    leave = Leave(user=request.user)
    print("==================================================")
    print("TOTAL NUMBER OF LEAVES IN YOUR ACCOUNT FROM BASE: ",leave.defaultdays)
    print("==================================================")
    return render(request,'accounts/user.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def manager(request):
    employee = Employee.objects.filter(user=request.user).first()
    leaves = Leave.objects.all_pending_leaves()
    context = {'employee':employee,'leave_count':len(leaves)}
    return render(request,'accounts/manager.html',context)

# @login_required(login_url='login')
# def submitleave(request):
#     context = {}
#     if request.method == "POST":
#         print(User.objects.filter(username=request.user).values_list('email',flat=True)[0])
#         print(type(User.objects.filter(username=request.user).values_list('email',flat=True)[0]))

#         employee = Employee.objects.get(Email_Address = User.objects.filter(username=request.user).values_list('email',flat=True)[0])
#         # empMgrDept = EmpMgrDept.objects.get(Emp_No_EmpMgrDept_id=employee)
#         # manager = Employee.objects.get(Emp_No=empMgrDept.Manager_Emp_ID_id)

#         # empleaverequest = EmpLeaveRequest(Emp_ID=employee, Emp_FullName=empMgrDept.Emp_FullName,
#         #                                   Leave_Type=request.POST['leavetype'],
#         #                                   Manager_Emp_No=manager, Manager_FullName=empMgrDept.Manager_FullName,
#         #                                   Begin_Date=request.POST['fromdate'],
#         #                                   End_Date=request.POST['todate'], Requested_Days=request.POST['requesteddays'],
#         #                                   Leave_Status="Pending", Emp_Comments=request.POST['comment'])
#         print(employee)
#     return render(request,'accounts/submitleave.html',context)

@unauthorized_user
def login_(request):
    # form = loginUserForm()
    new_user = False
    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            # employee = Employee.objects.filter(user = user)[0]
            # new_user = employee.last_login is None
            # if new_user:
            #     return HttpResponseRedirect(reverse('admin:password_change'))
            #     user.last_login = datetime.datetime.now()
            #     user.save(update_fields=['last_login'])
            return redirect('dashboard')
        else:
            messages.info(request,message="Invalid credentials!")
            return render(request,'accounts/login.html')
    context = {}
    return render(request,'accounts/login.html',context)

@unauthorized_user
def register(request):
    form = createUserForm()
    if request.method=="POST":
        form = createUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            messages.info(request,message="Invalid credentials!")
    context = {'form':form}
    return render(request,'accounts/register.html',context)

def logout_(request):
    logout(request)
    return redirect('home')

def status(request):
    return HttpResponse("You are in status page")

@login_required(login_url='login')
def applyleave(request):
    if request.method == 'POST':
        form = LeaveCreationForm(request.POST)
        if form.is_valid():
            instance = form.save(commit = False)
            user = request.user
            instance.user = user
            instance.save()
            print("LEAVE APPLIED SUCCESSFULLY!!!")
            print(request.POST['startdate'])
            print(request.POST['enddate'])
            # messages.success(request,"Submitted Successfully! Check <a href=\"{% url 'view_my_leave_table' %}\">STATUS</a>.")


            from django.core.mail import EmailMultiAlternatives
            from django.template import Context
            from django.template.loader import render_to_string
            leave_applied_by = request.user.email
            subject = "Trellissoft"
            content = { 'user':user,
                'startdate': request.POST['startdate'], 'enddate': request.POST['enddate'],
                'leavetype': request.POST['leavetype'], 'reason': request.POST['reason']
            }
            #to = request.POST.get('email')
            #to=["tejusbunny@gmail.com"]
            html_body = get_template('accounts/email.html').render(content)
            bod = ""
            sent_by = "tejusgowda95@gmail.com"
            leave_applied_by = request.user.email
            msg = EmailMultiAlternatives(subject=subject, from_email=sent_by,
                                         to=[leave_applied_by], body=bod)
            msg.attach_alternative(html_body, "text/html")
            msg.send()
            print("Mail sent successfully")
            return redirect('view_my_leave_table')
        messages.error(request, 'Failed to request a leave. Please check the dates')
        return redirect('applyleave')
    else:
        dataset = dict()
        form = LeaveCreationForm()
        employee= Employee.objects.filter(user = request.user).first()
        dataset['form'] = form
        dataset['title'] = 'Apply for Leave'
        context = {'form':form,
                    'dataset':dataset,
                    'employee':employee}
        return render(request,'accounts/leave.html',context)

# @login_required(login_url='login')
# @allowed_users(allowed_roles = ['manager','hr'])
# def leaves_list(request):
# 	leaves = Leave.objects.all_pending_leaves()
# 	return render(request,'accounts/leaves_recent.html',{'leave_list':leaves,'title':'leaves list - pending'})


@login_required(login_url='login')
@allowed_users(allowed_roles = ['employee'])
def view_my_leave_table(request):
    user = request.user
    leaves = Leave.objects.filter(user = user)
    employee = Employee.objects.filter(user = user).first()
    print(leaves)
    context = {}
    dataset = dict()
    dataset['leave_list'] = leaves
    dataset['employee'] = employee
    dataset['title'] = 'Leaves List'
    context={'dataset':dataset}
    print(dataset)
    print(context)
    return render(request,'accounts/leave_status_employee.html',context)


@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def leaves_list_mh(request):
	leaves = Leave.objects.all_pending_leaves()
	return render(request,'accounts/leave_list_mh.html',{'leave_list':leaves,'title':'leaves list - pending'})

@login_required(login_url='login')
def leaves_view(request,id):
    leave = get_object_or_404(Leave, id = id)
    print(leave)
    employee = Employee.objects.filter(user = leave.user)[0]
    print(employee)
    return render(request,'accounts/leave_detail_view.html',{'leave':leave,'employee':employee,'title':'{0}-{1} leave'.format(leave.user.username,leave.status)})

@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def leaves_view_mh(request,id):
	leave = get_object_or_404(Leave, id = id)
	employee = Employee.objects.filter(user = leave.user)[0]
	print(employee)
	return render(request,'accounts/leave_detail_view_mh.html',{'leave':leave,'employee':employee,'title':'{0}-{1} leave'.format(leave.user.username,leave.status)})


@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def approve_leave(request,id):
    leave = get_object_or_404(Leave, id = id)
    d=leave.leave_days
    print("==================================================")
    print("TOTAL NUMBER OF DAYS APPLIED : ",d)
    print("==================================================")
    leave.defaultdays-=d
    leave.save()
    if leave.defaultdays<0:
        print("you don't have any leaves left\n")
        print("you have taken"+-(leave.defaultdays)+"paid leaves")
        print("==================================================")
    else:
        print("TOTAL NUMBER OF DAYS YOU LEFT : ",leave.defaultdays)
        print("==================================================")
    user = leave.user
    employee = Employee.objects.filter(user = user)[0]
    leave.approve_leave
	# messages.error(request,'Leave successfully approved for {0}'.format(employee.get_full_name),extra_tags = 'alert alert-success alert-dismissible show')
    return redirect('leaves_approved_list')

@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def reject_leave(request,id):
	leave = get_object_or_404(Leave, id = id)
	leave.reject_leave
	# messages.success(request,'Leave is rejected',extra_tags = 'alert alert-success alert-dismissible show')
	return redirect('leave_rejected_list')

@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def leaves_approved_list(request):
	leaves = Leave.objects.all_approved_leaves() #approved leaves -> calling model manager method
	return render(request,'accounts/all_leaves_approved.html',{'leave_list':leaves,'title':'approved leave list'})

@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def leaves_rejected_list(request):
	leaves = Leave.objects.all_rejected_leaves() #rejected leaves -> calling model manager method
	return render(request,'accounts/all_leaves_rejected.html',{'leave_list':leaves,'title':'rejected leave list'})

@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def unapprove_leave(request,id):
    leave = get_object_or_404(Leave, id = id)
    d=leave.leave_days
    leave.defaultdays+=d
    leave.save()
    print("TOTAL NUMBER OF DAYS YOU LEFT : ",leave.defaultdays)
    print("==================================================")
    leave.unapprove_leave
    return redirect('leaves_list_mh') #redirect to unapproved list

@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def unreject_leave(request,id):
	leave = get_object_or_404(Leave, id = id)
	leave.status = 'pending'
	leave.is_approved = False
	leave.save()
	# messages.success(request,'Leave is now in pending list ',extra_tags = 'alert alert-success alert-dismissible show')
	return redirect('leaves_list_mh')


@login_required(login_url='login')
def edit_profile(request,id):
    obj= get_object_or_404(Employee,id=id)
    # if request.method=='POST':
    #     form=EditProfileForm(request.POST or None,request.FILES,instance=obj)
    #
    #     if form.is_valid():
    #         form.save()
    #         return redirect('/account/manager')
    #
    #
    # form=EditProfileForm(request.POST or None,request.FILES,instance=request.user)
    # print(form)
    # context={'form':form}
    # return render(request,'accounts/edit_profile.html',context)

    form = EditProfileForm(request.POST or None, instance= obj)
    context= {'form': form}

    if form.is_valid():
        obj= form.save(commit= False)

        obj.save()

        context= {'form': form}

        return redirect('/account/manager')

    else:
        context= {'form': form,
                   'error': 'The form was not updated successfully. Please enter in a title and content'}
        return render(request,'accounts/edit_profile.html',context)

# def days_left(request,id):
#     leave = get_object_or_404(Leave, id = id)
# 	d=leave.leave_days()
#     leave.defaultdays-=int(d)
# 	leave.save()

from .models import *
from externalfeeds.jira_helper import *
from .enmconmgr import *

logger = logging.getLogger(__name__)

def close_jira(ticket_number):
    try:
        orders = Order.objects.filter(jira_ticket__ticket_number = ticket_number)
    except Order.DoesNotExist:
        orders = Order([])

    open_orders = 0
    at_least_one_order_is_approved = False
    at_least_one_order_is_declined = False

    for order in orders:

        if order.is_approved == False and order.is_declined == False:
            open_orders = open_orders+1
        if order.is_approved == True:
            at_least_one_order_is_approved = True
        if order.is_declined == True:
            at_least_one_order_is_declined = True

    if open_orders == 0:
        if at_least_one_order_is_approved == True and at_least_one_order_is_declined == True:
            closeJira(ticket_number,"Part of account was rejected, please see comments","Resolved")          
        elif at_least_one_order_is_approved == True :
            closeJira(ticket_number,"All accounts were accepted","Resolved")
        else:
            closeJira(ticket_number,"Account(s) has been rejected","Cancelled")
        try:
            jira = JiraTicket.objects.get(ticket_number = ticket_number)
            jira.is_closed = True
            jira.save()
        except Order.DoesNotExist:
            jira = jira([])

def remove_account_helper(account):
    for system in System.objects.filter(account__name=account.name):
        if "ENM" in str(system.type):
            user_exist = check_enmuser(account.name,system)
            if user_exist == 27:
                raise Exception("Can't check enm user.")
            elif user_exist == 28:
                raise Exception("Can't get SED.")
            elif user_exist == 22:
                raise Exception("Can't establish session towards ENM.")     
            elif user_exist == 0:
                logger.info("Remove account for: "+account.name+" on system: "+system.name)


                not_removed = remove_enm_account(account.name,system.name)
                if not_removed == 27:
                    raise("Can't remove account.")
                elif user_exist == 28:
                    raise("Can't get SED.")        
                elif not_removed == 1:
                    try:
                        enmaccount =  ENMUser.objects.get(account = account,system = system)
                    except ENMUser.DoesNotExist:
                        enmaccount = None
                    try:                            
                        enmaccount.delete()
                        account.systems.remove(system)
                        return "OK"
                    except Exception as e :
                        raise Exception("Account "+account.name+" on system "+system.name+" has been removed. But AMS account protected" + e)   

                else:
                   raise Exception( "Account "+account.name+" on system "+system.name+" is not removed.")
            else:
                try:
                    enmaccount =  ENMUser.objects.get(account = account,system = system)
                except ENMUser.DoesNotExist:
                    enmaccount = None
                try:                            
                    enmaccount.delete()
                    account.systems.remove(system)
                except Exception as e :
                    raise Exception("Account "+account.name+" on system "+system.name+" has been removed. But AMS account protected" + e)  
                
                raise Exception( "Account "+account.name+" doest not exist on system - removing from AMS: "+system.name+".")
            
        ############ EO #################    
        elif str(system.type) == "EO":
            #print("Verify ",system.type," if account exists.")
            raise Exception("Not implemented yet")
        #elif str(system.type) == "cENM":
        #    print("Verify ",system.type," if account exists.")
        #    message = "Not implemented yet"
        #    status = "Unknown"
        elif str(system.type) == "EIC":
  
            raise Exception("Not implemented yet")
        else:

            raise Exception("System Type not known")
        

def remove_system_account_helper(account,system):

        if "ENM" in str(system.type):

            user_exist = check_enmuser(account.name,system)
            if user_exist == 27:
                raise Exception("Can't check enm user.")
            elif user_exist == 28:
                raise Exception("Can't get SED.")
            elif user_exist == 22:
                raise Exception("Can't establish session towards ENM.")     
            elif user_exist == 0:
                logger.info("Remove account for: "+account.name+" on system: "+system.name)


                not_removed = remove_enm_account(account.name,system.name)
                if not_removed == 27:
                    raise("Can't remove account.")
                elif user_exist == 28:
                    raise("Can't get SED.")        
                elif not_removed == 1:
                    try:
                        enmaccount =  ENMUser.objects.get(account = account,system = system)
                    except ENMUser.DoesNotExist:
                        enmaccount = None
                    try:                            
                        enmaccount.delete()
                        account.systems.remove(system)
                        return "OK"
                    except Exception as e :
                        raise Exception("Account "+account.name+" on system "+system.name+" has been removed. But AMS account protected" + str(e))   

                else:
                   raise Exception( "Account "+account.name+" on system "+system.name+" is not removed.")
            else:
                try:
                    enmaccount =  ENMUser.objects.get(account = account,system = system)
                except ENMUser.DoesNotExist:
                    enmaccount = None
                try:                            
                    enmaccount.delete()
                    account.systems.remove(system)
                except Exception as e :
                    raise Exception("Account "+account.name+" on system "+system.name+" has been removed. But AMS account protected" + str(e))  
                
                raise Exception( "Account "+account.name+" doest not exist on system - removing from AMS: "+system.name+".")
        ############ EO #################    
        elif str(system.type) == "EO":

            raise Exception("Not implemented yet")
        #elif str(system.type) == "cENM":
        #    print("Verify ",system.type," if account exists.")
        #    message = "Not implemented yet"
        #    status = "Unknown"
        elif str(system.type) == "EIC":

            raise Exception("Not implemented yet")
        else:

            raise Exception("System Type not known")
    
def check_if_account_active(account):
    if account.systems.exists():
        account.is_active = True
    else:
        account.is_active = False
    account.save()
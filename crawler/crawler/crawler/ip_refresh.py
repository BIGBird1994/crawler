import os
import time



release_command = 'echo Y |gcloud compute addresses delete {} --region {} '
del_command = 'echo Y|gcloud compute instances delete-access-config {} \
    --access-config-name "External NAT" --zone us-west1-b'
create_command = 'gcloud compute addresses create {} --region {}'
add_commamd = 'echo Y|gcloud compute instances add-access-config  {}\
   --access-config-name "External NAT"  --address  {}'
grep_command = 'gcloud compute addresses list| grep {}'



def refresh_ip(last_ip_name,ip_name,region,instance):
    
    try:
        os.system(release_command.format(last_ip_name,region))
        os.system(create_command.format(ip_name,region))
        ip = os.popen(grep_command.format(ip_name))
        ip_address = ip.read().split()[1]
        print(ip_address)
        os.system(del_command.format(instance))
        time.sleep(3)
        os.system(add_commamd.format(instance,ip_address))
        print('==== {} ip_address change to {}'.format(instance,ip_address))
    except Exception as e:
        print(e)
        

    
    
    

    
refresh_ip('amazon-ip','amazon-ip','us-west1','spider-05')

    


# meraki-purger.py

### Overview 
Deletes every network in your organization. Lock the ones you don't want to delete

### How to run
Python 3.6+ needed.
The script uses the python ```requests``` module to make the calls to the Meraki Dashboard API. 
Run ```pip install requests``` to install it.
I used some color coding for the script output. 

In Windows, it is likely that you have to enable it in the Registry Editor: 
https://user-images.githubusercontent.com/5589855/36943005-11e41fe2-1f36-11e8-9401-7ac40d300f10.png

### --help output
 ```usage: purger.py [-h] -k KEY [-o] [-d  | -l  | -u ]

Purge your organization easily

optional arguments:
  -h, --help         show this help message and exit
  -o , --org         List networks in that organization
  -d , --delete      Network ID to delete. Type <purge> instead to delete
                     every network that is not locked
  -l , --lock        Network ID to lock. Locks a network so it cannot be
                     deleted. Type <show> instead to print your locked
                     networks
  -u , --unlock      Network ID to unlock. Unlocks a network so it can be
                     deleted

required arguments:
  -k KEY, --key KEY  API Key
```

## Arguments

### --key

The only required argument. If the --key argument is  only one passed, it prints your organizations:

```
C:\Users\agustin.algorta>python purger.py -k <api_key>

You have 2 organizations linked to your account, with the following IDs and names:

<org_id>, AGUS API_TEST ORG

<org_id>, AgusOrg

```
### --org

Prints your networks in that organization. The --org argument is required when executing the --unlock, --lock and --delete methods.

```
C:\Users\agustin.algorta>python purger.py -k <api_key> -o <org_id>

You have 4 networks in your organization, with the following IDs and names:

<net_id>, important_network

<net_id>, test_network3

<net_id>, test_network1

<net_id>, test_network2

```
### --lock

Stores the network id passed as an argument in a .txt file in the running directory with the name 'locked_in_org_<org_id>.txt' 
```
C:\Users\agustin.algorta>python purger.py -k <api_key> -o <org_id> -l <net_id>

Network <important_network> locked

```
Now when printing your networks it will show which ones you have locked

```
C:\Users\agustin.algorta>python purger.py -k <api_key> -o <org_id>

You have 4 networks in your organization, with the following IDs and names:

<net_id>, important_network, LOCKED

<net_id>, test_network3

<net_id>, test_network1

<net_id>, test_network2


```
### --unlock
Removes the network id passed as an argument from the .txt file created

```
C:\Users\agustin.algorta>python purger.py -k <api_key> -o <org_id> -u <net_id>

Network unlocked
```
### --delete

Deletes the network passed as an argument. If instead you pass 'purge' as an argument, deletes every network not locked.
 
 ```
 C:\Users\agustin.algorta>python purger.py -k <api_key> -o <org_id> -d <net_id>

Delete completed

The remaining networks are:

<net_id>, important_network

<net_id>, test_network1

<net_id>, test_network2
```
```
C:\Users\agustin.algorta>python purger.py -k <api_key> -o <org_id> -d purge

Your locked networks are:

<net_id>

Purge completed
```
```
C:\Users\agustin.algorta>python purger.py -k <api_key> -o <org_id>

You have 1 networks in your organization, with the following IDs and names:

<net_id>, important_network, LOCKED

```

## How to add new arguments

You can easily add new arguments to the script following this 3 steps:

1. Declare the new argument using argparse.

2. Add conditional to check that the new argument is not passed in order to trigger the ```create_json_orgs``` method
```
def main():

    if args.org is None:

        if args.delete is None:

            if args.lock is None:

                if args.unlock is None:
                   
                   **if args.new_argument is None:**

                       create_json_orgs(args.key)
```
3. Add conditional to check if the argument is passed in order to trigger the new method.
```
    elif args.delete is not None:
        if args.delete == 'purge' or args.delete == 'PURGE':
            purge_networks(args.key, args.org)
        else:
            delete_network(args.key, args.org, args.delete)

    elif args.lock is not None:
        lock_network(args.key, args.org, args.lock)

    elif args.unlock is not None:
        unlock_network(args.unlock, args.org)
     
    **elif args.new_argument is not None:**
        new_method(args*)
```

  
  
 ## Future enhancements
 
 - Add ASCII tables in output
 - Set -p its own purge flag
 
 

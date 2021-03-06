import argparse
import json
import requests
import os
import time

API_EXEC_DELAY = 0.21  # Delay added to avoid hitting dashboard API max request rate


def is_in_org(network_id, networks_json):
    for i in range(len(networks_json)):
        if network_id == networks_json[i]['id']:
            return True
    return False


def reads_from_file_nodup(org_id):
    list1 = []
    # reads from file with locked ids and strip from them the '\n' at the end
    [list1.append(line.strip()) for line in open('locked_in_org_' + org_id + '.txt', 'r')]
    # ensures that there's no duplicates in the text
    list1 = list(dict.fromkeys(list1))
    return list1


def get_net_name_from_id(id, networks_json):
    for i in networks_json:
        if i['id'] == id:
            return i['name']


def create_json_orgs(apikey):
    orgs = requests.get('https://api.meraki.com/api/v0/organizations',
                        headers={"X-Cisco-Meraki-API-Key": apikey})

    if orgs.ok:
        # returns True if http code response is less than 400
        # loads() transform string into json object (same as dictionary in python)
        orgs_json = json.loads(orgs.text)
        print('\u001b[36m\nYou have {} organizations linked to your account, with the following IDs and '
              'names:'.format(len(orgs_json)))
        for i in range(len(orgs_json)):
            print('\u001b[36;1m\n{}, {}'.format(orgs_json[i]['id'], orgs_json[i]['name']))
        # Resets color coding
        print('\u001b[0m')
    else:
        print('\nError ' + str(orgs.status_code))


def create_json_networks(apikey, org_id):
    networks = requests.get('https://api.meraki.com/api/v0/organizations/' + org_id + '/networks',
                            headers={"X-Cisco-Meraki-API-Key": apikey})
    if networks.ok:
        networks_json = json.loads(networks.text)
        return networks_json
    else:
        print('\nError ' + str(networks.status_code))
        exit()  # I used exit() method here because the create_json_networks method is used by more methods


def unlock_network(network_id, org_id):
    try:
        locked_ids = reads_from_file_nodup(org_id)
    except FileNotFoundError:
        print('\nYou have 0 networks locked')
        exit()

    try:
        # removes networkID from list
        locked_ids.remove(network_id)
    except ValueError:
        print('\nNetwork ID not found')
        exit()

    if len(locked_ids) > 0:
        # Writes new locked list without removed value
        with open('locked_in_org_' + org_id + '.txt', 'w') as f:
            for i in locked_ids:
                f.write(i + '\n')
    else:
        # deletes .txt file if theres no more locked networks
        os.remove('locked_in_org_' + org_id + '.txt')

    print('\nNetwork unlocked')


def lock_network(apikey, org_id, network_id):
    networks_json = create_json_networks(apikey, org_id)
    try:
        locked_ids = reads_from_file_nodup(org_id)
    except FileNotFoundError:
        if network_id == 'show' or network_id == 'SHOW':
            print('\nNo locked networks in your organization')
            exit()

        elif is_in_org(network_id, networks_json):

            # creates new .txt file if the id passed is in the organization
            with open('locked_in_org_' + org_id + '.txt', 'w') as f:
                f.write(network_id + '\n')
                l_id_p = list()
                l_id_p.append(network_id + '\n')
            print("\nNetwork '" + get_net_name_from_id(network_id, networks_json) + "' locked")
        else:
            # doesnt create .txt if netID is not found
            print("\nNetwork ID not found in org " + org_id)
        exit()

    if network_id == 'show' or network_id == 'SHOW':
        print('\nYour locked networks are:')
        for i in locked_ids:
            print('\n' + i)
    elif is_in_org(network_id, networks_json):
        if network_id in locked_ids:
            print('\nNetwork already locked')
        else:
            locked_ids.append(network_id)
            # Writes the .txt with the new netID value appended
            with open('locked_in_org_' + org_id + '.txt', 'w') as g:
                for i in locked_ids:
                    g.write(i + '\n')
            print("\nNetwork '" + get_net_name_from_id(network_id, networks_json) + "' locked")
            exit()
    else:
        print('\nNetwork not found in org ' + org_id)


def delete_network(apikey, org_id, network_id):
    try:
        locked_ids = reads_from_file_nodup(org_id)

    except FileNotFoundError:
        delete = requests.delete('https://api.meraki.com/api/v0/networks/' + network_id,
                                 headers={"X-Cisco-Meraki-API-Key": apikey})

        if delete.ok:
            print('\nDelete completed')

        else:
            print('\nError ' + str(delete.status_code))
            exit()
        networks_json = create_json_networks(apikey, org_id)
        print('\nYou have now ' + str(len(networks_json)) + ' networks in your organization')
        exit()

    # checks if netID passed is locked
    if network_id not in locked_ids:

        delete = requests.delete('https://api.meraki.com/api/v0/networks/' + network_id,
                                 headers={"X-Cisco-Meraki-API-Key": apikey})

        if delete.ok:
            print('\nDelete completed')

        else:
            print('\nError ' + str(delete.status_code))
            exit()
        time.sleep(API_EXEC_DELAY)
        networks_json = create_json_networks(apikey, org_id)

        print('\n\nYou have now ' + str(len(networks_json)) + ' networks in your organization')
    else:
        print('\nYou are trying to delete a locked network, unlock it first to delete it')


def purge_networks(apikey, org_id):
    networks_json = create_json_networks(apikey, org_id)
    try:
        locked_id_txt = reads_from_file_nodup(org_id)
    except FileNotFoundError:
        y_n = input(
            '\nNo locked networks found. \n\nDo you want to delete all of them? (Y/N):').lower()  # using -d purge with no locked networks

        if y_n == 'y' or y_n == 'yes':
            for i in range(len(networks_json)):
                r_d = requests.delete('https://api.meraki.com/api/v0/networks/' + networks_json[i]['id'],
                                      headers={"X-Cisco-Meraki-API-Key": apikey})
                if r_d.ok:
                    print("\n\n'" + networks_json[i]['name'] + "', " + networks_json[i]['id'] + " deleted successfully")
                    time.sleep(API_EXEC_DELAY)
                    continue
                else:
                    print('\nError ' + str(r_d.status_code))
                    exit()
            print('\nPurge completed')
            exit()
        if y_n == 'n' or y_n == 'no':
            print('\nPurge aborted')
            exit()
        else:
            print('\nBad input')
            exit()

    locked_ids = list()
    for i in range(len(networks_json)):
        for j in range(len(locked_id_txt)):
            if networks_json[i]['id'] == locked_id_txt[j]:  # checks that the locked ID that is in the .txt file is actually in the network
                locked_ids.append(networks_json[i]['id'])
    print('\nYour locked networks are:')
    for i in locked_ids:
        print('\n' + i + ', ' + get_net_name_from_id(i, networks_json))
        print('\n\n')

    # get the IDs of the network to delete
    network_ids = list()
    for i in range(len(networks_json)):
        network_ids.append(networks_json[i]['id'])
    networks_id_to_delete = list(set(network_ids) - set(locked_ids))

    if len(networks_id_to_delete) == 0:  # if all networks are locked
        print('\n\nNo networks to delete')
    else:
        for i in networks_id_to_delete:
            delete_r = requests.delete('https://api.meraki.com/api/v0/networks/' + i,
                                       headers={"X-Cisco-Meraki-API-Key": apikey})

            if delete_r.ok:
                print("\n" + i + ", " + "'" + get_net_name_from_id(i, networks_json) + "'" + " deleted successfully")
                time.sleep(API_EXEC_DELAY)
                continue
            else:
                print('\nError ' + str(delete_r.status_code))
                exit()

        print('\nPurge completed \n\nYou have deleted ' + str(len(networks_id_to_delete)) + ' networks')

    with open('locked_in_org_' + org_id + '.txt', 'w') as g:  # protection against manually editing the .txt file
        for i in locked_ids:
            g.write(i + '\n')


###################
##               ##
##      MAIN     ##
##               ##
###################


def main():
    parser = argparse.ArgumentParser(description='Purge your organization easily')

    required = parser.add_argument_group('required arguments')

    required.add_argument('-k', '--key', type=str, required=True, help='API Key')
    parser.add_argument('-o', '--org', metavar='', type=str, required=False, help='List networks in that organization')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--delete', metavar='', type=str, required=False,
                       help='Network ID to delete. Type <purge> instead to delete every network that is not locked')

    group.add_argument('-l', '--lock', metavar='', type=str, required=False,
                       help='Network ID to lock. Locks a network so it cannot be deleted. Type <show> instead to print your locked networks')
    group.add_argument('-u', '--unlock', metavar='', type=str, required=False,
                       help='Network ID to unlock. Unlocks a network so it can be deleted')

    args = parser.parse_args()

    if args.org is None:

        if args.delete is None:

            if args.lock is None:

                if args.unlock is None:
                    create_json_orgs(args.key)

    elif args.delete is not None:
        if args.delete.lower() == 'purge':
            purge_networks(args.key, args.org)
        else:
            delete_network(args.key, args.org, args.delete)

    elif args.lock is not None:
        lock_network(args.key, args.org, args.lock)

    elif args.unlock is not None:
        unlock_network(args.unlock, args.org)

    else:

        try:
            locked_ids = reads_from_file_nodup(args.org)
        except FileNotFoundError:
            locked_ids = list()

        networks_json = create_json_networks(args.key, args.org)

        if len(networks_json) > 0:
            print('\u001b[36m\nYou have {} networks in your organization, with the following IDs and names:'.format(
                len(networks_json)))

            for i in range(len(networks_json)):
                if networks_json[i]['id'] in locked_ids:
                    print('\u001b[36;1m\n' + '{}, {}'.format(networks_json[i]['id'],
                                                             networks_json[i]['name']) + ', LOCKED')
                else:
                    print('\u001b[36;1m\n' + '{}, {}'.format(networks_json[i]['id'],
                                                             networks_json[i]['name']))
        else:
            print('\u001b[36m\nYou have 0 networks in your organization')

        print('\u001b[0m')  # resets color coding

    if (args.delete is not None or args.lock is not None or args.unlock is not None) and args.org is None:
        print('\n -o org_id input needed')


if __name__ == '__main__':
    main()


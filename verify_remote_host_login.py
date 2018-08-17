import paramiko
import argparse

def verify_login(host, user, passwd):
    try:
        ssh_session = paramiko.SSHClient()
        ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_session.connect(host, username=user, password=passwd)
        return ssh_session
    except paramiko.ssh_exception.AuthenticationException as error:
        print "wrong username/password combination"
        return 0
    except paramiko.ssh_exception.NoValidConnectionsError as error:
        print error
        return 0
    except IOError as error:
        print error
        return 0

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, help='host ip', required=False)
    parser.add_argument("--username", type=str, help='host ip', required=False)
    parser.add_argument("--password", type=str, help='host ip', required=False)
    args = parser.parse_args()
    return [args.host, args.username, args.password]


if __name__ == "__main__":
    if not get_arguments():
        host = "192.168.1.1"
        username = "test"
        passwd = "test"
    else:
        host, username, passwd = get_arguments()

    ssh_handle = verify_login(host, username, passwd)
    if ssh_handle:
        print("successfuly connected to %s" % host) 
        ssh_handle.close()
    else:
        print("connection error")

import paramiko
import os

# rackIp =[f"10.6.65.1",f"10.6.78.1",f"10.6.71.1",f"10.6.69.1"]
#
#
for rack in rackIp:
    try:
        print("Getting "+ rack)
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        target_host = rack
        client.connect(hostname=target_host, port=22, username="root", password="fortinet", timeout=1)
        stdin, stdout, stderr = client.exec_command("cd /var/log/bit_pro; find ./* -maxdepth 1 -name 'FGT61F*.log'")
        # stdin, stdout, stderr = client.exec_command(
        #     "cd /var/log/bit_pro; find ./* -maxdepth 1 -name 'FG33E1*.log'| grep '2019-9-2'")
        data = stdout.read()
        data_str = data.decode("utf-8")
        data_str = data_str.split('\n')
        data_str = filter(None, data_str)
        log_paths = [x for x in data_str]
        for log in log_paths:

            stdin, stdout, stderr = client.exec_command("cd /var/log/bit_pro; cp --backup=existing --suffix=.log -t /var/log/andy {}".format(log))
            stdout.readlines()

    except TimeoutError:
        print("Rack is not connected" + '\n')

    except IOError:
        print("Rack is not connected" + '\n')

    finally:
        client.close()


# for filename in os.listdir("F:\\logs\\IQC\\10-17-2019"):
#     if filename[20:]:
#         os.rename("F:\\logs\\IQC\\10-17-2019\\"+filename, "F:\\logs\\IQC\\10-17-2019\\dup\\{}".format(filename[:-4]))
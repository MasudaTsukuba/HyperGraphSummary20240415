import os

local_path = '../../data/'
remote_path = '/home/masuda/kdesvr1/ubuntu2204/PycharmProjects/HyperGraphSummarySpark20240829/data/'

local_files = os.listdir(local_path)
remote_files = os.listdir(remote_path)
for index in range(8890, 8899):
    for level in ['020', '050', '070', '080', '090']:
        remote_file0 = ''
        for remote_file in remote_files:
            if remote_file.find(str(index)) >= 0 and remote_file.find(level) >= 0 and remote_file.endswith('.csv') and os.path.isfile(remote_path + remote_file):
                # print(remote_file)
                with open(remote_path + remote_file, 'r') as input_file:
                    lines = input_file.readlines()
                    remote_length = len(lines)
                    remote_file0 = remote_file
                    # print(len(lines))
                break
        local_length = 0
        local_file0 = ''
        for local_file in local_files:
            # if local_file.find(str(index)) >= 0 and local_file.find(level) >= 0 and local_file.endswith('.csv') and os.path.isfile(local_path + local_file):
            if local_file.find(remote_file) >= 0 and local_file.startswith('889'):
                # print(local_file)
                with open(local_path + local_file, 'r') as input_file:
                    lines = input_file.readlines()
                    local_length = len(lines)
                    local_file0 = local_file
                    # print(len(lines))
                    # if local_length != remote_length or True:  # debug
                    if local_length != remote_length:
                        print('##############', local_file0, local_length)
                        print('>>>>>>>>>>>>>>', remote_file, remote_length)
pass